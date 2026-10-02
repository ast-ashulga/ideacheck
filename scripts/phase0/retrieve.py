"""Phase 0, step 7b: run the approved queries and collect candidates.

    .venv/bin/python scripts/phase0/retrieve.py phase0/runs/idea-01/queries.json

Reads queries.json (remote queries plus local SQL) and writes the following next to it:
    remote_hits.json   raw Google Patents hits per query
    candidates.json    merged candidates with the query IDs that found each one
Only the query strings in queries.json are sent to Google Patents.
"""

import asyncio
import json
import re
import sys
from pathlib import Path

import duckdb
from patent_client_agents.google_patents import GooglePatentsClient

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "extract.duckdb"
TAG = re.compile(r"<[^>]+>|&hellip;")


def to_bq(pub: str) -> str:
    """'US12023137B2' -> 'US-12023137-B2' (BigQuery form)."""
    m = re.fullmatch(r"([A-Z]{2})(\d+)([A-Z]\d?)", pub)
    return f"{m[1]}-{m[2]}-{m[3]}" if m else pub


async def run_remote(queries: list[dict]) -> dict:
    hits = {}
    async with GooglePatentsClient() as client:
        for q in queries:
            resp = await client.search_patents(
                keywords=q["keywords"], cpc_codes=q.get("cpc"), page_size=100)
            hits[q["id"]] = [
                {"publication_number": to_bq(r.publication_number),
                 "title": TAG.sub("", r.title or "").strip(),
                 "assignee": getattr(r, "assignee", None),
                 "priority_date": str(getattr(r, "priority_date", "") or "")}
                for r in resp.results
            ]
            print(f"{q['id']}: {len(hits[q['id']])} of {resp.total_results} hits")
            await asyncio.sleep(3)
    return hits


def run_local(local: list[dict]) -> dict:
    con = duckdb.connect(str(DB), read_only=True)
    hits = {}
    for q in local:
        rows = con.sql(q["sql"]).fetchall()
        hits[q["id"]] = [{"publication_number": r[0], "title": (r[1] or [""])[0] if r[1] else ""}
                         for r in rows]
        print(f"{q['id']}: {len(rows)} hits (local)")
    con.close()
    return hits


def merge(hits: dict) -> list[dict]:
    """One entry per family: keep the first-seen publication, record every query that hit it."""
    con = duckdb.connect(str(DB), read_only=True)
    family = dict(con.sql("SELECT publication_number, family_id FROM publications").fetchall())
    con.close()
    by_family: dict[str, dict] = {}
    for qid, rows in hits.items():
        for rank, r in enumerate(rows, 1):
            fam = family.get(r["publication_number"], "pub:" + r["publication_number"])
            entry = by_family.setdefault(fam, {**r, "family_id": fam, "found_by": {}})
            entry["found_by"].setdefault(qid, rank)
            if not entry.get("title") and r.get("title"):
                entry["title"] = r["title"]
    return sorted(by_family.values(), key=lambda e: (-len(e["found_by"]), min(e["found_by"].values())))


def main() -> None:
    qfile = Path(sys.argv[1])
    spec = json.loads(qfile.read_text())
    hits = asyncio.run(run_remote(spec["remote"]))
    (qfile.parent / "remote_hits.json").write_text(json.dumps(hits, indent=1, ensure_ascii=False))
    hits.update(run_local(spec["local"]))
    candidates = merge(hits)
    (qfile.parent / "candidates.json").write_text(json.dumps(candidates, indent=1, ensure_ascii=False))
    print(f"{len(candidates)} candidate families")


if __name__ == "__main__":
    main()
