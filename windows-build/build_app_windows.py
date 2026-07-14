#!/usr/bin/env python3
"""
Build a Windows installer for UPScale.

Requirements:
    pip install PyInstaller PySide6 Pillow
    wix.exe or wix must be available on PATH for MSI creation

Usage:
    python build_app_windows.py
    python build_app_windows.py --skip-msi
    python build_app_windows.py --msi-only

Default output:
    dist/UPScale/UPScale.exe
    dist/UPScale.msi
"""

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
import textwrap
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "UPScale"
DEFAULT_VERSION = os.environ.get("UPSCALE_VERSION", "1.0.0")
MANUFACTURER = os.environ.get("UPSCALE_MANUFACTURER", APP_NAME)
UPGRADE_CODE = os.environ.get("UPSCALE_UPGRADE_CODE", "7D16E7A0-9DB4-42B8-B7A4-D3F22D9826AC")


def parse_args():
    parser = argparse.ArgumentParser(description="Build the UPScale Windows app and MSI installer.")
    parser.add_argument(
        "--version",
        default=DEFAULT_VERSION,
        help=f"MSI product version (default: {DEFAULT_VERSION})",
    )
    parser.add_argument(
        "--skip-msi",
        action="store_true",
        help="Only build the Windows app bundle and skip MSI creation.",
    )
    parser.add_argument(
        "--msi-only",
        action="store_true",
        help="Skip PyInstaller and package an existing dist/UPScale folder into an MSI.",
    )
    return parser.parse_args()


def run_command(command, *, cwd=ROOT):
    print(f"   Command: {subprocess.list2cmdline(command)}")
    return subprocess.run(command, cwd=cwd)


def validate_version(version):
    parts = version.split(".")
    if len(parts) != 3 or any(not part.isdigit() for part in parts):
        print(f"ERROR: Invalid version '{version}'")
        print("   Use Windows MSI format: major.minor.patch, for example 1.0.0")
        return False
    return True


def ensure_build_prerequisites():
    if sys.platform != "win32":
        print("ERROR: Windows packaging must be run on Windows.")
        print("   Use a Windows machine or the GitHub Actions Windows workflow.")
        return False

    if sys.version_info < (3, 9):
        print(f"ERROR: Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        return False

    print(f"   Python executable: {sys.executable}")
    print(f"   Python version: {sys.version.split()[0]}")
    print(f"   Platform: {sys.platform}")

    required_modules = ["PyInstaller", "PySide6"]
    missing_modules = [name for name in required_modules if importlib.util.find_spec(name) is None]
    if missing_modules:
        print(f"ERROR: Missing required package(s): {', '.join(missing_modules)}")
        print()
        print("Install with:")
        print("  pip install PyInstaller PySide6 Pillow")
        return False

    return True


def ensure_runtime_assets():
    icon_path = ROOT / "app.ico"
    html_path = ROOT / "led-pixelmap-tool_121.html"

    if not icon_path.exists():
        print(f"ERROR: Icon not found: {icon_path}")
        return None, None

    if not html_path.exists():
        print(f"ERROR: Runtime asset not found: {html_path}")
        return None, None

    print(f"   Using icon: {icon_path}")
    print(f"   Using HTML: {html_path}")

    return icon_path, html_path


def build_windows_bundle():
    """Build a Windows app bundle using PyInstaller."""

    icon_path, html_path = ensure_runtime_assets()
    if not icon_path or not html_path:
        return None

    pyinstaller_args = [
        sys.executable,
        "-m",
        "PyInstaller",
        f"--name={APP_NAME}",
        "--onedir",
        "--windowed",
        "--noconfirm",
        "--clean",
        f"--icon={icon_path}",
        f"--add-data={html_path}{os.pathsep}.",
        "--hidden-import=PySide6.QtWebEngineCore",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWebEngineWidgets",
        str(ROOT / "app.py"),
    ]

    print("Building Windows app bundle...")
    result = run_command(pyinstaller_args)

    bundle_dir = ROOT / "dist" / APP_NAME
    exe_path = bundle_dir / f"{APP_NAME}.exe"

    if result.returncode != 0:
        print("ERROR: PyInstaller build failed")
        return None

    if not exe_path.exists():
        print(f"ERROR: Expected app executable not found: {exe_path}")
        return None

    size_mb = sum(path.stat().st_size for path in bundle_dir.rglob("*") if path.is_file()) / (1024 * 1024)
    print()
    print("Windows app bundle built successfully.")
    print(f"   Location: {bundle_dir}")
    print(f"   Size: {size_mb:.1f} MB")
    return bundle_dir


def find_wix_executable():
    for candidate in ("wix.exe", "wix"):
        wix_path = shutil.which(candidate)
        if wix_path:
            return wix_path
    return None


def write_wix_source(bundle_dir, version):
    wix_dir = ROOT / "build" / "wix"
    wix_dir.mkdir(parents=True, exist_ok=True)

    wix_source = wix_dir / f"{APP_NAME}.wxs"
    start_menu_guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{APP_NAME}-start-menu-shortcut"))
    desktop_guid = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{APP_NAME}-desktop-shortcut"))

    wix_source.write_text(
        textwrap.dedent(
            f"""\
            <?xml version="1.0" encoding="UTF-8"?>
            <Wix xmlns="http://wixtoolset.org/schemas/v4/wxs">
              <Package
                  Name="{APP_NAME}"
                  Manufacturer="{MANUFACTURER}"
                  Version="{version}"
                  UpgradeCode="{UPGRADE_CODE}"
                  Language="1033"
                  Scope="perMachine">
                <MajorUpgrade DowngradeErrorMessage="A newer version of {APP_NAME} is already installed." />
                <MediaTemplate EmbedCab="yes" CompressionLevel="high" />

                <StandardDirectory Id="ProgramFiles64Folder">
                  <Directory Id="INSTALLFOLDER" Name="{APP_NAME}" />
                </StandardDirectory>
                                <StandardDirectory Id="ProgramMenuFolder">
                                    <Directory Id="ProgramMenuDir" Name="{APP_NAME}" />
                                </StandardDirectory>
                                <StandardDirectory Id="DesktopFolder" />

                <Feature Id="MainFeature" Title="{APP_NAME}" Level="1">
                                    <Files Directory="INSTALLFOLDER" Include="!(bindpath.appfiles)\**" />
                                    <ComponentRef Id="StartMenuShortcutComponent" />
                                    <ComponentRef Id="DesktopShortcutComponent" />
                </Feature>

                                <Component Id="StartMenuShortcutComponent" Directory="ProgramMenuDir" Guid="{start_menu_guid}">
                                    <Shortcut
                                            Id="StartMenuShortcut"
                                            Name="{APP_NAME}"
                                            Description="Launch {APP_NAME}"
                                            Target="[INSTALLFOLDER]{APP_NAME}.exe"
                                            WorkingDirectory="INSTALLFOLDER" />
                                    <RemoveFolder Id="RemoveProgramMenuDir" On="uninstall" />
                                    <RegistryValue
                                            Root="HKCU"
                                            Key="Software\{MANUFACTURER}\{APP_NAME}"
                                            Name="StartMenuShortcut"
                                            Type="integer"
                                            Value="1"
                                            KeyPath="yes" />
                                </Component>

                                <Component Id="DesktopShortcutComponent" Directory="DesktopFolder" Guid="{desktop_guid}">
                                    <Shortcut
                                            Id="DesktopShortcut"
                                            Name="{APP_NAME}"
                                            Description="Launch {APP_NAME}"
                                            Target="[INSTALLFOLDER]{APP_NAME}.exe"
                                            WorkingDirectory="INSTALLFOLDER" />
                                    <RegistryValue
                                            Root="HKCU"
                                            Key="Software\{MANUFACTURER}\{APP_NAME}"
                                            Name="DesktopShortcut"
                                            Type="integer"
                                            Value="1"
                                            KeyPath="yes" />
                                </Component>
              </Package>
            </Wix>
            """
        ),
        encoding="utf-8",
    )
    return wix_source


def build_windows_msi(bundle_dir, version):
    wix_executable = find_wix_executable()
    if not wix_executable:
        print("ERROR: WiX Toolset not found on PATH.")
        print("   Install WiX 4/5 and ensure the 'wix' command is available.")
        print("   GitHub Actions can do this automatically on Windows.")
        return False

    exe_path = bundle_dir / f"{APP_NAME}.exe"
    if not exe_path.exists():
        print(f"ERROR: Expected app executable not found: {exe_path}")
        return False

    wix_source = write_wix_source(bundle_dir, version)
    msi_path = ROOT / "dist" / f"{APP_NAME}.msi"

    print()
    print("Building MSI installer...")
    result = run_command(
        [
            wix_executable,
            "build",
            str(wix_source),
            "-bindpath",
            f"appfiles={bundle_dir}",
            "-arch",
            "x64",
            "-o",
            str(msi_path),
        ]
    )

    if result.returncode != 0:
        print("ERROR: WiX build failed")
        return False

    if not msi_path.exists():
        print(f"ERROR: MSI file not found after build: {msi_path}")
        return False

    size_mb = msi_path.stat().st_size / (1024 * 1024)
    print("MSI installer built successfully.")
    print(f"   Location: {msi_path}")
    print(f"   Size: {size_mb:.1f} MB")
    return True


def main():
    args = parse_args()

    print("=" * 70)
    print("UPScale Windows Build")
    print("=" * 70)
    print()

    if not validate_version(args.version):
        return False

    bundle_dir = ROOT / "dist" / APP_NAME

    if not args.msi_only:
        if not ensure_build_prerequisites():
            return False
        bundle_dir = build_windows_bundle()
        if not bundle_dir:
            return False
    elif not (bundle_dir / f"{APP_NAME}.exe").exists():
        print(f"ERROR: Existing app bundle not found: {bundle_dir}")
        print("   Run a full build first or omit --msi-only.")
        return False

    if not args.skip_msi:
        if not build_windows_msi(bundle_dir, args.version):
            return False
    
    print()
    print("=" * 70)
    print("Build complete.")
    print()
    print("Next steps:")
    print(f"  1. Test: dist/{APP_NAME}/{APP_NAME}.exe")
    if args.skip_msi:
        print(f"  2. Share the folder: dist/{APP_NAME}")
    else:
        print(f"  2. Install/test: dist/{APP_NAME}.msi")
        print(f"  3. Share the installer: dist/{APP_NAME}.msi")
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
