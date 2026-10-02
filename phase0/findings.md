# Phase 0 findings (running log)

## Steps 1–2: environment and data access (2026-10-01)
- Python 3.11.13, uv 0.8.12, gcloud 586. Application Default Credentials work for project `patent-landscape-ashulga`.
- `patent-client-agents` 0.29.0 runs as a local stdio MCP server with 136 tools. It needs `fastmcp<4`: the package declares no upper bound, and fastmcp 4.x removed `fastmcp.tools.tool`.
- Google Patents records include `structured_limitations` (claims already split into limitations), so stage 6 needs no claim parser of its own.
- `lookup_cpc` and `search_cpc` need an EPO OPS key. Workaround: check classification codes by searching with them and reading the codes on real hits.

## Step 3: GCP project
- Billing is not enabled, so the project is in BigQuery sandbox mode: 1 TB/month of queries as a hard limit, no charges possible, 10 GB of storage.
- September use: 175 GB over 8 jobs (the earlier landscape-skill trial).

## Step 4: costs
- See PLAN.md §7a and `phase0/dryrun_costs.md`. Tables are unclustered and unpartitioned, so cost is the sum of the columns and sub-fields read, and filters don't reduce it.

## Steps 5–6: extract and freshness
- Extract `scripts/phase0/extract.py`, with classification prefixes `B62B`, `A61G7/` and `A61G1/`.
  - Billed 197.1 GB. Downloaded 246,285 publications (117,264 families) in 183 s. Result is `data/extract.duckdb` (128 MB).
- The latest publication date is 2026-09-17, about two weeks behind real time.
- `embedding_v1`: 100% filled for every publication year, including September 2026.
- `similar[]`: about 99–100% filled up to April 2026, then 68% in May 2026 and **0% from June 2026 on**. Google's similar-document lists lag about 4–5 months behind publication. For the most recent publications, use `embedding_v1` k-NN and xhr keyword search, not `similar[]`.
- English titles: 79.4% of rows. The rest are untranslated non-English records, but they share a family with an English member, which family deduplication can use.
- Largest countries: US 58k, CN 49k, DE 23k, EP 21k, GB 14k, WO 12k, KR 12k, FR 10k, JP 8k.
- Control patent JP-4616127-B2 (family 37919331) is in the extract, with 25 similar documents and a 64-dimensional embedding.
- Remember that applications are published about 18 months after filing, so nothing filed after about April 2025 can be found in any public source.
- DuckDB gotcha: `similar` is a reserved word in DuckDB. Quote it as `"similar"`.

## Step 7b: retrieval for idea 01
- 10 approved Google Patents queries plus 3 local queries gave 1,068 candidate families.
- The 5 full-text queries with no classification filter (G1, G2, G5, G6, G10) were mostly noise: surgical robots, vehicle-to-vehicle communication, lidar. In Phase 1, always pair Google full-text queries with a classification filter or a narrow phrase.
- **Local title-keyword search (L1) found the closest art that the remote queries ranked low or missed:**
  - DE-202004010854-U1 (driven steerable rollers + push-bar force sensors).
  - US-2019183707-A1 (two motor-driven steering wheels for omnidirectional hospital-bed movement).
- Rate limit: after about 10 searches plus a few lookups, Google Patents returned 503 for about 40 minutes. A resumable fetch with a 30-second delay and saves after every record works. Budget about 30 s per record, or 1 hour for 100 records.
- Seed expansion (embedding k-NN + `similar[]`) found 157 more families. **3 of the 10 seeds were not in the extract** (JP-2008137631-A, JP-2014046890-A, JP-6837910-B2), because their classification codes are outside B62B/A61G (probably B60K/B60B/B62D). The extract scope needs omnidirectional and active-caster vehicle codes too.

## Steps 7c–7e: ranking, comparison and report for idea 01
- Ranking by Claude from title, abstract and claim 1 (option a) worked for about 100 candidates, about 1 reading pass.
- Deep comparison: 13 full texts (about 930k characters) split across 5 parallel agents, 2–3 documents each, about 2.5–4.5 minutes per agent.
  - **124 of 124 positive findings passed verbatim quote verification** (`scripts/phase0/verify_quotes.py`).
- **Google's claim data is unreliable for independence:** the structured data marks every claim as independent. My regex for dependent claims (`claim N` in the first 200 characters) is also fragile. In Phase 1, detect dependency from the claim's opening phrase in several languages, and test it.
- **The parallel agents shared one scratchpad and overwrote each other's helper scripts.** One agent ran another's script, which could have rewritten other output files. They didn't, as checked by publication number, timestamps and summaries. In Phase 1, give each agent its own working directory and allow it to write only its own output file.
- **Japanese utility-model numbers are ambiguous on Google Patents:** "JP UM Publication No. 6-25224" gave unrelated documents as JPH0625224U and JPH0625224Y2. A resolver is needed (EPO OPS `convert_epo_number` or J-PlatPat).
- Timings: Google fetch about 25–30 s per record when paced. The rate limit lasted about 40 min after a burst of about 10 searches plus lookups.
- **Result for idea 01:** the closest art is US-12564527-B2 (Hill-Rom). It discloses E1, E3, E4, E5 and E6 and part of E2 (differential dual-wheel casters, with single-wheel motorized casters also mentioned). The idea as written is likely not novel. No in-force independent claim is fully met. See `phase0/runs/idea-01/REPORT.md`.
- Process caveat: the same session that knew the idea also generated the queries and ranked the results. For the known-answer control, steps 7a–7c must be run **blind** by a fresh agent.

## Step 7f: blind known-answer control (PASS)
- Setup:
  - A fresh agent received only `phase0/control-01-input.md`, which has no answer, number, assignee or year. It was forbidden to read the answer file and idea-01's files, and wrote only into `phase0/runs/control-01/`.
  - Score with `scripts/phase0/score_control.py`.
- Retrieval: 6 remote queries plus 4 local queries gave 461 families.
  - **The answer family 37919331 was retrieved by 3 of the 6 queries independently** (ranks 32, 32 and 8).
  - The agent chose its own classification codes (B62B5/0069, B62B5/0026) and narrow phrases ("virtual repulsive force", "repulsive force" + obstacle + operating force + assist).
- Ranking: **the answer is at rank 3 of 20** (JP-2007055480-A, the published application in the same family as JP-4616127-B2).
  - Ranks 1, 2 and 4 are Panasonic "electric vehicle" patents (2009–2011) that also use a virtual repulsive force. They are plausible genuine near-matches, not noise.
- Limitation: the ranking used **titles and metadata only**. Google Patents returned 503 for every detail fetch for over an hour, from about 20:31. So this tests retrieval plus title-level triage, not abstract- or claim-level ranking.
- Rate limiting is now the main operational risk. It hit twice in one day, each time after about 10 searches plus a few lookups. Phase 1 needs a second source for detail text (an EPO OPS key, or USPTO PPUBS for US documents) and a persistent fetch cache.
