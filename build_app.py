from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def _copy_if_exists(source: Path, dest: Path) -> bool:
    if source.exists():
        dest.write_bytes(source.read_bytes())
        return True
    return False


def build_app_icns() -> None:
    iconset_source = ROOT / "icon_fullbleed.iconset"
    if not iconset_source.exists():
        iconset_source = ROOT / "icon.iconset"

    if not iconset_source.exists():
        return

    tmp_iconset = ROOT / "tmp_iconset_full.iconset"
    if tmp_iconset.exists():
        shutil.rmtree(tmp_iconset)
    tmp_iconset.mkdir(parents=True, exist_ok=True)

    # copy all standard iconset files, then generate @2x retina variants
    for png in iconset_source.glob("*.png"):
        dest = tmp_iconset / png.name
        dest.write_bytes(png.read_bytes())

    retina_pairs = [
        ("icon_32x32.png", "icon_16x16@2x.png"),
        ("icon_64x64.png", "icon_32x32@2x.png"),
        ("icon_256x256.png", "icon_128x128@2x.png"),
        ("icon_512x512.png", "icon_256x256@2x.png"),
        ("icon_1024x1024.png", "icon_512x512@2x.png"),
    ]
    for source_name, dest_name in retina_pairs:
        source = iconset_source / source_name
        dest = tmp_iconset / dest_name
        if source.exists():
            dest.write_bytes(source.read_bytes())

    target = ROOT / "app.icns"
    if not target.exists() or any(p.stat().st_mtime > target.stat().st_mtime for p in tmp_iconset.glob("*.png")):
        subprocess.run(
            ["iconutil", "-c", "icns", str(tmp_iconset), "-o", str(target)],
            cwd=ROOT,
            check=True,
        )


def create_dmg_background(target: Path, width: int = 780, height: int = 480) -> None:
    import struct
    import zlib

    bg = bytearray()
    for y in range(height):
        row = bytearray()
        t = y / (height - 1)
        r = int(20 + t * 30)
        g = int(34 + t * 40)
        b = int(60 + t * 50)
        for x in range(width):
            row.extend((r, g, b, 255))
        bg.append(0)
        bg.extend(row)

    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        chunk = chunk_type + data
        return struct.pack(
            ">I", len(data)
        ) + chunk + struct.pack(
            ">I", zlib.crc32(chunk) & 0xFFFFFFFF
        )

    with open(target, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
        f.write(png_chunk(b"IDAT", zlib.compress(bytes(bg), 9)))
        f.write(png_chunk(b"IEND", b""))


def build_dmg() -> None:
    app_path = ROOT / "dist" / "UPScale.app"
    if not app_path.exists():
        print("Kan UPScale.app niet vinden. Bouw eerst de app met python3 build_app.py.")
        return

    dmg_path = ROOT / "dist" / "UPScale.dmg"
    tmp_src = ROOT / "tmp_dmg_src"
    tmp_mount = ROOT / "tmp_dmg_mount"
    tmp_dmg = ROOT / "tmp_dmg.dmg"

    for p in [tmp_src, tmp_mount, tmp_dmg]:
        if p.exists():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()

    tmp_src.mkdir(parents=True, exist_ok=True)
    shutil.copytree(app_path, tmp_src / "UPScale.app", symlinks=True)
    (tmp_src / "Applications").symlink_to("/Applications")

    background_dir = tmp_src / ".background"
    background_dir.mkdir(parents=True, exist_ok=True)
    create_dmg_background(background_dir / "background.png")

    subprocess.run(
        [
            "hdiutil",
            "create",
            "-srcfolder",
            str(tmp_src),
            "-volname",
            "UPScale",
            "-ov",
            "-format",
            "UDRW",
            "-fs",
            "HFS+",
            str(tmp_dmg),
        ],
        cwd=ROOT,
        check=True,
    )

    tmp_mount.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "hdiutil",
            "attach",
            "-nobrowse",
            "-noverify",
            "-mountpoint",
            str(tmp_mount),
            str(tmp_dmg),
        ],
        cwd=ROOT,
        check=True,
    )

    applescript = f'''
        tell application "Finder"
            activate
            open (POSIX file "{tmp_mount}")
            delay 0.5
            set targetWindow to front Finder window
            set current view of targetWindow to icon view
            set toolbar visible of targetWindow to false
            set statusbar visible of targetWindow to false
            set bounds of targetWindow to {{100, 100, 740, 520}}
            set theViewOptions to icon view options of targetWindow
            set arrangement of theViewOptions to not arranged
            set icon size of theViewOptions to 96
            set background picture of theViewOptions to POSIX file "{tmp_mount}/.background/background.png"
            set position of item "UPScale.app" of targetWindow to {{140, 180}}
            set position of item "Applications" of targetWindow to {{500, 180}}
            delay 1
            close targetWindow
        end tell
    '''

    script_file = ROOT / "tmp_dmg_layout.scpt"
    script_file.write_text(applescript)
    subprocess.run(["osascript", str(script_file)], cwd=ROOT, check=True)
    script_file.unlink()

    try:
        subprocess.run(["hdiutil", "detach", str(tmp_mount)], cwd=ROOT, check=True)
    except subprocess.CalledProcessError:
        pass

    if dmg_path.exists():
        dmg_path.unlink()

    subprocess.run(
        [
            "hdiutil",
            "convert",
            "-ov",
            str(tmp_dmg),
            "-format",
            "UDZO",
            "-imagekey",
            "zlib-level=9",
            "-o",
            str(dmg_path),
        ],
        cwd=ROOT,
        check=True,
    )

    if tmp_dmg.exists():
        tmp_dmg.unlink()
    if tmp_src.exists():
        shutil.rmtree(tmp_src)
    if tmp_mount.exists():
        try:
            shutil.rmtree(tmp_mount)
        except OSError:
            pass

    print(f"DMG klaar: {dmg_path}")


def install_app() -> None:
    src_path = ROOT / "dist" / "UPScale.app"
    dest_path = Path("/Applications") / "UPScale.app"
    if not src_path.exists():
        print("Kan UPScale.app niet vinden. Bouw eerst de app met python3 build_app.py.")
        return

    if dest_path.exists():
        shutil.rmtree(dest_path)
    shutil.copytree(src_path, dest_path, symlinks=True)
    print(f"UPScale is geïnstalleerd in: {dest_path}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_app()
        return

    build_app_icns()

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name",
        "UPScale",
        "--windowed",
        "--onedir",
        "--noconfirm",
        "--icon",
        "app.icns",
        "--add-data",
        "led-pixelmap-tool_121.html:.",
        "--add-data",
        "app.icns:.",
        "--add-data",
        "icon.iconset:icon.iconset",
        "--add-data",
        "icon_fullbleed.iconset:icon_fullbleed.iconset",
        "app.py",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)

    dist = ROOT / "dist" / "UPScale.app"
    if dist.exists():
        print(f"Build klaar: {dist}")
        build_dmg()
    else:
        print("Build voltooid, maar het app-pakket is niet gevonden in dist/.")


if __name__ == "__main__":
    main()
