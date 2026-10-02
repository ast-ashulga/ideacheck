"""Fetch title, abstract, independent claims, dates and status for a list of publications.

Resumable and polite to Google Patents: saves after every record, skips records
already saved, waits between requests, and gives up on a record after a timeout
(it is retried on the next run).

    .venv/bin/python -u scripts/phase0/fetch_details.py <ids.txt> <out.json> [--delay 20]
"""

import argparse
import asyncio
import json
import re
from pathlib import Path

from patent_client_agents.google_patents import GooglePatentsClient

DEPENDENT = re.compile(r"\b(claim|claims|anspruch|revendication)\s+\d", re.I)


def gp_forms(bq: str) -> list[str]:
    """BigQuery 'US-2019183707-A1' -> Google forms to try: 'US2019183707A1', 'US20190183707A1'."""
    cc, num, kind = bq.split("-")
    forms = [f"{cc}{num}{kind}"]
    if cc == "US" and len(num) == 10:  # compressed US pre-grant publication number
        forms.append(f"{cc}{num[:4]}0{num[4:]}{kind}")
    return forms


def record(p) -> dict:
    independent = [c for c in (p.claims or []) if not DEPENDENT.search(c["text"][:200])][:3]
    limitations = p.structured_limitations or {}
    return {
        "title": p.title, "abstract": p.abstract, "family_id": p.family_id,
        "priority_date": str(p.priority_date), "status": p.status,
        "legal_status": p.legal_status_category,
        "assignee": p.current_assignee or p.original_assignee,
        "independent_claims": independent,
        "structured_limitations": {c["number"]: limitations.get(c["number"]) for c in independent},
        "source_language": p.source_language,
    }


async def main(ids_path: Path, out_path: Path, delay: float, timeout: float) -> None:
    ids = [line.strip() for line in ids_path.read_text().splitlines() if line.strip()]
    out = json.loads(out_path.read_text()) if out_path.exists() else {}
    todo = [i for i in ids if "error" in out.get(i, {"error": 1})]
    print(f"{len(ids) - len(todo)} already saved, {len(todo)} to fetch", flush=True)
    async with GooglePatentsClient() as client:
        for n, bq in enumerate(todo, 1):
            error = None
            for form in gp_forms(bq):
                try:
                    out[bq] = record(await asyncio.wait_for(client.get_patent_data(form), timeout))
                    error = None
                    break
                except Exception as e:  # try the next number form, then give up for this run
                    error = f"{type(e).__name__}: {str(e)[:150]}"
            if error:
                out[bq] = {"error": error}
            out_path.write_text(json.dumps(out, indent=1, ensure_ascii=False, default=str))
            print(f"[{n}/{len(todo)}] {bq}: {'ERROR ' + error if error else 'ok'}", flush=True)
            await asyncio.sleep(delay)
    failed = sum("error" in v for v in out.values())
    print(f"done: {len(out) - failed} saved, {failed} failed (re-run to retry)", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--delay", type=float, default=20.0)
    ap.add_argument("--timeout", type=float, default=240.0)
    a = ap.parse_args()
    asyncio.run(main(a.ids, a.out, a.delay, a.timeout))
