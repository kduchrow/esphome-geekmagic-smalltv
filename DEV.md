# Developer Guide

This document defines the authoritative development workflow for this project.
All contributors and AI agents must strictly follow the commands and patterns
described here.

---

## Repository Structure

```
esphome-geekmagic-smalltv/
├── components/
│   └── display_framework/          # The external component (tracked)
│       ├── __init__.py             # ESPHome config schema + code-gen
│       ├── display_framework.h     # C++ class declaration
│       └── display_framework.cpp   # C++ render + page-stack logic
├── examples/                       # Community-facing templates (tracked)
│   ├── smalltv-minimal.yaml        # Minimal device config (no weather)
│   └── smalltv-with-weather.yaml   # Device config with weather integration
├── my_examples/                    # Personal device configs (gitignored)
│   ├── displayarbeitszimmer.base.yaml  # Full shared device config (no external_components)
│   ├── displayarbeitszimmer.dev.yaml   # Local Docker testing (type: local)
│   ├── displayarbeitszimmer.ha.yaml    # HA deployment (type: git + SHA)
│   └── secrets.yaml                    # Credentials (never committed)
├── docker-compose.yml              # ESPHome dev environment (tracked, repo root)
├── DEV.md                          # This file
├── display-framework.md            # Component design spec
├── FEATURE_REQUESTS.md             # Feature backlog
└── README.md                       # Public-facing docs
```

---

## Config File Roles

### `my_examples/displayarbeitszimmer.base.yaml`
Contains the full device configuration — everything **except** `external_components`.
This is the single source of truth for device-specific settings: ESPHome name,
hardware pins, fonts, sensors, display config, and `display_framework` options.

### `my_examples/displayarbeitszimmer.dev.yaml`
Used for local testing via Docker Compose. Uses ESPHome `packages:` to include
the base, then declares `external_components` with `type: local` pointing to
the repo's `components/` folder (path is relative to this file):

```yaml
packages:
  device: !include displayarbeitszimmer.base.yaml

external_components:
  - source:
      type: local
      path: ../components      # relative to this file → repo root /components
    components: [display_framework]
  - source:
      type: git
      url: https://github.com/lhartmann/esphome-st7789v-fractional-framebuffer
      ref: main
    refresh: 0s
    components: [st7789v]
```

### `my_examples/displayarbeitszimmer.ha.yaml`
Used for Home Assistant deployment. Uses `packages:` to include the same base,
then declares `external_components` with `type: git` referencing a pinned commit SHA:

```yaml
packages:
  device: !include displayarbeitszimmer.base.yaml

external_components:
  - source:
      type: git
      url: https://github.com/kduchrow/esphome-geekmagic-smalltv
      ref: <SHA>               # update after each commit
    components: [display_framework]
  - source:
      type: git
      url: https://github.com/lhartmann/esphome-st7789v-fractional-framebuffer
      ref: main
    refresh: 0s
    components: [st7789v]
```

---

## docker-compose.yml

Located at the **repo root** (tracked). Mounts the repo root as `/config` inside the container.

```yaml
services:
  esphome:
    image: esphome/esphome:2026.4.5
    container_name: esphome
    restart: unless-stopped
    volumes:
      - .:/config:rw           # repo root → /config
    working_dir: /config
    command: ["version"]
```

All ESPHome commands are run via `docker compose` from the **repo root**.
Never run ESPHome outside of Docker.

---

## All Commands

All commands are run from the **repository root** (`c:\Git\esphome-geekmagic-smalltv`).

### Compile

Compile the dev config without flashing. Use this first to catch errors:

```powershell
docker compose run --rm esphome compile my_examples/displayarbeitszimmer.dev.yaml
```

### Flash (OTA)

Compile and flash to the device over the air:

```powershell
docker compose run --rm esphome run my_examples/displayarbeitszimmer.dev.yaml
```

### Validate Config

Validate YAML and schema without building:

```powershell
docker compose run --rm esphome config my_examples/displayarbeitszimmer.dev.yaml
```

### View Logs

Stream device logs over the network:

```powershell
docker compose run --rm esphome logs my_examples/displayarbeitszimmer.dev.yaml
```

### Clean Build Cache

Remove the `.esphome/` build cache for a clean rebuild:

```powershell
docker compose run --rm esphome clean my_examples/displayarbeitszimmer.dev.yaml
```

### Get Current Commit SHA

Get the SHA to pin in `displayarbeitszimmer.ha.yaml` before HA deployment:

```powershell
git rev-parse HEAD
```

### Start ESPHome Dashboard (optional)

```powershell
docker compose up -d
```

---

## Development Workflow

### Step 1 — Edit the component

Make changes to files in `components/display_framework/`:
- `display_framework.h` — class declaration + setters
- `display_framework.cpp` — implementation
- `__init__.py` — config schema + code-gen wiring

All three files must stay in sync whenever a new config option is added.

### Step 2 — Validate

```powershell
docker compose run --rm esphome config my_examples/displayarbeitszimmer.dev.yaml
```

### Step 3 — Compile

```powershell
docker compose run --rm esphome compile my_examples/displayarbeitszimmer.dev.yaml
```

### Step 4 — Flash and test

```powershell
docker compose run --rm esphome run my_examples/displayarbeitszimmer.dev.yaml
```

### Step 5 — Commit

```powershell
git add -A
git commit -m "feat: <description>"
```

### Step 6 — Prepare HA deployment

Get the SHA of the commit just made:

```powershell
git rev-parse HEAD
```

Update `ref:` in `my_examples/displayarbeitszimmer.ha.yaml` to that SHA.

### Step 7 — Copy to Home Assistant

Copy `my_examples/displayarbeitszimmer.ha.yaml` to your HA ESPHome folder
and flash from the HA ESPHome UI.

---

## Adding a New Device

To add a new device (e.g., `wohnzimmer`):

1. Copy `my_examples/displayarbeitszimmer.base.yaml` → `my_examples/wohnzimmer.base.yaml`
   and adjust device name, pins, and `display_framework` options.
2. Copy `my_examples/displayarbeitszimmer.dev.yaml` → `my_examples/wohnzimmer.dev.yaml`
   and update the `!include` path.
3. Copy `my_examples/displayarbeitszimmer.ha.yaml` → `my_examples/wohnzimmer.ha.yaml`
   and update the `!include` path and `ref` SHA.

---

## Adding to `examples/` (community templates)

Files in `examples/` are tracked and must:
- Use `type: git, ref: main` for `external_components` (always points to latest).
- Contain no secrets or personal values.
- Be self-contained (no `!include` of personal configs).

---

## `.gitignore` Rules

```gitignore
# ESPHome build cache
/.esphome/

# Secrets — never commit credentials
**/secrets.yaml

# Personal device configs (gitignored — use examples/ as templates)
/my_examples/
```

`my_examples/` is fully gitignored. `docker-compose.yml` lives at the repo root
and is tracked.
