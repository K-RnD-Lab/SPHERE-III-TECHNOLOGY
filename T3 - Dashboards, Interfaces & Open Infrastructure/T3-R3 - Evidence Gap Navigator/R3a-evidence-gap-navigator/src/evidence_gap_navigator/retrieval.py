from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

from evidence_gap_navigator.ingestion import load_documents
from evidence_gap_navigator.models import EvidenceDocument, SearchResult


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9][a-z0-9_-]+", text.lower())


def _minmax(values: np.ndarray) -> np.ndarray:
    if not len(values):
        return values
    minimum, maximum = float(values.min()), float(values.max())
    if maximum <= minimum:
        return np.ones_like(values)
    return (values - minimum) / (maximum - minimum)


class EvidenceSearchEngine:
    def __init__(
        self,
        documents_path: Path,
        index_dir: Path,
        embedding_model: str,
        reranker_model: str,
    ) -> None:
        self.documents_path = documents_path
        self.index_dir = index_dir
        self.embedding_model_name = embedding_model
        self.reranker_model_name = reranker_model
        self.documents: list[EvidenceDocument] = load_documents(documents_path)
        self._corpus_tokens = [tokenize(document.text) for document in self.documents]
        self._bm25 = BM25Okapi(self._corpus_tokens)
        self._embedder: SentenceTransformer | None = None
        self._reranker: CrossEncoder | None = None
        self._embeddings: np.ndarray | None = None

    @property
    def embedder(self) -> SentenceTransformer:
        if self._embedder is None:
            self._embedder = SentenceTransformer(self.embedding_model_name)
        return self._embedder

    @property
    def reranker(self) -> CrossEncoder:
        if self._reranker is None:
            self._reranker = CrossEncoder(self.reranker_model_name)
        return self._reranker

    def build_dense_index(self, force: bool = False) -> Path:
        self.index_dir.mkdir(parents=True, exist_ok=True)
        embeddings_path = self.index_dir / "embeddings.npy"
        metadata_path = self.index_dir / "metadata.json"
        if embeddings_path.exists() and not force:
            self._embeddings = np.load(embeddings_path)
            if len(self._embeddings) == len(self.documents):
                return embeddings_path

        texts = [document.text for document in self.documents]
        self._embeddings = self.embedder.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
            batch_size=32,
        )
        np.save(embeddings_path, self._embeddings)
        metadata_path.write_text(
            json.dumps(
                {
                    "embedding_model": self.embedding_model_name,
                    "documents": len(self.documents),
                    "dimensions": int(self._embeddings.shape[1]),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return embeddings_path

    def _load_embeddings(self) -> np.ndarray:
        if self._embeddings is None:
            embeddings_path = self.index_dir / "embeddings.npy"
            if not embeddings_path.exists():
                self.build_dense_index()
            else:
                self._embeddings = np.load(embeddings_path)
        if len(self._embeddings) != len(self.documents):
            self.build_dense_index(force=True)
        return self._embeddings

    def _top_results(
        self,
        scores: np.ndarray,
        method: str,
        top_k: int,
        components: dict[str, np.ndarray] | None = None,
    ) -> list[SearchResult]:
        indexes = np.argsort(scores)[::-1][:top_k]
        return [
            SearchResult(
                document=self.documents[index],
                score=float(scores[index]),
                rank=rank,
                method=method,
                component_scores={
                    name: float(component[index]) for name, component in (components or {}).items()
                },
            )
            for rank, index in enumerate(indexes, start=1)
        ]

    def search_bm25(self, query: str, top_k: int = 8) -> list[SearchResult]:
        scores = np.asarray(self._bm25.get_scores(tokenize(query)), dtype=float)
        return self._top_results(scores, "bm25", top_k)

    def search_dense(self, query: str, top_k: int = 8) -> list[SearchResult]:
        embeddings = self._load_embeddings()
        query_embedding = self.embedder.encode([query], normalize_embeddings=True)[0]
        scores = embeddings @ query_embedding
        return self._top_results(scores, "dense", top_k)

    def search_hybrid(
        self,
        query: str,
        top_k: int = 8,
        alpha: float = 0.58,
        rerank: bool = False,
    ) -> list[SearchResult]:
        bm25_scores = np.asarray(self._bm25.get_scores(tokenize(query)), dtype=float)
        embeddings = self._load_embeddings()
        query_embedding = self.embedder.encode([query], normalize_embeddings=True)[0]
        dense_scores = embeddings @ query_embedding
        hybrid_scores = (1 - alpha) * _minmax(bm25_scores) + alpha * _minmax(dense_scores)
        candidate_count = min(max(top_k * 4, 24), len(self.documents))
        candidates = self._top_results(
            hybrid_scores,
            "hybrid",
            candidate_count,
            {"bm25": _minmax(bm25_scores), "dense": _minmax(dense_scores)},
        )
        if not rerank:
            return candidates[:top_k]

        pairs = [(query, result.document.text) for result in candidates]
        rerank_scores = np.asarray(self.reranker.predict(pairs), dtype=float)
        order = np.argsort(rerank_scores)[::-1][:top_k]
        return [
            SearchResult(
                document=candidates[index].document,
                score=float(rerank_scores[index]),
                rank=rank,
                method="hybrid_rerank",
                component_scores={
                    **candidates[index].component_scores,
                    "hybrid": candidates[index].score,
                },
            )
            for rank, index in enumerate(order, start=1)
        ]

    def search(self, query: str, method: str = "hybrid_rerank", top_k: int = 6):
        if method == "bm25":
            return self.search_bm25(query, top_k)
        if method == "dense":
            return self.search_dense(query, top_k)
        if method == "hybrid":
            return self.search_hybrid(query, top_k, rerank=False)
        if method == "hybrid_rerank":
            return self.search_hybrid(query, top_k, rerank=True)
        raise ValueError(f"Unsupported retrieval method: {method}")

    def corpus_summary(self) -> dict:
        by_year: dict[int, int] = defaultdict(int)
        unique_works: set[str] = set()
        for document in self.documents:
            unique_works.add(document.work_id)
            if document.year:
                by_year[document.year] += 1
        return {
            "works": len(unique_works),
            "chunks": len(self.documents),
            "years": dict(sorted(by_year.items())),
        }

