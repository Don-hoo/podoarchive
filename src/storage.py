from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


class ArchiveStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS archived_media (
                    tweet_id TEXT NOT NULL,
                    media_index INTEGER NOT NULL,
                    username TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    archived_at TEXT NOT NULL,
                    tweet_text TEXT,
                    PRIMARY KEY (tweet_id, media_index)
                )
                """
            )

    def is_archived(self, tweet_id: str, media_index: int) -> bool:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT 1 FROM archived_media
                WHERE tweet_id = ? AND media_index = ?
                """,
                (tweet_id, media_index),
            ).fetchone()
        return row is not None

    def mark_archived(
        self,
        tweet_id: str,
        media_index: int,
        username: str,
        file_path: Path,
        tweet_text: str | None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO archived_media
                (tweet_id, media_index, username, file_path, archived_at, tweet_text)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    tweet_id,
                    media_index,
                    username,
                    str(file_path),
                    datetime.now(timezone.utc).isoformat(),
                    tweet_text,
                ),
            )
