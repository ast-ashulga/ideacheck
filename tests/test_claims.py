import json
from pathlib import Path

import pytest

from ideacheck.claims import independent_claims, parse_claims, references

FULL = Path(__file__).resolve().parents[1] / "phase0" / "runs" / "idea-01" / "full"

# Independent claims, checked by hand against the Phase 0 full texts.
EXPECTED_INDEPENDENT = {
    "EP-2897566-B1": ["1", "13"],
    "US-12564527-B2": ["1"],
    "US-8756726-B2": ["1", "21"],
    "US-2019183707-A1": ["11"],          # claims 1-10 canceled
    "JP-2023019525-A": ["1", "9"],
    "JP-2023144611-A": ["1"],
    "JP-7853860-B2": ["1"],
    "JP-7570286-B2": ["1"],              # claim 7: a bed fitted with the device of claims 4-6
    "JP-6837910-B2": ["1"],
    "JP-2014046890-A": ["1", "2"],
    "JP-2008137631-A": ["1"],
    "DE-202004010854-U1": ["1"],
    "DE-102004033572-A1": ["1"],
}


@pytest.mark.parametrize("pub,expected", sorted(EXPECTED_INDEPENDENT.items()))
def test_independent_claims_on_phase0_documents(pub, expected):
    doc = json.loads((FULL / f"{pub}.json").read_text())
    got = [c.number for c in independent_claims(doc["claims"], doc["structured_limitations"])]
    assert got == expected


def test_reference_forms():
    assert references("The apparatus of claim 1 wherein", 2) == [1]
    assert references("The bogie according to any one of claims 1 to 4, wherein", 5) == [1, 2, 3, 4]
    assert references("of any preceding claim wherein", 12) == list(range(1, 12))
    assert references("請求項５又は６に記載の台車。", 7) == [5, 6]
    assert references("請求項１から３のいずれか１項に記載された", 4) == [1, 2, 3]
    assert references("Zustellerwagen nach Anspruch 1 und 2, dadurch gekennzeichnet", 3) == [1, 2]
    assert references("根据权利要求1所述的装置", 2) == [1]
    assert references("A patient support apparatus comprising a frame", 1) == []


def test_dependent_claims_record_their_parents():
    doc = json.loads((FULL / "US-12564527-B2.json").read_text())
    claims = {c.number: c for c in parse_claims(doc["claims"], doc["structured_limitations"])}
    assert claims["21"].refers_to == [1]
    assert claims["4"].refers_to == [3]


def test_empty_translation_is_flagged_and_original_used():
    doc = json.loads((FULL / "JP-2023019525-A.json").read_text())
    claims = {c.number: c for c in parse_claims(doc["claims"], doc["structured_limitations"])}
    assert claims["2"].text_missing and claims["2"].original
    assert claims["2"].refers_to  # dependency still found from the original
