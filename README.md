<p align="center">
  <img src="https://github.com/iamjrmh/CHSuite/blob/main/Windows/_internal/Images/JURMRWEED.png?raw=true" width="120" />
</p>

<h1 align="center">MK8DEdenChecker</h1>

<p align="center">
  The quickest way to get <strong>Mario Kart 8 Deluxe</strong> running on <a href="https://eden-emu.dev">Eden Emulator</a> - downloads MK8D and keeps your emulator up to date, all in one place.
</p>

---

## What it does

This tool bundles everything you need to get MK8D up and running on Eden Emulator with minimal effort:

- **Downloads MK8D** directly - one click, no hunting through Google Drive yourself
- **Installs Eden Emulator** - grabs the latest stable or nightly build for Windows, macOS, or Linux straight from the Eden Gitea and handles extraction automatically
- **Sets up keys, NAND & firmware** - copies your keys and system files into the right places and walks you through firmware installation so Eden is ready to go

## Download

Grab the latest `MK8DEdenChecker.zip` from [here](https://github.com/iamjrmh/MK8D-Eden-Checker/releases/latest/download/MK8DEdenChecker.zip).

## Usage

Just run the executable for your platform. No installation needed. Every build ships inside the same `MK8DEdenChecker.zip`, so keep the binary next to the bundled `Keys 21.2.0/`, `System & User/`, and `Firmware 21.2.0.zip` files.

**Windows:**

```
EdenChecker.exe
```

**Linux** (added in v3.0): mark it executable once, then run it from a terminal:

```bash
chmod +x EdenCheckerLinux
./EdenCheckerLinux
```

**macOS** (added in v3.0): a single universal binary that runs natively on both Apple Silicon and Intel:

```bash
chmod +x EdenCheckerMac
./EdenCheckerMac
```

You'll see a menu like this:

```
=============================================================
   Eden Emulator - Latest Release Checker
   Platform: Windows
=============================================================

 Selected : None

 1. Download MK8D
 2. Choose version
 3. Setup (Keys, NAND & Firmware)
 4. Enable nightly
 5. Multiplayer Info
 6. About This Tool
 7. Exit
```

- **Download MK8D** opens the MK8D Google Drive download link in your browser - start here if you just need the game
- **Choose version** lists recent releases so you can pick one
- **Setup** copies your keys and NAND folders into Eden's appdata and walks you through firmware installation
- **Enable nightly** switches to nightly builds from the Eden CI repo
- **Multiplayer Info** shows step-by-step ZeroTier LAN instructions for hosting and joining a Mario Kart 8 Deluxe room
- **About This Tool** displays this usage info, the recommended order, directory layout, and useful links right inside the program
- After picking a version you get a 3 second countdown before the download starts, press any key to cancel

## Getting Started (Recommended Order)

1. Run the tool and select **Download MK8D** to grab the game file
2. Select **Choose version** to download and install Eden Emulator
3. Select **Setup** to install your keys, NAND, and firmware
4. Launch Eden and load MK8D

## Multiplayer (ZeroTier)

LAN multiplayer uses [ZeroTier](https://zerotier.com) to put everyone on one virtual LAN so Eden's LAN Play can find each other. It is free and works on Windows, macOS, and Linux. The in-app **Multiplayer Info** screen has the full host/join walkthrough; this is the short version.

**Install ZeroTier One:**

- **Windows:** run the bundled `ZeroTier One.msi`
- **macOS:** run the bundled `ZeroTier One.pkg`
- **Linux** (Debian/Ubuntu/CentOS/RHEL/Fedora and others), run in a terminal:

  ```bash
  curl -s https://install.zerotier.com | sudo bash
  ```

  Or, if you have GPG and prefer to verify the installer:

  ```bash
  curl -s 'https://raw.githubusercontent.com/zerotier/ZeroTierOne/main/doc/contact%40zerotier.com.gpg' | gpg --import && \
  if z=$(curl -s 'https://install.zerotier.com/' | gpg); then echo "$z" | sudo bash; fi
  ```

  After install, manage updates to `zerotier-one` with `apt` or `yum`.

**Then:**

1. The host creates a free network at [my.zerotier.com](https://my.zerotier.com) and shares the 16-character Network ID.
2. Everyone joins it (tray icon > Join Network on Windows/macOS, or `sudo zerotier-cli join <NetworkID>` on Linux).
3. The host authorizes each member on my.zerotier.com (tick the checkbox).
4. Host: Eden > Multiplayer > **Create Room**. Joiners: Eden > Multiplayer > **Direct Connect To Room** using the host's ZeroTier IP.
5. In MK8D, open the Title Screen and press **Left Bumper + Right Bumper + Left Stick (in)** to switch Wireless Play to **LAN Play**, then host/join the room.

### Backup options

ZeroTier is recommended, but if it gives you trouble these also create a virtual LAN you can use the same way (install it on every player's machine, then host/join in Eden by IP):

- **[Radmin VPN](https://www.radmin-vpn.com)** - free, simple network name + password flow. **Windows only.**
- **[LogMeIn Hamachi](https://www.vpn.net)** - free, cross-platform (Windows, macOS, Linux). Capped at **5 devices per network** on the free tier, and the Linux client is barebones.

## Directory Structure

```
MK8D-Eden-Checker/
├── EdenChecker.exe         # Windows build
├── EdenCheckerLinux        # Linux build (chmod +x to run)
├── EdenCheckerMac          # macOS build, Apple Silicon + Intel (chmod +x to run)
├── ZeroTier One.msi        # ZeroTier installer (Windows)
├── ZeroTier One.pkg        # ZeroTier installer (macOS)
├── Firmware 21.2.0.zip
├── Keys 21.2.0/
│   ├── prod.keys
│   └── title.keys
└── System & User/
    ├── system/
    │   └── Contents/
    │       └── registered/  (219 items)
    └── user/
        ├── Contents/
        │   └── registered/
        └── temp/
```

## Links

- [Eden Emulator](https://eden-emu.dev)
- [Eden Releases](https://git.eden-emu.dev/eden-emu/eden/releases)
- [Eden Nightly](https://git.eden-emu.dev/eden-ci/nightly/releases)
