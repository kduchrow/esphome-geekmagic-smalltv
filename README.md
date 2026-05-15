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
    `details` (string), `valid_for_s` (int, 0 = no expiry)
- `set_header`
  - `active` (bool), `icon` (string), `title` (string), `subtitle` (string), `valid_for_s` (int, 0 = no expiry),
    `icon_color` (hex string), `pulse` (bool), `pulse_period_ms` (int), `pulse_min` (float), `pulse_max` (float)
- `set_notification`
  - `enabled` (bool), `icon` (string)

## Examples

See the `examples/` folder for complete configurations and Home Assistant automations.

## Notes

- Default delimiter is `-|-` and up to four detail lines are rendered.
- Fonts and colors can be overridden via the component configuration.
- Footer defaults to IP on the left and WiFi strength on the right when `wifi_ip` and `wifi_signal` are configured.
- Header icon can pulse when `pulse` is enabled in the `set_header` service call.
- For smoother header pulse animation, lower `update_interval` (for example `200ms`).
- Multiple header messages are queued (default 3) and rotated every 5 seconds.
