from __future__ import annotations

import re
from collections.abc import Iterable

from evidence_gap_navigator.models import EvidenceDocument


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def chunk_text(text: str, max_chars: int = 1_800, overlap_chars: int = 180) -> list[str]:
    clean = normalize_space(text)
    if len(clean) <= max_chars:
        return [clean] if clean else []

    sentences = re.split(r"(?<=[.!?])\s+", clean)
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > max_chars:
            chunks.append(current)
            current = f"{current[-overlap_chars:]} {sentence}".strip()
        else:
            current = candidate
    if current:
        chunks.append(current)
    return chunks


def chunk_work(work: dict, max_chars: int = 1_800) -> Iterable[EvidenceDocument]:
    abstract = normalize_space(work.get("abstract", ""))
    title = normalize_space(work.get("title", "Untitled work"))
    source_text = f"Title: {title}. Abstract: {abstract}"
    for index, chunk in enumerate(chunk_text(source_text, max_chars=max_chars)):
        yield EvidenceDocument(
            id=f"{work['work_id']}::chunk-{index}",
            work_id=work["work_id"],
            title=title,
            text=chunk,
            abstract=abstract,
            year=work.get("year"),
            authors=work.get("authors", []),
            cited_by_count=work.get("cited_by_count", 0),
            doi=work.get("doi"),
            url=work.get("url") or work.get("doi") or "https://openalex.org",
            source_name=work.get("source_name"),
            concepts=work.get("concepts", []),
            chunk_index=index,
        )

