"""Claim structure: which claims are independent, and what each dependent claim refers to.

Google's structured data marks every claim as independent, and machine-translated
claims are often empty or start mid-sentence. So dependency is read from the
ORIGINAL-language text in `structured_limitations` first (it keeps references such
as 請求項１に記載の… / nach Anspruch 1), with the English claim text as a fallback.

A claim that refers to any other claim is treated as dependent, including claims in
another category ("a bed fitted with the device of claims 4 to 6"), because it
includes the limitations of the claims it refers to.
"""

import re
from dataclasses import dataclass, field

_FULLWIDTH = str.maketrans("０１２３４５６７８９－～", "0123456789-~")

# A reference word followed by a number list: "claim 1", "claims 1 to 4", "請求項５又は６".
_REF = re.compile(
    r"(?:claims?|請求項|权利要求|權利要求|청구항|Anspr(?:uch|üche|uchs)|revendications?|reivindicaci(?:ón|ones))"
    r"\s*((?:\d+\s*(?:,|and|or|to|-|~|bis|und|oder|et|ou|à|y|o|から|又は|または|及び|乃至|至|或|和|내지|또는)?\s*)+)",
    re.IGNORECASE,
)
_RANGE = re.compile(r"(\d+)\s*(?:to|-|~|bis|à|から|乃至|至|내지)\s*(\d+)", re.IGNORECASE)
_ANY_PRECEDING = re.compile(
    r"any (?:one )?(?:of the )?preceding claims?|einem der vorhergehenden Ansprüche|"
    r"l'une quelconque des revendications précédentes|前記いずれかの請求項", re.IGNORECASE)
_CANCELED = re.compile(r"^\s*-?\s*\d*\s*\.?\s*\((?:canceled|cancelled|deleted)\)", re.IGNORECASE)


@dataclass
class Claim:
    number: str
    text: str                       # English (possibly machine-translated, possibly empty)
    original: str = ""              # original-language text from structured_limitations
    refers_to: list[int] = field(default_factory=list)
    canceled: bool = False

    @property
    def independent(self) -> bool:
        return not self.canceled and not self.refers_to

    @property
    def text_missing(self) -> bool:
        """English text is empty; use `original` instead."""
        return not self.text.strip()


def _first_number(number: str) -> int | None:
    m = re.match(r"\d+", number)
    return int(m.group()) if m else None


def references(text: str, own: int | None) -> list[int]:
    """Claim numbers that `text` refers to (excluding its own number)."""
    text = text.translate(_FULLWIDTH)
    found: set[int] = set()
    for m in _REF.finditer(text):
        group = m.group(1)
        for a, b in _RANGE.findall(group):
            found.update(range(int(a), int(b) + 1))
        found.update(int(n) for n in re.findall(r"\d+", group))
    if own and _ANY_PRECEDING.search(text):
        found.update(range(1, own))
    if own:
        found = {n for n in found if n < own}  # a claim can only refer to earlier claims
    return sorted(found)


def parse_claims(claims: list[dict], structured_limitations: dict | None = None) -> list[Claim]:
    limitations = structured_limitations or {}
    out = []
    for c in claims or []:
        number, text = str(c.get("number", "")), c.get("text") or ""
        original = " ".join(limitations.get(number) or [])
        own = _first_number(number)
        canceled = bool(_CANCELED.match(text)) or "-" in number and not text.strip("-0123456789. ()canceled")
        refs = references(original, own) if original.strip() else []
        if not refs and not original.strip():
            refs = references(text, own)
        out.append(Claim(number, text, original, refs, canceled))
    return out


def independent_claims(claims: list[dict], structured_limitations: dict | None = None) -> list[Claim]:
    return [c for c in parse_claims(claims, structured_limitations) if c.independent]
