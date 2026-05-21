"""Shared constants for display framework integration tests."""

import os

ENCRYPTION_KEY = os.environ.get("ENCRYPTION_KEY") or ""

DEFAULT_HOST = os.environ.get("DEVICE_HOST") or "arbeitszimmer-display.local"
DEFAULT_PORT = 6053
DEFAULT_DELAY = 4

CLEAR_HEADER_ARGS = {
    "active": False, "icon": "", "title": "", "subtitle": "",
    "valid_for_s": 0, "icon_color": "", "pulse": False,
    "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
}

DEFAULT_PAGE_ARGS = {
    "page_id": "test", "active": True,
    "icon": "", "title": "", "subtitle": "", "details": "",
    "valid_for_s": 300, "progress": 0, "font_size": 0,
}

# MDI icons confirmed present in icon_font_48 glyph list
VALID_ICONS = [
    "mdi:home", "mdi:flash", "mdi:lightning-bolt", "mdi:solar-power",
    "mdi:battery", "mdi:battery-charging", "mdi:bell", "mdi:bell-ring",
    "mdi:weather-sunny", "mdi:weather-cloudy", "mdi:weather-rainy",
    "mdi:weather-partly-cloudy", "mdi:weather-windy",
]
