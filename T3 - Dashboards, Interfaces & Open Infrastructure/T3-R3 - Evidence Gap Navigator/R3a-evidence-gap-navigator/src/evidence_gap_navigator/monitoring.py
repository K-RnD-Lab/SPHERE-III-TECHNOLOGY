from __future__ import annotations

import sqlite3
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from evidence_gap_navigator.models import RAGResponse


class MonitoringStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS interactions (
                    interaction_id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    question TEXT NOT NULL,
                    retrieval_method TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    latency_ms REAL NOT NULL,
                    retrieved_count INTEGER NOT NULL,
                    citation_count INTEGER NOT NULL,
                    input_tokens INTEGER NOT NULL,
                    output_tokens INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS feedback (
                    feedback_id TEXT PRIMARY KEY,
                    interaction_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    rating INTEGER NOT NULL,
                    comment TEXT,
                    FOREIGN KEY(interaction_id) REFERENCES interactions(interaction_id)
                );
                """
            )

    def log_interaction(self, response: RAGResponse) -> str:
        interaction_id = str(uuid.uuid4())
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO interactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    interaction_id,
                    datetime.now(UTC).isoformat(),
                    response.question,
                    response.retrieval_method,
                    response.provider,
                    response.model,
                    response.latency_ms,
                    len(response.sources),
                    response.answer.count("[") if response.provider != "retrieval-only-preview" else 0,
                    int(response.metadata.get("input_tokens", 0)),
                    int(response.metadata.get("output_tokens", 0)),
                ),
            )
        return interaction_id

    def add_feedback(self, interaction_id: str, rating: int, comment: str = "") -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO feedback VALUES (?, ?, ?, ?, ?)",
                (
                    str(uuid.uuid4()), interaction_id,
                    datetime.now(UTC).isoformat(), rating, comment,
                ),
            )

    def interactions(self) -> pd.DataFrame:
        with self.connect() as connection:
            return pd.read_sql_query("SELECT * FROM interactions ORDER BY created_at", connection)

    def feedback(self) -> pd.DataFrame:
        with self.connect() as connection:
            return pd.read_sql_query("SELECT * FROM feedback ORDER BY created_at", connection)
