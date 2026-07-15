# UPScale - Build Guide

This project contains build scripts for both macOS and Windows.

## 📦 macOS Build

Automatic build creates DMG installer:
```bash
python3 build_app.py
```

Output: `dist/UPScale.dmg`

See [README](README.md) for details.

## 🪟 Windows Build

Build Windows installer:
```bash
python build_app_windows.py
```

Output: `dist/UPScale.msi`

**Requirements:**
- Python 3.9+
- pip install PyInstaller PySide6 Pillow
- WiX Toolset 4 or 5 on PATH

See [Windows Build Guide](WINDOWS_BUILD.md) for detailed instructions.

## 📁 Project Structure

```
upscale-desktop-app/
├── app.py                      # Main PySide6 app (cross-platform)
├── led-pixelmap-tool_121.html  # Web UI
├── build_app.py                # macOS build script
├── build_app_windows.py        # Windows MSI build script
├── icon_fullbleed.iconset/     # macOS icons
├── app.ico                     # Windows icon
└── dist/                       # Build output
    ├── UPScale.dmg            # macOS installer
    ├── UPScale/               # Windows app bundle
    └── UPScale.msi            # Windows installer
```

## ✨ Features

- ✅ Cross-platform (macOS + Windows)
- ✅ Native installers for both platforms
- ✅ Beautiful UI with SVG scaling
- ✅ Export multiple scales
- ✅ Project save/load as JSON
- ✅ Professional appearance with rounded icons

## 🚀 Distribution

### macOS
Share: `UPScale-installer.zip` or `dist/UPScale.dmg`

### Windows
Share: `dist/UPScale.msi`

Windows also keeps a portable build in `dist/UPScale/` if you need it.

### Windows via GitHub Actions
Push to `main` to build the installer in GitHub Actions.
Download the `UPScale-Windows-Installer` artifact from the latest successful `Build Windows Installer` run.
