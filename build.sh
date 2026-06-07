#!/usr/bin/env bash
set -e

OS="$(uname -s)"

case "$OS" in
    MINGW*|MSYS*|CYGWIN*)   PLATFORM="Windows" ;;
    Darwin)                  PLATFORM="macOS"   ;;
    Linux)                   PLATFORM="Linux"   ;;
    *)                       PLATFORM="$OS"     ;;
esac

echo "Building Eden Checker for $PLATFORM..."

pip install pyinstaller -q

if [ "$PLATFORM" = "Windows" ]; then
    pyinstaller --onefile --console --icon=eden.ico --name="Eden Checker" eden_update.py
    mv -f "dist/Eden Checker.exe" "Eden Checker.exe"
else
    pyinstaller --onefile --console --name="Eden Checker" eden_update.py
    mv -f "dist/Eden Checker" "Eden Checker"
    chmod +x "Eden Checker"
fi

rm -rf dist build "Eden Checker.spec"

echo "Done! Output: Eden Checker$([ "$PLATFORM" = "Windows" ] && echo .exe)"
