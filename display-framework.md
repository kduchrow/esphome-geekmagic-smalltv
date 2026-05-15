# Display Framework (ESPHome) - Project Brief

Goal
- Build an external ESPHome component/module that provides a reusable display "card framework".
- Keep the rendering logic, page stack, rotation, expiry, and card layout inside the module.
- Provide a clean API (services or C++ calls) to push cards from Home Assistant.

Current Working Behavior (Reference)
- Platform: ESP8266 (esp12e) with ST7789V display (240x240) using fractional framebuffer.
- UI layout:
  - Top row: time/date.
  - Weather icon + state at top area.
  - Divider line.
  - Notification icon (top right).
  - Card area (bottom) showing icon, title, subtitle, and 0-4 detail lines.
  - Dots above cards indicate active pages and current page index.
- Card data is managed as a 5-slot stack (circular behavior via rotation and shift).
- Page rotation: every 20s, switch to next active page.
- Page expiry: every 10s, remove expired pages.
- Page update triggers: display refresh every 1s/5s.

Display Module Requirements
- External component with a configurable display renderer.
- Provide a card/page stack with:
  - max_pages (default 5)
  - page_id (string), active (bool)
  - icon (string, MDI or raw glyph), title, subtitle, details (string)
  - expiry timestamp or valid_for_s handling
  - current_page_index
- Render pipeline:
  - draw header (time/date)
  - draw weather block (icon + state)
  - draw notification icon (optional)
  - draw card area with icon/title/subtitle/details
  - draw page dots
- Details rendering:
  - split details string by a delimiter (currently "-|-"), render up to 4 lines
- Must be able to set a custom delimiter via config.

Services / API (ESPHome)
- set_page:
  - inputs: page_id, active, icon, title, subtitle, details, valid_for_s
  - behavior:
    - if active=false: remove page by id
    - if active=true:
      - update if exists
      - insert new slot if available
      - if full: drop oldest, shift left
    - update current_page_index to first active
- set_notification:
  - inputs: enabled, icon

Home Assistant Example Automation
- Example service call to update a card (single-line details; delimiter "-|-" used):

```yaml
- alias: Display Weather Forecast (15m)
  description: ""
  triggers:
  - trigger: time_pattern
    minutes: /15
  conditions:
  - condition: time
    after: 05:00:00
    before: "22:00:00"
  actions:
  - action: esphome.arbeitszimmer_display_set_page
    data:
      page_id: weather_forecast
      active: true
      icon: mdi:weather-rainy
      title: Weather
      subtitle: Forecast
      details: "{{ 'Now ' ~ (state_attr('weather.home', 'temperature') | round(0) if state_attr('weather.home', 'temperature') is not none else 'n/a') ~ (state_attr('weather.home', 'temperature_unit') | default('C')) ~ '-|-' ~ 'Tomorrow ' ~ ((state_attr('weather.home', 'forecast')[0].temperature | round(0)) if (state_attr('weather.home', 'forecast') or []) | count > 0 and (state_attr('weather.home', 'forecast')[0].temperature is not none) else 'n/a') ~ (state_attr('weather.home', 'temperature_unit') | default('C')) ~ '-|-' ~ 'Rain ' ~ ('yes' if (state_attr('weather.home', 'forecast') or []) | count > 0 and (state_attr('weather.home', 'forecast')[0].condition | default('')) in ['rainy','pouring','lightning-rainy','hail','snowy-rainy'] else 'no') }}"
      valid_for_s: 3600
  mode: single
```

Fonts / Icons
- MDI font used: materialdesignicons-webfont.ttf
- Include glyphs for weather and status icons.
- For raw glyphs, allow string to be passed directly.

Configuration Inputs (Module)
- Display hardware pins, size, and SPI config.
- Fonts (text + icon), icon size.
- Colors (accent day/night, background, etc.).
- Delimiter for details (default: "-|-").
- Rotation interval, expiry interval, update interval.

Logging / Debugging
- Add log lines when a page arrives, is updated, removed, dropped, or expired.
- Optional logging for current page index and active count.

External Component Structure (Proposed)
- components/display_framework/
  - __init__.py (config schema + codegen)
  - display_framework.cpp (render + page stack)
  - display_framework.h
  - fonts/ (optional)
- Expose a custom ESPHome component that can be used in YAML.

Notes
- Avoid newline characters in details; use delimiter splitting.
- Keep all templates in HA single-line to avoid line breaks.
