"""Extract v2 (PLAN.md §9.1 B): metadata + English title/abstract + similar + embedding, for a CPC scope.

    .venv/bin/python scripts/extract_v2.py --dry-run [--variant research|localized] [--prefix B62B A61G ...]
    .venv/bin/python scripts/extract_v2.py --max-gb 450 --prefix ...      # real run, writes data/extract_v2.duckdb

Variants (the abstract source):
- research:  google_patents_research.publications.title/abstract, English and machine-translated
             where needed (one value per publication, so it also covers non-English documents).
- localized: patents.publications.title_localized/abstract_localized, English entries only (no translation).
The class filter matches CPC, IPC or FI codes (Japanese documents often have no CPC). It decides which rows are downloaded, not what is billed: billing depends on the columns read.
"""

import argparse
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJECT = "patent-landscape-ashulga"
DEFAULT_PREFIXES = ["B62B", "A61G", "B62D51/", "B60K7/", "B60B19/", "B60B33/", "B62D7/", "B66F9/"]

META = """
  p.publication_number, p.family_id, p.country_code, p.kind_code,
  p.priority_date, p.filing_date, p.publication_date,
  ARRAY(SELECT a.name FROM UNNEST(p.assignee_harmonized) a) AS assignees,
  ARRAY(SELECT c.code FROM UNNEST(r.cpc) c) AS cpc,
  ARRAY(SELECT c.code FROM UNNEST(p.ipc) c) AS ipc,
  ARRAY(SELECT c.code FROM UNNEST(p.fi) c) AS fi,
  ARRAY(SELECT s.publication_number FROM UNNEST(r.similar) s) AS similar,
  r.embedding_v1"""

TEXT = {
    "research": "r.title AS title_en, r.abstract AS abstract_en, r.abstract_translated",
    "localized": ("(SELECT t.text FROM UNNEST(p.title_localized) t WHERE t.language = 'en' LIMIT 1) AS title_en, "
                  "(SELECT a.text FROM UNNEST(p.abstract_localized) a WHERE a.language = 'en' LIMIT 1) AS abstract_en"),
}


def sql(variant: str, n_prefixes: int) -> str:
    cond = " OR ".join(f"STARTS_WITH(c.code, @p{i})" for i in range(n_prefixes))
    return f"""
SELECT {META}, {TEXT[variant]}
FROM `patents-public-data.google_patents_research.publications` r
JOIN `patents-public-data.patents.publications` p USING (publication_number)
WHERE EXISTS (SELECT 1 FROM UNNEST(r.cpc) c WHERE {cond})
   OR EXISTS (SELECT 1 FROM UNNEST(p.ipc) c WHERE {cond})
   OR EXISTS (SELECT 1 FROM UNNEST(p.fi) c WHERE {cond})
"""


def main() -> None:
    from google.cloud import bigquery

    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--variant", choices=sorted(TEXT), default="research")
    ap.add_argument("--prefix", nargs="+", default=DEFAULT_PREFIXES)
    ap.add_argument("--max-gb", type=float, default=450.0)
    a = ap.parse_args()

    client = bigquery.Client(project=PROJECT)
    cfg = bigquery.QueryJobConfig(
        dry_run=a.dry_run, use_query_cache=not a.dry_run, maximum_bytes_billed=int(a.max_gb * 1e9),
        query_parameters=[bigquery.ScalarQueryParameter(f"p{i}", "STRING", p)
                          for i, p in enumerate(a.prefix)])
    job = client.query(sql(a.variant, len(a.prefix)), job_config=cfg)
    if a.dry_run:
        print(f"[{a.variant}] dry run: would scan {job.total_bytes_processed / 1e9:.1f} GB "
              f"(limit {a.max_gb:.0f} GB); prefixes: {' '.join(a.prefix)}")
        return

    import duckdb

    started = time.time()
    rows = job.result().to_arrow(create_bqstorage_client=True)
    print(f"Billed {job.total_bytes_billed / 1e9:.1f} GB; {rows.num_rows:,} rows in {time.time() - started:.0f}s")
    db = ROOT / "data" / "extract_v2.duckdb"
    con = duckdb.connect(str(db))
    con.execute("CREATE OR REPLACE TABLE publications AS SELECT * FROM rows")
    con.execute("CREATE OR REPLACE TABLE extract_meta AS SELECT ? AS job_id, ? AS bytes_billed, "
                "? AS variant, ? AS cpc_prefixes, now() AS extracted_at",
                [job.job_id, job.total_bytes_billed, a.variant, " ".join(a.prefix)])
    con.close()
    print(f"Saved to {db}")


if __name__ == "__main__":
    main()
