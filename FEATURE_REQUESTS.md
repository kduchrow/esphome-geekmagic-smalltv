# Feature Requests

## Known Issues

- **Unknown icon fallback renders as yellow warning triangle**: When an unrecognised icon name is passed, the intended fallback glyph `\U000F0026` (mdi:alert-circle-outline) does not render — instead the display shows a yellow Unicode warning triangle. Root cause: the glyph is likely absent from the compiled icon font bitmap so ESPHome's display library falls back to a system symbol. Fix: ensure `\U000F0026` is explicitly included in the `icon_font_48` glyph list, OR choose a different fallback glyph that is already confirmed present.

## Backlog

- [ ] Footer layout presets per page (ip/wifi/clock/custom)
- [ ] Per-page theme overrides (accent/title/detail colors)
- [ ] Custom icon images (static PNG/bitmap) in addition to MDI glyphs
- [ ] Text scrolling/marquee for long titles/details
- [ ] Sleep/Do-Not-Disturb window with dimming in the component
- [ ] Page priority and sticky pages (exclude from rotation)

## Testing

- [ ] Corner-case tests: unicode/special characters, empty strings, max_pages overflow
- [ ] Corner-case tests: max_headers overflow, rapid-fire service calls
- [ ] Corner-case tests: progress=-1, font_size=invalid, pulse_period_ms=0
- [ ] Corner-case tests: delimiter in title/subtitle, same page_id multiple times

## Infrastructure

- [ ] CI/CD: GitHub Actions with `esphome config` + `esphome compile` validation
- [ ] Refactor `tests/test_display.py`: split scenarios and runner into separate modules

## Portability

- [ ] Support for other ESP32/ESP8266 boards beyond GeekMagic SmallTV Ultra
- [ ] Support for other display drivers/resolutions
- [ ] GIF/animation rendering support (subject to ESP8266 RAM constraints)
