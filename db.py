"""
db.py — SQLite setup for the news dashboard.

Uses SQLite (a single local file, no server to install) so you
can get running in minutes. If you later outgrow it, the upgrade
path is Postgres — the SQL here is close enough to standard that
the switch is mostly a connection-string change.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "news.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # lets us access columns by name, e.g. row["title"]
    return conn


def init_db():
    conn = get_connection()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS stories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            first_seen_at TEXT NOT NULL,
            last_updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            story_id INTEGER NOT NULL,
            source_name TEXT NOT NULL,
            title TEXT NOT NULL,
            url TEXT NOT NULL UNIQUE,
            published_at TEXT,
            fetched_at TEXT NOT NULL,
            is_first_source INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (story_id) REFERENCES stories (id)
        );
        """
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print(f"Database ready at {DB_PATH}")
