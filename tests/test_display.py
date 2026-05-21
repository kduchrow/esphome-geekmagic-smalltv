#!/usr/bin/env python3
"""
Display Framework — Integration Test Script

Calls all ESPHome native API services in various combinations so you can
visually verify formatting on the physical device.

Setup (once):
    cp .env.example .env          # then edit .env and fill in ENCRYPTION_KEY

Usage (via Docker Compose — recommended):
    docker compose run --rm test
    docker compose run --rm test --filter "header"
    docker compose run --rm test --filter "corner"
    docker compose run --rm test --delay 2

Usage (direct Python):
    pip install aioesphomeapi
    python -m tests.test_display --filter "queue"
"""

import argparse
import asyncio
import copy
import sys

try:
    from aioesphomeapi import APIClient
except ImportError:
    print("ERROR: aioesphomeapi not installed. Run: pip install aioesphomeapi")
    sys.exit(1)

from .constants import ENCRYPTION_KEY, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_DELAY
from .scenarios import SCENARIOS


# ── Runner ────────────────────────────────────────────────────────────────────

async def call_service(client, services, action: str, args: dict):
    """Find a registered service by suffix and execute it."""
    svc = next((s for s in services if s.name.endswith(action)), None)
    if svc is None:
        print(f"  \u26a0  Service '{action}' not found on device "
              f"(available: {[s.name for s in services]})")
        return

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
        test_id = f"[{i:>2}/{len(filtered)}]"
        print(f"{test_id} {scenario['name']}")

        def _labeled(action_args, action_type):
            """Inject test ID into title so it appears on the display."""
            if action_type == "set_notification":
                return action_args
            labeled = copy.deepcopy(action_args)
            prefix = f"{test_id} "
            for field in ("title", "subtitle"):
                if field in labeled and labeled[field]:
                    labeled[field] = prefix + labeled[field]
                    break
            return labeled

        try:
            if "_before" in scenario:
                before = scenario["_before"]
                btype = before["action"]
                bargs = _labeled(before["args"], btype)
                await call_service(client, services, btype, bargs)

            atype = scenario["action"]
            args = _labeled(scenario["args"], atype)
            await call_service(client, services, atype, args)

            if "_also" in scenario:
                also = scenario["_also"]
                atype2 = also["action"]
                aargs2 = _labeled(also["args"], atype2)
                await call_service(client, services, atype2, aargs2)

        except Exception as exc:
            print(f"         ERROR: {exc}")

        if i < len(filtered):
            await asyncio.sleep(delay)

    print("\nAll scenarios complete.")
    await client.disconnect()


def main():
    if not ENCRYPTION_KEY:
        print("ERROR: ENCRYPTION_KEY environment variable is not set.")
        print("  cp .env.example .env  then edit .env and paste your key")
        print("  The key is found in your ESPHome device YAML under api.encryption.key.")
        sys.exit(1)

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
