"""Step 7d check: every quote in the comparison files must be a verbatim substring of the source document.

    .venv/bin/python scripts/phase0/verify_quotes.py phase0/runs/idea-01
Matching ignores differences in whitespace only. Writes compare/verified.json, where any
finding whose quote fails is downgraded to "unverified", and prints a summary.
"""

import json
import re
import sys
from pathlib import Path

WS = re.compile(r"\s+")


def norm(s: str) -> str:
    return WS.sub(" ", s or "").strip()


def corpus(doc: dict) -> str:
    claims = " ".join(c.get("text", "") for c in doc.get("claims") or [])
    limits = " ".join(" ".join(v or []) for v in (doc.get("structured_limitations") or {}).values())
    return norm(" ".join([doc.get("abstract") or "", claims, limits, doc.get("description") or ""]))


def main(run: Path) -> None:
    results, stats = {}, {"checked": 0, "failed": 0}
    for cmp_file in sorted((run / "compare").glob("*.json")):
        if cmp_file.name == "verified.json":
            continue
        cmp = json.loads(cmp_file.read_text())
        text = corpus(json.loads((run / "full" / cmp_file.name).read_text()))
        failures = []

        def check(item: dict, positive: bool, label: str) -> None:
            if not positive:
                return
            stats["checked"] += 1
            if not item.get("quote") or norm(item["quote"]) not in text:
                stats["failed"] += 1
                failures.append(label)
                item["verified"] = False
            else:
                item["verified"] = True

        for feat, f in cmp["prior_art"].items():
            check(f, f["verdict"] in ("disclosed", "partial"), f"prior_art.{feat}")
            if f.get("verified") is False:
                f["verdict"] = "unverified"
        for claim in cmp.get("claim_overlap", []):
            for i, lim in enumerate(claim["limitations"]):
                check(lim, lim["met_by_idea"] == "yes", f"claim {claim['claim']} limitation {i + 1}")
                if lim.get("verified") is False:
                    lim["met_by_idea"] = "unverified"
            claim["all_met_verified"] = all(l["met_by_idea"] == "yes" for l in claim["limitations"])
        cmp["quote_failures"] = failures
        results[cmp["publication_number"]] = cmp
        print(f"{cmp['publication_number']:20} failures: {failures or 'none'}")
    (run / "compare" / "verified.json").write_text(json.dumps(results, indent=1, ensure_ascii=False))
    print(f"\n{stats['checked']} positive findings checked, {stats['failed']} quotes failed verification")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
