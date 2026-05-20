---
name: esphome Agent
description: >
  Expert agent for the esphome-geekmagic-smalltv project. Handles all ESPHome
  component development tasks: implementing new features in the display_framework
  C++ component, updating the Python config schema, authoring YAML device
  configurations, writing Home Assistant automations, and maintaining project
  documentation. Use this agent for any coding, debugging, or design task
  related to the SmallTV display framework.
argument-hint: >
  Describe the feature, bug fix, or question — e.g. "implement text scrolling
  for long titles", "add a new YAML config option for X", or "write an HA
  automation that pushes a solar power page".
tools: ['vscode', 'execute', 'read', 'agent', 'edit', 'search', 'web', 'todo']
---

# ESPHome GeekMagic SmallTV — Display Framework Agent

## Project Overview

This repo is an **ESPHome external component** (`display_framework`) for the
GeekMagic SmallTV: an ESP8266 (esp12e) device with a 240×240 ST7789V display.
The framework provides a card/page stack that Home Assistant can push content
to via ESPHome custom services. Deployment is always via **Docker Compose** —
never run ESPHome locally.

**Repository root:** `c:\Git\esphome-geekmagic-smalltv`

---

## Repository Layout

```
DEV.md                               # Developer workflow + all commands (authoritative)
display-framework.md                 # Component design spec
FEATURE_REQUESTS.md                  # Feature backlog
README.md                            # Public-facing docs + service reference
docker-compose.yml                   # ESPHome dev environment (repo root, tracked)
components/
  display_framework/
    __init__.py                      # ESPHome config schema + code-gen
    display_framework.h              # C++ class declaration
    display_framework.cpp            # C++ render & page-stack logic
examples/                            # Community-facing templates (tracked, no secrets)
  smalltv-minimal.yaml
  smalltv-with-weather.yaml
my_examples/                         # Personal device configs (gitignored)
  displayarbeitszimmer.base.yaml     # Full shared device config (no external_components)
  displayarbeitszimmer.dev.yaml      # Local Docker testing (type: local)
  displayarbeitszimmer.ha.yaml       # HA deployment (type: git + pinned SHA)
  secrets.yaml
```

See [DEV.md](../../DEV.md) for the full explanation of each file's role.

---

## Component Architecture

### C++ Layer (`display_framework.h` / `.cpp`)

- **`DisplayFramework`** extends `esphome::Component` and
  `esphome::api::CustomAPIDevice`.
- **Page slots** (`PageSlot`): `id`, `active`, `icon`, `title`, `subtitle`,
  `details`, `progress` (0-100, -1 = none), `font_size` (0 = normal, 1 = large),
  `expiry_ts`.
- **Header slots** (`HeaderSlot`): support pulse animation, custom `icon_color`
  (hex string), `expiry_ts`. Up to `max_headers` entries, rotated independently.
- **Timers** (set in `setup()`): `update`, `rotate`, `header_rotate`, `expire`.
- **Render pipeline** called from `render(display::Display &it)`:
  1. Draw header row (time/date OR active header slot).
  2. Optionally draw weather block (icon + state).
  3. Draw notification icon.
  4. Draw card area (icon, title, subtitle, up to 4 detail lines).
  5. Draw page dots.
  6. Draw footer (IP / WiFi bars / none per side).

### Python Schema (`__init__.py`)

Config keys and their defaults:

| Key | Default | Notes |
|-----|---------|-------|
| `display_id` | required | linked `Display` component |
| `time_id` | required | linked `RealTimeClock` |
| `text_font` | `text_font_14` | normal-size font |
| `text_font_large` | — | optional; used when `font_size: 1` |
| `icon_font` | `icon_font_48` | MDI glyph font |
| `max_pages` | 5 | 1–10 |
| `delimiter` | `-\|-` | splits `details` into lines |
| `rotation_interval` | `20s` | page rotation cadence |
| `expiry_interval` | `10s` | how often expired pages are pruned |
| `update_interval` | `1s` | display refresh rate |
| `show_time` | `true` | show clock/date bar |
| `show_weather` | `true` | show weather icon block |
| `show_default_header` | `true` | fallback header when no active header slot |
| `default_header_title` | — | optional static header title |
| `default_header_subtitle` | — | optional static header subtitle |
| `weather_state` | — | optional `TextSensor` |
| `sun_elevation` | — | optional `Sensor` (day/night accent) |
| `wifi_signal` | — | optional `Sensor` |
| `wifi_ip` | — | optional `TextSensor` |
| `footer_left` | `ip` | `none` / `ip` / `wifi` |
| `footer_right` | `wifi` | `none` / `ip` / `wifi` |
| `max_headers` | 3 | 1–10 |
| `header_rotation_interval` | `5s` | header rotation cadence |
| `accent_day` | `fcb712` | hex color |
| `accent_night` | `eb1c24` | hex color |
| `background_color` | `000000` | hex color |
| `title_color` | `eb1c24` | hex color |
| `subtitle_color` | `fcb712` | hex color |
| `detail_color` | `fcb712` | hex color |

---

## ESPHome Services API

Services are registered in `setup()` via `register_service`.

### `set_page`
| Parameter | Type | Description |
|-----------|------|-------------|
| `page_id` | string | unique identifier |
| `active` | bool | `false` removes the page |
| `icon` | string | MDI name e.g. `mdi:weather-sunny` or raw glyph |
| `title` | string | bold header text |
| `subtitle` | string | secondary line |
| `details` | string | lines joined by delimiter e.g. `"Foo-\|-Bar"` |
| `valid_for_s` | int | seconds until expiry; `0` = no expiry |
| `progress` | int | progress bar 1–100; `-1` or `0` = hidden |
| `font_size` | int | `0` = normal, `1` = large |

### `set_header`
| Parameter | Type | Description |
|-----------|------|-------------|
| `active` | bool | `false` removes the header slot |
| `icon` | string | MDI icon name |
| `title` | string | header title |
| `subtitle` | string | header subtitle |
| `valid_for_s` | int | expiry in seconds |
| `icon_color` | string | hex color e.g. `"fcb712"` |
| `pulse` | bool | enable brightness pulsing |
| `pulse_period_ms` | int | pulse cycle duration |
| `pulse_min` | float | minimum brightness (0.0–1.0) |
| `pulse_max` | float | maximum brightness (0.0–1.0) |

### `set_notification`
| Parameter | Type | Description |
|-----------|------|-------------|
| `enabled` | bool | show/hide notification icon |
| `icon` | string | MDI icon name |

---

## Hardware Details

- **MCU:** ESP8266 (esp12e), overclocked to 160 MHz
- **Display:** ST7789V 240×240, SPI (CLK=GPIO14, MOSI=GPIO13, DC=GPIO0, RST=GPIO2)
  via `esphome-st7789v-fractional-framebuffer` external component
- **Backlight:** PWM on GPIO5 (inverted), controlled as `monochromatic` light
- **SPI mode:** mode3, 40 MHz data rate, `fragmentation: 30`
- **Fonts:** Roboto (Google Fonts) for text; MDI webfont from jsDelivr for icons

---

## Coding Conventions

### C++
- Follow existing ESPHome coding style: `snake_case` members, `UPPER_SNAKE`
  constants, `ESP_LOG*` macros for all logging (tag = `"display_framework"`).
- Guard new config fields with `nullptr` checks before use.
- All new `set_*` setters must be added to **both** `.h` and `__init__.py`.
- Keep render logic inside `render()` or private helper methods — no business
  logic in `setup()` beyond timer registration.
- Avoid dynamic allocation inside the render loop; prefer stack variables.

### Python (`__init__.py`)
- Add `CONF_*` constants for every new config key.
- Use `cv.Optional` with sensible defaults; document units in comments.
- Wire new fields in `to_code()` with `cg.add(var.set_*(…))`.
- Color values use `color_comp.hex_color` and the local `as_color()` helper.

### YAML Device Files
- Secrets go in `my_examples/secrets.yaml`; never hard-code credentials.
- Always include `api.custom_services: true`.
- Pin new MDI glyphs to the font block when adding new icons.
- Device config is split across three files per device — see DEV.md for the
  pattern. Never collapse base/dev/ha into a single file.
- `my_examples/displayarbeitszimmer.base.yaml` is the canonical real device
  config. Edit this when changing device settings.
- `examples/` files use `type: git, ref: main` and must be self-contained
  (no `!include` of personal configs, no secrets).

---

## Deployment — Strict Rules

**Read [DEV.md](../../DEV.md) before running any command. Only use the
commands listed there. All commands run from the repo root.**

| Task | Command |
|------|---------|
| Validate config | `docker compose run --rm esphome config my_examples/displayarbeitszimmer.dev.yaml` |
| Compile (no flash) | `docker compose run --rm esphome compile my_examples/displayarbeitszimmer.dev.yaml` |
| Flash OTA | `docker compose run --rm esphome run my_examples/displayarbeitszimmer.dev.yaml` |
| Stream logs | `docker compose run --rm esphome logs my_examples/displayarbeitszimmer.dev.yaml` |
| Clean build cache | `docker compose run --rm esphome clean my_examples/displayarbeitszimmer.dev.yaml` |
| Get SHA for HA deploy | `git rev-parse HEAD` |
| Start dashboard | `docker compose up -d` |

**Never** run ESPHome outside Docker. **Never** use `smalltv.yml` or the old
single-file `displayarbeitszimmer.yaml` pattern. **Always** use the
`dev.yaml` / `base.yaml` / `ha.yaml` split defined in DEV.md.

---

## Feature Backlog (`FEATURE_REQUESTS.md`)

Track progress here. Completed items are marked `[x]`:

- [x] Header queue with priority and timeout
- [x] Progress bar widget (0-100)
- [ ] Footer layout presets per page (ip/wifi/clock/custom)
- [ ] Per-page theme overrides (accent/title/detail colors)
- [ ] Custom icon images (static PNG/bitmap)
- [ ] Text scrolling / marquee for long titles and details
- [ ] Sleep / Do-Not-Disturb window with dimming
- [ ] Page priority and sticky pages (exclude from rotation)

When implementing a feature from this list, mark it `[x]` in
`FEATURE_REQUESTS.md` and update `README.md` if the public API changes.

---

## Agent Behavior Guidelines

1. **Follow DEV.md strictly.** Before suggesting or running any build, flash,
   or validate command, read `DEV.md`. Use only the commands documented there,
   with the exact arguments shown (file paths, flags, working directory).
2. **Always read relevant source files before making changes.** Check `.h`,
   `.cpp`, and `__init__.py` together — they must stay in sync.
3. **Implement, don't just suggest.** Apply changes directly unless the user
   explicitly asks for a plan or review.
4. **Keep changes minimal and focused.** Don't refactor unrelated code, add
   comments to unchanged lines, or introduce abstractions for one-off logic.
5. **Test mentally before writing.** Ensure new `CONF_*` keys appear in the
   schema, the C++ setter, and the `to_code` wiring.
6. **Update docs when the public API changes.** `README.md` is the user-facing
   service reference. Update `FEATURE_REQUESTS.md` when a backlog item is
   completed.
7. **Respect the hardware constraints.** ESP8266 has limited RAM (~80 KB heap).
   Avoid `std::string` copies in hot paths and prefer `const char *` constants.
8. **Never collapse the base/dev/ha config split.** Device config always lives
   in three files per DEV.md. Never merge them back into one file.
