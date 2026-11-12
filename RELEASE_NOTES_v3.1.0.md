# UPScale Release v3.1.0

## Summary

UPScale v3.1.0 voegt slice-koppeling toe. Als een object groter is dan één slice, kun je meerdere slices fysiek aan elkaar koppelen (horizontaal of verticaal). Het kruis en de cirkel worden dan als één geheel over het virtuele vlak berekend en lopen door over de naad tussen de slices.

## What's New

- **Slice selecteren op de canvas**: klik je een slice aan in de 1:1-compositie, dan komt die slice bovenaan de slicelijst te staan zonder dat de pagina of canvas verspringt. Alleen de slicelijst zelf scrolt; het canvas blijft exact op zijn plek. Die kaart blijft bovenaan staan terwijl je er iets in wijzigt — ook bij het kiezen of uitzetten van een testpatroon — zodat de lijst niet naar een andere slice verspringt.
- **Tab in het objecten-menu**: met Tab ga je direct naar de invulbare velden (naam, R/G/B, positie, resolutie, checkboxes). De ▲/▼-stapknoppen, schuifbalken en icoon-knoppen worden overgeslagen, zodat je snel door de gegevens heen tabt. Alles blijft gewoon met de muis bedienbaar.
- **Live Output vloeiend met meerdere uitgangen**: elk live-venster krijgt alleen nog een nieuw beeld als zijn eigen canvas echt verandert. Bij 1, 2 en 4 live outputs blijven de vensters op 60 fps en blijft ook de hoofdapp op 60 fps, ook tijdens het slepen van een slice. Lopende testpatroon-animaties worden bij een update niet meer gereset, maar pakken de beweging op waar ze waren.
- **Slice actief/inactief**: naast de naam van elke slice staat een rond actief-balletje. Uitvinken maakt de slice grijs, verbergt hem uit het canvas, de Stage, de live-uitgang en de export, en vergrendelt alle bediening (velden, knoppen, slepen en pijltjestoetsen) tot je hem weer aanvinkt. Zo bescherm je een scherm tijdelijk tegen aanpassingen zonder het te verwijderen.
- **Eigen projectbestand (.UP)**: projecten worden opgeslagen als `*.UP` in plaats van `*.json`. Bij **Opslaan als…** stelt de app automatisch de `.UP`-extensie in. Oude `.json`-projecten kun je nog steeds openen; bij de eerstvolgende keer opslaan worden ze als `.UP` bewaard.
- **Opslaan als… met het native opslaanvenster**: **Opslaan als…** opent het vertrouwde macOS-opslaanvenster (op Windows het Windows-opslaanvenster) met een invulbare bestandsnaam en locatiekiezer, zodat je zelf bepaalt hoe het bestand heet en waar het komt. De gekozen map wordt onthouden. Bestaat het bestand al, dan bevestigt het systeem het overschrijven. **Opslaan** schrijft daarna direct naar hetzelfde bestand, zonder nieuwe download of extra vraag.
- **Slice-koppeling**: selecteer 2 of meer slices en klik op **Koppel ↔** of **Koppel ↕** in de balk boven de compositie. **Koppel ↔** zet alle geselecteerde slices virtueel in één rij van links naar rechts; **Koppel ↕** zet ze in één kolom van boven naar onder. De volgorde volgt de leesvolgorde op de canvas (rij voor rij, links → rechts), maar de fysieke posities op de canvas blijven precies staan. Zo wordt een 3×2-raster bij horizontaal koppelen één virtueel vlak van 1×6, terwijl de slices op de canvas in hun 3×2-opstelling blijven liggen. Cirkel en kruis lopen over alle naden heen door.
- **Slice roteren**: in de slice-kaart kies je **0°**, **90°**, **180°** of **270°**. De hele slice draait mee: paneelraster, kruis, cirkel, tekst en namen. Bij 90° of 270° wisselen breedte en hoogte op het canvas, zodat de voetafdruk, de resolutie en de uitvoer kloppen. Werkt in 1:1, Scaled Output, Stage, Overview, live-uitgang en PNG-export. Gekoppelde slices draai je niet; ontkoppel eerst.
- **Virtuele indeling vastgezet**: op het moment van koppelen wordt de virtuele plaats van elke slice vastgelegd (rij, kolom, offset en resolutie). Verplaats je daarna een slice op de pixelmap, dan blijft het virtuele beeld gelijk: de slice behoudt zijn eigen deel van het virtuele vlak en alleen de fysieke positie verandert. Met **Herbereken indeling** leg je de indeling opnieuw vast op basis van de huidige posities.
- **Koppel custom… (vrije routing)**: met **Koppel custom…** open je een routing-canvas waarin je elke slice zelf in de gewenste virtuele positie zet. Het routing-canvas is onafhankelijk van de canvasmaat van het project en groeit automatisch mee: je kunt slices vrij naast elkaar of ver onder elkaar plaatsen zonder tegen een kader aan te lopen. Sleep de slice-tegels vrij rond; randen en hartlijnen magnetiseren (houd **Alt** ingedrukt om vrij te plaatsen) en de editor scrolt mee als je voorbij de rand sleept. Met de presets **Rij**, **Kolom** en **Raster** begin je snel, met de pijltjestoetsen stel je posities pixel voor pixel bij (Shift = 10 px) en in het zijpaneel typ je X/Y exact in. **Toepassen** legt de vrije indeling vast; **Annuleren** laat alles ongemoeid. Open je het custom-menu later opnieuw, dan staan de eerder gekozen posities er weer; pas nadat je de koppeling hebt verbroken begin je weer met de standaardindeling. Een bestaande koppeling pas je ook aan via **Indeling…** in de Koppeling-sectie.
- **Doorlopend kruis en rondje**: markeringen worden op het virtuele vlak van de hele groep berekend en per slice geclipt, zodat ze exact op de naad aansluiten.
- **Testmode toont alleen het testpatroon**: staat een testpatroon aan, dan zie je op de canvas, Stage, Overview, live-uitgang en in de export uitsluitend het patroon. Cirkel, kruis, naam, positie, resolutie en paneelaantal worden dan onderdrukt — ook binnen een gekoppelde groep, zodat het patroon altijd boven de markeringen ligt.
- **Koppeling-sectie per slice**: badge met positie (bijv. 🔗 2/3), rij/kolom of vrije X/Y in het virtuele vlak, **Selecteer groep**, **Indeling…**, **Herbereken indeling** en **Ontkoppel**.
- **Leider bepaalt de cirkelvorm**: de eerste slice in de groep bepaalt de cirkelvervorming (zodat de vorm op de naad aansluit). Cirkel, kruis en tekstkleur (zwart/wit) blijven **per slice** instelbaar en werken gewoon door in een gekoppelde groep.
- **Automatische volgorde**: bij koppelen wordt de selectie in leesvolgorde gesorteerd (boven → beneden, links → rechts) en daarna vastgezet.
- **Live Output pixel-per-pixel**: de live-uitgang toont nu de echte canvasresolutie 1:1 vanaf 0,0 (canvaspixel = uitvoerpixel), zonder de geschaalde 1300×640-overview en zonder CSS-schaling. Is de canvas groter dan het scherm, dan worden de buitenste pixels afgeknipt.
- **Testpatroon op de hele live-output**: per canvas kies je in Live Output een testpatroon uit dezelfde bank als bij 1:1 (zwart, rood, groen, blauw, wit, diagonaal, gradient, grid en de 100%-colorbars verticaal/horizontaal/diagonaal). Het patroon vult de **hele output op exact de canvasresolutie** — is het canvas 3840×2160, dan is het patroon ook 3840×2160 vanaf 0,0. Tijdens het testpatroon worden slices en labels onderdrukt, zodat alleen het signaal naar de LED-processor gaat. Snelheid en beweging zijn per canvas regelbaar en het patroon wordt met het project opgeslagen.
- **RGB-waarden per object**: onder de kleur-slider staan drie velden met de exacte R/G/B-waarden (0–255). Je kunt ze bewerken, met de kopieerknop kopiëren en met de plakknop direct op een ander object toepassen (of handmatig plakken als `r, g, b`), zodat de kleur exact gelijk wordt.
- **Bevestiging bij bestaand exportbestand**: als je 1:1 + Scaled Output exporteert en er bestaat al een PNG met dezelfde naam, vraagt de app eerst om bevestiging met **Annuleren** of **Overschrijven**. Er wordt nooit stilzwijgend overschreven of automatisch hernoemd.
- **Colorbars 100% (diagonaal, bewegend)**: nieuw testpatroon met de zeven 100%-kleurbalken als diagonale banden die schuin naar beneden schuiven en naadloos loopen, zoals in Megapixel VR/HELIOS. Snelheid regelbaar met de bestaande slider; Motion uitzetten maakt het patroon statisch.
- **Los verplaatsen of als groep**: een gekoppelde slice kun je gewoon individueel slepen en snappen. Selecteer je de hele groep (Shift+klik of **Selecteer groep**), dan verplaatst en snapt de groep als één object op andere slices en de canvas.
- **Shift+klik multi-select**: houd Shift (of Cmd/Ctrl) ingedrukt en klik slices aan of uit in de 1:1-weergave en Stage; de selectiebalk en koppel-knoppen volgen direct.
- **Duurzaam**: koppeling wordt opgeslagen in project/autosave, meegenomen in undo/redo, en opgeruimd bij verwijderen of plakken.

## Fixes

- **IM mode werkt weer**: een fout in de IM-paneeltekening (`idNs is not defined`) zorgde ervoor dat IM mode de compositie niet kon renderen. Daardoor leken ook de actief-schakelaar en het testpatroon daarna niet meer te reageren. IM mode rendert nu correct en blokkeert de overige bediening niet meer.
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
- [x] Horizontaal koppelen: alle geselecteerde slices virtueel in één rij, posities op de canvas blijven staan
- [x] Slice actief/inactief-balletje: inactief grijs, verborgen in canvas/uitvoer en vergrendeld
- [x] Projectbestanden gebruiken de eigen .UP-extensie (oude .json-bestanden blijven leesbaar)
- [x] Opslaan als… opent het native macOS/Windows-opslaanvenster met bestandsnaam en locatiekeuze
- [x] Opslaan schrijft direct naar het gekozen bestand (zonder browserdownload)
- [x] Virtuele indeling blijft vast bij verplaatsen van een gekoppelde slice
- [x] **Koppel custom…** opent een routing-canvas met sleepbare slice-tegels
- [x] Sleepbare tegels met magnetiseren op randen en hartlijnen (Alt = vrij plaatsen)
- [x] Routing-canvas staat los van de canvasmaat en groeit mee bij vrij plaatsen
- [x] Vrij onder of naast elkaar plaatsen voorbij de oorspronkelijke rand werkt (met autoscroll)
- [x] Presets Rij, Kolom en Raster werken in de routing-editor
- [x] Pijltjestoetsen (1 px) en Shift+pijltjestoetsen (10 px) verplaatsen de geselecteerde tegel
- [x] X/Y zijn exact in te typen in het zijpaneel
- [x] Toepassen legt de vrije indeling vast; Annuleren laat de slices ongemoeid
- [x] Bestaande koppeling aanpassen via **Indeling…** in de Koppeling-sectie
- [x] Slice roteren 0/90/180/270 draait kruis, cirkel, tekst en namen mee in alle weergaven en exports
- [x] Gekoppelde slices blokkeren rotatie (ontkoppel eerst)
- [x] Custom-menu onthoudt de toegepaste posities bij opnieuw openen
- [x] Na ontkoppelen start het custom-menu weer met de standaardindeling
- [x] Vrije indeling blijft bewaard na undo/redo, herladen en autosave
- [x] Vrije indeling werkt door in 1:1, Stage, Overview, live-uitgang en export
- [x] Knop **Herbereken indeling** om de virtuele indeling opnieuw vast te leggen
- [x] 2×3-koppeling vormt één virtueel vlak met doorlopende cirkel/kruis
- [x] Live-uitgang toont 1:1 canvasresolutie vanaf 0,0 (geen overview/schaling)
- [x] Live-testpatroon vult de hele output op exact de canvasresolutie (3840×2160 → patroon 3840×2160)
- [x] Live-testpatroon gebruikt dezelfde bank als 1:1 en verbergt slices/labels in de uitgang
- [x] Live-testpatroon is per canvas instelbaar (type, snelheid, beweging) en wordt opgeslagen
- [x] Live-router per canvas blijft werken
- [x] 1, 2 en 4 live outputs blijven op 60 fps
- [x] Hoofdapp blijft op 60 fps tijdens slepen met 4 live outputs
- [x] Testpatroon-animatie loopt door in live output tijdens updates
- [x] Tab in objecten-menu slaat pijltjes, sliders en knoppen over
- [x] RGB-velden tonen de exacte waarden en zijn bewerkbaar
- [x] Kopieer- en plakknop voor exacte objectkleur werken
- [x] Gekopieerde kleur plakken als 'r, g, b' werkt in een ander object
- [x] Kleur en RGB blijven bewaard na herladen
- [x] Export naar bestaande PNG vraagt om Annuleren of Overschrijven
- [x] Annuleren laat bestaande bestanden ongemoeid
- [x] Overschrijven vervangt precies hetzelfde bestand
- [x] Colorbars 100% diagonaal beweegt naadloos naar beneden
- [x] Testmode verbergt cirkel, kruis, naam, positie, resolutie en paneelaantal in canvas, Stage, Overview, live en export
- [x] Testmode werkt ook binnen een gekoppelde groep, zonder markeringen over het patroon
- [x] Klik op een slice in de canvas scrolt de slicelijst naar die slice, met de properties bovenaan
- [x] De geselecteerde slice blijft bovenaan staan bij het wijzigen van bijvoorbeeld het testpatroon
- [x] Een slice aanklikken in de canvas laat de pagina en canvas staan; alleen de slicelijst scrolt naar de selectie
- [x] IM mode aan/uit rendert zonder fouten en blokkeert andere bediening niet
- [x] Actief/inactief, testpatroon, koppelen, undo/redo en live/export werken na de IM-fix
- [x] Bestaande colorbars (verticaal/horizontaal) werken ongewijzigd
- [x] Persistentie na herladen (autosave)
- [x] Groep wordt opgeheven bij verwijderen van een lid
- [ ] macOS DMG mount en app copy naar Applications werkt
- [ ] Windows installer/portable ZIP start correct
