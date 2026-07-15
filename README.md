# UPScale Desktop App

[![Build Windows Installer](https://github.com/The-Ledguys-blip/UPScale/actions/workflows/build-windows.yml/badge.svg)](https://github.com/The-Ledguys-blip/UPScale/actions/workflows/build-windows.yml)
[![Build macOS App](https://github.com/The-Ledguys-blip/UPScale/actions/workflows/build-macos.yml/badge.svg)](https://github.com/The-Ledguys-blip/UPScale/actions/workflows/build-macos.yml)

## Direct downloaden

- [Download Windows Installer (MSI)](https://github.com/The-Ledguys-blip/UPScale/releases/latest/download/UPScale.msi)
- [Download macOS Installer (DMG)](https://github.com/The-Ledguys-blip/UPScale/releases/latest/download/UPScale.dmg)
- [Alle releases](https://github.com/The-Ledguys-blip/UPScale/releases)
- [Windows build artifacts (Actions)](https://github.com/The-Ledguys-blip/UPScale/actions/workflows/build-windows.yml)
- [macOS build artifacts (Actions)](https://github.com/The-Ledguys-blip/UPScale/actions/workflows/build-macos.yml)

Als een directe downloadlink toch een 404 geeft, controleer dan of de nieuwste tag-build nog bezig is in GitHub Actions.

UPScale is een desktoptool voor het schalen en exporteren van pixel-art assets, gebouwd met Python en PySide6.
De repository bevat de volledige broncode en build-scripts voor zowel macOS als Windows.

## Inhoud

- Broncode van de applicatie
- Build-scripts voor macOS en Windows
- GitHub Actions workflows voor cloud builds
- Packaging assets (icons, installer-configuratie)

## Volledige projectcode downloaden

Met Git:

```bash
git clone https://github.com/The-Ledguys-blip/UPScale.git
cd UPScale
```

Zonder Git:

1. Open de repository op GitHub.
2. Klik op Code.
3. Klik op Download ZIP.
4. Pak het ZIP-bestand uit.

## Snel starten (macOS)

1. Installeer dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Bouw app + DMG:

```bash
python3 build_app.py
```

3. Open de installer:

```bash
open dist/UPScale.dmg
```

4. Sleep UPScale.app naar Applications.

Direct installeren naar Applications:

```bash
python3 build_app.py install
```

## Windows build

Bouw op Windows een MSI installer met:

```bash
python build_app_windows.py
```

Output:

- dist/UPScale.msi
- dist/UPScale/ (portable app folder)

Details: [WINDOWS_BUILD.md](WINDOWS_BUILD.md)

## Releases en distributie

Er zijn twee manieren om distributie-bestanden te verkrijgen:

1. Lokaal bouwen met de scripts hierboven.
2. Bouwen via GitHub Actions en artifacts downloaden.

GitHub Actions workflows:

- Windows workflow: Build Windows Installer
- macOS workflow: Build macOS App

Artifacts:

- UPScale-Windows-Installer met UPScale.msi
- UPScale-macOS-Installer met UPScale.dmg en UPScale.app

### Releasebeleid

- Gebruik semantic versioning: MAJOR.MINOR.PATCH.
- Maak een release-tag als vX.Y.Z (bijvoorbeeld v1.2.0).
- Voeg bij elke release release notes toe met:
	- Wijzigingen voor gebruikers
	- Fixes en bekende beperkingen
	- Platformstatus (Windows, macOS)
- Publiceer per release minimaal deze bestanden:
	- Windows: UPScale.msi
	- macOS: UPScale.dmg
- Gebruik GitHub Releases als centrale downloadpagina voor eindgebruikers.
- Gebruik [.github/release-template.md](.github/release-template.md) als vaste structuur voor release notes.

## CI/CD (GitHub Actions)

- Push naar main of master start automatische builds.
- Handmatig starten kan via Actions > Run workflow.
- Artifacts zijn te downloaden vanuit de betreffende workflow-run.

Configuratie en gebruik:

- [GITHUB_ACTIONS_SETUP.md](GITHUB_ACTIONS_SETUP.md)
- [.github/workflows/build-windows.yml](.github/workflows/build-windows.yml)
- [.github/workflows/build-macos.yml](.github/workflows/build-macos.yml)

## Belangrijke projectbestanden

- [app.py](app.py): hoofdapplicatie
- [build_app.py](build_app.py): macOS buildscript
- [build_app_windows.py](build_app_windows.py): Windows MSI buildscript
- [BUILD_GUIDE.md](BUILD_GUIDE.md): platformoverzicht voor builds

## Build-output overzicht

- macOS: dist/UPScale.app en dist/UPScale.dmg
- Windows: dist/UPScale/ en dist/UPScale.msi

## Bijdragen

Bijdragen zijn welkom. Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor de werkwijze voor branches, pull requests en quality checks.
