# control-01 method (blind run)

**Caveat: the ranking uses titles and metadata only.** Detail fetching was blocked by Google Patents 503 rate limiting, so no abstracts or claims were read. It is based on titles, CPC codes, assignees, dates, which query hit each patent, and local embedding/"similar" expansion.

## Queries (queries.json)
- R1 obstacle AND (repulsive force|virtual force|repulsion), CPC B62B5/0069: 45 hits
- R2 obstacle AND distance AND "force sensor" AND handle, CPC B62B5/0026: 100 of 280
- R3 "virtual repulsive force" AND (cart|trolley|carriage), no CPC: 46 of 50
- R4 "repulsive force" AND obstacle AND operating force AND assist, CPC B62B: 14
- R5 ("potential field"|"virtual force") AND obstacle AND "power assist" AND handle: 100 of 2062 (noisy, mostly robotics/surgery)
- R6 obstacle AND (virtual|repulsive force) AND (walker|wheelchair) AND "force sensor": 100 of 716 (noisy)
- L1 B62B5/0069 + "obstacle" in title: 6. L2 title repuls/virtual force/potential field: 0. L3 B62B5/0069/0026/0073 + avoid/collision in title: 4. L4 B62B5/0069 co-classified G05D1/02*, G01S*, G05D1/6*: 424
- 461 candidate families after the merge

## Expansion
- Embedding k-NN (top 25, cosine on embedding_v1) plus "similar" from 10 seeds (the Panasonic, Toshiba Tec and collision-cart families). Added JP-2008296900-A, US-8672081-B2, Funai handcarts and others. Many "similar" targets are not in the extract.
- A final local title search (B62B5/A61G + obstacle/collision/avoid/repuls/bump): 12 rows, nothing new of note.

## Problems
- My first local SQL had a DuckDB unnest-alias bug and crashed retrieve.py after the remote phase. I fixed the SQL and re-ran only the local part plus the merge (work/merge_local.py), so there were no extra remote calls.
- Six seeds have empty embeddings (length 0), so they were filtered out.
- fetch_details: every request got 503 or timed out, from 20:31 for over 40 min (the first try, a retry after 15 min, then 10-min probes). The coordinator told me to stop, and details.json was never populated. The 40 planned ids are in work/ids.txt.

## Timing (MSK, 2026-10-01)
- Setup and query design: 20:29. Remote retrieve: 20:29-20:30 (36 s). Local and expansion: about 2 min.
- Fetch attempts: 20:31-21:15, all failed. Final metadata ranking: about 21:20.

## Rank basis
- The Panasonic "electric vehicle" families (2009-2011) and Toshiba Tec "power assist vehicle" (2005) rank top because they hit the exact "virtual repulsive force" / "repulsive force + operating force + assist" queries inside the B62B5/0069/0073 power-assist-control classes. They are the likeliest disclosures of C3-C5. Unverified.
