# Step 7d: per-document comparison instructions (for comparison agents)

You compare ONE confidential invention idea against patent documents that are already on local disk.
**Do not use the web or any network tool. Do not put the idea text into any search or external request.** Read local files only.

## Inputs
- Idea and features: `phase0/idea-01-power-assist-cart.md`. Use the features table E1–E6 and the "Clarifications" section: passive wheels are free-swivel casters, and the vector is translation only.
- Document full text: `phase0/runs/idea-01/full/<PUB>.json`, with fields `claims` (list of {number, text}), `structured_limitations` (claim number → list of limitation strings), `description`, `abstract`, `status` and `legal_status`.
  Descriptions can be long (up to 350k characters). Search them with grep/Read for the relevant passages: wheel layout, casters, steering, drive, handle, force sensor, vector, speed or acceleration, control.

## Task A: prior-art disclosure (every document)
For each feature E1–E6, decide whether THIS document discloses it anywhere (claims, description or abstract):
- `disclosed`: clearly and fully disclosed.
- `partial`: a similar but not identical teaching. Say exactly what differs, e.g. "steering by differential wheel speed rather than a dedicated 360° steering motor", or "4 driven wheels, not 2 diagonal".
- `absent`: not found.

Pay special attention to the distinctive combination:
- E2 + E3: exactly two active steer-and-drive wheels, placed diagonally, with the other two wheels as free-swivel casters.
- E5 → E6: handle force turned into a translation vector, using speed or acceleration, then into per-wheel steering angle plus drive.

## Task B: claim overlap (only if `legal_status` is "active")
For each independent claim (a claim that does not refer to another claim), take its limitations from `structured_limitations` (or split the claim text yourself if missing). For each limitation, decide whether a product built as described in the idea would meet it:
- `yes` / `no` / `unclear`, with a one-line reason.

A claim is "all_met" only if every limitation is `yes`. Be strict: an omni wheel or a Mecanum wheel is NOT a steer-and-drive wheel. A limitation the idea doesn't specify (e.g. "a display") is `unclear` if the idea might include it, or `no` if it contradicts the idea.

## Evidence rule (mandatory)
Every `disclosed`/`partial` verdict and every `yes` must include a `quote`: an **exact, verbatim substring** of the document text (claims, description or abstract), 8–40 words, copied character for character, including the translation's odd wording, punctuation and reference numerals. Quotes are checked by string match afterwards, and any finding with a quote that doesn't match is discarded. Don't paraphrase inside `quote`. Put explanations in `note`.

## Output
Write `phase0/runs/idea-01/compare/<PUB>.json` (one file per document), exactly this shape:

```json
{
  "publication_number": "<PUB>",
  "legal_status": "active|not_active",
  "one_line_summary": "what the document is about, in one sentence",
  "prior_art": {
    "E1": {"verdict": "disclosed|partial|absent", "quote": "...", "location": "claim 1 | description | abstract", "note": "..."},
    "E2": {...}, "E3": {...}, "E4": {...}, "E5": {...}, "E6": {...}
  },
  "combination_note": "does it disclose E2+E3 together? E5->E6 together? what is the closest gap to the idea?",
  "claim_overlap": [
    {"claim": "1", "all_met": false,
     "limitations": [{"limitation": "...", "met_by_idea": "yes|no|unclear", "quote": "<required when yes; verbatim from the claim>", "reason": "..."}]}
  ]
}
```
Use `"claim_overlap": []` for documents that aren't active. For `absent` verdicts, use `"quote": ""`.
Finish by replying with 2–3 sentences per document: the closest overlap and the biggest difference.
