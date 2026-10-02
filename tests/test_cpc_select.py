from ideacheck.cpc_select import main_group, subclass, suggest_scope


def test_rollups():
    assert main_group("B62B5/0073") == "B62B5/00"
    assert main_group("B62B2301/04") == "B62B2301/00"
    assert subclass("A61G7/08") == "A61G"
    assert main_group("not a code") is None


def test_suggest_flags_missing_groups_and_counts_each_seed_once():
    seeds = {
        "A": ["B62B5/0026", "B62B5/0073", "B60K7/0007"],
        "B": ["B62B5/0026", "B60K7/0007", "Y02T10/64"],
        "C": ["B60B19/003", "B62B5/0069"],
        "D": [],  # unknown seed: ignored in the shares
    }
    got = {s.group: s for s in suggest_scope(seeds, ["B62B", "A61G7/"], min_share=0.3)}
    assert got["B62B5/00"].seeds == 3 and got["B62B5/00"].already_covered
    assert got["B60K7/00"].seeds == 2 and not got["B60K7/00"].already_covered
    assert got["B60K7/00"].prefix == "B60K7/"
    assert "B60B19/00" in got          # 1 of 3 seeds = 33% >= 30%
    assert not any(g.startswith("Y") for g in got)
