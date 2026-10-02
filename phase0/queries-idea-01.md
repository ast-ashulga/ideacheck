# Idea 01: search queries (step 7a, waiting for user approval)

**Sent to Google Patents** (`patents.google.com/xhr/query`): only the groups in the "Query" column below. Each bracketed group becomes one `q=` term, and the terms are ANDed. Inside a group, `OR` means any of the alternatives.
**Never sent:** the idea text, the feature list, application contexts, and anything about who you are.

**Remaining risk:** Google sees each query on its own and could link them (same IP, same session) into a rough picture: "steerable drive wheels + diagonal + casters + handle force". Any patent search reveals that much, and it is the trade-off you accepted ("keywords only").

## Remote queries (Google Patents, worldwide, all dates, 100 results each)

| # | Targets | Query (AND of groups) | Classification filter |
|---|---|---|---|
| G1 | E2 + E3 core layout | `(diagonal OR diagonally OR "opposite corners")` · `("drive wheel" OR "driven wheel" OR "drive unit")` · `(steerable OR steering OR swivel)` · `(caster OR castor)` | — |
| G2 | E5 → E6 (handle force → steered drive) | `("force sensor" OR "load cell" OR "strain gauge" OR "force sensing")` · `handle` · `("steering motor" OR "swivel motor" OR "turning motor" OR steerable)` · `("drive motor" OR "traction motor")` | — |
| G3 | Omnidirectional power assist | `(omnidirectional OR holonomic OR "any direction")` · `("power assist" OR "power-assisted" OR "assist force")` · `(cart OR trolley OR bed OR stretcher)` | — |
| G4 | Active or powered casters with handle input | `("active caster" OR "powered caster" OR "driven caster" OR "motorized caster" OR "steerable caster")` · `(handle OR "operating force")` | — |
| G5 | Two active wheels and two casters | `("two drive wheels" OR "pair of drive wheels" OR "two steerable wheels")` · `("two casters" OR "two castors" OR "free casters")` | — |
| G6 | Swerve modules placed diagonally (also catches robots and AGVs) | `(swerve OR "steer and drive" OR "drive and steer" OR "independently steerable")` · `(diagonal OR diagonally)` | — |
| G7 | Force-measuring hand carts with steering | `(steer OR steering OR swivel)` · `(direction OR vector)` | `B62B5/0073` |
| G8 | Bed movers with handle sensing | `("force sensor" OR "load cell" OR handle)` · `(steer OR swivel OR omnidirectional)` | `A61G7/08` |
| G9 | E5 detail: force → vector with speed and acceleration | `("operating force" OR "handle force" OR "push force")` · `(vector OR direction)` · `(velocity OR acceleration)` · `(assist OR "target velocity")` | `B62B5/0026` |
| G10 | Manually guided mode on AGVs and mobile robots | `("manual mode" OR "manually guided" OR "hand guided")` · `("force sensor" OR "force sensing")` · `handle` · `(omnidirectional OR swerve OR "steerable drive")` | — |

Throttling: the client rate-limits itself, and the queries run one after another with pauses.

## Local queries (DuckDB extract, nothing leaves the machine)

| # | What |
|---|---|
| L1 | Title keywords: (diagonal OR caster OR castor OR steer* OR swivel OR omnidirectional) AND (assist* OR drive OR motor OR power*) within B62B and A61G |
| L2 | Classification co-occurrence: `B62B5/0073` (force measuring) AND `B62B3/001` or `B62B2301/*` (steering and wheel arrangement) |
| L3 | Classification co-occurrence: `A61G7/08` AND `A61G2203/3*` (sensor means) |
| L4 | Expansion: `embedding_v1` k-NN (top 30) and `similar[]` from the 10 best seeds found by G1–G10 and L1–L3 |
