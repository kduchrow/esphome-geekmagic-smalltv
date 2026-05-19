# ESPHome GeekMagic SmallTV Display Framework

This repo provides an ESPHome external component that implements a reusable display framework with dynamic pages, rotation, and expiry. Users keep their ESPHome YAML minimal and feed cards/pages via services.

## Features

- Page stack with rotation and expiry
- Services to add/update/remove pages and notifications
- Configurable max pages, delimiter, and timers
- Simple render hook for ST7789V display

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
