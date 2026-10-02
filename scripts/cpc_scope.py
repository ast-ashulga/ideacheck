"""Suggest extract classification prefixes from seed publications.

    .venv/bin/python scripts/cpc_scope.py SEEDS.txt [--min-share 0.15] [--current B62B A61G7/ A61G1/]
SEEDS.txt holds one publication number per line. Codes come from the local extract or
from cached records (records fetched since Phase 0.5 store a `cpc` field). Seeds with no
known codes are listed, so they can be looked up before the scope is fixed.
Local only: no network calls.
"""

import argparse
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ideacheck.cache import Cache  # noqa: E402
from ideacheck.cpc_select import suggest_scope  # noqa: E402
from ideacheck.numbers import canonical  # noqa: E402


def _strip_fi(code: str) -> str:
    """FI codes carry a suffix: 'B60B33/00@Z', 'A47L9/00,102' -> 'B60B33/00'."""
    return code.split("@")[0].split(",")[0]


def seed_codes(pubs: list[str]) -> dict[str, list[str]]:
    """CPC + IPC + FI codes per seed (Japanese documents often have no CPC)."""
    db = ROOT / "data" / ("extract_v2.duckdb" if (ROOT / "data" / "extract_v2.duckdb").exists() else "extract.duckdb")
    con = duckdb.connect(str(db), read_only=True)
    cols = {r[0] for r in con.sql("DESCRIBE publications").fetchall()}
    expr = "list_concat(cpc, ipc, fi)" if {"ipc", "fi"} <= cols else "cpc"
    local = dict(con.sql(
        f"SELECT publication_number, {expr} FROM publications WHERE publication_number IN "
        f"({','.join('?' * len(pubs))})", params=pubs).fetchall()) if pubs else {}
    local = {k: sorted({_strip_fi(c) for c in (v or [])}) for k, v in local.items()}
    con.close()
    cache, out = Cache(), {}
    for p in pubs:
        rec = cache.get(p, "details") or {}
        out[p] = list(local.get(p) or rec.get("cpc") or [])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("seeds", type=Path)
    ap.add_argument("--min-share", type=float, default=0.15)
    ap.add_argument("--current", nargs="*", default=["B62B", "A61G7/", "A61G1/"])
    a = ap.parse_args()
    pubs = [canonical(x) for x in a.seeds.read_text().split() if x.strip()]
    codes = seed_codes(pubs)
    unknown = [p for p, c in codes.items() if not c]
    print(f"{len(pubs)} seeds, {len(pubs) - len(unknown)} with known codes")
    for s in suggest_scope(codes, a.current, a.min_share):
        flag = "covered" if s.already_covered else "MISSING from scope"
        print(f"  {s.group:12} {s.seeds:3} seeds ({s.share:4.0%})  {flag}  -> prefix {s.prefix}")
    if unknown:
        print(f"No codes known for {len(unknown)} seeds (not in extract or cache): {' '.join(unknown)}")


if __name__ == "__main__":
    main()
