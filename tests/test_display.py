#!/usr/bin/env python3
"""
Display Framework — Integration Test Script

Calls all ESPHome native API services in various combinations so you can
visually verify formatting on the physical device.

Usage (via Docker Compose — recommended):
    docker compose run --rm test

Usage (direct Python):
    pip install aioesphomeapi
    python tests/test_display.py
    python tests/test_display.py --host 192.168.198.41 --delay 5

Arguments:
    --host    Device hostname or IP  (default: arbeitszimmer-display.local)
    --port    API port               (default: 6053)
    --delay   Seconds between tests  (default: 4)
    --filter  Only run scenarios whose name contains this string (case-insensitive)
              e.g. --filter "header" or --filter "queue" or --filter "wrap"

Notes on icons:
    Only icons present in both resolve_icon_glyph_() and the icon_font_48 glyph
    list will render correctly. Unknown icon names fall back to mdi:alert-circle-outline.
    Valid icon names for this device:
      mdi:home, mdi:flash, mdi:lightning-bolt, mdi:solar-power,
      mdi:battery, mdi:battery-charging, mdi:bell, mdi:bell-ring,
      mdi:weather-sunny, mdi:weather-cloudy, mdi:weather-rainy,
      mdi:weather-partly-cloudy, mdi:weather-windy
"""

import argparse
import asyncio
import sys

try:
    from aioesphomeapi import APIClient
except ImportError:
    print("ERROR: aioesphomeapi not installed. Run: pip install aioesphomeapi")
    sys.exit(1)

# ── Connection settings ───────────────────────────────────────────────────────
# Encryption key from displayarbeitszimmer.base.yaml  api.encryption.key
ENCRYPTION_KEY = "Pu0T9XatYALpR2HBL1wSrskkeKgLALswWayVbIkVFP0="
DEFAULT_HOST = "arbeitszimmer-display.local"
DEFAULT_PORT = 6053
DEFAULT_DELAY = 4  # seconds between scenarios

# ── Reusable helper: clears the entire header queue ──────────────────────────
_CLEAR_HEADER_ARGS = {
    "active": False, "icon": "", "title": "", "subtitle": "",
    "valid_for_s": 0, "icon_color": "", "pulse": False,
    "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
}

# ── Test scenarios ────────────────────────────────────────────────────────────
# Each entry is a dict with:
#   name    — printed to console so you know what to look at
#   action  — "set_page", "set_header", or "set_notification"
#   args    — dict matching the service parameters exactly
#   _before — optional: action fired immediately before the main one (no delay)
#   _also   — optional: action fired immediately after the main one (no delay)
#
# set_page args:
#   page_id (str), active (bool), icon (str), title (str), subtitle (str),
#   details (str), valid_for_s (int, 0=no expiry), progress (int, 0=none, 1-100=bar),
#   font_size (int, 0=normal/14px, 1=large/20px)
#
# set_header args:
#   active (bool), icon (str), title (str), subtitle (str),
#   valid_for_s (int), icon_color (str, hex e.g. "FF8800"), pulse (bool),
#   pulse_period_ms (int), pulse_min (float 0.0-1.0), pulse_max (float 0.0-1.0)
#
# set_notification args:
#   enabled (bool), icon (str)

SCENARIOS = [
    # ── Baseline clear ────────────────────────────────────────────────────────
    {
        "name": "CLEAR — remove all pages and headers",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": False,
            "icon": "", "title": "", "subtitle": "", "details": "",
            "valid_for_s": 0, "progress": 0, "font_size": 0,
        },
        "_also": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },

    # ── Pages: font_size 0 (normal / 14px text_font) ─────────────────────────
    {
        "name": "Page — title only, no icon, normal font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "", "title": "Hello World",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — icon + title, normal font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:home", "title": "Living Room",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — icon + title + subtitle, normal font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:weather-sunny", "title": "Temperature",
            "subtitle": "21.5 \u00b0C",
            "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — icon + title + subtitle + details, normal font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:weather-sunny", "title": "Weather",
            "subtitle": "22 \u00b0C \u2014 sunny",
            "details": "Wind: 12 km/h SW",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — no icon, title + subtitle + details, normal font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "", "title": "No Icon Page",
            "subtitle": "Subtitle text here",
            "details": "Extra details line",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },

    # ── Pages: font_size 1 (large / 20px text_font_large) ────────────────────
    {
        "name": "Page — title only, no icon, LARGE font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "", "title": "Big Title",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 1,
        },
    },
    {
        "name": "Page — icon + title, LARGE font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:flash", "title": "1.23 kW",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 1,
        },
    },
    {
        "name": "Page — icon + title + subtitle, LARGE font",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:battery-charging", "title": "87 %",
            "subtitle": "Charging \u2014 ETA 2h",
            "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 1,
        },
    },

    # ── Pages: progress bar ───────────────────────────────────────────────────
    {
        "name": "Page — progress bar 0% (no bar drawn)",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:battery", "title": "Downloading",
            "subtitle": "0 %", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — progress bar 25%",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:battery", "title": "Downloading",
            "subtitle": "25 %", "details": "",
            "valid_for_s": 300, "progress": 25, "font_size": 0,
        },
    },
    {
        "name": "Page — progress bar 50%",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:battery", "title": "Downloading",
            "subtitle": "50 %", "details": "",
            "valid_for_s": 300, "progress": 50, "font_size": 0,
        },
    },
    {
        "name": "Page — progress bar 75%",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:battery", "title": "Downloading",
            "subtitle": "75 %", "details": "",
            "valid_for_s": 300, "progress": 75, "font_size": 0,
        },
    },
    {
        "name": "Page — progress bar 100%",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:battery", "title": "Done!",
            "subtitle": "100 %", "details": "",
            "valid_for_s": 300, "progress": 100, "font_size": 0,
        },
    },

    # ── Pages: long text — word-wrap ─────────────────────────────────────────
    {
        "name": "Page — very long title (word-wrap test, with icon)",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:home",
            "title": "This Is An Extremely Long Title That Should Wrap Nicely",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — long title + subtitle + details (wrap all fields)",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:weather-cloudy",
            "title": "Long Content Test With Multiple Words",
            "subtitle": "Subtitle with quite a bit of text that wraps",
            "details": "Details line that is also rather long and should wrap too",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — long text, no icon, wider wrap area",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "",
            "title": "Without icon there is more horizontal space for wrapping long text",
            "subtitle": "Subtitle also wraps correctly across the full display width",
            "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page — long text LARGE font (tighter space)",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:bell",
            "title": "Long Title In Large Font Should Also Wrap",
            "subtitle": "And the subtitle too",
            "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 1,
        },
    },

    # ── Pages: icon gallery (verify glyph rendering) ──────────────────────────
    {
        "name": "Page icon — mdi:home",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:home", "title": "mdi:home",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page icon — mdi:lightning-bolt",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:lightning-bolt", "title": "mdi:lightning-bolt",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page icon — mdi:solar-power",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:solar-power", "title": "mdi:solar-power",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page icon — mdi:battery-charging",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:battery-charging", "title": "mdi:battery-charging",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page icon — mdi:bell-ring",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:bell-ring", "title": "mdi:bell-ring",
            "subtitle": "", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "Page icon — unknown icon (shows fallback: mdi:alert-circle-outline)",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:this-icon-does-not-exist", "title": "Bad Icon",
            "subtitle": "Shows alert-circle-outline fallback", "details": "",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },

    # ── Headers ───────────────────────────────────────────────────────────────
    # Each header test clears the queue first via _before so you see exactly
    # one header at a time (no cycling through leftovers from previous tests).
    {
        "name": "Header — title only, no icon, no pulse",
        "action": "set_header",
        "args": {
            "active": True, "icon": "", "title": "Header Title",
            "subtitle": "", "valid_for_s": 300,
            "icon_color": "", "pulse": False,
            "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
        },
        "_before": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },
    {
        "name": "Header — mdi:bell + title + subtitle, no pulse",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:bell", "title": "Doorbell",
            "subtitle": "Someone is at the door",
            "valid_for_s": 300, "icon_color": "", "pulse": False,
            "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
        },
        "_before": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },
    {
        "name": "Header — mdi:flash + title, colored icon (orange FF8800)",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:flash", "title": "High Power",
            "subtitle": "", "valid_for_s": 300,
            "icon_color": "FF8800", "pulse": False,
            "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
        },
        "_before": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },
    {
        "name": "Header — mdi:bell-ring + title, colored icon (red FF0000)",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:bell-ring", "title": "Alert!",
            "subtitle": "Check the basement", "valid_for_s": 300,
            "icon_color": "FF0000", "pulse": False,
            "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
        },
        "_before": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },
    {
        "name": "Header — PULSING mdi:bell (1s period, 20%-100%, color FF0044)",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:bell", "title": "Pulsing Alert",
            "subtitle": "", "valid_for_s": 300,
            "icon_color": "FF0044", "pulse": True,
            "pulse_period_ms": 1000, "pulse_min": 0.2, "pulse_max": 1.0,
        },
        "_before": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },
    {
        "name": "Header — FAST pulse mdi:bell-ring (250ms, 10%-100%, color FFAA00)",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:bell-ring", "title": "Network Issue",
            "subtitle": "Reconnecting\u2026", "valid_for_s": 300,
            "icon_color": "FFAA00", "pulse": True,
            "pulse_period_ms": 250, "pulse_min": 0.1, "pulse_max": 1.0,
        },
        "_before": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },

    # ── Notification dot ──────────────────────────────────────────────────────
    {
        "name": "Notification — ON (mdi:bell)",
        "action": "set_notification",
        "args": {"enabled": True, "icon": "mdi:bell"},
    },
    {
        "name": "Notification — stays on, change icon to mdi:bell-ring",
        "action": "set_notification",
        "args": {"enabled": True, "icon": "mdi:bell-ring"},
    },
    {
        "name": "Notification — OFF",
        "action": "set_notification",
        "args": {"enabled": False, "icon": ""},
    },

    # ── Combined: page + header simultaneously ────────────────────────────────
    {
        "name": "Combined — solar page (large font) + grid-export header (green)",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": True,
            "icon": "mdi:solar-power", "title": "Solar",
            "subtitle": "3.2 kW producing",
            "details": "Battery: 92 %",
            "valid_for_s": 300, "progress": 92, "font_size": 1,
        },
        "_before": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
        "_also": {
            "action": "set_header",
            "args": {
                "active": True, "icon": "mdi:lightning-bolt", "title": "Grid Export",
                "subtitle": "0.8 kW", "valid_for_s": 300,
                "icon_color": "00FF88", "pulse": False,
                "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
            },
        },
    },

    # ── Queue: page rotation ──────────────────────────────────────────────────
    # Sends 3 pages with different IDs; the device rotates them on
    # rotation_interval (default 20s). Watch the dot indicators cycle.
    {
        "name": "QUEUE pages — setup: clear all pages",
        "action": "set_page",
        "args": {
            "page_id": "q1", "active": False,
            "icon": "", "title": "", "subtitle": "", "details": "",
            "valid_for_s": 0, "progress": 0, "font_size": 0,
        },
        "_also": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },
    {
        "name": "QUEUE pages — page 1/3 (mdi:home / Living Room)",
        "action": "set_page",
        "args": {
            "page_id": "q1", "active": True,
            "icon": "mdi:home", "title": "Living Room",
            "subtitle": "Page 1 of 3",
            "details": "Rotates every 20s",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },
    {
        "name": "QUEUE pages — page 2/3 (mdi:flash / Power)",
        "action": "set_page",
        "args": {
            "page_id": "q2", "active": True,
            "icon": "mdi:flash", "title": "Power",
            "subtitle": "Page 2 of 3",
            "details": "1.23 kW",
            "valid_for_s": 300, "progress": 45, "font_size": 0,
        },
    },
    {
        "name": "QUEUE pages — page 3/3 (mdi:solar-power / Solar) — watch dots rotate after this",
        "action": "set_page",
        "args": {
            "page_id": "q3", "active": True,
            "icon": "mdi:solar-power", "title": "Solar",
            "subtitle": "Page 3 of 3",
            "details": "3.2 kW producing",
            "valid_for_s": 300, "progress": 0, "font_size": 0,
        },
    },

    # ── Queue: header rotation ────────────────────────────────────────────────
    # Sends 3 headers; the device rotates them on header_rotation_interval
    # (default 5s). Watch the header cycle through all three.
    {
        "name": "QUEUE headers — setup: clear all headers",
        "action": "set_header",
        "args": _CLEAR_HEADER_ARGS,
    },
    {
        "name": "QUEUE headers — header 1/3 (mdi:bell / Doorbell, accent color)",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:bell", "title": "Doorbell",
            "subtitle": "Header 1 of 3", "valid_for_s": 300,
            "icon_color": "", "pulse": False,
            "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
        },
    },
    {
        "name": "QUEUE headers — header 2/3 (mdi:flash / Power, orange)",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:flash", "title": "High Power",
            "subtitle": "Header 2 of 3", "valid_for_s": 300,
            "icon_color": "FF8800", "pulse": False,
            "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
        },
    },
    {
        "name": "QUEUE headers — header 3/3 (mdi:bell-ring / Alert, pulsing red) — watch all 3 cycle every 5s",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:bell-ring", "title": "Alert!",
            "subtitle": "Header 3 of 3", "valid_for_s": 300,
            "icon_color": "FF0000", "pulse": True,
            "pulse_period_ms": 800, "pulse_min": 0.2, "pulse_max": 1.0,
        },
    },

    # ── Final: clean up ───────────────────────────────────────────────────────
    {
        "name": "DONE — clear all pages, headers, and notification",
        "action": "set_page",
        "args": {
            "page_id": "test", "active": False,
            "icon": "", "title": "", "subtitle": "", "details": "",
            "valid_for_s": 0, "progress": 0, "font_size": 0,
        },
        "_also": {"action": "set_header", "args": _CLEAR_HEADER_ARGS},
    },
]


# ── Runner ────────────────────────────────────────────────────────────────────

async def call_service(client, services, action: str, args: dict):
    """Find a registered service by suffix and execute it."""
    svc = next((s for s in services if s.name.endswith(action)), None)
    if svc is None:
        print(f"  \u26a0  Service '{action}' not found on device "
              f"(available: {[s.name for s in services]})")
        return

    # Build typed args in the order the service declares them
    service_args = {}
    for arg_def in svc.args:
        key = arg_def.name
        if key in args:
            service_args[key] = args[key]

    await client.execute_service(svc, service_args)


async def run_tests(host: str, port: int, delay: float, name_filter: str | None):
    print(f"\nConnecting to {host}:{port} \u2026")
    client = APIClient(host, port, password=None, noise_psk=ENCRYPTION_KEY)

    try:
        await client.connect(login=True)
    except Exception as exc:
        print(f"ERROR: Could not connect \u2014 {exc}")
        print("  Check that the device is online and the encryption key matches.")
        sys.exit(1)

    _, services = await client.list_entities_services()
    print(f"Connected. Found {len(services)} services.\n")

    filtered = [
        s for s in SCENARIOS
        if name_filter is None or name_filter.lower() in s["name"].lower()
    ]

    if not filtered:
        print(f"No scenarios match filter '{name_filter}'.")
        await client.disconnect()
        return

    print(f"Running {len(filtered)} scenario(s) with {delay}s delay between each.\n")

    for i, scenario in enumerate(filtered, 1):
        print(f"[{i:>2}/{len(filtered)}] {scenario['name']}")
        try:
            # Fire _before action immediately (no extra delay)
            if "_before" in scenario:
                before = scenario["_before"]
                await call_service(client, services, before["action"], before["args"])

            await call_service(client, services, scenario["action"], scenario["args"])

            # Fire _also action immediately after (no extra delay)
            if "_also" in scenario:
                also = scenario["_also"]
                await call_service(client, services, also["action"], also["args"])

        except Exception as exc:
            print(f"         ERROR: {exc}")

        if i < len(filtered):
            await asyncio.sleep(delay)

    print("\nAll scenarios complete.")
    await client.disconnect()


def main():
    parser = argparse.ArgumentParser(description="Display Framework integration tests")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Device hostname or IP")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="ESPHome API port")
    parser.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                        help="Seconds to display each scenario (default: 4)")
    parser.add_argument("--filter", dest="name_filter", default=None,
                        help="Only run scenarios whose name contains this string")
    args = parser.parse_args()

    asyncio.run(run_tests(args.host, args.port, args.delay, args.name_filter))


if __name__ == "__main__":
    main()
