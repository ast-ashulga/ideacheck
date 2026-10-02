"""Shared on-disk cache of patent records plus a cross-process rate governor.

One SQLite file (data/cache.sqlite) holds:
- records:   one row per (publication, source, level). level is 'full' (complete page:
             all claims, description, CPC...) or 'details' (partial: independent claims only).
             A 'full' row also satisfies a 'details' request.
- remote_calls: the last call and last throttle time per remote source, shared by every
             process, so parallel scripts and agents can't burst-hit one source.
"""

import json
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

from ideacheck.numbers import canonical

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "data" / "cache.sqlite"
LEVELS = {"details": 1, "full": 2}

_SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    publication_number TEXT NOT NULL,
    source TEXT NOT NULL,
    level TEXT NOT NULL CHECK (level IN ('details', 'full')),
    fetched_at TEXT NOT NULL,
    payload TEXT NOT NULL,
    PRIMARY KEY (publication_number, source, level)
);
CREATE TABLE IF NOT EXISTS remote_calls (
    source TEXT PRIMARY KEY,
    last_call REAL NOT NULL DEFAULT 0,
    throttled_until REAL NOT NULL DEFAULT 0
);
"""


class Cache:
    def __init__(self, path: Path = DEFAULT_PATH):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as con:
            con.executescript(_SCHEMA)

    @contextmanager
    def _conn(self):
        con = sqlite3.connect(self.path, timeout=30, isolation_level=None)
        try:
            con.execute("PRAGMA journal_mode=WAL")
            yield con
        finally:
            con.close()

    # ---- records ---------------------------------------------------------------
    def get(self, number: str, level: str = "details", source: str | None = None) -> dict | None:
        """Best cached record at or above `level`, from `source` or any source."""
        pub = canonical(number)
        wanted = [lv for lv, rank in LEVELS.items() if rank >= LEVELS[level]]
        sql = (f"SELECT payload FROM records WHERE publication_number = ? "
               f"AND level IN ({','.join('?' * len(wanted))})")
        args: list = [pub, *wanted]
        if source:
            sql += " AND source = ?"
            args.append(source)
        sql += " ORDER BY CASE level WHEN 'full' THEN 0 ELSE 1 END, fetched_at DESC LIMIT 1"
        with self._conn() as con:
            row = con.execute(sql, args).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, number: str, source: str, level: str, record: dict,
            fetched_at: str | None = None) -> None:
        pub = canonical(number)
        when = fetched_at or datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._conn() as con:
            con.execute(
                "INSERT OR REPLACE INTO records VALUES (?, ?, ?, ?, ?)",
                (pub, source, level, when, json.dumps(record, ensure_ascii=False, default=str)),
            )

    def stats(self) -> dict:
        with self._conn() as con:
            rows = con.execute(
                "SELECT source, level, COUNT(*) FROM records GROUP BY 1, 2 ORDER BY 1, 2").fetchall()
        return {f"{s}/{lv}": n for s, lv, n in rows}

    # ---- rate governor ----------------------------------------------------------
    def wait_turn(self, source: str, min_interval: float) -> None:
        """Block until `source` may be called again, then record the call.

        Raises Throttled if the source is in a cooldown after a throttle response.
        """
        while True:
            with self._conn() as con:
                con.execute("BEGIN IMMEDIATE")
                con.execute("INSERT OR IGNORE INTO remote_calls (source) VALUES (?)", (source,))
                last, until = con.execute(
                    "SELECT last_call, throttled_until FROM remote_calls WHERE source = ?",
                    (source,)).fetchone()
                now = time.time()
                if until > now:
                    con.execute("COMMIT")
                    raise Throttled(source, until - now)
                wait = last + min_interval - now
                if wait <= 0:
                    con.execute("UPDATE remote_calls SET last_call = ? WHERE source = ?",
                                (now, source))
                    con.execute("COMMIT")
                    return
                con.execute("COMMIT")
            time.sleep(wait)

    def mark_throttled(self, source: str, cooldown: float) -> None:
        """Record a throttle response (e.g. HTTP 503/429); every process then backs off."""
        with self._conn() as con:
            con.execute("INSERT OR IGNORE INTO remote_calls (source) VALUES (?)", (source,))
            con.execute("UPDATE remote_calls SET throttled_until = ? WHERE source = ?",
                        (time.time() + cooldown, source))


class Throttled(RuntimeError):
    def __init__(self, source: str, remaining: float):
        super().__init__(f"{source} is throttled for another {remaining:.0f} s")
        self.source, self.remaining = source, remaining
