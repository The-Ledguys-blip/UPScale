# Contributing to UPScale

Bedankt voor je interesse om bij te dragen aan UPScale.
Deze handleiding zorgt ervoor dat wijzigingen voorspelbaar en reviewbaar blijven.

## Development setup

1. Fork of clone de repository.
2. Installeer dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Start de app lokaal:

```bash
python3 app.py
```

## Branch strategy

- Base branch: main
- Maak voor elke wijziging een aparte branch, bijvoorbeeld:
  - feature/export-improvement
  - fix/windows-installer-path
  - docs/readme-release-section

## Commit guidelines

- Gebruik korte, beschrijvende commit messages in de gebiedende wijs.
- Voorbeelden:
  - Add macOS artifact upload step
  - Fix MSI output path validation
  - Improve README release instructions

## Pull request checklist

Maak een PR met:

1. Duidelijke titel en samenvatting van de wijziging.
2. Motivatie: welk probleem lost dit op.
3. Testresultaat:
   - lokaal getest op relevant platform
   - of succesvolle GitHub Actions run
4. Screenshots of terminal-output indien relevant.

## Quality expectations

- Houd wijzigingen klein en gericht.
- Werk documentatie bij als gedrag of build-stappen veranderen.
- Breek geen bestaande build-scripts voor andere platformen.
- Controleer waar mogelijk zowel Windows als macOS impact.

## CI and artifacts

- Elke push naar main of master kan workflows triggeren.
- Gebruik Actions artifacts voor validatie van distributiebestanden.
- Bij release-kandidaten: verifieer altijd zowel UPScale.msi als UPScale.dmg.

## Security and sensitive data

- Commit nooit API keys, certificaten, wachtwoorden of tokens.
- Gebruik GitHub Secrets voor signing/notarization-informatie.

## Vragen

Open een issue of start een draft PR als je vroeg feedback wilt op je aanpak.
