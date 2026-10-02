"""Check that the EPO OPS credentials in ideacheck/.env work, without printing them.

    .venv/bin/python scripts/check_epo.py
"""

import asyncio
import os
import sys
from pathlib import Path

ENV = Path(__file__).resolve().parents[1] / ".env"


def load_env() -> None:
    if not ENV.exists():
        sys.exit(f"No {ENV} file. Copy .env.example to .env and fill in the two values.")
    for line in ENV.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))
    for name in ("EPO_OPS_API_KEY", "EPO_OPS_API_SECRET"):
        if not os.environ.get(name):
            sys.exit(f"{name} is empty in {ENV}.")


async def main() -> None:
    from patent_client_agents.epo_ops.client import client_from_env

    async with client_from_env() as client:
        cpc = await client.retrieve_cpc(symbol="B62B5/0073")
        print("OK: authenticated to EPO OPS. CPC lookup works:", str(cpc)[:160])


if __name__ == "__main__":
    load_env()
    asyncio.run(main())
