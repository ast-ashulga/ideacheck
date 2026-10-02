# Verdict rubric (PLAN.md §9.1 E), v1.1, 2026-10-02 (user decisions applied)

Every comparison agent and every human labeller uses this rubric, so verdicts mean the same thing across documents, runs and people.
The examples are real, verified Phase 0 findings for idea 01 (`phase0/runs/idea-01/compare/verified.json`).

It answers two different questions. Never mix them:
- **A. Prior art (disclosure):** does this document, anywhere in its text or figures, teach the idea's feature? This matters for **novelty** and is asked of every document, in force or not.
- **B. Claim overlap:** would a product built as the idea describes meet this claim limitation? This is an early **freedom-to-operate** signal. It is asked only of in-force documents, and only of independent claims, found with `ideacheck/claims.py`.

---

## A. Prior-art verdicts (per feature × document)

| Verdict | Use when | Don't use when |
|---|---|---|
| **disclosed** | The document teaches the feature **as the idea states it**, including every qualifier (number, arrangement, type, condition), in one passage or in clearly connected passages about the same embodiment. | Any qualifier is missing or different. Then it's `partial`. |
| **equivalent** | The document achieves the **same function and the same result** as the feature, but by a **different mechanism**, and every other qualifier matches. Example: 360° steering by the speed difference of two wheels instead of a dedicated steering motor. This is likely obviousness material. | Anything besides the mechanism also differs (number, arrangement, condition). Then it's `partial`. |
| **partial** | The document teaches a **related** function or purpose with a **stated, specific difference** in number, arrangement, condition or result, or teaches the feature only as an option in a different arrangement. | You can't name the difference in one sentence. Then decide between `disclosed` and `absent`. |
| **absent** | Nothing in the document teaches the feature or a functional equivalent. | You just didn't search the whole description. Search before you write `absent`. |

### Decision rules

1. **Qualifiers decide.** Split each feature into its qualifiers first. For example, E2 is "two wheels" + "traction drive" + "360° **steering drive**". `disclosed` needs all of them.
2. **Name the difference.** Every `equivalent` and `partial` has a `note` that starts with the difference: "Difference: …". For `equivalent`, the difference must be the mechanism only.
3. **One embodiment for `disclosed`.** If the qualifiers are spread over different embodiments that the document does not combine, the verdict is `partial`. Note "combination of embodiments".
4. **Options count, if stated.** "may be aligned along a diagonal" is a teaching. Classify it by rules 1–3 like any other passage.
5. **Claims, description and abstract all count for disclosure.** For drawings, use the description's text about the figure. Never infer from a figure you can't read.
6. **Translations:** the quote is verbatim from the (machine) translation. If the verdict hinges on one translated word (e.g. "steering" vs "swivel"), set `translation_sensitive: true`. Those findings get the original-language check.
7. **Evidence:** every `disclosed`, `equivalent` and `partial` verdict has a verbatim quote of 8–40 words, which is checked by `verify_quotes.py`. A finding whose quote fails becomes `unverified` and is not used.
8. **Confidence:** add `confidence: high | medium | low`. `low` means a reasonable expert could pick a different verdict. These go to the second-opinion check, **and they are shown in the report right away**, marked "low confidence, not yet double-checked". Hiding a possible match costs more than showing a noisy one.

### Worked examples (idea 01)

| Document | Feature | Verdict | Why (the quote is verified) |
|---|---|---|---|
| US-12564527-B2 | E3: active wheels diagonal, other two free casters | **disclosed** | Claim 21: "…single-wheel casters being coupled to the frame at first and second coupling regions that are disposed along a first diagonal of the imaginary rectangle, and the first and second dual-wheel motorized casters…". Every qualifier is present: diagonal, the other two are casters. |
| US-12564527-B2 | E2: two wheels with traction + 360° steering drive | **equivalent** | Difference (mechanism only): steering by **differential speed of two wheels** in one caster, not a dedicated steering drive ("motors may be operable to rotate the first and second wheels in opposite directions…"). Two active wheels, traction drive and 360° steering all match. |
| JP-6837910-B2 | E2 | **disclosed** | "Of the four casters, two are active casters 5 having drive wheels 4 … and the remaining two are driven casters 6…", plus a separate steering actuator and drive actuator per active caster. All qualifiers are present. |
| JP-7853860-B2 | E2 | **partial** | Difference: two of four wheels are active, but they are **omnidirectional drive-disc wheels with no steering**. The qualifier "360° steering" itself is absent, not just realized differently, so this is not `equivalent`. |
| JP-7570286-B2 | E3 | **partial** | "…may be aligned along a diagonal direction…" teaches a diagonal option (rule 4). Difference: the two driven wheels are **extra wheels in a central unit**, not two of the four corner wheels. |
| EP-2897566-B1 | E5: force → translation-only vector | **partial** | Difference: purely translational **only below a threshold speed**, and turning is added above it ("…purely translational motion … if the speed sensor(s) indicates … under a threshold speed"). |
| JP-2008137631-A | E5 | **partial** | Difference: the command comes from **lever tilt, not measured handle force** ("determines a traveling direction by tilting an operation lever…"). |
| JP-6837910-B2 | E4: handlebar / joystick / handle sensors | **absent** | The user interface isn't described anywhere in the document. |

---

## B. Claim-overlap verdicts (per limitation of an independent claim)

| Verdict | Use when |
|---|---|
| **yes** | A product built as the idea describes would **clearly** meet the limitation. Quote the limitation verbatim from the claim. |
| **no** | The idea, as described, **contradicts** the limitation. Example: the claim requires omnidirectional wheels and the idea uses steer-and-drive wheels. |
| **unclear** | The idea **doesn't specify** this detail, so the outcome depends on the product design. Say which design choice decides it. |

Rules:
1. **Read limitations literally.** "a wheel" is open-ended: one or more wheels meets it. "a plurality of user inputs" needs at least two inputs.
2. **A claim is `all_met` only if every limitation is `yes`.** One `no` breaks it, and so does one `unclear`. Then report it as "depends on: …".
3. **Design-around note:** for each `unclear` and each narrow `no`, write the product choice that keeps the claim from being met. Example, from US-8756726-B2: "a single continuous force-vector input, with no separate direction buttons, avoids the 'plurality of user inputs' limitation".
4. **Check dependent claims only when the independent claim is `all_met`**, or when the user asks. Dependent claims can't be infringed without their independent claim.
5. **Family scope:** a verdict holds for that publication only. Family members in other countries are separate claims (PLAN.md §9.1 F).

---

## Output fields (added to the Phase 0 format)

```json
{"verdict": "disclosed|equivalent|partial|absent", "quote": "...", "location": "claim 21 | description | abstract",
 "note": "Difference: ...", "confidence": "high|medium|low", "translation_sensitive": false}
```

## Decisions log

- 2026-10-02, Q1: "same function, different mechanism" gets its own verdict, **`equivalent`** (option B).
- 2026-10-02, Q2: low-confidence findings **are shown** in the report, marked, before the second-opinion check (option A).
