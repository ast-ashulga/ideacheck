"""Fetch the full record (all claims, structured limitations, description) for deep comparison.

    .venv/bin/python -u scripts/phase0/fetch_full.py <ids.txt> <out_dir> [--delay 25]
Writes one <publication>.json per document and skips documents already saved.
"""
import argparse, asyncio, json
from pathlib import Path
from patent_client_agents.google_patents import GooglePatentsClient
from fetch_details import gp_forms


async def main(ids: Path, out_dir: Path, delay: float, timeout: float) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    todo = [i for i in ids.read_text().split() if not (out_dir / f"{i}.json").exists()]
    print(f"{len(todo)} to fetch", flush=True)
    async with GooglePatentsClient() as client:
        for n, bq in enumerate(todo, 1):
            p = err = None
            for form in gp_forms(bq):
                try:
                    p = await asyncio.wait_for(client.get_patent_data(form), timeout); break
                except Exception as e:
                    err = f"{type(e).__name__}: {str(e)[:150]}"
            if p is None:
                print(f"[{n}/{len(todo)}] {bq}: ERROR {err}", flush=True); continue
            rec = {
                "publication_number": bq, "title": p.title, "abstract": p.abstract,
                "assignee": p.current_assignee or p.original_assignee, "family_id": p.family_id,
                "priority_date": str(p.priority_date), "status": p.status,
                "legal_status": p.legal_status_category, "expiration_date": str(p.expiration_date),
                "source_language": p.source_language, "claims": p.claims,
                "structured_limitations": p.structured_limitations,
                "description": p.description_markdown or p.description,
            }
            (out_dir / f"{bq}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False, default=str))
            print(f"[{n}/{len(todo)}] {bq}: ok, description {len(rec['description'] or '')} chars", flush=True)
            await asyncio.sleep(delay)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", type=Path); ap.add_argument("out_dir", type=Path)
    ap.add_argument("--delay", type=float, default=25.0); ap.add_argument("--timeout", type=float, default=240.0)
    a = ap.parse_args()
    asyncio.run(main(a.ids, a.out_dir, a.delay, a.timeout))
