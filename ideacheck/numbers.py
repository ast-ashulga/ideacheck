"""Publication-number forms.

The canonical form is the BigQuery one: 'US-2019183707-A1', 'JP-4616127-B2'.
Google Patents uses the compact form 'US2019183707A1', and pads compressed US
pre-grant numbers to 11 digits: 'US20190183707A1'.
"""

import re

_COMPACT = re.compile(r"([A-Z]{2})(\d+)([A-Z]\d?)")
_CANONICAL = re.compile(r"([A-Z]{2})-([A-Z]?\d+)-([A-Z]\d?)")


def canonical(number: str) -> str:
    """Any supported form -> 'CC-NUMBER-KIND'. Unknown forms are returned unchanged, upper-cased."""
    n = number.strip().upper().replace(" ", "")
    if _CANONICAL.fullmatch(n):
        return n
    m = _COMPACT.fullmatch(n)
    if not m:
        return n
    cc, num, kind = m.groups()
    if cc == "US" and len(num) == 11 and num[4] == "0":  # 11-digit Google form of a pre-grant number
        num = num[:4] + num[5:]
    return f"{cc}-{num}-{kind}"


def google_forms(number: str) -> list[str]:
    """Canonical -> Google Patents forms to try, most likely first."""
    n = canonical(number)
    m = _CANONICAL.fullmatch(n)
    if not m:
        return [n.replace("-", "")]
    cc, num, kind = m.groups()
    forms = [f"{cc}{num}{kind}"]
    if cc == "US" and len(num) == 10:  # compressed US pre-grant publication number
        forms.append(f"{cc}{num[:4]}0{num[4:]}{kind}")
    return forms
