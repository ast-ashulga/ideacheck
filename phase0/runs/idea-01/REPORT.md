# Idea 01: power-assisted cart, two diagonal steer-and-drive wheels + two casters. Prior-art and claim-overlap report

_Phase 0 manual run, 2026-10-01. **Confidential.** This is a research aid, not a legal opinion on patentability or freedom to operate. Have a registered patent attorney review it before you make any decision._

## 1. Bottom line

- **The idea as currently described is very likely not new.** Hill-Rom's **US-12564527-B2** (priority 2022-03-07, in force until about 2044) discloses almost every feature:
  - four casters, with **two motorized 360° steer-and-drive casters on one diagonal** and **two free-swivel casters on the other** (its claim 21, FIG. 23);
  - **load cells in the push handles**;
  - handle forces summed into a **speed-and-direction command vector**;
  - closed-loop control using **accelerations, yaw rate and wheel speeds**;
  - a separate swivel angle and drive for each caster, including a **no-yaw (translation-only) mode**.
- **The remaining differences are small and already known elsewhere:**
  1. Each Hill-Rom caster steers by the **speed difference between its two wheels**. The idea uses a **dedicated steering drive** (a swerve module). Wheel modules with a dedicated steering motor are known from **THK JP-6837910-B2** (two active casters with motor-driven 360° steering plus two free casters) and **Stryker EP-2897566-B1** (motor-steered wheels with handle force sensing). Mitsuba **JP-2008137631-A** also describes older art with "four tires, which are a pair of traveling wheels (drive wheels) and a pair of idle wheels, and are arranged at diagonal positions", where "the driving wheel can be steered by the steering motor".
     Hill-Rom itself also says the teaching works with "motorized casters, either dual-wheel or single-wheel".
  2. In Hill-Rom, translation-only is a selectable mode and the default yaws. In the idea it is the only mode. That's a design choice, not a technical contribution.
  3. Applying it to retail and warehouse carts: Hill-Rom states its teachings "are applicable to all types of patient support apparatuses as well as other maneuverable apparatuses having casters", and Mitsuba is already a factory/warehouse cart.
- **Implication:** a patent claim on the idea as written would likely be refused as anticipated by, or obvious over, Hill-Rom '527 combined with THK, Stryker or the Mitsuba background. Any patentable contribution would have to come from **a more specific technical solution not found here**, for example:
  - a particular way of using instantaneous speed or acceleration in the force-to-vector mapping;
  - a specific handle sensor design;
  - obstacle or slope handling;
  - a mechanical layout of the swerve modules.
- **Freedom-to-operate signal (the claims, not the disclosure):** none of the in-force independent claims we checked is fully met by the idea **as described**. Three have narrow margins that a product design must respect (§4).

## 2. Feature matrix (13 documents compared in full; every ● and ◐ backed by a verified verbatim quote)

Features:
- E1: four-wheel base for heavy or delicate loads.
- E2: two active wheels, each with traction drive and 360° steering.
- E3: the active wheels on a diagonal, the other two free-swivel casters.
- E4: handlebar, joystick or handle sensors.
- E5: handle force → translation vector using speed or acceleration.
- E6: vector → per-wheel steering angle and drive.

Key: ● disclosed · ◐ partly · ○ not found.

| # | Document | Owner, priority, status | E1 | E2 | E3 | E4 | E5 | E6 | Closest gap to the idea |
|---|---|---|---|---|---|---|---|---|---|
| 1 | **US-12564527-B2** | Hill-Rom, 2022, **active** | ● | ◐ | ● | ● | ● | ● | Steering by differential dual-wheel caster, no dedicated steering motor |
| 2 | **JP-2008137631-A** | Mitsuba, 2006, withdrawn | ● | ◐ | ● | ● | ◐ | ◐ | Differential steering. Lever input, not handle force. No speed/acceleration term |
| 3 | **EP-2897566-B1** | Stryker, 2012, **active** | ● | ◐ | ◐ | ● | ◐ | ● | Two steer-and-drive wheels side by side plus 4 casters (6 wheels). Rotates above a speed threshold |
| 4 | US-2019183707-A1 | Info Solution, 2016, abandoned | ◐ | ◐ | ◐ | ● | ◐ | ● | True swerve wheels, but a separate 3-wheel mover hitched to a bed. Joystick input |
| 5 | JP-7853860-B2 | Honda, 2021, **active** | ● | ◐ | ◐ | ● | ◐ | ◐ | Rear omni wheels side by side, no steering. Handle-force translation is otherwise close |
| 6 | JP-2023019525-A | Honda, 2021, **active** | ● | ◐ | ◐ | ● | ◐ | ◐ | Same cart. Claim 9: force → target velocity vector |
| 7 | JP-2023144611-A | Honda, 2022, **active** | ● | ◐ | ◐ | ● | ◐ | ◐ | Same cart, plus yaw from the handle's twisting moment |
| 8 | DE-202004010854-U1 | Expresso, 2004, expired | ● | ◐ | ◐ | ● | ◐ | ◐ | Two fixed rear drive wheels on one axle, steering by speed difference |
| 9 | DE-102004033572-A1 | Expresso, 2004, withdrawn | ● | ◐ | ◐ | ● | ◐ | ◐ | Same as #8 |
| 10 | JP-7570286-B2 | JTEKT, 2021, **active** | ● | ◐ | ◐ | ◐ | ◐ | ◐ | Mecanum assist unit under a bed. Mentions a diagonal wheel placement as an option |
| 11 | JP-6837910-B2 | THK, 2017, **active** | ◐ | ● | ◐ | ○ | ○ | ◐ | **Real steer-and-drive active casters** (2 active + 2 free), but side by side and with no handle force |
| 12 | US-8756726-B2 | Hill-Rom, 2006, **active** | ◐ | ◐ | ◐ | ● | ◐ | ◐ | One central drive wheel that swivels 90°. Lateral mode chosen with buttons |
| 13 | JP-2014046890-A | Araki, 2012, pending | ◐ | ○ | ◐ | ● | ◐ | ◐ | Unsteered omni wheels plus four free casters. 3-axis handle load cell |

Every feature is at least partly disclosed by several documents. **E2 + E3 + E4 + E5 + E6 together** appear in #1, with only the steering mechanism of E2 differing.

## 3. Closest-art detail (verified quotes)

**US-12564527-B2 (Hill-Rom):**
- "…supported on an underlying floor by four casters, two of which are freely swivelable, single-wheel non-motorized casters **24** and two of which are dual-wheel motorized casters **30**".
- Claim 21: "…single-wheel casters being coupled to the frame at first and second coupling regions that are disposed along a first diagonal of the imaginary rectangle…".
- "…load cells … are coupled to push handles **64**…".
- "The power drive circuitry processes the load cell signals from the two push handles **64**, such as by summing the forces and/or using trigonometric functions to determine a speed and direction of a single, virtual input command **200**."

**JP-2008137631-A (Mitsuba):**
- "The free casters 23 and 24 are disposed on the other diagonal line passing through the remaining two corners of the vehicle body 2 and the vehicle body center of gravity C1".
- The background cites a mobile vehicle with "four tires, which are a pair of traveling wheels (drive wheels) and a pair of idle wheels, and are arranged at diagonal positions", and says "the driving wheel can be steered by the steering motor" (Japanese Utility Model Publication No. 6-25224; not yet retrieved, see §6).

## 4. Claim overlap for in-force patents (independent claims only; no claim is fully met)

Claim dependency was checked by hand: US-12564527-B2 claim 21 (the diagonal layout) depends on claim 1, so it can't be infringed without claim 1. The other listed claim pairs are independent.

| Patent (until) | Claim | yes / no / unclear | Margin. What a product must avoid |
|---|---|---|---|
| **US-8756726-B2** Hill-Rom (≈2028) | 1, 21 | 7/0/1, 6/0/1 | **Narrow.** Everything is met except the requirement for *separate, spaced-apart user inputs* for lengthwise versus other-direction propulsion. A single continuous force vector avoids it. Separate forward and sideways controls would not. |
| **EP-2897566-B1** Stryker (≈2032, EP states) | 1 | 6/1/1 | **Narrow.** For a bed, all structural limitations are met. The only "no" is using the **moment of the push force** to amplify turning. If the product ever turns in response to an off-centre push, claim 1 likely reads on it, so keep it strictly translation-only. Claim 13 (method): 1/1/1. |
| **US-12564527-B2** Hill-Rom (≈2044) | 1 | 2/0/3 | Requires **dual-wheel differential motorized casters** and a joystick that swivels the casters in a dead-band before driving. Single-wheel modules with a dedicated steering motor, controlled by handle force, stay outside claim 1. |
| JP-7853860-B2 / JP-2023019525-A / JP-2023144611-A Honda (≈2041–42) | 1 / 1, 9 / 1 | 4/2/2 · 6/2/2 · 3/6/1 | Each requires **omnidirectional wheels**, so steer-and-drive wheels avoid them. JP-2023019525-A claim 9 (force → target velocity vector) is the closest: it fails only on the omni-wheel and drive-unit wording. |
| JP-6837910-B2 THK (≈2037) | 1 | 4/0/5 | Requires a caster offset, a steering actuator and drive motor fixed to the body side, gear transmission through the steering axis, and mirrored modules. An in-wheel motor or a zero-offset module avoids it. |
| JP-7570286-B2 JTEKT (≈2041) | 1 | 2/5/0 | Requires Mecanum wheels and strain-nulling control. Avoided. |
| JP-2014046890-A Araki (pending) | 1, 2 | 1/6/1 | Requires omni wheels. Avoided. |

**Caveats:**
- These are single publications. **Family members in other countries may have different claims.** The Hill-Rom and Stryker families in particular should be checked in US, EP, CN and JP before any product decision.
- "unclear" means the idea doesn't specify that detail yet. The product design determines the answer.

## 5. What would make the idea stronger

1. **Find the real technical gap.** Candidate areas not seen in the 13 documents:
   - How the *instantaneous* speed and acceleration shape the force-to-vector mapping, e.g. inertia compensation for heavy loads, or deliberately gentle limits for beds.
   - How the two diagonal modules are coordinated so a 4-point base with two passive casters tracks a pure translation without caster flutter.
   - Handling caster re-orientation transients when the direction reverses.
   - Obstacle and slope behaviour.
   - Each needs its own search, because Panasonic WO-2012063476-A1 (target speed from force plus measured speed) and Stryker already touch speed-dependent behaviour.
2. **Design-around constraints, if you build without licensing:**
   - single-wheel steer-and-drive modules (not dual-wheel differential casters);
   - one continuous force-vector input (no separate direction buttons);
   - strictly no yaw response to off-centre pushes, at least for EP markets until about 2032.

## 6. Limits of this run

- Coverage:
  - The searches used 10 Google Patents queries and a local extract of hand-cart and bed classes (B62B, A61G7, A61G1), with about 100 candidates screened and 13 read in full.
  - The extract **missed omnidirectional-vehicle and wheel classes**, where Mitsuba, Araki and THK sit. There may be more close art in B60K7, B60B19, B62D7 or B66F (AGVs and swerve platforms).
  - Applications filed after about April 2025 aren't published yet.
- Not retrieved: the Japanese utility model 6-25224 that Mitsuba cites. Two number forms on Google Patents (JPH0625224U, JPH0625224Y2) gave unrelated documents, so it needs an EPO/J-PlatPat lookup.
- Analysis: done by LLM agents with programmatic quote checking (124 positive findings, 0 failed). The verdicts are judgements. Read the quoted passages in `compare/*.json` before relying on them.

## Files
- `shortlist.md`: top-20 ranking. `compare/<PUB>.json`: per-document verdicts. `compare/verified.json`: the same after quote checking.
- `full/<PUB>.json`: full texts. `candidates.json`, `expansion.json`, `details*.json`: the retrieval trail.
