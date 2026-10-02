# Idea vs. Google Patents: tool selection and build plan

_Researched 2026-10-01. Constraints you set: only the LLM API (Claude) sees the raw idea text, data comes from BigQuery plus free services with no paid APIs, worldwide coverage, and the interface is to be decided (options compared in §4)._

---

## 1. Bottom line

No existing tool does your whole workflow (idea → find similar patents → **map where they overlap with your idea**). The retrieval and data-access parts are well covered. The part that compares your idea with each patent's claims is not. Two existing tools come closest:

- **PQAI** takes a plain-language idea and returns similar prior art. However, its API needs a paid PQAI+ subscription (a free token is available only for academic use), it covers **US patents only**, and the idea text would go to their cloud. That fails all three of your constraints.
- **Claude-Patent-Creator** has a `prior-art-searcher` agent. It is built for drafting US applications and searches BigQuery by keyword and CPC. It produces a patentability verdict, not an element-by-element overlap matrix.

**Recommendation:** combine two existing data layers and build one thin custom layer on top.

| Layer | What to use | Build or reuse |
|---|---|---|
| Data access (Google Patents, EPO, USPTO, CPC) | **`patent-client-agents`** (Apache-2.0), used as a local Python library or stdio MCP server | Reuse |
| Semantic expansion and metadata (CPC, family, citations) | **BigQuery `patents-public-data`** (`patents.publications` + `google_patents_research.publications`), queried once into a **local DuckDB/Parquet extract** | Reuse |
| Idea parsing, query generation, ranking, **intersection analysis**, report | Your own `ideacheck` package (Python + Claude API) | **Build** (this is the gap) |

---

## 2. What the three lists contain

| Repo | What's in it | Useful for you |
|---|---|---|
| parkerhancock/awesome-patents | A short list of official USPTO and court resources, plus `patent_client` and the BigQuery dataset. The international section is still TODO. | Only the BigQuery pointer and `patent_client`, which is now archived and has a successor. |
| asobl/awesome-patent-tools | The broadest open-source list (873 repos surveyed, Apr 2026), with sections for APIs, EPO, bulk ETL, AI/NLP, and MCP/agents, plus a "Gaps" section. | The main source for the decisions in §3. Its gaps include "multi-office unified search" and "no-code interfaces", which overlap with what you're building. |
| ishandutta2007/Awesome-Patent-Analytics | Mostly paid SaaS (PatSnap, Derwent, Orbit, and others) plus about 10 open-source projects. | PQAI, Google public data, Lens.org. The SaaS entries are excluded by your budget. |

### Facts I checked that change the picture

- **`parkerhancock/patent_client` was archived in April 2026.** Its successor is **`parkerhancock/patent-client-agents`**, which was pushed today, is Apache-2.0, and has 136+ tools. It includes a Google Patents client (search, full text, claims, citations, families, PDFs), EPO OPS, USPTO ODP, a CPC lookup, and a bundled `ip_research` skill.
  - Its Google Patents client uses the **unofficial** `patents.google.com/xhr/query` endpoint and the patent HTML pages. It has built-in rate limiting and a cooldown when Google returns 503. It works without a key, but it can break and is not covered by any Google terms of service.
  - `search_patents()` takes **keywords and filters only** (keywords, CPC, assignee, country, dates, status). It has no semantic or "similar to this text" search.
  - The project offers a hosted demo at `mcp.patentclient.com`, which explicitly says not to send confidential material. **Don't use the hosted demo.** Run it locally.
- **The `google/patents-public-data` repo is archived (2024), but the BigQuery dataset is still live.** `google_patents_research.publications` contains:
  - `similar[]`: Google's precomputed list of semantically similar documents for each publication.
  - `top_terms`.
  - `embedding_v1`: Google's patent embedding. The repo's `examples/patent_set_expansion.ipynb` notebook uses it for nearest-neighbour expansion.
  - **Caveat:** you can't embed *your own idea text* into `embedding_v1` space. It only works by starting from seed patents.
- **The PatentsView API was shut down on 2026-03-20**, and its data moved to USPTO ODP bulk datasets. Every tool that depends on that API, including the R `patentsview` package and the citation-graph tools, is effectively dead for live queries.
- `riemannzeta/patent_mcp_server` is active and MIT-licensed. It covers **USPTO only** (PPUBS full text, ODP, PTAB). It's useful as a backup for US full text but isn't needed if you use `patent-client-agents`.

---

## 3. Decision per tool

| Tool | Verdict | Why |
|---|---|---|
| **patent-client-agents** | ✅ **Use** (core data layer) | Worldwide Google Patents access, EPO OPS families and legal status, USPTO, CPC. Active, permissive license, works as both a library and an MCP server. |
| **BigQuery patents-public-data** | ✅ **Use** (official semantic and metadata layer, through a local extract) | Official and stable. Has CPC, family_id, claims and abstracts in many languages, citations, `similar`, and `embedding_v1`. The free tier gives 1 TB of queries a month, but large columns use it up quickly (see §7), so don't query it live for each idea. |
| google/patents-public-data (repo) | 📖 Reference | Archived, but its notebooks (`patent_set_expansion`, landscaping) show how to do embedding and `similar` expansion in SQL. |
| Claude-Patent-Creator | 📖 Reference / optional | Borrow prompt design from its `prior-art-searcher` agent and its BigQuery tool layout. It's built around drafting US applications, which isn't what you need. |
| patent_mcp_server | ⚪ Optional | Only needed if Google Patents full text fails for US documents. |
| python-epo-ops-client / epo-cli | ⚪ Covered | `patent-client-agents` already wraps EPO OPS. EPO OPS needs a free key. |
| PQAI (hosted API) | ❌ Skip | Paid or academic-only token, US-only, and the idea would be sent to their cloud. Self-hosting is possible under its MIT license but heavy: you'd need to build their index. Revisit later only if semantic recall turns out poor. |
| Lens.org | ⚪ Later, maybe | Free tier with an approved token. It isn't Google data, but it could add scholarly non-patent literature. |
| patzilla (AGPL), P2N-v3, PatentInspector | ❌ Skip | Research UIs and analytics toolkits. They're stale (2023–24) or AGPL, and none does idea-to-claim mapping. |
| patent_client, pypatent, PatentsView-based tools | ❌ Skip | Archived, or the upstream API is dead. |
| SaaS (PatSnap, Derwent, Orbit, IFI, Cipher…) | ❌ Skip | Outside your budget. |
| **LeonardHope/Claude-Skill-for-Patent-Landscape-Analysis** | 📖 Reuse parts + ⚪ optional add-on | See §3a. It shows who is filing in a technology area, not how your idea overlaps with specific patents. |
| **vserifoglu/bq-ai-patent-analyst** | 📖 Borrow the idea only | See §3b. A hackathon demo over 403 sample PDFs that depends on Gemini/Vertex. Its matching at the level of individual components is worth copying. |
| **LeonardHope/Google-Patents-Natural-Language-API-Search** | 📖 Reuse parts | See §3a. A cost-gated BigQuery client and SQL templates. Its "similar patents" query probably uses the wrong column name. |

### 3a. LeonardHope repos (reviewed 2026-10-01, at your request)

**Claude-Skill-for-Patent-Landscape-Analysis** (MIT, 12★, last pushed 2026-05-08, about 3k lines of Python)
- **What it does:** a Claude Code skill that takes a technology area, translates it into **CPC prefixes**, runs one BigQuery query that pulls metadata only, and writes a single self-contained interactive HTML report. The report shows top applicants, a world map, filing trends, CPC areas in plain English, notable patents, and a methodology section.
- **What it does not do:** it never reads claims or abstracts. In BigQuery mode it sets `abstract=""`. It has no idea input, no similarity ranking and no overlap analysis. It answers "who is filing in this area and how much", not "which patents overlap with my idea". So it **does not replace `ideacheck`**.
- **Worth borrowing:**
  - `data_fetcher_bigquery.py`: a query that selects metadata only, filters with `EXISTS(UNNEST(cpc))`, and caps the scan at 20 GB. It reports 5–40 GB per landscape, which is a real-world data point for §7.
  - `data_layer.py`: the canonical `PatentRecord` schema and family deduplication (`select_family_representatives`).
  - `provenance.py`: `Metric`/`ReportBundle` objects that store the patents behind every number. This is the same idea as the quote checking in `ideacheck`'s comparison step, and a good model for its report JSON.
  - `html_renderer.py` + `report.html.jinja`: the single-file, offline, interactive HTML report pattern. It's a strong model for the overlap-matrix report, and it may mean you can skip the web UI.
  - Google Patents URL normalization, which fixes the 10- vs 11-digit US application number mismatch.
  - `applicant_normalizer.py` and `cpc_plain_english.json` (250+ CPC classes in plain English).
- **Optional add-on:** run it on the CPC codes `ideacheck` picks for your idea to get a section on who is active in this area.

**Google-Patents-Natural-Language-API-Search** (Apache-2.0, 8★, last pushed 2026-04-07). The landscape skill requires it.
- A Claude skill with a BigQuery client that **dry-runs every query and refuses anything over 5 GB by default** (`BQ_MAX_BYTES`). It has search functions for claims, descriptions, keywords, assignees, international filings and CPC trends, plus a `research_search.find_similar_patents()`.
- **Issue I spotted in the code (not tested live):** `find_similar_patents` reads `UNNEST(similar_documents)`. Google's schema docs name the column `similar`. The code catches the error and falls back to something else, so the feature most useful to you probably doesn't work as written.
- **Its `cost-reference.md` gives approximate scan sizes:**
  - `patents.publications` is about 2.74 TB with 166M+ rows.
  - A title/abstract keyword search scans about **30 GB**, so about 33 queries use up 1 TB.
  - A full-text claims search scans about **131 GB**, so about 7–8 queries use up 1 TB.
  - Even a single lookup by publication number measured about 2.6 GB.
  - These figures support the plan's local-extract approach.
- Its `patentsview_search.py` uses the BigQuery copy of PatentsView. That copy may still work, but it is US-only and may stop updating now that the PatentsView API has shut down. It isn't needed here.
- **Verdict:** borrow the cost guard (`bigquery_client.py`) and the SQL templates in `references/query-patterns.md`. Don't depend on the skill as a whole.

### 3b. vserifoglu/bq-ai-patent-analyst (reviewed 2026-10-01)

- **What it is:** a winning entry from the Kaggle "BigQuery AI" hackathon (2025), with a Streamlit dashboard. 2★, last pushed 2025-10-26. It's licensed **CC-BY-4.0**, which is unusual for code and requires attribution if you reuse it.
- **Pipeline:**
  1. BigQuery Object Tables over **403 sample patent PDFs** in `gs://gcs-public-data--labeled-patents`.
  2. `ML.GENERATE_TEXT` with **Gemini 2.5 Flash** extracts metadata and analyses the drawings.
  3. `AI.GENERATE_TABLE` builds a **graph of each patent's technical components, their functions and how they relate**.
  4. **`gemini-embedding-001`** embeds each component and its function, and a SQL function computes a weighted average of the two vectors.
  5. BigQuery `VECTOR_SEARCH` finds the components closest to the user's query text.
- **Why you can't use it as is:**
  - It covers a fixed sample of about 400 PDFs, not Google Patents' full collection, and has no way to fetch more.
  - Every query sends the query text to **Gemini through Vertex AI**, which is paid and is a second LLM provider seeing your idea. That breaks your privacy and budget constraints.
  - It has no idea input, no claim parsing and no overlap verdicts.
  - It's demo-grade: SQL is built by string formatting with only basic escaping, and an LLM checks whether each query is technical.
- **The idea worth borrowing:** search and match at the level of **individual components (a component plus its function)**, not whole documents. This fits `ideacheck`, because your idea is already split into features E1..En. Proposed stage **5b** (below) applies it to the shortlist: Claude extracts each patent's components and functions from its claims and description, a local embedding model embeds them, and each idea feature is matched against the closest components. This gives a fast feature-by-component similarity heat map before the more expensive claim-by-claim comparison, and helps decide which patent/feature pairs go to the full comparison.

---

## 4. Interface options compared

| | A. Claude Code plugin (skill + MCP) | B. Standalone CLI | C. Web UI |
|---|---|---|---|
| Result quality | High. You can steer interactively ("ignore the medical ones, dig into claim 7"). | High and **reproducible**: the same idea gives the same pipeline every run. | Same as B, since it runs on the same engine. |
| Build effort | Lowest. Mostly prompts plus existing MCP servers. | Medium | Highest |
| Repeatable, batch, regression tests | Weak | Strong | Strong |
| Reviewing a 10×20 overlap matrix | Poor in the terminal (fine as an HTML file) | Report file | **Best**: sortable matrix, click a cell to see the quoted claim text |
| Privacy control | **Prompt-dependent.** Even with a local stdio MCP server, Claude writes the tool arguments, and those arguments go to patents.google.com and EPO. Only the prompts keep your idea text out of them. | **Enforced in code.** Only generated keyword and CPC queries leave the machine, and every outbound call is logged. | Same as B (localhost) |

**Recommendation:** don't choose one. Build **one core Python library** (`ideacheck`) and put three thin front ends on it:

1. **CLI first.** It's the engine you can test.
2. **A local MCP server and skill that wrap the same functions.** This gives you option A almost for free.
3. **A local web UI for viewing and iterating on reports** (FastAPI + a small frontend, or Streamlit for speed).

**Phase 0 below is a no-code trial of option A.** It shows how good a pure Claude-plus-MCP approach is before you write any code.

---

## 5. Target pipeline

```
idea.md
  │
  ▼  [1] Idea decomposition (Claude)  — raw text only goes to the LLM API
  │      → problem, elements E1..En, key terms + synonyms (multi-lingual), candidate CPC codes
  │        (CPC codes checked against patent-client-agents' CPC tool)
  ▼  [2] Query generation (Claude)    — only short keyword/CPC queries leave this point
  │      → 5–15 queries: narrow, broad, per-element, CPC-restricted
  ▼  [3] Multi-source retrieval (union)
  │      a. Google Patents xhr search      (patent-client-agents, worldwide, rate-limited)
  │      b. Local DuckDB extract (CPC-filtered subset of BigQuery: title, abstract, CPC, family_id,
  │         dates, `similar[]`, `embedding_v1`): keyword + CPC search, offline and free
  │      c. Semantic expansion from top seeds: `similar[]` + `embedding_v1` k-NN on the local extract
  │      d. Citation expansion (forward/backward) of top seeds
  ▼  [4] Dedupe by family_id → rank
  │      local embedding model (e.g. bge-base / PatentSBERTa via sentence-transformers)
  │      idea vs. title+abstract+first claim → top 50 → Claude rerank → top 15–25
  ▼  [5] Fetch full records for the shortlist via patent-client-agents (Google Patents /en pages;
  │      NOT BigQuery — referencing `claims_localized` bills the whole column)
  │      independent claims, abstract, CPC, priority date, assignee, legal status, family
  ▼  [5b] (optional) component-level prefilter, inspired by bq-ai-patent-analyst:
  │      extract each shortlisted patent's components and their functions (Claude) → embed locally →
  │      feature × component similarity → send only the strongest pairs to [6]
  ▼  [6] INTERSECTION ENGINE  ← the part you build
  │      • split each independent claim into limitations (L1..Lm)
  │      • for each (idea element Ei × patent): disclosed / partial / absent
  │        + **verbatim quote** + claim/paragraph reference
  │      • verify each quote really appears in the source text (string match) and
  │        reject any finding whose quote can't be found
  │      • roll-ups: per-element "closest art", uncovered elements (white space),
  │        closest 2-reference combination (obviousness hint),
  │        "in-force patent whose every limitation your idea meets" warning
  ▼  [7] Report: report.json (schema) + report.md + report.html (matrix)
```

Notes:
- Retrieval quality comes mostly from steps 2 and 3c. Generating many keyword angles makes up for the lack of free semantic search over raw text. Seed-based `similar` and embedding expansion then adds the semantic recall.
- Steps 4 and 6 run on **independent claims, not abstracts**. Claims define what a patent actually covers.
- Cache every remote fetch on disk (SQLite or Parquet). This keeps you within Google rate limits and the BigQuery quota, and makes reruns cheap.
- Optional sources (EPO OPS legal status, USPTO PPUBS backup, Lens) go behind config flags that are **off by default**.

---

## 6. Phased plan

**Phase 0: trial with existing tools, no code (about half a day)**
1. Install `patent-client-agents` locally as a stdio MCP server or Claude Code plugin. Don't use the hosted demo.
2. Create a GCP project, enable BigQuery, and set a 1 TB monthly quota cap. **Dry-run each planned query type** (keyword over `abstract_localized`, `similar[]` lookup by publication number, `embedding_v1` scan, CPC-subset extract) and write down the bytes each would bill. Also check the tables' clustering fields and the latest `publication_date` in `google_patents_research.publications` to see how far behind it is. If the per-query costs are too high, make Google Patents xhr the main keyword source and use BigQuery only for the one-time extract.
3. In Claude Code, run the whole pipeline in §5 by hand on a **non-confidential idea**. A good choice is the summary of an existing granted patent, which also gives you a known correct answer to check recall against. Do this using the `ip_research` skill and your own prompts.
4. Write down what worked, where recall was weak, and how long it took. This decides how much of Phase 1–2 is worth automating.

**Phase 1: core library and CLI (2–4 days)**
- `ideacheck` package with stages 1–5 as separate, cacheable steps. Each step writes JSON.
- Reuse LeonardHope's patterns: the cost-gated BigQuery client, the `PatentRecord` schema and family deduplication, and Google Patents URL normalization (MIT and Apache-2.0, so keep their attribution).
- Command: `ideacheck run idea.md --out reports/<slug>/`, with flags `--max-results`, `--since`, `--countries`.
- `ideacheck extract --cpc <codes>`: a one-time BigQuery export of only the needed columns into local Parquet/DuckDB. Dry-run it first and refuse to run if it exceeds the byte limit. Every idea after that is searched locally at no cost.

**Phase 2: intersection engine and report (3–5 days)**
- Claim limitation parser, element × limitation mapping via Claude with structured output, quote verification, roll-ups.
- JSON schema for the report, plus Markdown and HTML renderers. Model the HTML on LeonardHope's single-file offline report, with every overlap cell linking back to its verified quote, the same way his metrics link back to their patents.
- Optional: an "activity in this area" section produced by running the landscape skill on the idea's CPC codes.

**Phase 3: front ends (2–4 days)**
- Local MCP server and Claude Code skill wrapping `decompose / search / analyze / report`.
- Local web UI: paste or edit an idea, watch the stages run, browse the matrix, click through to claim text and the Google Patents link.

**Phase 4: evaluation (ongoing)**
- Build a test set from known patents: write each one's summary as an "idea" and check that the tool retrieves that patent or its family in the top k (recall@k).
- Track recall@20 and the rate of rejected (unverifiable) quotes as you change prompts and sources.

---

## 7. Risks and how to handle them

| Risk | How to handle it |
|---|---|
| The unofficial Google Patents endpoint breaks or gets blocked | Use BigQuery as the stable main source for bulk retrieval and keep xhr search as a supplement. Cache results and keep request rates low. |
| BigQuery costs | Approximate scan sizes from LeonardHope's `cost-reference.md`: a title/abstract keyword query ≈ 30 GB, a full-text claims query ≈ 131 GB, a single lookup by publication number ≈ 2.6 GB. On-demand billing charges for **every byte in each column a query references**, and a `WHERE` clause doesn't reduce that unless partition or cluster pruning applies. Fetching claims for 20 patents still scans all of `claims_localized`. A `LIKE` over abstracts or an `embedding_v1` k-NN scans that whole column every time. For scale, Google's 2018 snapshot documents `patents.publications` at about 900 GB and `google_patents_research.publications` at about 254 GB, and today's tables are larger. With 5–15 live queries per idea, 1 TB could run out after one or two ideas. Fix: do a one-time column-pruned, CPC-filtered extract to local DuckDB, fetch full text through patent-client-agents, dry-run before every BigQuery job, and set a hard project quota. |
| The LLM invents overlaps | Require a verbatim quote for every finding, check it programmatically, and drop anything that fails. |
| Research tables are stale (the repo is archived, so `similar` and `embedding_v1` may stop at some past date) | Check the latest date in Phase 0. Recent filings are the most dangerous prior art, so always include xhr keyword search sorted by newest and limited to recent dates. |
| `embedding_v1` can't embed your raw idea | Use it only to expand from seed patents. Use a local embedding model to score your idea against candidates. |
| Treating the output as legal advice | Label every report as a research aid. It is not a novelty or freedom-to-operate opinion. Have a patent attorney review anything you plan to file. |
| Leaking the idea | Only the Claude API sees the raw text. In the CLI, patent sources see only short generated queries, and every outbound request is logged. In the MCP/plugin mode this depends on the prompts, so use that mode for exploration, not for your most sensitive ideas. |

---

## 7a. Measured BigQuery costs (Phase 0, 2026-10-01)

These come from free dry runs (`scripts/phase0/dryrun_costs.sh`; full table in `phase0/dryrun_costs.md`). Neither table is clustered or partitioned (`patents.publications` is 3.17 TB, `research.publications` 0.52 TB, both modified 2026-09-23). **A query's cost is the sum of the columns and nested sub-fields it reads. The `WHERE` filter and the size of the classification-code subset make no difference.**

| Use | Scan | Decision |
|---|---|---|
| Lean index extract (ids, dates, `cpc.code`, English title, `assignee.name`) | **43 GB** | ✅ Run once with a broad set of classification codes |
| Plus `similar.publication_number` + `embedding_v1` (join) | **196 GB** | ✅ Run at most once a month, with the broadest code set you might need, because re-running costs the full amount again |
| Abstracts (`abstract_localized.text`) | 213 GB | ❌ Fetch abstracts for candidates from Google Patents instead |
| Claims (`claims_localized`) | 125 GB, even for a single patent | ❌ Never. Use patent-client-agents |
| Live `similar[]` lookup per seed | 64 GB | ❌ Never live. Read it from the extract |
| Live `embedding_v1` k-NN per seed | 91 GB | ❌ Never live. Run it locally on the extract |
| Live keyword search over title + abstract | 232 GB | ❌ Use Google Patents xhr search or the local extract |

Sandbox mode (billing off) gives 1 TB/month as a hard limit with no possible charges, and only 10 GB of storage, so the extract must go to local DuckDB, not to a BigQuery table.

## 8. Open questions for later
- Should the tool also search non-patent literature (papers)? Google Patents with `include_npl` or Lens.org could cover it.
- Should it watch for new filings that match a saved idea? The awesome-patent-tools Gaps section says no open-source tool does this, and your cached pipeline would make it easy to add.
