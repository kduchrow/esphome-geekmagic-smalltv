# -*- coding: utf-8 -*-
"""Test scenarios for display framework integration tests.

Each scenario is a dict with:
    name    — printed to console so you know what to look at
    action  — "set_page", "set_header", or "set_notification"
    args    — dict matching the service parameters exactly
    _before — optional: action fired immediately before (no delay)
    _also   — optional: action fired immediately after (no delay)

set_page args:
    page_id (str), active (bool), icon (str), title (str), subtitle (str),
    details (str), valid_for_s (int), progress (int, 0=none, 1-100=bar),
    font_size (int, 0=normal/14px, 1=large/20px)

set_header args:
    active (bool), icon (str), title (str), subtitle (str),
    valid_for_s (int), icon_color (hex str), pulse (bool),
    pulse_period_ms (int), pulse_min (float), pulse_max (float)

set_notification args:
    enabled (bool), icon (str)
"""

from .constants import CLEAR_HEADER_ARGS, DEFAULT_PAGE_ARGS


def _page(overrides=None):
    """Shortcut to build a page scenario args from defaults."""
    args = dict(DEFAULT_PAGE_ARGS)
    if overrides:
        args.update(overrides)
    return args


def _header_scenario(name, args, clear_first=True):
    """Build a header scenario, optionally clearing the queue first."""
    scenario = {"name": name, "action": "set_header", "args": args}
    if clear_first:
        scenario["_before"] = {"action": "set_header", "args": CLEAR_HEADER_ARGS}
    return scenario


def _icon_gallery_scenario(icon):
    return {
        "name": f"Page icon — {icon}",
        "action": "set_page",
        "args": _page({"icon": icon, "title": icon}),
    }


SCENARIOS = [
    # ═══════════════════════════════════════════════════════════════════════════
    # Baseline clear
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "CLEAR — remove all pages and headers",
        "action": "set_page",
        "args": {"page_id": "test", "active": False, "icon": "", "title": "",
                 "subtitle": "", "details": "", "valid_for_s": 0,
                 "progress": 0, "font_size": 0},
        "_also": {"action": "set_header", "args": CLEAR_HEADER_ARGS},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Pages — normal font (font_size 0)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Page — title only, no icon, normal font",
        "action": "set_page",
        "args": _page({"title": "Hello World"}),
    },
    {
        "name": "Page — icon + title, normal font",
        "action": "set_page",
        "args": _page({"icon": "mdi:home", "title": "Living Room"}),
    },
    {
        "name": "Page — icon + title + subtitle, normal font",
        "action": "set_page",
        "args": _page({"icon": "mdi:weather-sunny", "title": "Temperature",
                        "subtitle": "21.5 \u00b0C"}),
    },
    {
        "name": "Page — icon + title + subtitle + details, normal font",
        "action": "set_page",
        "args": _page({"icon": "mdi:weather-sunny", "title": "Weather",
                        "subtitle": "22 \u00b0C \u2014 sunny",
                        "details": "Wind: 12 km/h SW"}),
    },
    {
        "name": "Page — no icon, title + subtitle + details, normal font",
        "action": "set_page",
        "args": _page({"title": "No Icon Page",
                        "subtitle": "Subtitle text here",
                        "details": "Extra details line"}),
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Pages — large font (font_size 1)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Page — title only, no icon, LARGE font",
        "action": "set_page",
        "args": _page({"title": "Big Title", "font_size": 1}),
    },
    {
        "name": "Page — icon + title, LARGE font",
        "action": "set_page",
        "args": _page({"icon": "mdi:flash", "title": "1.23 kW", "font_size": 1}),
    },
    {
        "name": "Page — icon + title + subtitle, LARGE font",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery-charging", "title": "87 %",
                        "subtitle": "Charging \u2014 ETA 2h", "font_size": 1}),
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Progress bar
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Page — progress bar 0% (no bar drawn)",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery", "title": "Downloading",
                        "subtitle": "0 %"}),
    },
    {
        "name": "Page — progress bar 25%",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery", "title": "Downloading",
                        "subtitle": "25 %", "progress": 25}),
    },
    {
        "name": "Page — progress bar 50%",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery", "title": "Downloading",
                        "subtitle": "50 %", "progress": 50}),
    },
    {
        "name": "Page — progress bar 75%",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery", "title": "Downloading",
                        "subtitle": "75 %", "progress": 75}),
    },
    {
        "name": "Page — progress bar 100%",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery", "title": "Done!",
                        "subtitle": "100 %", "progress": 100}),
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Word-wrap (long text)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Page — very long title (word-wrap test, with icon)",
        "action": "set_page",
        "args": _page({"icon": "mdi:home",
                        "title": "This Is An Extremely Long Title That Should Wrap Nicely"}),
    },
    {
        "name": "Page — long title + subtitle + details (wrap all fields)",
        "action": "set_page",
        "args": _page({"icon": "mdi:weather-cloudy",
                        "title": "Long Content Test With Multiple Words",
                        "subtitle": "Subtitle with quite a bit of text that wraps",
                        "details": "Details line that is also rather long and should wrap too"}),
    },
    {
        "name": "Page — long text, no icon, wider wrap area",
        "action": "set_page",
        "args": _page({"title": "Without icon there is more horizontal space for wrapping long text",
                        "subtitle": "Subtitle also wraps correctly across the full display width"}),
    },
    {
        "name": "Page — long text LARGE font (tighter space)",
        "action": "set_page",
        "args": _page({"icon": "mdi:bell",
                        "title": "Long Title In Large Font Should Also Wrap",
                        "subtitle": "And the subtitle too", "font_size": 1}),
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Icon gallery
    # ═══════════════════════════════════════════════════════════════════════════
    _icon_gallery_scenario("mdi:home"),
    _icon_gallery_scenario("mdi:lightning-bolt"),
    _icon_gallery_scenario("mdi:solar-power"),
    _icon_gallery_scenario("mdi:battery-charging"),
    _icon_gallery_scenario("mdi:bell-ring"),
    {
        "name": "Page icon — unknown icon (fallback: mdi:alert-circle-outline)",
        "action": "set_page",
        "args": _page({"icon": "mdi:this-icon-does-not-exist", "title": "Bad Icon",
                        "subtitle": "Shows alert-circle-outline fallback"}),
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Headers
    # ═══════════════════════════════════════════════════════════════════════════
    _header_scenario("Header — title only, no icon, no pulse", {
        "active": True, "icon": "", "title": "Header Title",
        "subtitle": "", "valid_for_s": 300,
        "icon_color": "", "pulse": False,
        "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
    }),
    _header_scenario("Header — mdi:bell + title + subtitle, no pulse", {
        "active": True, "icon": "mdi:bell", "title": "Doorbell",
        "subtitle": "Someone is at the door", "valid_for_s": 300,
        "icon_color": "", "pulse": False,
        "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
    }),
    _header_scenario("Header — mdi:flash + title, colored icon (orange FF8800)", {
        "active": True, "icon": "mdi:flash", "title": "High Power",
        "subtitle": "", "valid_for_s": 300,
        "icon_color": "FF8800", "pulse": False,
        "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
    }),
    _header_scenario("Header — mdi:bell-ring + title, colored icon (red FF0000)", {
        "active": True, "icon": "mdi:bell-ring", "title": "Alert!",
        "subtitle": "Check the basement", "valid_for_s": 300,
        "icon_color": "FF0000", "pulse": False,
        "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
    }),
    _header_scenario("Header — PULSING mdi:bell (1s period, 20%-100%, color FF0044)", {
        "active": True, "icon": "mdi:bell", "title": "Pulsing Alert",
        "subtitle": "", "valid_for_s": 300,
        "icon_color": "FF0044", "pulse": True,
        "pulse_period_ms": 1000, "pulse_min": 0.2, "pulse_max": 1.0,
    }),
    _header_scenario("Header — FAST pulse mdi:bell-ring (250ms, 10%-100%, color FFAA00)", {
        "active": True, "icon": "mdi:bell-ring", "title": "Network Issue",
        "subtitle": "Reconnecting\u2026", "valid_for_s": 300,
        "icon_color": "FFAA00", "pulse": True,
        "pulse_period_ms": 250, "pulse_min": 0.1, "pulse_max": 1.0,
    }),

    # ═══════════════════════════════════════════════════════════════════════════
    # Notification dot
    # ═══════════════════════════════════════════════════════════════════════════
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

    # ═══════════════════════════════════════════════════════════════════════════
    # Combined: page + header simultaneously
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Combined — solar page (large font) + grid-export header (green)",
        "action": "set_page",
        "args": _page({"icon": "mdi:solar-power", "title": "Solar",
                        "subtitle": "3.2 kW producing",
                        "details": "Battery: 92 %",
                        "progress": 92, "font_size": 1}),
        "_before": {"action": "set_header", "args": CLEAR_HEADER_ARGS},
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

    # ═══════════════════════════════════════════════════════════════════════════
    # Queue: page rotation (3 pages, different IDs)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "QUEUE pages — setup: clear all pages",
        "action": "set_page",
        "args": {"page_id": "q1", "active": False, "icon": "", "title": "",
                 "subtitle": "", "details": "", "valid_for_s": 0,
                 "progress": 0, "font_size": 0},
        "_also": {"action": "set_header", "args": CLEAR_HEADER_ARGS},
    },
    {
        "name": "QUEUE pages — page 1/3 (mdi:home / Living Room)",
        "action": "set_page",
        "args": _page({"page_id": "q1", "icon": "mdi:home", "title": "Living Room",
                        "subtitle": "Page 1 of 3",
                        "details": "Rotates every 20s"}),
    },
    {
        "name": "QUEUE pages — page 2/3 (mdi:flash / Power)",
        "action": "set_page",
        "args": _page({"page_id": "q2", "icon": "mdi:flash", "title": "Power",
                        "subtitle": "Page 2 of 3", "details": "1.23 kW",
                        "progress": 45}),
    },
    {
        "name": "QUEUE pages — page 3/3 (mdi:solar-power / Solar) — watch dots rotate",
        "action": "set_page",
        "args": _page({"page_id": "q3", "icon": "mdi:solar-power", "title": "Solar",
                        "subtitle": "Page 3 of 3",
                        "details": "3.2 kW producing"}),
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Queue: header rotation (3 headers, rotating every 5s)
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "QUEUE headers — setup: clear all headers",
        "action": "set_header",
        "args": CLEAR_HEADER_ARGS,
    },
    {
        "name": "QUEUE headers — header 1/3 (mdi:bell / Doorbell)",
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
        "name": "QUEUE headers — header 3/3 (mdi:bell-ring / Alert, pulsing red) — all 3 cycle",
        "action": "set_header",
        "args": {
            "active": True, "icon": "mdi:bell-ring", "title": "Alert!",
            "subtitle": "Header 3 of 3", "valid_for_s": 300,
            "icon_color": "FF0000", "pulse": True,
            "pulse_period_ms": 800, "pulse_min": 0.2, "pulse_max": 1.0,
        },
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Corner cases
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "Corner — unicode / special characters (\u00e4\u00f6\u00fc\u00df \u20ac \u2603)",
        "action": "set_page",
        "args": _page({"icon": "mdi:weather-sunny", "title": "M\u00fcnchen",
                        "subtitle": "Sch\u00f6nes Wetter \u2600",
                        "details": "12 \u00b0C \u2014 Regen: 30 %-|-St\u00fcck: 5 \u20ac"}),
    },
    {
        "name": "Corner — empty strings for all fields",
        "action": "set_page",
        "args": _page({"icon": "", "title": "", "subtitle": "", "details": ""}),
    },
    {
        "name": "Corner — very long details (multi-line delimiter stress)",
        "action": "set_page",
        "args": _page({"icon": "mdi:bell",
                        "title": "Overflow Test",
                        "subtitle": "Check text clipping",
                        "details": "Line 1 with some text-|-Line 2 with more text here-|-Line 3 even more text to test-|-Line 4 fourth line of content-|-Line 5 should be clipped or ignored-|-Line 6 definitely beyond max"}),
    },
    {
        "name": "Corner — progress = -1 (should not draw bar)",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery", "title": "Progress -1",
                        "subtitle": "Should show NO bar", "progress": -1}),
    },
    {
        "name": "Corner — font_size = 2 (invalid value)",
        "action": "set_page",
        "args": _page({"title": "Invalid Font Size", "font_size": 2}),
    },
    {
        "name": "Corner — font_size = -1 (invalid value)",
        "action": "set_page",
        "args": _page({"title": "Negative Font Size", "font_size": -1}),
    },
    {
        "name": "Corner — progress = 150 (out of range)",
        "action": "set_page",
        "args": _page({"icon": "mdi:battery", "title": "Progress 150",
                        "subtitle": "Clamped or weird bar?", "progress": 150}),
    },
    {
        "name": "Corner — details without delimiter (single line)",
        "action": "set_page",
        "args": _page({"icon": "mdi:home", "title": "Single Detail Line",
                        "subtitle": "No delimiter used",
                        "details": "Just one continuous line of text that is quite long"}),
    },
    {
        "name": "Corner — same page_id updated multiple times",
        "action": "set_page",
        "args": _page({"page_id": "update_test", "icon": "mdi:home",
                        "title": "Update Test 1", "subtitle": "This is the first version"}),
    },
    {
        "name": "Corner — same page_id updated (v2)",
        "action": "set_page",
        "args": _page({"page_id": "update_test", "icon": "mdi:flash",
                        "title": "Update Test 2", "subtitle": "This is the SECOND version"}),
    },
    {
        "name": "Corner — same page_id updated (v3) then deleted",
        "action": "set_page",
        "args": _page({"page_id": "update_test", "active": True, "icon": "mdi:bell",
                        "title": "Update Test 3", "subtitle": "Will be deleted next"}),
    },
    {
        "name": "Corner — same page_id deleted (active=false)",
        "action": "set_page",
        "args": {"page_id": "update_test", "active": False, "icon": "", "title": "",
                 "subtitle": "", "details": "", "valid_for_s": 0,
                 "progress": 0, "font_size": 0},
    },

    # Header corner cases
    _header_scenario("Corner header — pulse with period_ms = 0", {
        "active": True, "icon": "mdi:bell", "title": "Period Zero",
        "subtitle": "Pulse with 0ms period", "valid_for_s": 300,
        "icon_color": "FF0000", "pulse": True,
        "pulse_period_ms": 0, "pulse_min": 0.3, "pulse_max": 0.8,
    }),
    _header_scenario("Corner header — pulse min > max", {
        "active": True, "icon": "mdi:bell-ring", "title": "Inverted Range",
        "subtitle": "min=0.8 max=0.2", "valid_for_s": 300,
        "icon_color": "FF8800", "pulse": True,
        "pulse_period_ms": 500, "pulse_min": 0.8, "pulse_max": 0.2,
    }),
    _header_scenario("Corner header — very short expiry (1 second)", {
        "active": True, "icon": "mdi:bell", "title": "Expires Fast",
        "subtitle": "Should disappear quickly", "valid_for_s": 1,
        "icon_color": "FF0000", "pulse": False,
        "pulse_period_ms": 0, "pulse_min": 0.0, "pulse_max": 1.0,
    }),

    # ═══════════════════════════════════════════════════════════════════════════
    # Rapid-fire: send many services with minimal delay
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "RAPID — page 1 (instant)",
        "action": "set_page",
        "args": _page({"page_id": "rf1", "icon": "mdi:home", "title": "Rapid 1",
                        "subtitle": "Fired instantly"}),
    },
    {
        "name": "RAPID — page 2 (instant)",
        "action": "set_page",
        "args": _page({"page_id": "rf2", "icon": "mdi:flash", "title": "Rapid 2",
                        "subtitle": "Fired instantly"}),
    },
    {
        "name": "RAPID — page 3 (instant)",
        "action": "set_page",
        "args": _page({"page_id": "rf3", "icon": "mdi:solar-power", "title": "Rapid 3",
                        "subtitle": "Fired instantly"}),
    },
    {
        "name": "RAPID — clear all (instant)",
        "action": "set_page",
        "args": {"page_id": "rf1", "active": False, "icon": "", "title": "",
                 "subtitle": "", "details": "", "valid_for_s": 0,
                 "progress": 0, "font_size": 0},
        "_also": {"action": "set_page",
                  "args": {"page_id": "rf2", "active": False, "icon": "", "title": "",
                           "subtitle": "", "details": "", "valid_for_s": 0,
                           "progress": 0, "font_size": 0}},
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # Final cleanup
    # ═══════════════════════════════════════════════════════════════════════════
    {
        "name": "DONE — clear all pages, headers, and notification",
        "action": "set_page",
        "args": {"page_id": "test", "active": False, "icon": "", "title": "",
                 "subtitle": "", "details": "", "valid_for_s": 0,
                 "progress": 0, "font_size": 0},
        "_also": {"action": "set_header", "args": CLEAR_HEADER_ARGS},
    },
]
