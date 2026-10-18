# UPScale — Windows 11 build

De Windows-build maakt met PyInstaller een `UPScale.exe` en optioneel een
Inno Setup-installer of een draagbare ZIP. Het build-script leest het
versienummer automatisch uit `led-pixelmap-tool_121.html` (`APP_VERSION`),
dus je hoeft nergens anders een versie aan te passen.

## Vereisten
- **Windows 11** (64-bit)
- **Python 3.9+** van [python.org](https://www.python.org/downloads/) — vink **"Add Python to PATH"** aan
- Optioneel voor de installer: [Inno Setup 6](https://jrsoftware.org/isdl.php) (ISCC.exe)

## Stap 1 — Dependencies
Open Command Prompt in de projectmap en run:

```bat
py -m pip install -r requirements.txt
```

## Stap 2 — Bouwen

```bat
py build_app_windows.py            :: alleen dist\UPScale\UPScale.exe
py build_app_windows.py zip        :: + dist\UPScale-<versie>-win64.zip
py build_app_windows.py installer  :: + installer_output\UPScale-Setup-<versie>.exe (Inno Setup 6)
py build_app_windows.py clean      :: verwijder build\ en dist\
```

Resultaat van de standaard-build:
- `dist\UPScale\UPScale.exe` — start het programma (de hele map `dist\UPScale\` is de draagbare app)

## Stap 3 — Installer (optioneel)

`build_app_windows.py installer` zoekt `ISCC.exe` automatisch op deze plekken:
- `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`
- `C:\Program Files\Inno Setup 6\ISCC.exe`
- of `ISCC` in `PATH`

Het script geeft de versie mee via `/DMyAppVersion=<versie>`, dus de
installer-naam en versie-info blijven in sync met de HTML.

## Stap 4 — Testen

1. Start `dist\UPScale\UPScale.exe` (of installeer de Setup-EXE)
2. Open/opslaan van een project, exporteren van een afbeelding
3. Export-bestanden komen in `%USERPROFILE%\Downloads\UPScale-export-*`

## Delen
- **Installer**: `installer_output\UPScale-Setup-<versie>.exe`
- **Draagbare map**: `dist\UPScale\`
- **Draagbare ZIP**: `dist\UPScale-<versie>-win64.zip`

## GitHub Actions
Geen Windows-machine? De workflow "Build Windows Installer" in `.github/workflows`
bouwt de installer op GitHub. Push naar `main`, open **Actions**, kies de
laatste geslaagde run en download het artifact.

## Problemen oplossen

### "Python not found"
- Herinstalleer Python met "Add Python to PATH" en heropen Command Prompt.

### "Module not found"
```bat
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
```

### "ISCC.exe niet gevonden"
- Installeer Inno Setup 6 en heropen Command Prompt, of voeg het installatiepad aan `PATH` toe.

### App start niet na installatie
- Start vanuit Command Prompt om de foutmelding te zien:
  ```bat
  "C:\Program Files\UPScale\UPScale.exe"
  ```

### SmartScreen-waarschuwing
- De app is niet ondertekend; klik "Meer informatie" → "Toch uitvoeren".

## Notities
- Zelfde UI en exportstructuur als de macOS-versie.
- Op macOS bouw je met `python3 build_app.py` (DMG + install naar /Applications).
