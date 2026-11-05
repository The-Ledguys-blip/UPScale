"""Windows MSI-builder voor UPScale (WiX Toolset v5).

Draai dit op een Windows-11 machine NADAT je de app hebt gebouwd:

    py -m pip install -r requirements.txt
    py build_app_windows.py               :: maakt dist\\UPScale\\UPScale.exe
    py build_msi_windows.py               :: maakt installer_output\\UPScale-<versie>-x64.msi

Eenmalige voorbereiding (WiX v5 als dotnet-tool):

    winget install Microsoft.DotNet.SDK.8     :: of download dotnet-sdk van microsoft.com
    dotnet tool install --global wix

Het script harvest automatisch alle bestanden uit dist\\UPScale\\, bouwt een
WiX-bronbestand (.wxs) en compileert daar de MSI van. Versie wordt uit
led-pixelmap-tool_121.html gelezen.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "UPScale"
HTML_FILE = "led-pixelmap-tool_121.html"
APP_DIR = ROOT / "dist" / APP_NAME
WXS_FILE = ROOT / "installer_output" / f"{APP_NAME}.wxs"
OUT_DIR = ROOT / "installer_output"

# Vaste UpgradeCode zodat upgrades de vorige versie netjes vervangen.
# Verander deze NOOIT tussen versies.
UPGRADE_CODE = "{B7C4E2A1-3F5D-4E8B-9A2C-6D1E7F804B29}"


def read_app_version() -> str:
    try:
        text = (ROOT / HTML_FILE).read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"const APP_VERSION\s*=\s*'v?([0-9]+\.[0-9]+\.[0-9]+)'", text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "0.0.0"


def msi_version(version: str) -> str:
    """MSI wil major.minor.build met getallen (build <= 65535)."""
    parts = re.findall(r"\d+", version)[:3]
    while len(parts) < 3:
        parts.append("0")
    major, minor, build = (min(int(p), 65535) for p in parts)
    return f"{major}.{minor}.{build}"


def esc(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def find_wix() -> str | None:
    which = shutil.which("wix") or shutil.which("wix.exe")
    if which:
        return which
    candidates = [
        Path.home() / ".dotnet" / "tools" / "wix.exe",
        Path(r"C:\Program Files\dotnet\tools\wix.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def collect_tree(app_dir: Path):
    """Loop de onedir-output door en geef (dirs, files_by_dir) terug.

    dirs: rel ('' = root) -> {'id', 'parent', 'name'}
    files_by_dir: rel -> [filenames]
    """
    dirs: dict[str, dict] = {"": {"id": "INSTALLFOLDER", "parent": None, "name": APP_NAME}}
    files_by_dir: dict[str, list[str]] = {}
    counter = {"n": 0}

    for dirpath, dirnames, filenames in os.walk(app_dir):  # noqa: F821 (os imported below)
        dirnames.sort()
        rel = os.path.relpath(dirpath, app_dir)  # noqa: F821
        rel = "" if rel == "." else rel.replace(os.sep, "/")
        if rel and rel not in dirs:
            parent = rel.rsplit("/", 1)[0] if "/" in rel else ""
            counter["n"] += 1
            dirs[rel] = {"id": f"d{counter['n']}", "parent": parent, "name": os.path.basename(rel)}
        files_by_dir[rel] = sorted(f for f in filenames)  # noqa: F821
    return dirs, files_by_dir


def render_dirs(dirs: dict, parent: str) -> str:
    out = []
    for rel, info in sorted(dirs.items(), key=lambda kv: kv[1]["name"].lower()):
        if info["parent"] != parent:
            continue
        out.append(f'      <Directory Id="{info["id"]}" Name="{esc(info["name"])}">')
        out.append(render_dirs(dirs, rel))
        out.append('      </Directory>')
    return "\n".join(line for line in out if line)


def render_components(app_dir: Path, dirs: dict, files_by_dir: dict) -> str:
    out = []
    counter = {"n": 0}
    for rel in sorted(files_by_dir):
        files = files_by_dir[rel]
        if not files:
            continue
        dir_id = dirs[rel]["id"]
        out.append(f'    <Component Directory="{dir_id}" Guid="*">')
        for fname in files:
            counter["n"] += 1
            src = (app_dir / rel / fname) if rel else (app_dir / fname)
            out.append(f'      <File Id="f{counter["n"]}" Source="{esc(str(src))}" />')
        out.append('    </Component>')
    return "\n".join(out)


def build_wxs(version: str, dirs: dict, files_by_dir: dict) -> str:
    ver = msi_version(version)
    dirs_xml = render_dirs(dirs, "")
    comps_xml = render_components(APP_DIR, dirs, files_by_dir)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://wixtoolset.org/schemas/v4/wxs">
  <Package Name="{APP_NAME}"
           Manufacturer="{APP_NAME}"
           Version="{ver}"
           Language="1033"
           UpgradeCode="{UPGRADE_CODE}"
           Scope="perMachine"
           Compressed="yes"
           InstallerVersion="500">

    <MajorUpgrade DowngradeErrorMessage="Een nieuwere versie van [ProductName] is al geinstalleerd." />
    <MediaTemplate EmbedCab="yes" />

    <Icon Id="AppIcon" SourceFile="app.ico" />
    <Property Id="ARPPRODUCTICON" Value="AppIcon" />
    <Property Id="ARPCOMMENTS" Value="UPScale LED pixel mapping" />
    <Property Id="ARPNOMODIFY" Value="1" />

    <StandardDirectory Id="ProgramFiles64Folder">
      <Directory Id="INSTALLFOLDER" Name="{APP_NAME}">
{dirs_xml}
      </Directory>
    </StandardDirectory>

    <StandardDirectory Id="ProgramMenuFolder">
      <Directory Id="ApplicationProgramsFolder" Name="{APP_NAME}" />
    </StandardDirectory>

    <StandardDirectory Id="DesktopFolder" />

    <Feature Id="MainFeature" Title="{APP_NAME}" Level="1">
      <ComponentGroupRef Id="AppFiles" />
      <ComponentRef Id="StartMenuShortcut" />
      <ComponentRef Id="DesktopShortcut" />
    </Feature>
  </Package>

  <Fragment>
    <ComponentGroup Id="AppFiles">
{comps_xml}
    </ComponentGroup>
  </Fragment>

  <Fragment>
    <Component Id="StartMenuShortcut" Directory="ApplicationProgramsFolder" Guid="*">
      <Shortcut Id="SmShortcut" Name="{APP_NAME}" Description="UPScale LED pixel mapping"
                Target="[INSTALLFOLDER]{APP_NAME}.exe" WorkingDirectory="INSTALLFOLDER" />
      <RemoveFolder Id="RemoveProgramsFolder" Directory="ApplicationProgramsFolder" On="uninstall" />
      <RegistryValue Root="HKCU" Key="Software\\{APP_NAME}" Name="StartMenu" Type="integer" Value="1" KeyPath="yes" />
    </Component>
    <Component Id="DesktopShortcut" Directory="DesktopFolder" Guid="*">
      <Shortcut Id="DesktopShortcutLink" Name="{APP_NAME}" Description="UPScale LED pixel mapping"
                Target="[INSTALLFOLDER]{APP_NAME}.exe" WorkingDirectory="INSTALLFOLDER" />
      <RegistryValue Root="HKCU" Key="Software\\{APP_NAME}" Name="Desktop" Type="integer" Value="1" KeyPath="yes" />
    </Component>
  </Fragment>
</Wix>
"""


def main() -> None:
    if not sys.platform.startswith("win"):
        print("Dit script hoort op Windows te draaien (WiX/MSI is Windows-only).")
        print("Op macOS bouw je de DMG met: python3 build_app.py")
        sys.exit(1)

    if not APP_DIR.exists():
        print(f"Kan {APP_DIR} niet vinden. Bouw eerst: py build_app_windows.py")
        sys.exit(1)

    wix = find_wix()
    if wix is None:
        print("WiX (wix) niet gevonden. Installeer eenmalig:")
        print("  winget install Microsoft.DotNet.SDK.8")
        print("  dotnet tool install --global wix")
        sys.exit(1)

    version = read_app_version()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    dirs, files_by_dir = collect_tree(APP_DIR)
    WXS_FILE.write_text(build_wxs(version, dirs, files_by_dir), encoding="utf-8")
    print(f"WiX-bron geschreven: {WXS_FILE}")

    out_msi = OUT_DIR / f"{APP_NAME}-{version}-x64.msi"
    if out_msi.exists():
        out_msi.unlink()

    cmd = [wix, "build", "-arch", "x64", str(WXS_FILE), "-o", str(out_msi)]
    print("MSI bouwen met:", " ".join(cmd))
    subprocess.run(cmd, cwd=ROOT, check=True)

    if out_msi.exists():
        print(f"MSI klaar: {out_msi}")
    else:
        print("MSI-build voltooid, maar het bestand is niet gevonden in installer_output\\.")


if __name__ == "__main__":
    main()
