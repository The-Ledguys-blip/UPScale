# UPScale desktop app

Deze map bevat een eenvoudige Python desktopversie van de HTML-app.

## Aan de slag

1. Installeer de afhankelijkheden:
   ```bash
   python3 -m pip install -r requirements.txt
   ```
2. Bouw de app en het installatiediskimage:
   ```bash
   python3 build_app.py
   ```
3. Open de DMG om `UPScale.app` te installeren:
   ```bash
   open dist/UPScale.dmg
   ```
4. Sleep `UPScale.app` naar de `Applications` map in het geopende schijfkopievenster.

## Direct installeren

Je kunt de app ook rechtstreeks naar `/Applications` kopiëren met:
```bash
python3 build_app.py install
```

## Windows installer bouwen

Op Windows kun je een echte installer maken met:
```bash
python build_app_windows.py
```

Dat maakt `dist/UPScale.msi` plus een portable app-map in `dist/UPScale/`.
Voor details, zie [WINDOWS_BUILD.md](/Users/kevinveen/Downloads/upscale-desktop-app/WINDOWS_BUILD.md).

## Wat er gebeurt

- `build_app.py` maakt eerst `app.icns` op basis van de full-bleed iconset.
- Daarna bouwt het `dist/UPScale.app` met PyInstaller.
- Tot slot genereert het `dist/UPScale.dmg` met een `Applications` symlink voor makkelijke installatie.
