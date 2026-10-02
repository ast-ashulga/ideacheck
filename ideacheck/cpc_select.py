"""Choose the extract scope from the classification codes of seed hits (PLAN.md §9.1 A).

Count CPC codes over a set of seed publications (e.g. the top ~50 hits of narrow seed
searches), roll them up to main groups ('B62B5/00') and subclasses ('B62B'), and
propose every group that appears in at least `min_share` of the seeds. Breadth is free:
BigQuery bills the columns read, not the number of codes in the filter.
"""

import re
from collections import Counter
from dataclasses import dataclass

_CODE = re.compile(r"^([A-HY]\d{2}[A-Z])(\d{1,4})/(\d{2,6})$")


def subclass(code: str) -> str | None:
    m = _CODE.match(code.replace(" ", ""))
    return m.group(1) if m else None


def main_group(code: str) -> str | None:
    """'B62B5/0073' -> 'B62B5/00'. Indexing-scheme codes (2000-series) keep their own group."""
    m = _CODE.match(code.replace(" ", ""))
    return f"{m.group(1)}{m.group(2)}/00" if m else None


def covered(code: str, prefixes: list[str]) -> bool:
    return any(code.startswith(p) for p in prefixes)


@dataclass
class Suggestion:
    group: str        # main group, e.g. 'B60K7/00'
    seeds: int        # how many seed families carry at least one code in this group
    share: float
    already_covered: bool

    @property
    def prefix(self) -> str:
        """Extract-filter prefix for this group: 'B60K7/00' -> 'B60K7/'."""
        return self.group[: self.group.index("/") + 1]


def census(seed_codes: dict[str, list[str]]) -> tuple[Counter, Counter]:
    """Per main group and per subclass: number of seeds carrying it (each seed counted once)."""
    groups, subclasses = Counter(), Counter()
    for codes in seed_codes.values():
        groups.update({g for g in map(main_group, codes) if g})
        subclasses.update({s for s in map(subclass, codes) if s})
    return groups, subclasses


def suggest_scope(seed_codes: dict[str, list[str]], current_prefixes: list[str],
                  min_share: float = 0.15, ignore_y: bool = True) -> list[Suggestion]:
    """Main groups present in >= min_share of seeds, flagged if the current scope misses them."""
    seeds = {k: v for k, v in seed_codes.items() if v}
    if not seeds:
        return []
    groups, _ = census(seeds)
    out = []
    for g, n in groups.most_common():
        if ignore_y and g.startswith("Y"):  # Y-section tags (e.g. Y02T) are cross-cutting, not technology
            continue
        share = n / len(seeds)
        if share >= min_share:
            out.append(Suggestion(g, n, share, covered(g, current_prefixes)))
    return out
