"""
Eden Emulator - Check for Latest & Auto-Download
Supports Windows, macOS, and Linux.

Build commands:
  Windows : pyinstaller --onefile --console --icon=eden.ico --name="Eden Checker" eden_update.py
  macOS   : pyinstaller --onefile --console --name="Eden Checker" eden_update.py
  Linux   : pyinstaller --onefile --console --name="Eden Checker" eden_update.py
"""

import urllib.request
import urllib.error
import json
import os
import sys
import re
import shutil
import subprocess
import threading
import time
import tarfile

# Platform
PLATFORM = sys.platform  # "win32", "darwin", "linux"
IS_WIN   = PLATFORM == "win32"
IS_MAC   = PLATFORM == "darwin"
IS_LIN   = PLATFORM.startswith("linux")

# Per-platform asset patterns
#   Windows : Eden-Windows-<anything>-amd64-msvc-standard.zip
#   macOS   : Eden-macOS-<anything>.dmg
#   Linux   : Eden-Linux-<anything>-amd64-gcc-standard.AppImage
if IS_WIN:
    ASSET_PATTERN = re.compile(r"Eden-Windows-.+amd64-msvc-standard\.zip", re.IGNORECASE)
elif IS_MAC:
    ASSET_PATTERN = re.compile(r"Eden-macOS-.+\.dmg", re.IGNORECASE)
else:
    ASSET_PATTERN = re.compile(r"Eden-Linux-.+amd64-gcc-standard\.AppImage", re.IGNORECASE)

API_URL_STABLE  = "https://git.eden-emu.dev/api/v1/repos/eden-emu/eden/releases?limit=10&page=1"
API_URL_NIGHTLY = "https://git.eden-emu.dev/api/v1/repos/eden-ci/nightly/releases?limit=10&page=1"
DOWNLOAD_DIR    = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
WINDOW_COLS     = 61
WINDOW_ROWS     = 16   # exact height of the main menu screen
W               = WINDOW_COLS

# Lines printed by header(): ===, title, platform, ===, blank
HEADER_ROWS     = 5


# ── Terminal helpers ──────────────────────────────────────────────────────────

def set_window_size(cols, rows):
    if IS_WIN:
        subprocess.call(f"mode con: cols={cols} lines={rows}", shell=True)
    # macOS/Linux: resize via ANSI escape (best-effort, terminal must support it)
    else:
        sys.stdout.write(f"\033[8;{rows};{cols}t")
        sys.stdout.flush()


def clear():
    os.system("cls" if IS_WIN else "clear")


def header(nightly):
    clear()
    mode = " [NIGHTLY]" if nightly else ""
    if IS_WIN:
        platform_label = "Windows"
    elif IS_MAC:
        platform_label = "macOS"
    else:
        platform_label = "Linux"
    print("=" * W)
    print(f"   Eden Emulator - Latest Release Checker{mode}")
    print(f"   Platform: {platform_label}")
    print("=" * W)
    print()


def getch():
    """Read a single keypress cross-platform (blocking)."""
    if IS_WIN:
        import msvcrt
        return msvcrt.getch()
    else:
        import tty, termios
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def countdown_or_cancel(seconds=3):
    """Returns True to proceed, False if user cancelled."""
    cancelled = threading.Event()

    def watch_key():
        getch()
        cancelled.set()

    t = threading.Thread(target=watch_key, daemon=True)
    t.start()

    for remaining in range(seconds, 0, -1):
        if cancelled.is_set():
            print(f"\r {' ' * 55}\r Cancelled.", flush=True)
            return False
        print(f"\r Starting in {remaining}s... (press any key to cancel) ", end="", flush=True)
        time.sleep(1)

    if cancelled.is_set():
        print(f"\r {' ' * 55}\r Cancelled.", flush=True)
        return False

    print(f"\r {' ' * 55}", end="", flush=True)
    return True


# ── Network ───────────────────────────────────────────────────────────────────

def fetch_releases(nightly=False):
    url = API_URL_NIGHTLY if nightly else API_URL_STABLE
    req = urllib.request.Request(url, headers={"User-Agent": "eden-update-checker/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def find_asset(release):
    for asset in release.get("assets", []):
        name = asset.get("name", "").strip()
        if ASSET_PATTERN.search(name):
            return asset
    return None


def get_releases_with_assets(nightly=False):
    releases = fetch_releases(nightly)
    results = []
    for r in releases:
        a = find_asset(r)
        if a:
            results.append((r, a))
    return results


def download_file(url, dest_path):
    req = urllib.request.Request(url, headers={"User-Agent": "eden-update-checker/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        total = int(resp.headers.get("Content-Length", 0))
        downloaded = 0
        chunk_size = 1024 * 64

        with open(dest_path, "wb") as f:
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                f.write(chunk)
                downloaded += len(chunk)

                if total:
                    pct = downloaded / total * 100
                    bar_len = 30
                    filled = int(bar_len * downloaded / total)
                    bar = "█" * filled + "░" * (bar_len - filled)
                    mb_done  = downloaded / 1_048_576
                    mb_total = total / 1_048_576
                    print(f"\r [{bar}] {pct:.0f}%  {mb_done:.1f}/{mb_total:.1f} MB", end="", flush=True)
                else:
                    print(f"\r Downloading... {downloaded / 1_048_576:.1f} MB", end="", flush=True)
    print()


# ── Install helpers ───────────────────────────────────────────────────────────

def install_windows(zip_path):
    import zipfile
    print()
    print(" Extracting...")
    final_name = "Eden Emulator"
    final_path = os.path.join(DOWNLOAD_DIR, final_name)

    if os.path.exists(final_path):
        shutil.rmtree(final_path)

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()
        top_dirs = {n.split("/")[0] for n in names if n.split("/")[0]}
        zf.extractall(DOWNLOAD_DIR)

    if len(top_dirs) == 1:
        extracted = os.path.join(DOWNLOAD_DIR, top_dirs.pop())
        if os.path.isdir(extracted) and extracted != final_path:
            os.rename(extracted, final_path)
    else:
        os.makedirs(final_path, exist_ok=True)
        for name in names:
            src = os.path.join(DOWNLOAD_DIR, name)
            if os.path.exists(src) and src != final_path:
                shutil.move(src, final_path)

    os.remove(zip_path)
    print(f' Done! Installed to: "{final_name}"')


def install_macos(file_path):
    filename = os.path.basename(file_path)
    print()

    if filename.endswith(".dmg"):
        # Mount the DMG and copy the .app out
        print(" Mounting DMG...")
        result = subprocess.run(
            ["hdiutil", "attach", file_path, "-nobrowse", "-quiet"],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"hdiutil attach failed: {result.stderr.strip()}")

        # Find mount point
        mount_point = None
        for line in result.stdout.splitlines():
            parts = line.split("\t")
            if len(parts) >= 3 and parts[2].strip().startswith("/Volumes/"):
                mount_point = parts[2].strip()
                break

        if not mount_point:
            raise RuntimeError("Could not find DMG mount point.")

        try:
            apps = [f for f in os.listdir(mount_point) if f.endswith(".app")]
            if not apps:
                raise RuntimeError("No .app found in DMG.")
            app_src = os.path.join(mount_point, apps[0])
            app_dst = os.path.join("/Applications", apps[0])
            print(f" Copying {apps[0]} to /Applications...")
            if os.path.exists(app_dst):
                shutil.rmtree(app_dst)
            shutil.copytree(app_src, app_dst)
        finally:
            subprocess.run(["hdiutil", "detach", mount_point, "-quiet"])

        os.remove(file_path)
        print(f' Done! Installed to: /Applications/{apps[0]}')

    elif filename.endswith(".tar.gz"):
        print(" Extracting...")
        final_name = "Eden Emulator"
        final_path = os.path.join(DOWNLOAD_DIR, final_name)
        if os.path.exists(final_path):
            shutil.rmtree(final_path)

        with tarfile.open(file_path, "r:gz") as tf:
            members = tf.getnames()
            top_dirs = {m.split("/")[0] for m in members if m.split("/")[0]}
            tf.extractall(DOWNLOAD_DIR)

        if len(top_dirs) == 1:
            extracted = os.path.join(DOWNLOAD_DIR, top_dirs.pop())
            if os.path.isdir(extracted) and extracted != final_path:
                os.rename(extracted, final_path)

        os.remove(file_path)
        print(f' Done! Installed to: "{final_name}"')


def install_linux(appimage_path):
    print()
    print(" Installing AppImage...")
    dest = os.path.join(DOWNLOAD_DIR, "Eden-Emulator.AppImage")
    if os.path.exists(dest):
        os.remove(dest)
    shutil.move(appimage_path, dest)
    os.chmod(dest, 0o755)
    print(f' Done! Saved to: "{dest}"')
    print(" Run it with: ./Eden-Emulator.AppImage")


def install(file_path):
    if IS_WIN:
        install_windows(file_path)
    elif IS_MAC:
        install_macos(file_path)
    else:
        install_linux(file_path)


# ── Setup (Keys, NAND, Firmware) ─────────────────────────────────────────────

def setup_eden():
    """
    1. Make sure Eden's data folder exists (Windows briefly launches eden.exe;
       Linux/macOS just create it directly).
    2. Copy System & User/* folders  → <eden data>/nand/
    3. Copy Keys 21.2.0/* files       → <eden data>/keys/
    4. Tell the user to install the firmware ZIP.

    Eden's data folder per platform:
      Windows : %APPDATA%\\eden
      macOS   : ~/Library/Application Support/eden
      Linux   : $XDG_DATA_HOME/eden  (defaults to ~/.local/share/eden)
    """
    # ── Paths (per platform) ────────────────────────────────────────────────────
    base_dir = DOWNLOAD_DIR                                       # folder of this program
    nand_src = os.path.join(base_dir, "System & User")
    keys_src = os.path.join(base_dir, "Keys 21.2.0")

    if IS_WIN:
        eden_data = os.path.join(os.environ.get("APPDATA", ""), "eden")
        eden_exe  = os.path.join(base_dir, "Eden Emulator", "eden.exe")
    elif IS_MAC:
        eden_data = os.path.expanduser("~/Library/Application Support/eden")
        eden_exe  = None
    else:  # Linux
        xdg_data  = os.environ.get("XDG_DATA_HOME") or os.path.expanduser("~/.local/share")
        eden_data = os.path.join(xdg_data, "eden")
        eden_exe  = None

    nand_dst = os.path.join(eden_data, "nand")
    keys_dst = os.path.join(eden_data, "keys")

    # ── Pre-scan so the window can be sized to the exact content height ─────────
    # On Windows we briefly launch eden.exe so it creates its data folders; on
    # Linux/macOS we just create those folders ourselves.
    if IS_WIN:
        eden_found  = os.path.isfile(eden_exe)
        step1_lines = 1 if eden_found else 3   # "✓" vs "[!] not found"(2) + "Skipping"
    else:
        eden_found  = False
        step1_lines = 1                        # "✓ Eden data folder ready."
    if os.path.isdir(nand_src):
        nand_folders = [e for e in os.listdir(nand_src)
                        if os.path.isdir(os.path.join(nand_src, e))]
        step2_lines  = len(nand_folders) if nand_folders else 1
    else:
        nand_folders = None
        step2_lines  = 2                          # "[!] not found" + "Expected:"
    if os.path.isdir(keys_src):
        key_files   = [f for f in os.listdir(keys_src)
                       if os.path.isfile(os.path.join(keys_src, f))]
        step3_lines = len(key_files) if key_files else 1
    else:
        key_files   = None
        step3_lines = 2                           # "[!] not found" + "Expected:"

    total = (
        4                          # header: ===, title, ===, blank
        + 1 + step1_lines          # Step 1 label + result
        + 1                        # blank
        + 1 + step2_lines          # Step 2 label + result
        + 1                        # blank
        + 1 + step3_lines          # Step 3 label + result
        + 1                        # blank
        + 14                       # firmware instruction block
        + 2                        # input prompt (blank + prompt)
    )
    set_window_size(WINDOW_COLS, total)

    clear()
    print("=" * W)
    print("   Eden Setup - Keys, NAND & Firmware")
    print("=" * W)
    print()

    # ── Step 1 : Prepare Eden's data folders ──────────────────────────────────
    print(" Step 1/3 - Initialising Eden file structure...")
    os.makedirs(eden_data, exist_ok=True)
    if IS_WIN:
        # Briefly launch eden.exe so it creates the rest of its data structure.
        if not eden_found:
            print(f" [!] eden.exe not found at:\n     {eden_exe}")
            print("     Skipping launch step - directories may not exist yet.")
        else:
            try:
                proc = subprocess.Popen(
                    [eden_exe],
                    cwd=os.path.dirname(eden_exe),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                time.sleep(3)          # give it a moment to create its appdata dirs
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
                print("  ✓ eden.exe launched and closed.")
            except Exception as e:
                print(f" [!] Could not launch eden.exe: {e}")
                print("     Continuing anyway...")
    else:
        print("  ✓ Eden data folder ready.")

    print()

    # ── Step 2 : Copy System & User folders → nand ────────────────────────────
    print(" Step 2/3 - Copying NAND folders...")
    if nand_folders is None:
        print(f" [!] 'System & User' folder not found next to this exe.")
        print(f"     Expected: {nand_src}")
    else:
        os.makedirs(nand_dst, exist_ok=True)
        if not nand_folders:
            print("  [!] 'System & User' folder is empty - nothing to copy.")
        else:
            for folder in nand_folders:
                src = os.path.join(nand_src, folder)
                dst = os.path.join(nand_dst, folder)
                if os.path.exists(dst):
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"  ✓ Copied: {folder}")

    print()

    # ── Step 3 : Copy Keys 21.2.0 files → keys ───────────────────────────────
    print(" Step 3/3 - Copying key files...")
    if key_files is None:
        print(f" [!] 'Keys 21.2.0' folder not found next to this exe.")
        print(f"     Expected: {keys_src}")
    else:
        os.makedirs(keys_dst, exist_ok=True)
        if not key_files:
            print("  [!] 'Keys 21.2.0' folder is empty - nothing to copy.")
        else:
            for fname in key_files:
                src = os.path.join(keys_src, fname)
                dst = os.path.join(keys_dst, fname)
                shutil.copy2(src, dst)
                print(f"  ✓ Copied: {fname}")

    print()

    # ── Firmware instructions ─────────────────────────────────────────────────
    print("=" * W)
    print(" Setup complete!")
    print()
    print(" ACTION REQUIRED - Install Firmware:")
    print()
    print("  1. Open Eden Emulator")
    print("  2. Go to:  Tools")
    print("            > Install Firmware")
    print("            > Install from ZIP")
    print("  3. Select: Firmware 21.2.0.zip")
    print()
    print(" Make sure Firmware 21.2.0.zip is in the same folder")
    print(" as this program before opening Eden.")
    print("=" * W)
    input("\n Press Enter to return to the menu.")


# ── Multiplayer Info ──────────────────────────────────────────────────────────

def multiplayer_info():
    """LAN-over-VPN multiplayer instructions, split into host/join pages."""
    # Page 1 - hosting (sized to exact content height; no console scrollback).
    set_window_size(WINDOW_COLS, 29)
    clear()
    print("=" * W)
    print("   Multiplayer Info")
    print("=" * W)
    print()
    print(" To host:")
    print(" --------")
    print("  1. Install RadminVPN (RadminVPN.exe)")
    print("  2. Create a room and give your friend the Room Name")
    print("     and Password")
    print("  3. Launch Eden and navigate to Multiplayer >")
    print("     Create Room")
    print("  4. Fill the following info:")
    print("       - Room Name")
    print("       - Username")
    print("       - Preferred Game as Mario Kart 8 Deluxe")
    print("       - Password (leave blank for open game)")
    print("       - Max Players (2 minimum)")
    print("       - Port (leave default)")
    print("  5. Select Unlisted room")
    print("  6. Select Host Room")
    print("  7. Open Mario Kart 8 Deluxe")
    print("  8. Go to the main Title Screen where you see Single")
    print("     Player, Multiplayer, Online Play, and Wireless")
    print("     Play")
    print("  9. Press Left Bumper, Right Bumper, and Left Joystick")
    print("     Inwards to show LAN Play instead of Wireless Play")
    print(" 10. Select LAN Play and create a room")
    print()
    input(" Press Enter for join instructions...")

    # Page 2 - joining.
    set_window_size(WINDOW_COLS, 28)
    clear()
    print("=" * W)
    print("   Multiplayer Info")
    print("=" * W)
    print()
    print(" To join:")
    print(" --------")
    print("  1. Install RadminVPN (RadminVPN.exe)")
    print("  2. Join a room via the Room Name and Password given")
    print("     to you by the host")
    print("  3. Launch Eden and navigate to Multiplayer >")
    print("     Direct Connect To Room")
    print("  4. Fill the following info:")
    print("       - Server Address: the RadminVPN IP address of")
    print("         the host")
    print("       - Port: the port the host put in")
    print("       - Nickname: the name other players see in game")
    print("       - Password: the password set by the host")
    print("  5. Press Connect")
    print("  6. Open Mario Kart 8 Deluxe")
    print("  7. Go to the main Title Screen where you see Single")
    print("     Player, Multiplayer, Online Play, and Wireless")
    print("     Play")
    print("  8. Press Left Bumper, Right Bumper, and Left Joystick")
    print("     Inwards to show LAN Play instead of Wireless Play")
    print("  9. Select LAN Play and join the host's room (may")
    print("     show up as ---- for a bit while loading)")
    print()
    input(" Press Enter to return to the menu.")


# ── About ─────────────────────────────────────────────────────────────────────

def about_tool():
    """Display usage, getting-started, directory layout and links."""
    # The About content is taller than the menu window, and the console has no
    # scrollback (buffer == window height), so size the window to each page's
    # exact content height. The menu resizes itself again on return.
    set_window_size(WINDOW_COLS, 30)
    clear()
    print("=" * W)
    print("   About This Tool")
    print("=" * W)
    print()
    print(" MK8D Eden Checker bundles everything you need to get")
    print(" Mario Kart 8 Deluxe running on Eden Emulator with")
    print(" minimal effort.")
    print()
    print(" Usage")
    print(" -----")
    print(" Just run the executable. No installation needed.")
    print()
    print(f"  1. {'Download MK8D':<16} - opens the MK8D download")
    print( "     link in your browser; start here if you just")
    print( "     need the game")
    print(f"  2. {'Choose version':<16} - lists recent Eden")
    print( "     releases so you can pick and install one")
    print(f"  3. {'Setup':<16} - copies your keys and NAND")
    print( "     folders, then walks you through firmware")
    print(f"  4. {'Enable nightly':<16} - switches to nightly")
    print( "     Eden builds")
    print(f"  5. {'Multiplayer Info':<16} - LAN-over-VPN host and")
    print( "     join instructions")
    print(f"  6. {'About This Tool':<16} - this screen")
    print(f"  7. {'Exit':<16} - quits the program")
    print()
    print(" After picking a version you get a 3 second countdown")
    print(" before the download starts; press any key to cancel.")
    print()
    input(" Press Enter for more...")

    set_window_size(WINDOW_COLS, 34)
    clear()
    print("=" * W)
    print("   About This Tool")
    print("=" * W)
    print()
    print(" Getting Started (Recommended Order)")
    print(" -----------------------------------")
    print("  1. Select Download MK8D to grab the game file")
    print("  2. Select Choose version to download and install")
    print("     Eden Emulator")
    print("  3. Select Setup to install your keys, NAND, and")
    print("     firmware")
    print("  4. Launch Eden and load MK8D")
    print()
    print(" Directory Structure")
    print(" -------------------")
    print("  MK8D-Eden-Checker/")
    print("  |- Eden Checker.exe")
    print("  |- Firmware 21.2.0.zip")
    print("  |- Keys 21.2.0/")
    print("  |   |- prod.keys")
    print("  |   |- title.keys")
    print("  |- System & User/")
    print("      |- system/Contents/registered/")
    print("      |- user/Contents/registered/")
    print()
    print(" Links")
    print(" -----")
    print("  Eden Emulator : https://eden-emu.dev")
    print("  Eden Releases : https://git.eden-emu.dev/eden-emu/eden")
    print("  Eden Nightly  : https://git.eden-emu.dev/eden-ci/nightly")
    print()
    print("=" * W)
    input("\n Press Enter to return to the menu.")


# ── UI ────────────────────────────────────────────────────────────────────────

def menu(nightly, selected_release):
    # header(5) + Selected(1) + blank(1) + 7 options(7) + blank(1) + prompt(1)
    set_window_size(WINDOW_COLS, 16)
    header(nightly)

    if selected_release:
        name = selected_release.get("name") or selected_release.get("tag_name", "unknown")
        date = selected_release.get("published_at", "")[:10]
        print(f" Selected : {name} ({date})")
    else:
        print(" Selected : None")

    print()
    nightly_label = "4. Disable nightly" if nightly else "4. Enable nightly"
    print(" 1. Download MK8D")
    print(" 2. Choose version")
    print(" 3. Setup (Keys, NAND & Firmware)")
    print(f" {nightly_label}")
    print(" 5. Multiplayer Info")
    print(" 6. About This Tool")
    print(" 7. Exit")
    print()
    return input(" Select: ").strip()


def version_picker(nightly):
    """Returns (release, asset, should_download)."""
    # header(5) + "Fetching releases..."(1)
    set_window_size(WINDOW_COLS, HEADER_ROWS + 1)
    header(nightly)
    print(" Fetching releases...", end="", flush=True)
    try:
        pairs = get_releases_with_assets(nightly)
    except Exception as e:
        # header(5) + error(1) + blank(1) + prompt(1), with room for a wrapped error
        set_window_size(WINDOW_COLS, HEADER_ROWS + 4)
        header(nightly)
        print(f" [ERROR] {e}")
        input("\n Press Enter to go back.")
        return None, None, False

    if not pairs:
        # header(5) + message(1) + blank(1) + prompt(1)
        set_window_size(WINDOW_COLS, HEADER_ROWS + 3)
        header(nightly)
        print(" No matching releases found.")
        input("\n Press Enter to go back.")
        return None, None, False

    # header(5) + "Available versions:"(1) + blank(1) + N rows + blank(1) + prompt(1)
    set_window_size(WINDOW_COLS, HEADER_ROWS + 4 + len(pairs))
    header(nightly)
    print(" Available versions:\n")
    for i, (r, _) in enumerate(pairs, 1):
        name = r.get("name") or r.get("tag_name", "unknown")
        date = r.get("published_at", "")[:10]
        print(f"  {i}. {name} ({date})")

    print()
    choice = input(" Pick a number (or Enter to cancel): ").strip()
    if not choice:
        return None, None, False

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(pairs):
            release, asset = pairs[idx]
            # header(5) + Selected(1) + File(1) + blank(1) + countdown(1)
            set_window_size(WINDOW_COLS, HEADER_ROWS + 4)
            header(nightly)
            name = release.get("name") or release.get("tag_name", "unknown")
            date = release.get("published_at", "")[:10]
            print(f" Selected : {name} ({date})")
            print(f" File     : {asset['name']}")
            print()
            proceed = countdown_or_cancel(3)
            return release, asset, proceed
    except ValueError:
        pass

    # header(5) + "Invalid choice."(1) + prompt(1)
    set_window_size(WINDOW_COLS, HEADER_ROWS + 2)
    header(nightly)
    print(" Invalid choice.")
    input(" Press Enter to go back.")
    return None, None, False


def do_download(nightly, release, asset):
    filename  = asset["name"]
    dest_path = os.path.join(DOWNLOAD_DIR, filename)
    exists    = os.path.exists(dest_path)

    # header(5) + Release/File/blank(3) + "Downloading..."(1) + progress(1)
    # + blank(1) + install output + blank(1) + ===/done/===(3) + blank+prompt(2).
    # The installer prints 3 lines on Windows (blank/Extracting/Done) and 4 on
    # Linux/macOS (blank/Installing/Done/run-hint). An existing file adds the
    # "[!] exists" line + the re-download prompt (2) before downloading.
    install_lines = 3 if IS_WIN else 4
    base_rows     = 17 + install_lines          # 20 on Windows, 21 on Linux/macOS
    set_window_size(WINDOW_COLS, base_rows + (2 if exists else 0))
    header(nightly)
    name = release.get("name") or release.get("tag_name", "unknown")

    print(f" Release : {name}")
    print(f" File    : {filename}")
    print()

    if exists:
        print(" [!] File already exists in this folder.")
        choice = input(" Re-download anyway? (y/N): ").strip().lower()
        if choice != "y":
            print("\n Skipping. File already downloaded.")
            input("\n Press Enter to go back.")
            return

    print(" Downloading...")
    try:
        download_file(asset["browser_download_url"], dest_path)
        install(dest_path)
    except urllib.error.URLError as e:
        print(f"\n [ERROR] Download failed: {e.reason}")
        input("\n Press Enter to go back.")
        return
    except Exception as e:
        print(f"\n [ERROR] {e}")
        input("\n Press Enter to go back.")
        return

    print()
    print("=" * W)
    print(" All done! Eden Emulator is ready.")
    print("=" * W)
    input("\n Press Enter to return to the menu.")


# ── Entry ─────────────────────────────────────────────────────────────────────

def main():
    set_window_size(WINDOW_COLS, WINDOW_ROWS)

    nightly          = False
    selected_release = None
    selected_asset   = None

    while True:
        choice = menu(nightly, selected_release)

        if choice == "1":
            import webbrowser
            webbrowser.open("https://drive.google.com/file/d/17QRDd8uYMnONQl80GJn4bhWlniSfr7BJ/view?usp=sharing")

        elif choice == "2":
            r, a, should_download = version_picker(nightly)
            if r and a:
                selected_release, selected_asset = r, a
                if should_download:
                    do_download(nightly, selected_release, selected_asset)

        elif choice == "3":
            setup_eden()

        elif choice == "4":
            nightly = not nightly
            selected_release = None
            selected_asset   = None

        elif choice == "5":
            multiplayer_info()

        elif choice == "6":
            about_tool()

        elif choice == "7":
            sys.exit(0)


if __name__ == "__main__":
    main()
