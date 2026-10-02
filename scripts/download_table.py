"""Download a BigQuery table (e.g. a finished job's temporary result) to Parquet parts, then DuckDB.

    .venv/bin/python -u scripts/download_table.py PROJECT:DATASET.TABLE data/extract_v2.duckdb [--job-id ID]
Streams with the BigQuery Storage Read API, writing one Parquet file per batch group, so an
interrupted download resumes where it stopped. Reading a table doesn't re-run the query.
"""

import argparse
import time
from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
from google.cloud import bigquery
from google.cloud.bigquery_storage import BigQueryReadClient


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("table")
    ap.add_argument("db", type=Path)
    ap.add_argument("--job-id", default="")
    ap.add_argument("--rows-per-part", type=int, default=100_000)
    a = ap.parse_args()

    project, rest = a.table.split(":", 1)
    parts_dir = a.db.with_suffix(".parts")
    parts_dir.mkdir(parents=True, exist_ok=True)
    done = sorted(parts_dir.glob("part-*.parquet"))
    skip = sum(pq.ParquetFile(p).metadata.num_rows for p in done)

    client = bigquery.Client(project=project)
    table = client.get_table(rest if "." in rest else f"{project}.{rest}")
    print(f"{table.num_rows:,} rows; {skip:,} already downloaded in {len(done)} parts", flush=True)

    started, seen, buf, n_part = time.time(), 0, [], len(done)
    rows = client.list_rows(table, start_index=skip or None)
    for batch in rows.to_arrow_iterable(bqstorage_client=BigQueryReadClient()):
        buf.append(batch)
        seen += batch.num_rows
        if sum(b.num_rows for b in buf) >= a.rows_per_part:
            pq.write_table(pa.Table.from_batches(buf), parts_dir / f"part-{n_part:04d}.parquet")
            n_part, buf = n_part + 1, []
            print(f"  {skip + seen:,}/{table.num_rows:,} rows ({time.time() - started:.0f}s)", flush=True)
    if buf:
        pq.write_table(pa.Table.from_batches(buf), parts_dir / f"part-{n_part:04d}.parquet")

    con = duckdb.connect(str(a.db))
    con.execute(f"CREATE OR REPLACE TABLE publications AS SELECT * FROM read_parquet('{parts_dir}/part-*.parquet')")
    n = con.execute("SELECT COUNT(*) FROM publications").fetchone()[0]
    con.execute("CREATE OR REPLACE TABLE extract_meta AS SELECT ? AS job_id, ? AS source_table, now() AS extracted_at",
                [a.job_id, a.table])
    con.close()
    print(f"Saved {n:,} rows to {a.db} in {time.time() - started:.0f}s", flush=True)


if __name__ == "__main__":
    main()
