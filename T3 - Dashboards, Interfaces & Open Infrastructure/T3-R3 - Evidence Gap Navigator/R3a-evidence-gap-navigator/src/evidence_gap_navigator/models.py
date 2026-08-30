from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EvidenceDocument(BaseModel):
    id: str
    work_id: str
    title: str
    text: str
    abstract: str
    year: int | None = None
    authors: list[str] = Field(default_factory=list)
    cited_by_count: int = 0
    doi: str | None = None
    url: str
    source_name: str | None = None
    concepts: list[str] = Field(default_factory=list)
    chunk_index: int = 0


class SearchResult(BaseModel):
    document: EvidenceDocument
    score: float
    rank: int
    method: str
    component_scores: dict[str, float] = Field(default_factory=dict)


class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: list[SearchResult]
    retrieval_method: str
    latency_ms: float
    provider: str
    model: str
    rewritten_query: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationQuestion(BaseModel):
    id: str
    question: str
    relevant_work_ids: list[str]
    answer_notes: str
    tags: list[str] = Field(default_factory=list)

