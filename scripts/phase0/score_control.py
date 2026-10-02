"""Step 7f: score the blind control run against the hidden answer.

    .venv/bin/python scripts/phase0/score_control.py
Pass = the answer's family is in ranked.json's top 20. Also reports whether the answer
appeared at each earlier stage (candidates, fetched details), to show where recall was lost.
"""

import json
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "phase0" / "runs" / "control-01"
ANSWER_FAMILY = "37919331"  # JP-4616127-B2 (Toshiba Tec), see phase0/control-01-known-answer.md


def main() -> None:
    con = duckdb.connect(str(ROOT / "data" / "extract.duckdb"), read_only=True)
    family = dict(con.sql("SELECT publication_number, family_id FROM publications").fetchall())
    members = {p for p, f in family.items() if f == ANSWER_FAMILY}
    print(f"Answer family {ANSWER_FAMILY} members in extract: {sorted(members)}")

    def hit(pubs) -> list[str]:
        return [p for p in pubs if p in members or family.get(p) == ANSWER_FAMILY]

    cands = json.loads((RUN / "candidates.json").read_text()) if (RUN / "candidates.json").exists() else []
    found = [c for c in cands if c.get("family_id") == ANSWER_FAMILY or hit([c["publication_number"]])]
    print(f"Stage retrieve: {len(cands)} candidate families; answer present: {bool(found)}"
          + (f" (found by {found[0]['found_by']})" if found else ""))

    details = [p for p in RUN.glob("*.json") if p.name not in ("candidates.json", "ranked.json", "remote_hits.json", "queries.json")]
    fetched = set()
    for d in details:
        try:
            fetched |= set(json.loads(d.read_text()))
        except Exception:
            pass
    print(f"Stage fetch: answer fetched: {bool(hit(fetched))}")

    ranked = json.loads((RUN / "ranked.json").read_text())
    rank = next((r["rank"] for r in ranked if hit([r["publication_number"]])), None)
    print(f"Stage rank: top-{len(ranked)} list; answer rank: {rank}")
    print("RESULT:", "PASS" if rank is not None and rank <= 20 else "FAIL")


if __name__ == "__main__":
    main()
