<p align="center">
  <img src="https://github.com/iamjrmh/CHSuite/blob/main/Windows/_internal/Images/JURMRWEED.png?raw=true" width="120" />
</p>

<h1 align="center">MK8D-Eden-Checker</h1>

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

Just run the executable. No installation needed.

```
Eden Checker.exe
```

On macOS or Linux:

```bash
./Eden\ Checker
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
- **Multiplayer Info** shows step-by-step LAN-over-VPN (RadminVPN) instructions for hosting and joining a Mario Kart 8 Deluxe room
- **About This Tool** displays this usage info, the recommended order, directory layout, and useful links right inside the program
- After picking a version you get a 3 second countdown before the download starts, press any key to cancel

## Getting Started (Recommended Order)

1. Run the tool and select **Download MK8D** to grab the game file
2. Select **Choose version** to download and install Eden Emulator
3. Select **Setup** to install your keys, NAND, and firmware
4. Launch Eden and load MK8D

## Directory Structure

```
MK8DEdenChecker/
├── Eden Checker.exe
├── RadminVPN.exe
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
