#!/usr/bin/env python
"""Score blind gold-set attempts against the hidden answer key.

Usage:
  python scripts/score_gold.py <attempts.json> [--answers phase05/gold/answers/answers.json]
                               [--db data/extract_v2.duckdb]

attempts.json: {"case-NN": ["PUB-1", "PUB-2", ...]}  ranked best first, up to 50 used.

A hit is any attempted publication that belongs to the answer's family: either it is
listed in the answer's family_members, or the extract maps it to the answer's family_id.
Prints a per-case table and recall@20, recall@50, MRR (rank<=50) overall and per stratum.
Always exits 0.
"""
import argparse
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAXR = 50


def norm(p: str) -> str:
    return p.strip().upper().replace(" ", "")


def family_map(pubs, db_path):
    """publication_number -> family_id via the extract (read-only). Empty if unavailable."""
    if not pubs or not Path(db_path).exists():
        return {}
    import duckdb
    con = duckdb.connect(str(db_path), read_only=True)
    con.execute("create temp table q(p varchar)")
    con.executemany("insert into q values (?)", [(p,) for p in pubs])
    rows = con.execute(
        "select publication_number, family_id from publications where publication_number in (select p from q)"
    ).fetchall()
    con.close()
    return {p: str(f) for p, f in rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("attempts")
    ap.add_argument("--answers", default=str(ROOT / "phase05" / "gold" / "answers" / "answers.json"))
    ap.add_argument("--db", default=str(ROOT / "data" / "extract_v2.duckdb"))
    a = ap.parse_args()

    answers = json.load(open(a.answers))["answers"]
    attempts = json.load(open(a.attempts))
    attempts = {k: [norm(p) for p in v][:MAXR] for k, v in attempts.items()}

    all_pubs = sorted({p for v in attempts.values() for p in v})
    fmap = family_map(all_pubs, a.db)

    rows = []
    for ans in sorted(answers, key=lambda x: x["case_id"]):
        cid = ans["case_id"]
        members = {norm(p) for p in ans["family_members"]} | {norm(ans["publication_number"])}
        fam = str(ans["family_id"])
        rank = None
        for i, p in enumerate(attempts.get(cid, []), 1):
            if p in members or fmap.get(p) == fam:
                rank = i
                break
        rows.append((cid, ans["stratum"], rank, len(attempts.get(cid, []))))

    print(f"{'case':8} {'stratum':7} {'n_att':>5} {'rank':>5} {'top20':>5} {'top50':>5}")
    for cid, st, rank, n in rows:
        print(f"{cid:8} {st:7} {n:5d} {rank if rank else '-':>5} "
              f"{'yes' if rank and rank <= 20 else 'no':>5} {'yes' if rank and rank <= 50 else 'no':>5}")

    def summ(sub):
        n = len(sub)
        r20 = sum(1 for _, _, r, _ in sub if r and r <= 20) / n
        r50 = sum(1 for _, _, r, _ in sub if r and r <= 50) / n
        mrr = sum(1.0 / r for _, _, r, _ in sub if r) / n
        return n, r20, r50, mrr

    groups = defaultdict(list)
    for row in rows:
        groups[row[1]].append(row)
    print(f"\n{'group':8} {'n':>3} {'R@20':>6} {'R@50':>6} {'MRR':>6}")
    for g in sorted(groups):
        n, r20, r50, mrr = summ(groups[g])
        print(f"{g:8} {n:3d} {r20:6.3f} {r50:6.3f} {mrr:6.3f}")
    n, r20, r50, mrr = summ(rows)
    print(f"{'ALL':8} {n:3d} {r20:6.3f} {r50:6.3f} {mrr:6.3f}")
    missing = sorted(set(a2["case_id"] for a2 in answers) - set(attempts))
    if missing:
        print(f"\nno attempts for: {', '.join(missing)} (scored as misses)")
    unknown = sorted(set(attempts) - set(a2["case_id"] for a2 in answers))
    if unknown:
        print(f"ignored unknown case ids: {', '.join(unknown)}")


if __name__ == "__main__":
    main()
