# Feature Requests

## Known Issues
- **Unknown icon fallback renders as yellow ⚠ triangle**: When an unrecognised icon name is passed, the intended fallback glyph `\U000F0026` (mdi:alert-circle-outline) does not render — instead the display shows a yellow Unicode warning triangle (⚠). Root cause: the glyph is likely absent from the compiled icon font bitmap so ESPHome's display library falls back to a system symbol. Fix: ensure `\U000F0026` is explicitly included in the `icon_font_48` glyph list in `displayarbeitszimmer.base.yaml`, OR choose a different fallback glyph that is already confirmed present.

- [x] Header queue with priority and timeout instead of last-write-wins
- Footer layout presets per page (ip/wifi/clock/custom)
- Per-page theme overrides (accent/title/detail colors)
- Custom icon images (static PNG/bitmap) in addition to MDI glyphs
- Text scrolling/marquee for long titles/details
- [x] Progress bar widget type (0-100) instead of text-only progress
- Sleep/Do-Not-Disturb window with dimming in the component
- Page priority and sticky pages (exclude from rotation)
