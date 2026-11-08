# UPScale Release v3.1.0

## Summary

UPScale v3.1.0 voegt slice-koppeling toe. Als een object groter is dan één slice, kun je meerdere slices fysiek aan elkaar koppelen (horizontaal of verticaal). Het kruis en de cirkel worden dan als één geheel over het virtuele vlak berekend en lopen door over de naad tussen de slices.

## What's New

- **Live Output vloeiend met meerdere uitgangen**: elk live-venster krijgt alleen nog een nieuw beeld als zijn eigen canvas echt verandert. Bij 1, 2 en 4 live outputs blijven de vensters op 60 fps en blijft ook de hoofdapp op 60 fps, ook tijdens het slepen van een slice. Lopende testpatroon-animaties worden bij een update niet meer gereset, maar pakken de beweging op waar ze waren.
- **Slice-koppeling (horizontaal/verticaal)**: selecteer 2 of meer slices en klik op **Koppel ↔** of **Koppel ↕** in de balk boven de compositie.
- **Doorlopend kruis en rondje**: markeringen worden op het virtuele vlak van de hele groep berekend en per slice geclipt, zodat ze exact op de naad aansluiten.
- **Koppeling-sectie per slice**: badge met positie (bijv. 🔗 2/3), uitleg, volgorde aanpassen met ◀/▶, groep selecteren en ontkoppelen.
- **Leider bepaalt de cirkelvorm**: de eerste slice in de groep bepaalt de cirkelvervorming (zodat de vorm op de naad aansluit). Cirkel, kruis en tekstkleur (zwart/wit) blijven **per slice** instelbaar en werken gewoon door in een gekoppelde groep.
- **Automatische volgorde**: bij koppelen wordt horizontaal gesorteerd op X en verticaal op Y; daarna handmatig aan te passen.
- **Live Output pixel-per-pixel**: de live-uitgang toont nu de echte canvasresolutie 1:1 vanaf 0,0 (canvaspixel = uitvoerpixel), zonder de geschaalde 1300×640-overview en zonder CSS-schaling. Is de canvas groter dan het scherm, dan worden de buitenste pixels afgeknipt.
- **RGB-waarden per object**: onder de kleur-slider staan drie velden met de exacte R/G/B-waarden (0–255). Je kunt ze bewerken, met de kopieerknop kopiëren en met de plakknop direct op een ander object toepassen (of handmatig plakken als `r, g, b`), zodat de kleur exact gelijk wordt.
- **Bevestiging bij bestaand exportbestand**: als je 1:1 + Scaled Output exporteert en er bestaat al een PNG met dezelfde naam, vraagt de app eerst om bevestiging met **Annuleren** of **Overschrijven**. Er wordt nooit stilzwijgend overschreven of automatisch hernoemd.
- **Colorbars 100% (diagonaal, bewegend)**: nieuw testpatroon met de zeven 100%-kleurbalken als diagonale banden die schuin naar beneden schuiven en naadloos loopen, zoals in Megapixel VR/HELIOS. Snelheid regelbaar met de bestaande slider; Motion uitzetten maakt het patroon statisch.
- **Los verplaatsen of als groep**: een gekoppelde slice kun je gewoon individueel slepen en snappen. Selecteer je de hele groep (Shift+klik of **Selecteer groep**), dan verplaatst en snapt de groep als één object op andere slices en de canvas.
- **Shift+klik multi-select**: houd Shift (of Cmd/Ctrl) ingedrukt en klik slices aan of uit in de 1:1-weergave en Stage; de selectiebalk en koppel-knoppen volgen direct.
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
- [x] Shift+klik selecteert meerdere slices in de 1:1-weergave
- [x] Gewone klik selecteert één slice en deselecteert bij nogmaals klikken
- [x] Gekoppelde slice is los te verplaatsen en snapt daarbij
- [x] Snapt de hele groep als één object wanneer de groep geselecteerd is
- [x] Pijltjestoetsen verplaatsen de geselecteerde slices (groep bij groep-selectie)
- [x] Live-uitgang toont 1:1 canvasresolutie vanaf 0,0 (geen overview/schaling)
- [x] Live-router per canvas blijft werken
- [x] 1, 2 en 4 live outputs blijven op 60 fps
- [x] Hoofdapp blijft op 60 fps tijdens slepen met 4 live outputs
- [x] Testpatroon-animatie loopt door in live output tijdens updates
- [x] RGB-velden tonen de exacte waarden en zijn bewerkbaar
- [x] Kopieer- en plakknop voor exacte objectkleur werken
- [x] Gekopieerde kleur plakken als 'r, g, b' werkt in een ander object
- [x] Kleur en RGB blijven bewaard na herladen
- [x] Export naar bestaande PNG vraagt om Annuleren of Overschrijven
- [x] Annuleren laat bestaande bestanden ongemoeid
- [x] Overschrijven vervangt precies hetzelfde bestand
- [x] Colorbars 100% diagonaal beweegt naadloos naar beneden
- [x] Bestaande colorbars (verticaal/horizontaal) werken ongewijzigd
- [x] Persistentie na herladen (autosave)
- [x] Groep wordt opgeheven bij verwijderen van een lid
- [ ] macOS DMG mount en app copy naar Applications werkt
- [ ] Windows installer/portable ZIP start correct
