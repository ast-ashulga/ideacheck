#!/usr/bin/env python
"""Leak check for the phase-0.5 gold set.

For every case, compare the blind input (idea_text + feature texts) with the
hidden source (abstract_en + title_en) from answers.json and report:
  * every shared word n-gram of length >= 3 (maximal spans only), after
    lower-casing and ignoring n-grams made only of stop words;
  * the share of distinctive source word types (>= 6 letters, not stop words)
    that reappear in the input (unique types, light plural folding);
  * title leaks: the full normalised title, or any non-stop-word title 2-gram
    or title content word of >= 6 letters... (2-grams are reported; content
    words only informationally);
  * any digit in the input;
  * word count of idea_text (120-200) and feature count (4-6).

A case is FLAGGED if a shared n-gram of >= 4 words exists, the distinctive-word
overlap is > 35%, the full title or a title 2-gram appears, a digit appears,
or the word/feature counts are out of range.

Usage:
  python scripts/gold_leak_check.py [--gold phase05/gold] [--json-out FILE]
Exit code 1 if any case is flagged, else 0.
"""
import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STOP = set("""
a about above after again against all also am an and any are as at be because been before being below between both
but by can could did do does doing down during each either else even ever every few for from further had has have
having he her here hers herself him himself his how however i if in into is it its itself just least less like may
me might more most much must my myself neither no nor not now of off on once one only or other others otherwise our
ours ourselves out over own per rather same she should so some such than that the their theirs them themselves then
there therefore these they this those though through thus to too toward towards under until up upon us very via was
we were what when whenever where whereas wherever whether which while who whom whose why will with within without
would yet you your yours yourself yourselves its it's it’s etc i.e e.g
""".split())

BOILER = [
    r"\[selection\]\s*figure\s*\d*", r"selection drawing", r"problem to be solved\s*:?", r"solution\s*:",
    r"\[problems?\]", r"\[configuration\]", r"\[solution\]", r"【[^】]*】", r"<\s*/?\s*p\s*>",
]


def clean(text: str) -> str:
    t = html.unescape(html.unescape(text or ""))
    t = re.sub(r"<[^>]+>", " ", t)
    t = t.lower()
    for b in BOILER:
        t = re.sub(b, " ", t)
    # reference numerals such as (51, 52), (10), 21, 2B
    t = re.sub(r"\(\s*[\d\s,'’a-z\-]{0,20}\d[\d\s,'’a-z\-]*\)", " ", t)
    return t


def tokens(text: str):
    return re.findall(r"[a-z]+(?:'[a-z]+)?|\d+", text)


def fold(w: str) -> str:
    if len(w) > 4 and w.endswith("ies"):
        return w[:-3] + "y"
    if len(w) > 4 and w.endswith("es") and w[-3] in "sxz":
        return w[:-2]
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        return w[:-1]
    return w


def ngrams(toks, n):
    return {tuple(toks[i:i + n]) for i in range(len(toks) - n + 1)}


def content(gram):
    return any(w not in STOP for w in gram)


def shared_spans(src, inp, nmin=3):
    """Maximal shared n-grams (n >= nmin) that are not stop-word-only."""
    s_tok, i_tok = [fold(w) for w in src], [fold(w) for w in inp]
    nmax = min(len(s_tok), len(i_tok))
    found = {}
    for n in range(nmin, nmax + 1):
        common = ngrams(s_tok, n) & ngrams(i_tok, n)
        common = {g for g in common if content(g)}
        if not common:
            break
        found[n] = common
    spans = []
    for n in sorted(found, reverse=True):
        for g in found[n]:
            if not any(" ".join(g) in " ".join(h) for h in spans):
                spans.append(g)
    return sorted(spans, key=lambda g: (-len(g), g))


def check_case(ans, inp):
    src_text = clean(ans["abstract_en"]) + " . " + clean(ans["title_en"])
    src = tokens(src_text)
    raw_input = inp["idea_text"] + " . " + " . ".join(f["text"] for f in inp["features"])
    in_text = raw_input.lower()
    itoks = tokens(in_text)

    spans = shared_spans(src, itoks)
    max_n = max((len(g) for g in spans), default=0)

    dist = {fold(w) for w in src if w.isalpha() and len(w) >= 6 and w not in STOP}
    in_set = {fold(w) for w in itoks}
    reused = sorted(dist & in_set)
    overlap = len(reused) / len(dist) if dist else 0.0

    title_toks = [fold(w) for w in tokens(clean(ans["title_en"]))]
    in_fold = [fold(w) for w in itoks]
    in_str = " " + " ".join(in_fold) + " "
    full_title = bool(title_toks) and (" " + " ".join(title_toks) + " ") in in_str
    title_bigrams = sorted(" ".join(g) for g in ngrams(title_toks, 2)
                           if all(w not in STOP for w in g) and (" " + " ".join(g) + " ") in in_str)
    title_words = sorted({w for w in title_toks if len(w) >= 6 and w not in STOP} & set(in_fold))

    digits = re.findall(r"\d", raw_input)
    words = len(re.findall(r"\S+", inp["idea_text"]))
    nfeat = len(inp["features"])

    reasons = []
    if max_n >= 4:
        reasons.append(f"shared {max_n}-gram")
    if overlap > 0.35:
        reasons.append(f"distinctive overlap {overlap:.0%}")
    if full_title:
        reasons.append("full title present")
    if title_bigrams:
        reasons.append("title 2-gram present")
    if digits:
        reasons.append("digit in input")
    if not 120 <= words <= 200:
        reasons.append(f"idea_text {words} words")
    if not 4 <= nfeat <= 6:
        reasons.append(f"{nfeat} features")
    return {
        "case_id": inp["case_id"],
        "shared_ngrams_3plus": [" ".join(g) for g in spans],
        "max_shared_ngram": max_n,
        "distinctive_source_types": len(dist),
        "distinctive_reused": len(reused),
        "distinctive_overlap": round(overlap, 3),
        "distinctive_reused_words": reused,
        "title_full_present": full_title,
        "title_bigrams_present": title_bigrams,
        "title_content_words_present": title_words,
        "digits_in_input": len(digits),
        "idea_words": words,
        "n_features": nfeat,
        "flagged": bool(reasons),
        "reasons": reasons,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", default=str(ROOT / "phase05" / "gold"))
    ap.add_argument("--json-out")
    a = ap.parse_args()
    gold = Path(a.gold)
    answers = {x["case_id"]: x for x in json.load(open(gold / "answers" / "answers.json"))["answers"]}
    results = []
    for cid in sorted(answers):
        inp = json.load(open(gold / "inputs" / f"{cid}.json"))
        results.append(check_case(answers[cid], inp))

    print(f"{'case':8} {'words':>5} {'feat':>4} {'maxN':>4} {'dist%':>6} {'reused/types':>12} {'title2g':>7} {'dig':>3}  flag")
    for r in results:
        print(f"{r['case_id']:8} {r['idea_words']:5d} {r['n_features']:4d} {r['max_shared_ngram']:4d} "
              f"{r['distinctive_overlap']*100:5.1f}% {r['distinctive_reused']:>5}/{r['distinctive_source_types']:<6} "
              f"{len(r['title_bigrams_present']):7d} {r['digits_in_input']:3d}  {'FLAG ' + '; '.join(r['reasons']) if r['flagged'] else 'ok'}")
        if r["shared_ngrams_3plus"]:
            print("         shared 3+-grams:", " | ".join(r["shared_ngrams_3plus"]))
    nflag = sum(r["flagged"] for r in results)
    print(f"\nflagged: {nflag}/{len(results)}; max shared n-gram overall: "
          f"{max(r['max_shared_ngram'] for r in results)}; max distinctive overlap: "
          f"{max(r['distinctive_overlap'] for r in results):.1%}")
    if a.json_out:
        json.dump(results, open(a.json_out, "w"), indent=1)
    sys.exit(1 if nflag else 0)


if __name__ == "__main__":
    main()
