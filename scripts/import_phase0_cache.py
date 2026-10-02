"""One-off: import every record fetched in Phase 0 into data/cache.sqlite.

    .venv/bin/python scripts/import_phase0_cache.py
- phase0/runs/*/full/*.json       -> level 'full' (all claims + description; no CPC field)
- phase0/runs/*/details*.json      -> level 'details' (independent claims only)
Records that hold only an error are skipped. A 'full' row is never replaced by 'details'.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ideacheck.cache import Cache  # noqa: E402
from ideacheck.sources import GOOGLE  # noqa: E402


def mtime(p: Path) -> str:
    return datetime.fromtimestamp(p.stat().st_mtime, timezone.utc).isoformat(timespec="seconds")


def main() -> None:
    cache = Cache()
    added = {"full": 0, "details": 0, "skipped": 0}
    for f in sorted(ROOT.glob("phase0/runs/*/full/*.json")):
        rec = json.loads(f.read_text())
        cache.put(rec["publication_number"], GOOGLE, "full", rec, fetched_at=mtime(f))
        added["full"] += 1
    for f in sorted(ROOT.glob("phase0/runs/*/details*.json")):
        for pub, rec in json.loads(f.read_text()).items():
            if "error" in rec or cache.get(pub, "full"):
                added["skipped"] += 1
                continue
            cache.put(pub, GOOGLE, "details", rec, fetched_at=mtime(f))
            added["details"] += 1
    print("imported:", added, "| cache now:", cache.stats())


if __name__ == "__main__":
    main()
