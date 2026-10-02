#!/usr/bin/env bash
# Phase 0, step 4: BigQuery dry runs. A dry run validates a query and reports the
# bytes it WOULD scan; it scans nothing and costs nothing.
# Usage: scripts/phase0/dryrun_costs.sh [gcp-project]   (prints a Markdown table)
set -euo pipefail
PROJECT="${1:-patent-landscape-ashulga}"
PUB='`patents-public-data.patents.publications`'
RES='`patents-public-data.google_patents_research.publications`'

dry() { # $1 = label, $2 = SQL
  local out bytes
  out=$(bq query --project_id "$PROJECT" --use_legacy_sql=false --dry_run "$2" 2>&1) || { echo "| $1 | ERROR: ${out//$'\n'/ } |"; return; }
  bytes=$(grep -oE '[0-9]+ bytes' <<<"$out" | grep -oE '[0-9]+')
  printf '| %s | %s |\n' "$1" "$(awk -v b="$bytes" 'BEGIN{printf "%.1f GB", b/1e9}')"
}

echo "### Per-column scan cost (SELECT <column> FROM table)"
echo "| Column | Scan |"; echo "|---|---|"
for c in publication_number family_id country_code kind_code publication_date filing_date priority_date \
         title_localized abstract_localized claims_localized description_localized \
         cpc ipc assignee_harmonized inventor_harmonized citation; do
  dry "patents.publications.$c" "SELECT $c FROM $PUB"
done
for c in publication_number title abstract cpc top_terms similar cited_by embedding_v1 url country; do
  dry "research.publications.$c" "SELECT $c FROM $RES"
done

echo; echo "### Planned query patterns"
echo "| Query | Scan |"; echo "|---|---|"
dry "Keyword search, English title+abstract (LIKE)" \
  "SELECT publication_number FROM $PUB p WHERE EXISTS(SELECT 1 FROM UNNEST(p.abstract_localized) a WHERE a.language='en' AND LOWER(a.text) LIKE '%heat sink%') OR EXISTS(SELECT 1 FROM UNNEST(p.title_localized) t WHERE LOWER(t.text) LIKE '%heat sink%')"
dry "Keyword search over claims (LIKE)" \
  "SELECT publication_number FROM $PUB p WHERE EXISTS(SELECT 1 FROM UNNEST(p.claims_localized) c WHERE LOWER(c.text) LIKE '%heat sink%')"
dry "similar[] lookup for one publication" \
  "SELECT s.publication_number FROM $RES r, UNNEST(r.similar) s WHERE r.publication_number='US-10123456-B2'"
dry "embedding_v1 k-NN from one seed (full scan)" \
  "WITH seed AS (SELECT embedding_v1 e FROM $RES WHERE publication_number='US-10123456-B2') SELECT r.publication_number, (SELECT SUM(x*y) FROM UNNEST(r.embedding_v1) x WITH OFFSET i JOIN UNNEST(seed.e) y WITH OFFSET j ON i=j) AS dot FROM $RES r, seed ORDER BY dot DESC LIMIT 50"
dry "Detail lookup for 25 publications incl. claims" \
  "SELECT publication_number, claims_localized FROM $PUB WHERE publication_number IN UNNEST(['US-10123456-B2'])"
dry "Extract A: metadata + abstract, one CPC prefix (H05K7/20)" \
  "SELECT p.publication_number, p.family_id, p.country_code, p.kind_code, p.publication_date, p.filing_date, p.priority_date, p.title_localized, p.abstract_localized, p.cpc, p.assignee_harmonized FROM $PUB p WHERE EXISTS(SELECT 1 FROM UNNEST(p.cpc) c WHERE c.code LIKE 'H05K7/20%')"
dry "Extract B: Extract A + research (similar, embedding_v1, top_terms)" \
  "SELECT p.publication_number, p.family_id, p.country_code, p.kind_code, p.publication_date, p.filing_date, p.priority_date, p.title_localized, p.abstract_localized, p.cpc, p.assignee_harmonized, r.similar, r.embedding_v1, r.top_terms FROM $PUB p JOIN $RES r USING (publication_number) WHERE EXISTS(SELECT 1 FROM UNNEST(p.cpc) c WHERE c.code LIKE 'H05K7/20%')"
dry "Extract C: Extract B + English claims" \
  "SELECT p.publication_number, p.family_id, p.country_code, p.kind_code, p.publication_date, p.filing_date, p.priority_date, p.title_localized, p.abstract_localized, p.claims_localized, p.cpc, p.assignee_harmonized, r.similar, r.embedding_v1, r.top_terms FROM $PUB p JOIN $RES r USING (publication_number) WHERE EXISTS(SELECT 1 FROM UNNEST(p.cpc) c WHERE c.code LIKE 'H05K7/20%')"
dry "Research-table-only extract (title, abstract, cpc, similar, embedding_v1, top_terms)" \
  "SELECT publication_number, title, abstract, cpc, similar, embedding_v1, top_terms, country FROM $RES r WHERE EXISTS(SELECT 1 FROM UNNEST(r.cpc) c WHERE c.code LIKE 'H05K7/20%')"

echo; echo "### Lean variants (read only the nested sub-fields needed)"
echo "| Query | Scan |"; echo "|---|---|"
dry "cpc.code only" "SELECT ARRAY(SELECT c.code FROM UNNEST(cpc) c) FROM $PUB"
dry "title_localized.text only" "SELECT ARRAY(SELECT t.text FROM UNNEST(title_localized) t) FROM $PUB"
dry "abstract_localized.text only" "SELECT ARRAY(SELECT a.text FROM UNNEST(abstract_localized) a) FROM $PUB"
dry "assignee_harmonized.name only" "SELECT ARRAY(SELECT a.name FROM UNNEST(assignee_harmonized) a) FROM $PUB"
dry "research similar.publication_number only" "SELECT ARRAY(SELECT s.publication_number FROM UNNEST(similar) s) FROM $RES"
dry "research cpc.code only" "SELECT ARRAY(SELECT c.code FROM UNNEST(cpc) c) FROM $RES"
dry "Lean index extract: ids, dates, cpc.code, title.text, assignee.name (pub table)" \
  "SELECT p.publication_number, p.family_id, p.country_code, p.kind_code, p.priority_date, p.filing_date, ARRAY(SELECT c.code FROM UNNEST(p.cpc) c) cpc, ARRAY(SELECT t.text FROM UNNEST(p.title_localized) t WHERE t.language='en') title, ARRAY(SELECT a.name FROM UNNEST(p.assignee_harmonized) a) assignees FROM $PUB p WHERE EXISTS(SELECT 1 FROM UNNEST(p.cpc) c WHERE c.code LIKE 'H05K7/20%')"
dry "Lean semantic extract: research pub_no, cpc.code, similar.publication_number, embedding_v1" \
  "SELECT r.publication_number, ARRAY(SELECT s.publication_number FROM UNNEST(r.similar) s) similar, r.embedding_v1 FROM $RES r WHERE EXISTS(SELECT 1 FROM UNNEST(r.cpc) c WHERE c.code LIKE 'H05K7/20%')"
dry "Lean index + semantic (join)" \
  "SELECT p.publication_number, p.family_id, p.country_code, p.kind_code, p.priority_date, p.filing_date, ARRAY(SELECT c.code FROM UNNEST(p.cpc) c) cpc, ARRAY(SELECT t.text FROM UNNEST(p.title_localized) t WHERE t.language='en') title, ARRAY(SELECT a.name FROM UNNEST(p.assignee_harmonized) a) assignees, ARRAY(SELECT s.publication_number FROM UNNEST(r.similar) s) similar, r.embedding_v1 FROM $PUB p JOIN $RES r USING (publication_number) WHERE EXISTS(SELECT 1 FROM UNNEST(p.cpc) c WHERE c.code LIKE 'H05K7/20%')"
