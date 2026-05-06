<p align="center">
  <img src="https://github.com/iamjrmh/CHSuite/blob/main/Windows/_internal/Images/JURMRWEED.png?raw=true" width="120" />
</p>

<h1 align="center">MK8D-Eden-Checker</h1>

<p align="center">
  A simple CLI tool that checks for the latest <a href="https://eden-emu.dev">Eden Emulator</a> release and downloads it for you.
</p>

---

## What it does

Eden Checker grabs the latest Windows, macOS, or Linux build straight from the Eden Gitea and installs it in one shot. It supports both stable releases and nightly builds, lets you pick a specific version, and handles extraction automatically so you never have to dig through a browser.

## Download

Grab the latest `Eden Checker.exe` (or binary for your platform) from the [Releases](https://github.com/iamjrmh/MK8D-Eden-Checker/releases) page.

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

 1. Choose version
 2. Download MK8D
 3. Enable nightly
 4. Exit
```

- **Choose version** lists recent releases so you can pick one
- **Download MK8D** opens the MK8D Google Drive download link in your browser
- **Enable nightly** switches to nightly builds from the Eden CI repo
- After picking a version you get a 3 second countdown before the download starts, press any key to cancel

## Directory Structure

```
MK8D-Eden-Checker/
├── Eden Checker.exe
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
