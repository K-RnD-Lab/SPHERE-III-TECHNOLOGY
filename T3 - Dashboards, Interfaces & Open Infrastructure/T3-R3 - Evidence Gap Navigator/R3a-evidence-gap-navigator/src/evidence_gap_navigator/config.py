from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    data_dir: Path
    artifact_dir: Path
    documents_path: Path
    index_dir: Path
    monitoring_db: Path
    llm_provider: str
    llm_model: str
    judge_model: str
    groq_api_key: str | None
    openalex_email: str | None
    openalex_query: str
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def get_settings(root_dir: Path | None = None) -> Settings:
    root = (root_dir or Path(__file__).resolve().parents[2]).resolve()
    data_dir = (root / os.getenv("APP_DATA_DIR", "data")).resolve()
    artifact_dir = (root / os.getenv("APP_ARTIFACT_DIR", "artifacts")).resolve()
    return Settings(
        root_dir=root,
        data_dir=data_dir,
        artifact_dir=artifact_dir,
        documents_path=data_dir / "processed" / "documents.jsonl",
        index_dir=artifact_dir / "index",
        monitoring_db=(root / os.getenv("MONITORING_DB", "data/monitoring.db")).resolve(),
        llm_provider=os.getenv("LLM_PROVIDER", "groq"),
        llm_model=os.getenv("LLM_MODEL", "qwen/qwen3.6-27b"),
        judge_model=os.getenv("JUDGE_MODEL", "qwen/qwen3.6-27b"),
        groq_api_key=os.getenv("GROQ_API_KEY") or None,
        openalex_email=os.getenv("OPENALEX_EMAIL") or None,
        openalex_query=os.getenv(
            "OPENALEX_QUERY", "retrieval augmented generation"
        ),
    )
