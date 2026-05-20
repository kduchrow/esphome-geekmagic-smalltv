# ESPHome GeekMagic SmallTV Display Framework

This repo provides an ESPHome external component that implements a reusable display framework with dynamic pages, rotation, and expiry. Users keep their ESPHome YAML minimal and feed cards/pages via services.

> **Hardware:** Currently developed and tested on the **GeekMagic SmallTV Ultra** (ESP8266, 240×240 ST7789V display). Other GeekMagic models or similar ESP-based displays may work but are untested.

## Features

- Page stack with rotation and expiry
- Services to add/update/remove pages and notifications
- Configurable max pages, delimiter, and timers
- Simple render hook for ST7789V display

## First Flash (OTA — no USB required)

The GeekMagic SmallTV Ultra ships with stock firmware that includes an OTA update page. You can replace it with ESPHome entirely over the network.

### Step 1 — Set up the device with stock firmware

1. Power on the device.
2. Download the **GeekMagic** companion app and follow its pairing flow to connect the device to your WiFi network.
3. Note the device's IP address (shown in the app or your router's DHCP list).

### Step 2 — Build the ESPHome firmware binary

1. Create your ESPHome YAML (copy and adapt `examples/smalltv-minimal.yaml`).
2. Set your WiFi credentials and API encryption key.
3. Build the `.bin` file — **do not flash yet**:
   ```bash
   docker compose run --rm esphome compile my_examples/your_device.yaml
   ```
4. The firmware binary is written to:
   ```
   .esphome/build/<device-name>/.pioenvs/<device-name>/firmware.bin
   ```

### Step 3 — Upload via the stock firmware OTA page

1. Open a browser and navigate to the device's OTA update URL:
   ```
   http://<device-ip>/update
   ```
2. Select the `firmware.bin` file produced in Step 2 and click **Update**.
3. Wait for the upload to complete. The device will reboot automatically.

### Step 4 — Verify ESPHome is running

After the reboot the device runs ESPHome. You can confirm by checking Home Assistant (it should appear as a new device) or by connecting to it with the ESPHome logs command:
```bash
docker compose run --rm esphome logs my_examples/your_device.yaml
```

All future updates can be done with the normal ESPHome OTA flow — no more stock firmware involved.

---

## Quick Start

1. Include the external component and ST7789V driver in your ESPHome YAML.
2. Define the display and call the framework render method.
3. Send pages via the `set_page` service.

Note: set `api.custom_services: true` in your ESPHome YAML so custom services can be registered.

Example snippet:

```yaml
external_components:
  - source:
      type: git
      url: https://github.com/kduchrow/esphome-geekmagic-smalltv
      ref: main
    components: [display_framework]
  - source:
      type: git
      url: https://github.com/lhartmann/esphome-st7789v-fractional-framebuffer
      ref: main
    refresh: 0s
    components: [st7789v]

# ... display config ...

pages:
  - id: framework
    lambda: |-
      id(dfw).render(it);

api:
  custom_services: true

display_framework:
  id: dfw
  display_id: my_display
  time_id: sntp_time
  text_font: text_font_14
  icon_font: icon_font_48
```

## Services

- `set_page`
  - `page_id` (string), `active` (bool), `icon` (string), `title` (string), `subtitle` (string),
    `details` (string), `valid_for_s` (int, 0 = no expiry), `progress` (int, 1-100, optional),
    `font_size` (int, 0 = normal, 1 = large, optional)
- `set_header`
  - `active` (bool), `icon` (string), `title` (string), `subtitle` (string), `valid_for_s` (int, 0 = no expiry),
    `icon_color` (hex string), `pulse` (bool), `pulse_period_ms` (int), `pulse_min` (float), `pulse_max` (float)
- `set_notification`
  - `enabled` (bool), `icon` (string)

## Home Assistant Blueprints

Click a button below to import a blueprint directly into your Home Assistant instance.

**Device name:** in all blueprints you enter the ESPHome device name — the value from the `name:` field in your ESPHome YAML, with hyphens replaced by underscores (e.g. `my-smalltv` → `my_smalltv`).

---

### Send Page

Push any content page to the display on any trigger. Supports icon, title, subtitle, details, progress bar, font size, and expiry.

[![Import blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fkduchrow%2Fesphome-geekmagic-smalltv%2Fmain%2Fblueprints%2Fdisplay_page.yaml)

---

### Header Alert

Send a header alert with optional pulse animation and custom icon color, on any trigger.

[![Import blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fkduchrow%2Fesphome-geekmagic-smalltv%2Fmain%2Fblueprints%2Fdisplay_header_alert.yaml)

---

### Binary Sensor Notification

Show the notification icon when a binary sensor turns on; hide it automatically when it turns off.

[![Import blueprint](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fraw.githubusercontent.com%2Fkduchrow%2Fesphome-geekmagic-smalltv%2Fmain%2Fblueprints%2Fdisplay_binary_sensor_notification.yaml)

---

## Examples

Copy-ready Home Assistant automation snippets:

Header status with pulse:

```yaml
alias: Display Header
    trigger:
      - platform: time_pattern
        minutes: "/60"
    action:
      - service: esphome.geekmagic_smalltv_01_set_header
        data:
          active: true
          icon: mdi:bell
          title: "STATUS"
          subtitle: "All good"
          valid_for_s: 3600
          icon_color: "fcb712"
          pulse: true
          pulse_period_ms: 1200
          pulse_min: 0.4
          pulse_max: 1.0
```

Weather forecast page:

```yaml
alias: Display Weather Forecast
    trigger:
      - platform: time_pattern
        minutes: "/15"
    condition:
      - condition: time
        after: "05:00:00"
        before: "22:00:00"
    action:
      - service: esphome.geekmagic_smalltv_01_set_page
        data:
          page_id: weather_forecast
          active: true
          icon: mdi:weather-rainy
          title: Weather
          subtitle: Forecast
          details: "{{ 'Now ' ~ (state_attr('weather.home', 'temperature') | round(0) if state_attr('weather.home', 'temperature') is not none else 'n/a') ~ (state_attr('weather.home', 'temperature_unit') | default('C')) ~ '-|-' ~ 'Tomorrow ' ~ ((state_attr('weather.home', 'forecast')[0].temperature | round(0)) if (state_attr('weather.home', 'forecast') or []) | count > 0 and (state_attr('weather.home', 'forecast')[0].temperature is not none) else 'n/a') ~ (state_attr('weather.home', 'temperature_unit') | default('C')) ~ '-|-' ~ 'Rain ' ~ ('yes' if (state_attr('weather.home', 'forecast') or []) | count > 0 and (state_attr('weather.home', 'forecast')[0].condition | default('')) in ['rainy','pouring','lightning-rainy','hail','snowy-rainy'] else 'no') }}"
          valid_for_s: 3600
```

Door notification icon:

```yaml
alias: Display Notification
    trigger:
      - platform: state
        entity_id: binary_sensor.door
        to: "on"
    action:
      - service: esphome.geekmagic_smalltv_01_set_notification
        data:
          enabled: true
          icon: mdi:bell-ring
```

WashData summary with progress bar:

```yaml
alias: Display WashData Summary
    trigger:
      - platform: time_pattern
        minutes: "/2"
      - platform: state
        entity_id:
          - binary_sensor.spulmaschine_lauft
          - binary_sensor.waschmaschiene_lauft
    action:
      - choose:
          - conditions:
              - condition: template
                value_template: >
                  {{ is_state('binary_sensor.spulmaschine_lauft','on')
                     or is_state('binary_sensor.waschmaschiene_lauft','on') }}
            sequence:
              - service: esphome.geekmagic_smalltv_01_set_page
                data:
                  page_id: washdata
                  active: true
                  icon: mdi:washing-machine
                  title: WashData
                  subtitle: >
                    {{
                      ('Spuelmaschine ' ~ ('laeuft' if is_state('binary_sensor.spulmaschine_lauft','on') else 'aus'))
                      ~ ' | '
                      ~ ('Waschmaschine ' ~ ('laeuft' if is_state('binary_sensor.waschmaschiene_lauft','on') else 'aus'))
                    }}
                  details: >
                    {{
                      'SP ' ~ (states('sensor.spulmaschine_fortschritt') | default('0')) ~ '% '
                      ~ (states('sensor.spulmaschine_verbleibende_zeit') | default('n/a'))
                      ~ '-|-'
                      ~ (states('sensor.spulmaschine_programm') | default('Programm'))
                      ~ '-|-'
                      ~ 'WM ' ~ (states('sensor.waschmaschiene_fortschritt') | default('0')) ~ '% '
                      ~ (states('sensor.waschmaschiene_verbleibende_zeit') | default('n/a'))
                      ~ '-|-'
                      ~ (states('sensor.waschmaschiene_programm') | default('Programm'))
                    }}
                  progress: >
                    {{
                      [
                        (states('sensor.spulmaschine_fortschritt') | int(0)),
                        (states('sensor.waschmaschiene_fortschritt') | int(0))
                      ] | max
                    }}
                  valid_for_s: 3600
        default:
          - service: esphome.geekmagic_smalltv_01_set_page
            data:
              page_id: washdata
              active: false
```

## Layout Reference

The 240×240 display is divided into up to four stacked zones. Which zones are visible depends on the configuration.

```
┌────────────────────────────────────────┐
│  Time bar          (show_time: true)   │  22 px
├────────────────────────────────────────┤
│  Header area  (show_default_header:    │  44 px
│               true / active headers)  │
├────────────────────────────────────────┤
│  ●  ○  ○   page indicator dots        │  14 px
├────────────────────────────────────────┤
│  Page content                          │  remaining
├────────────────────────────────────────┤
│  Footer  (IP address / WiFi signal)    │
└────────────────────────────────────────┘
```

When `show_default_header: false` and no active headers are queued, the header zone and dots disappear entirely, giving more space to page content.

---

### Variant A — `show_time: true` + `show_default_header: true` (default)

Clock, header, dots, and page content. The most information-dense layout.

```
┌────────────────────────────────────────┐
│ 14:30:00                       12.05  │  ← time bar
│ [icon]  Header Title                  │  ← header
│         Header Subtitle               │
├────────────────────────────────────────┤
│          ●  ○  ○                      │  ← page dots
│ [icon]  Page Title                    │  ← page content
│         Subtitle                      │
│         Detail line 1                 │
│         Detail line 2                 │
├────────────────────────────────────────┤
│ 192.168.1.10                -65 dBm   │  ← footer
└────────────────────────────────────────┘
```

---

### Variant B — `show_time: true` + `show_default_header: false`

Clock stays; header zone and dots removed. Useful when pages speak for themselves.

```
┌────────────────────────────────────────┐
│ 14:30:00                       12.05  │  ← time bar
│ [icon]  Page Title                    │  ← page content starts here
│         Subtitle                      │
│         Detail line 1                 │
│         Detail line 2                 │
│         Detail line 3                 │
│         Detail line 4                 │
├────────────────────────────────────────┤
│ 192.168.1.10                -65 dBm   │  ← footer
└────────────────────────────────────────┘
```

---

### Variant C — `show_time: false` + `show_default_header: false`

Maximum page area. Best combined with `font_size: 1` for big single-value displays.

```
┌────────────────────────────────────────┐
│ [icon]  Page Title                    │  ← page content starts at top
│         Subtitle                      │
│         Detail line 1                 │
│         Detail line 2                 │
│         Detail line 3                 │
│         Detail line 4                 │
│         Detail line 5                 │
├────────────────────────────────────────┤
│ 192.168.1.10                -65 dBm   │  ← footer
└────────────────────────────────────────┘
```

---

### Icon vs. no icon

**With `icon` set** — text starts at x=64 to leave room for the 48 px icon glyph:

```
│ ┌──────┐  Page Title                  │
│ │ icon │  Subtitle                    │
│ └──────┘  Detail 1                   │
│           Detail 2                   │
```

**Without `icon`** — text expands to use the full width (x=6):

```
│ Page Title                           │
│ Subtitle                             │
│ Detail line 1                        │
│ Detail line 2                        │
```

---

### Font size

**`font_size: 0`** (default, 14 px, line height 18 px) — compact, fits up to 4 detail lines:

```
│ [icon]  Title                        │
│         Subtitle                     │
│         Detail 1                     │
│         Detail 2                     │
```

**`font_size: 1`** (large, 20 px, line height 24 px) — bigger text, fewer lines.  
Best combined with Variant B or C to reclaim the lost header/time space:

```
│ [icon]  Title                        │
│         Subtitle                     │
│         Detail 1                     │
```

Requires `text_font_large` to be set in the component config:

```yaml
display_framework:
  text_font: text_font_14
  text_font_large: text_font_20   # ← enables font_size: 1 in set_page
```

---

### Progress bar

When `progress` (1–100) is passed to `set_page`, a 140×10 px bar is drawn below the detail lines.  
Position and width are relative to the icon/no-icon text offset.

```
│ [icon]  Title                        │
│         Subtitle                     │
│         Detail 1  (60% done)         │
│         [████████████████░░░░░░░░░]  │  ← 140 px wide, accent color
```

---

### Header queue

Up to `max_headers` (default 3) messages can be queued via `set_header`. They rotate every `header_rotation_interval` seconds. Each header can have an icon, title, subtitle, expiry, and optional pulse animation.

```
┌────────────────────────────────────────┐
│ 14:30:00                       12.05  │
│ [🔔]  ALERT                          │  ← rotates between queued headers
│       Door opened                     │
├────────────────────────────────────────┤
│ ...                                   │
```

## Notes

- Default delimiter is `-|-` and up to four detail lines are rendered.
- Fonts and colors can be overridden via the component configuration.
- Footer defaults to IP on the left and WiFi strength on the right when `wifi_ip` and `wifi_signal` are configured.
- Header icon can pulse when `pulse` is enabled in the `set_header` service call.
- For smoother header pulse animation, lower `update_interval` (for example `200ms`).
- Multiple header messages are queued (default 3) and rotated every 5 seconds.
- `set_page` can draw a progress bar (140x10) after the details lines when `progress` is set (> 0).
- Set `show_time: false` to hide the clock/date bar at the top.
- Set `show_default_header: false` to disable the default header entirely and use full-screen page layout.
- Configure `default_header_title` and `default_header_subtitle` to show fixed text in the default header instead of weather or "HAPPY DAY".
- Add `text_font_large` to the component config and pass `font_size: 1` in `set_page` to use a larger font for that page.
- When a page has no icon, text expands to use the full display width.
- Time and date formats use `strftime` format strings (e.g. `%H:%M` for 24 h time, `%d.%m.%Y` for full date). Configure via `time_format` and `date_format`.
- Add a small clock icon to the time bar by setting `time_icon_font` to a 14 px MDI font that includes the `mdi:clock-outline` glyph (`\U000F0954`).
