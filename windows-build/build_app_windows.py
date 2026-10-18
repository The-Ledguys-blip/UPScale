"""Windows build script voor UPScale.

Run dit op een Windows-11 machine:
    py -m pip install -r requirements.txt
    py build_app_windows.py                 # bouwt dist\\UPScale\\UPScale.exe
    py build_app_windows.py zip             # + dist\\UPScale-<versie>-win64.zip
    py build_app_windows.py installer       # + installer via Inno Setup (ISCC.exe)
    py build_app_windows.py zip installer   # beide
    py build_app_windows.py clean           # verwijder build\\ en dist\\
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
APP_NAME = "UPScale"
HTML_FILE = "led-pixelmap-tool_121.html"


def read_app_version() -> str:
    """Lees de versie uit de HTML zodat build in sync blijft."""
    try:
        text = (ROOT / HTML_FILE).read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"const APP_VERSION\s*=\s*'v?([0-9]+\.[0-9]+\.[0-9]+)'", text)
        if match:
            return match.group(1)
    except Exception:
        pass
    return "0.0.0"


def write_version_file(version: str) -> Path:
    """Genereer een PyInstaller versie-resource zodat Explorer de versie toont."""
    major, minor, patch = (int(x) for x in version.split("."))
    path = ROOT / "windows_versioninfo.txt"
    path.write_text(
        f"""\
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({major}, {minor}, {patch}, 0),
    prodvers=({major}, {minor}, {patch}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'UPScale'),
        StringStruct('FileDescription', 'UPScale LED pixel mapping'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', '{APP_NAME}'),
        StringStruct('OriginalFilename', '{APP_NAME}.exe'),
        StringStruct('ProductName', '{APP_NAME}'),
        StringStruct('ProductVersion', '{version}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
""",
        encoding="utf-8",
    )
    return path


def clean() -> None:
    for name in ("build", "dist"):
        target = ROOT / name
        if target.exists():
            shutil.rmtree(target)


def build() -> Path:
    version = read_app_version()
    version_file = write_version_file(version)

    icon = ROOT / "app.ico"
    if not icon.exists():
        print("Waarschuwing: app.ico ontbreekt; bouw zonder icoon.")

    datas = [
        (HTML_FILE, "."),
    ]
    for extra in ("app.icns", "icon.iconset", "icon_fullbleed.iconset"):
        if (ROOT / extra).exists():
            datas.append((extra, "." if extra.endswith(".icns") else extra))

    # Windows gebruikt ';' als scheidingsteken in --add-data.
    add_data_args = []
    for src, dest in datas:
        add_data_args += ["--add-data", f"{src};{dest}"]

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name", APP_NAME,
        "--windowed",
        "--onedir",
        "--noconfirm",
        *add_data_args,
        "--version-file", str(version_file),
    ]
    if icon.exists():
        cmd += ["--icon", str(icon)]
    cmd.append("app.py")

    print(f"Bouwen {APP_NAME} v{version} voor Windows...")
    subprocess.run(cmd, cwd=ROOT, check=True)

    exe = ROOT / "dist" / APP_NAME / f"{APP_NAME}.exe"
    if exe.exists():
        print(f"Build klaar: {exe}")
        return exe
    print("Build voltooid, maar UPScale.exe niet gevonden in dist.")
    return exe


def make_zip() -> None:
    version = read_app_version()
    app_dir = ROOT / "dist" / APP_NAME
    if not app_dir.exists():
        print("Eerst bouwen: py build_app_windows.py")
        return
    zip_path = ROOT / "dist" / f"{APP_NAME}-{version}-win64.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in app_dir.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(app_dir.parent))
    print(f"Zip klaar: {zip_path}")


def make_installer() -> None:
    version = read_app_version()
    iss = ROOT / "installer.iss"
    if not iss.exists():
        print("installer.iss niet gevonden naast build_app_windows.py.")
        return
    iscc = _find_iscc()
    if iscc is None:
        print("ISCC.exe niet gevonden. Installeer Inno Setup 6 of voeg het pad aan PATH toe.")
        return
    print(f"Installer bouwen met {iscc}...")
    subprocess.run([str(iscc), f"/DMyAppVersion={version}", str(iss)], cwd=ROOT, check=True)
    out = ROOT / "installer_output" / f"{APP_NAME}-Setup-{version}.exe"
    if out.exists():
        print(f"Installer klaar: {out}")
    else:
        print("Installer voltooid, bestand niet gevonden in installer_output\\.")


def _find_iscc() -> Path | None:
    candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
    ]
    which = shutil.which("ISCC") or shutil.which("ISCC.exe")
    if which:
        candidates.insert(0, Path(which))
    for c in candidates:
        if c.exists():
            return c
    return None


def main() -> None:
    args = [a.lower() for a in sys.argv[1:]]
    if not sys.platform.startswith("win"):
        print("Dit script hoort op Windows te draaien. Op macOS: python3 build_app.py")
        if "force" not in args:
            sys.exit(1)
    if "clean" in args:
        clean()
        return
    build()
    if "zip" in args or "all" in args:
        make_zip()
    if "installer" in args or "all" in args:
        make_installer()


if __name__ == "__main__":
    main()
