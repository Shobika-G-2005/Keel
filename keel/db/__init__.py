import sqlite3
from pathlib import Path

SCHEMA = Path(__file__).with_name("schema.sql")


def connect(path: str = ":memory:") -> sqlite3.Connection:
    """Open the database in autocommit mode and make sure the schema exists."""
    con = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    con.executescript(SCHEMA.read_text(encoding="utf-8"))
    return con


def next_id(con: sqlite3.Connection, table: str, column: str, prefix: str) -> str:
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    return f"{prefix}{n + 1}"
