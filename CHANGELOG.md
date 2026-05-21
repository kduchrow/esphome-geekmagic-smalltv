# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-21

### Added

- Initial release of `display_framework` ESPHome external component
- Page stack with rotation, expiry, and configurable max pages
- Header queue with per-header expiry, pulse animation, and custom icon color
- Notification icon (top-right corner, configurable icon)
- Progress bar widget (1-100%) rendered below page details
- Dual font size support (normal 14px / large 20px) per page
- Configurable time/date bar with custom format strings
- Footer with IP address and WiFi signal strength
- Configurable delimiter (`-|-`) for multi-line page details
- Home Assistant blueprints: Send Page, Header Alert, Binary Sensor Notification
- Docker Compose-based ESPHome development environment
- Integration test script (`tests/test_display.py`) for visual verification
