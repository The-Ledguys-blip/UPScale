# UPScale v1.1.0

## Highlights

- Major Windows GUI stability and performance improvements.
- Reduced flicker/black flashes during scrolling and interaction.
- Smoother drag, pan (spacebar hand tool), and selection behavior.
- Improved rendering pipeline with lower redraw overhead.

## Fixed

- Guide line image now appears reliably right after upload at 50% opacity.
- Spacebar hand tool can pan with left mouse as expected.
- Several intermittent WebEngine repaint glitches on Windows.
- Improved startup render-mode handling with safer fallbacks.

## Packaging

- Updated Windows build artifacts generated:
  - `dist/UPScale/UPScale.exe`
  - `dist/UPScale.msi`

## Notes

- Existing project workflows and exports remain compatible.
- If needed, render mode can still be adjusted from the app settings for compatibility.
