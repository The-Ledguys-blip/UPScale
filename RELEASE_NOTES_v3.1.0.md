# UPScale Release v3.1.0

## Summary

UPScale v3.1.0 voegt slice-koppeling toe. Als een object groter is dan één slice, kun je meerdere slices fysiek aan elkaar koppelen (horizontaal of verticaal). Het kruis en de cirkel worden dan als één geheel over het virtuele vlak berekend en lopen door over de naad tussen de slices.

## What's New

- **Slice-koppeling (horizontaal/verticaal)**: selecteer 2 of meer slices en klik op **Koppel ↔** of **Koppel ↕** in de balk boven de compositie.
- **Doorlopend kruis en rondje**: markeringen worden op het virtuele vlak van de hele groep berekend en per slice geclipt, zodat ze exact op de naad aansluiten.
- **Koppeling-sectie per slice**: badge met positie (bijv. 🔗 2/3), uitleg, volgorde aanpassen met ◀/▶, groep selecteren en ontkoppelen.
- **Leider bepaalt de cirkelvorm**: de eerste slice in de groep bepaalt de cirkelvervorming (zodat de vorm op de naad aansluit). Cirkel, kruis en tekstkleur (zwart/wit) blijven **per slice** instelbaar en werken gewoon door in een gekoppelde groep.
- **Automatische volgorde**: bij koppelen wordt horizontaal gesorteerd op X en verticaal op Y; daarna handmatig aan te passen.
- **Duurzaam**: koppeling wordt opgeslagen in project/autosave, meegenomen in undo/redo, en opgeruimd bij verwijderen of plakken.

## Fixes

- Geen regressies in bestaande enkelvoudige cirkel/kruis-weergave; elke slice zonder groep gedraagt zich zoals voorheen.

## Downloads

### Windows

- Installer: UPScale-Setup-3.1.0.exe
- MSI: UPScale-3.1.0-x64.msi
- Portable: UPScale-3.1.0-win64.zip

### macOS

- Installer: UPScale-3.1.0.dmg
- App bundle: UPScale.app

## Upgrade Notes

- Projecten en autosave uit eerdere versies worden automatisch gemigreerd; slices zonder koppeling blijven ongewijzigd.
- Een koppeling vereist minimaal 2 slices; verwijder je er één, dan wordt de groep automatisch opgeheven.

## Known Issues

- Ongetekende binaries kunnen een SmartScreen- of Gatekeeper-waarschuwing tonen.
- De Windows MSI/EXE moet op Windows worden gebouwd (WiX/Inno Setup).

## Validation Checklist

- [x] Horizontaal koppelen: cirkel en kruis lopen exact door over de verticale naad
- [x] Verticaal koppelen: cirkel en kruis lopen exact door over de horizontale naad
- [x] Markeringen per slice geclipt op eigen rechthoek
- [x] Cirkel/kruis-checkboxen werken per slice, ook binnen een koppeling
- [x] Tekstkleur zwart/wit werkt per slice, ook binnen een koppeling
- [x] Cirkelvorm (vervorming) wordt door de leider bepaald
- [x] Badge, status en disabled controls in de slice-kaarten
- [x] Persistentie na herladen (autosave)
- [x] Groep wordt opgeheven bij verwijderen van een lid
- [ ] macOS DMG mount en app copy naar Applications werkt
- [ ] Windows installer/portable ZIP start correct
