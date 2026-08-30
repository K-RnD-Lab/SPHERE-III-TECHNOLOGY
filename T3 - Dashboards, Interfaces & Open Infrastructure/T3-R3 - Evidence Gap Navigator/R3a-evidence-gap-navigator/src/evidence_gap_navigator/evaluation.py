from __future__ import annotations

import json
import math
import re
from pathlib import Path

import pandas as pd

from evidence_gap_navigator.config import Settings
from evidence_gap_navigator.llm import GroqLLM
from evidence_gap_navigator.models import EvaluationQuestion
from evidence_gap_navigator.rag import RAGService
from evidence_gap_navigator.retrieval import EvidenceSearchEngine


def load_evaluation_questions(path: Path) -> list[EvaluationQuestion]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [EvaluationQuestion.model_validate(item) for item in payload]


def _ranked_work_ids(results) -> list[str]:
    seen: set[str] = set()
    ranked = []
    for result in results:
        work_id = result.document.work_id
        if work_id not in seen:
            seen.add(work_id)
            ranked.append(work_id)
    return ranked


def reciprocal_rank(ranked_ids: list[str], relevant_ids: set[str]) -> float:
    for rank, work_id in enumerate(ranked_ids, start=1):
        if work_id in relevant_ids:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(ranked_ids: list[str], relevant_ids: set[str], k: int) -> float:
    gains = [1.0 if work_id in relevant_ids else 0.0 for work_id in ranked_ids[:k]]
    dcg = sum(gain / math.log2(index + 2) for index, gain in enumerate(gains))
    ideal_count = min(len(relevant_ids), k)
    ideal = sum(1.0 / math.log2(index + 2) for index in range(ideal_count))
    return dcg / ideal if ideal else 0.0


def evaluate_retrieval(
    engine: EvidenceSearchEngine,
    questions: list[EvaluationQuestion],
    methods: tuple[str, ...] = ("bm25", "dense", "hybrid", "hybrid_rerank"),
    top_k: int = 10,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    details = []
    for method in methods:
        for question in questions:
            results = engine.search(question.question, method=method, top_k=top_k)
            ranked_ids = _ranked_work_ids(results)
            relevant = set(question.relevant_work_ids)
            details.append(
                {
                    "question_id": question.id,
                    "method": method,
                    "hit_rate_at_5": float(bool(set(ranked_ids[:5]) & relevant)),
                    "hit_rate_at_10": float(bool(set(ranked_ids[:10]) & relevant)),
                    "mrr_at_10": reciprocal_rank(ranked_ids[:10], relevant),
                    "ndcg_at_10": ndcg_at_k(ranked_ids, relevant, 10),
                    "top_work_ids": ranked_ids[:10],
                }
            )
    detail_frame = pd.DataFrame(details)
    summary = (
        detail_frame.groupby("method", as_index=False)[
            ["hit_rate_at_5", "hit_rate_at_10", "mrr_at_10", "ndcg_at_10"]
        ]
        .mean()
        .sort_values(["mrr_at_10", "ndcg_at_10"], ascending=False)
    )
    return summary, detail_frame


def _extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError(f"Judge did not return JSON: {text[:160]}")
    return json.loads(match.group(0))


def evaluate_rag(
    settings: Settings,
    service: RAGService,
    questions: list[EvaluationQuestion],
    prompt_versions: tuple[str, ...] = ("v1", "v2"),
    limit: int = 4,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY is required for end-to-end LLM evaluation")
    judge = GroqLLM(settings.groq_api_key, settings.judge_model)
    details = []
    evaluation_questions = questions[:limit]
    for prompt_version in prompt_versions:
        for index, question in enumerate(evaluation_questions, start=1):
            print(f"Evaluating {prompt_version}: {index}/{len(evaluation_questions)} ({question.id})")
            response = service.answer(
                question.question,
                retrieval_method="hybrid_rerank",
                top_k=3,
                prompt_version=prompt_version,
                max_completion_tokens=220,
            )
            retrieved_evidence = "\n\n".join(
                f"[{index}] {source.document.title}\n{source.document.text[:600]}"
                for index, source in enumerate(response.sources, start=1)
            )
            judge_prompt = f"""Evaluate this RAG answer against the reference notes.
Return only JSON with integer fields groundedness, relevance, completeness,
citation_quality (1-5), and a short string rationale.

Question: {question.question}
Reference notes: {question.answer_notes}
Retrieved evidence with citation mapping:\n{retrieved_evidence}
Answer: {response.answer}
"""
            scores = _extract_json(
                judge.complete(
                    "You are a strict RAG evaluator. Penalize unsupported claims and missing citations.",
                    judge_prompt,
                    temperature=0.0,
                    max_completion_tokens=220,
                    json_mode=True,
                ).text
            )
            details.append(
                {
                    "question_id": question.id,
                    "prompt_version": prompt_version,
                    "groundedness": int(scores["groundedness"]),
                    "relevance": int(scores["relevance"]),
                    "completeness": int(scores["completeness"]),
                    "citation_quality": int(scores["citation_quality"]),
                    "rationale": scores.get("rationale", ""),
                    "answer": response.answer,
                }
            )
    detail_frame = pd.DataFrame(details)
    metric_columns = ["groundedness", "relevance", "completeness", "citation_quality"]
    summary = detail_frame.groupby("prompt_version", as_index=False)[metric_columns].mean()
    summary["overall"] = summary[metric_columns].mean(axis=1)
    summary = summary.sort_values("overall", ascending=False)
    return summary, detail_frame


def write_evaluation_artifacts(
    output_dir: Path,
    name: str,
    summary: pd.DataFrame,
    details: pd.DataFrame,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_dir / f"{name}_summary.csv", index=False)
    serializable = details.copy()
    for column in serializable.columns:
        serializable[column] = serializable[column].apply(
            lambda value: json.dumps(value) if isinstance(value, (list, dict)) else value
        )
    serializable.to_csv(output_dir / f"{name}_details.csv", index=False)


def evaluation_overview(output_dir: Path) -> dict[str, pd.DataFrame]:
    frames: dict[str, pd.DataFrame] = {}
    for path in output_dir.glob("*_summary.csv"):
        frames[path.stem] = pd.read_csv(path)
    return frames
