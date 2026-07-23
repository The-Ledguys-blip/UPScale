# UPScale Release v2.0.0

## Summary

UPScale v2.0.0 verbetert vooral de Windows 11 distributie en platformcompatibiliteit, met een stabielere build-output voor installers en portable gebruik.

## What's New

- Windows releaseflow publiceert nu zowel een MSI installer als een portable ZIP.
- CI uploadt artifacts voor beide Windows distributievormen.
- Tag-releases voegen beide Windows bestanden toe aan GitHub Releases.

## Fixes

- Hardcoded macOS fallback pad verwijderd voor HTML runtime asset detectie.
- Downloads-locatie wordt nu platform-onafhankelijk bepaald.
- Export foldernamen worden opgeschoond voor geldige Windows bestandsnamen.
- Consistente pad- en exportlogica toegepast in zowel app.py als windows-build/app.py.

## Downloads

### Windows

- Installer: UPScale.msi
- Portable: UPScale-portable.zip

### macOS

- Installer: UPScale.dmg
- App bundle: UPScale.app

## Upgrade Notes

- Deze release vereist geen datamigratie.
- Voor Windows distributie wordt MSI aanbevolen; portable ZIP is beschikbaar als fallback.

## Known Issues

- Ongetekende binaries kunnen een SmartScreen waarschuwing tonen op Windows.

## Validation Checklist

- [ ] Windows installer installeert en start correct
- [ ] Windows portable ZIP start correct
- [ ] macOS DMG mount en app copy naar Applications werkt
- [ ] Export functionaliteit getest
- [ ] Open/save project getest
- [ ] GitHub Actions artifacts succesvol

## Checksums (optional)

Voeg hier checksums toe indien gewenst.

- SHA256 UPScale.msi:
- SHA256 UPScale-portable.zip:
- SHA256 UPScale.dmg:
