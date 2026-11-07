# UPScale Release v3.0.0

## Summary

UPScale v3.0.0 is een grote release: meerdere 1:1-canvassen als aparte werkruimtes, een Live Output-router per canvas, een uitgebreid testpatroon-systeem en vrije canvasresolutie met automatisch berekende aspect ratio.

## What's New

- Meerdere canvassen als aparte 1:1-werkruimtes, met eigen resolutie, slices en undo/redo.
- Live Output per canvas: handmatige routering, schermkeuze en een preview-grid van alle canvassen.
- Live-venster toont exact hetzelfde beeld als het Scaled Output-canvas.
- Testpatronen met eigen menu: Zwart, Rood, Groen, Blauw, Wit, Counters, Diagonale lijnen, Gradient, Grid en Colorbars 100% (verticaal/horizontaal).
- Testpatroon-opties: snelheidsslider en Motion/Horizontaal/Verticaal met seamless loop.
- Canvas & weergave: pixelresolutie is leidend, aspect ratio wordt automatisch berekend en is readonly (greyed out).
- Custom-modus voor vrije resolutie; presets (16:9, 16:10, 4:3, 21:9, 1:1, 9:16) schalen de andere zijde mee.
- macOS-app opent standaard gemaximaliseerd.

## Fixes

- Colorbars behouden hun exacte kleuren; horizontaal/verticaal wijzigt alleen de beweging.
- Cirkel/kruis volgen de zwart/wit-tekstkleur-slider.
- Canvassen-popup opent alleen via het pijltje naast de canvasnaam.

## Downloads

### Windows

- Installer: UPScale-Setup-3.0.0.exe
- MSI: UPScale-3.0.0-x64.msi
- Portable: UPScale-3.0.0-win64.zip

### macOS

- Installer: UPScale-3.0.0.dmg
- App bundle: UPScale.app

## Upgrade Notes

- Projecten en autosave uit eerdere versies worden automatisch gemigreerd.
- De gekozen aspect-modus (preset/custom) wordt per canvas opgeslagen.

## Known Issues

- Ongetekende binaries kunnen een SmartScreen- of Gatekeeper-waarschuwing tonen.
- De Windows MSI/EXE moet op Windows worden gebouwd (WiX/Inno Setup).

## Validation Checklist

- [ ] macOS DMG mount en app copy naar Applications werkt
- [ ] Windows installer/portable ZIP start correct
- [ ] Meerdere canvassen aanmaken, wisselen en hernoemen
- [ ] Live Output per canvas en preview-grid
- [ ] Testpatronen inclusief Colorbars 100%
- [ ] Custom resolutie en automatische aspect ratio
- [ ] Open/save project en autosave
- [ ] Export functionaliteit
