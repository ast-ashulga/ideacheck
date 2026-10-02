"""Phase 0, step 6: one-time BigQuery extract into local DuckDB.

Reads only the columns and nested sub-fields needed. A filter on classification
codes does NOT reduce the bytes scanned (the tables are unclustered); it only
limits how many rows are downloaded.

    .venv/bin/python scripts/phase0/extract.py --dry-run   # free, shows the scan size
    .venv/bin/python scripts/phase0/extract.py             # real run, guarded by --max-gb
"""

import argparse
import time
from pathlib import Path

import duckdb
from google.cloud import bigquery

PROJECT = "patent-landscape-ashulga"
CPC_PREFIXES = ["B62B", "A61G7/", "A61G1/"]
DB_PATH = Path(__file__).resolve().parents[2] / "data" / "extract.duckdb"

SQL = """
SELECT
  p.publication_number,
  p.family_id,
  p.country_code,
  p.kind_code,
  p.priority_date,
  p.filing_date,
  p.publication_date,
  ARRAY(SELECT c.code FROM UNNEST(p.cpc) c) AS cpc,
  ARRAY(SELECT t.text FROM UNNEST(p.title_localized) t WHERE t.language = 'en') AS title_en,
  ARRAY(SELECT a.name FROM UNNEST(p.assignee_harmonized) a) AS assignees,
  ARRAY(SELECT s.publication_number FROM UNNEST(r.similar) s) AS similar,
  r.embedding_v1
FROM `patents-public-data.patents.publications` p
LEFT JOIN `patents-public-data.google_patents_research.publications` r
  USING (publication_number)
WHERE EXISTS (
  SELECT 1 FROM UNNEST(p.cpc) c
  WHERE STARTS_WITH(c.code, @p0) OR STARTS_WITH(c.code, @p1) OR STARTS_WITH(c.code, @p2)
)
"""


def job_config(dry_run: bool, max_gb: float) -> bigquery.QueryJobConfig:
    return bigquery.QueryJobConfig(
        dry_run=dry_run,
        use_query_cache=not dry_run,
        maximum_bytes_billed=int(max_gb * 1e9),
        query_parameters=[
            bigquery.ScalarQueryParameter(f"p{i}", "STRING", prefix)
            for i, prefix in enumerate(CPC_PREFIXES)
        ],
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--max-gb", type=float, default=210.0,
                        help="Hard limit: BigQuery refuses the job if it would bill more")
    args = parser.parse_args()

    client = bigquery.Client(project=PROJECT)
    job = client.query(SQL, job_config=job_config(args.dry_run, args.max_gb))
    if args.dry_run:
        print(f"Dry run: would scan {job.total_bytes_processed / 1e9:.1f} GB "
              f"(limit {args.max_gb:.0f} GB). Classification prefixes: {CPC_PREFIXES}")
        return

    started = time.time()
    arrow_rows = job.result().to_arrow(create_bqstorage_client=True)
    print(f"Billed {job.total_bytes_billed / 1e9:.1f} GB; {arrow_rows.num_rows:,} rows "
          f"in {time.time() - started:.0f}s")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE OR REPLACE TABLE publications AS SELECT * FROM arrow_rows")
    con.execute(
        "CREATE OR REPLACE TABLE extract_meta AS SELECT ? AS job_id, ? AS bytes_billed, "
        "? AS cpc_prefixes, now() AS extracted_at",
        [job.job_id, job.total_bytes_billed, ",".join(CPC_PREFIXES)],
    )
    con.close()
    print(f"Saved to {DB_PATH}")


if __name__ == "__main__":
    main()
