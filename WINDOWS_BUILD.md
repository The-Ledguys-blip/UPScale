# UPScale Windows MSI Build Instructions

## System Requirements
- **Windows 10 or later** (64-bit recommended)
- **Python 3.9 or higher** (from python.org)
- **pip** (comes with Python)
- **WiX Toolset 4 or 5** for creating the MSI installer

If you are currently on macOS, use a Windows machine or the GitHub Actions Windows workflow to create the installer.

## Step 1: Install Python
1. Download Python 3.11 from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **IMPORTANT**: Check "Add Python to PATH" during installation
4. Click "Install Now"

## Step 2: Verify Python Installation
Open Command Prompt and run:
```bash
python --version
pip --version
```

Both should show their versions without errors.

## Step 3: Install Dependencies
Open Command Prompt in the project folder and run:
```bash
pip install PyInstaller PySide6 Pillow
```

This may take a few minutes to download and install.

## Step 4: Install WiX Toolset
Install WiX so the build script can create a real Windows installer:

1. Download WiX Toolset 4 or 5
2. Make sure the `wix` command is available in Command Prompt
3. Verify with:

```bash
wix --version
```

## Step 5: Build the Installer

Run the Windows build script:
```bash
python build_app_windows.py
```

The script will:
- Check dependencies
- Build the app folder with PyInstaller
- Create `dist/UPScale/UPScale.exe`
- Create `dist/UPScale.msi`

This takes 2-5 minutes depending on your system.

## Step 6: Test the Installer

1. Double-click `dist\UPScale.msi`
2. Complete the installer
3. Launch UPScale from the Start menu or desktop shortcut

Verify:
- ✅ App launches
- ✅ Can open/save projects
- ✅ Can export images
- ✅ Files save to `%USERPROFILE%\Downloads\UPScale-export-*`

## Step 7: Share

Once tested, you can share:
- **Installer**: `dist/UPScale.msi`
- **Portable folder**: `dist/UPScale/`

Users can now install UPScale with a standard one-click Windows installer.

## Troubleshooting

### "Python not found"
- Reinstall Python with "Add Python to PATH" checked
- Restart Command Prompt after reinstalling

### "Module not found" errors
- Run: `pip install --upgrade pip`
- Run: `pip install PyInstaller PySide6 Pillow` again

### "wix" is not recognized
- Reinstall WiX Toolset
- Open a new Command Prompt after installation
- Run `wix --version` to confirm it is on PATH

### App doesn't launch after install
- Try running from Command Prompt to see error messages:
  ```bash
  "C:\Program Files\UPScale\UPScale.exe"
  ```

### Security warning from Windows
- Windows may warn about unsigned executables
- Click "More info" → "Run anyway"
- This is normal for unsigned apps and installers

## Notes

- **MSI installer** - Installs to `Program Files\UPScale`
- **Shortcuts** - Creates Start menu and desktop shortcuts
- **Portable fallback** - `dist/UPScale/` can still be copied manually
- **Same UI** as macOS version
- **Same export structure** - `UPScale-export-{projectname}/`

## Support

If you have issues:
1. Check the troubleshooting section above
2. Verify Python is installed correctly
3. Try running from Command Prompt to see error messages
4. Contact support with the error message
