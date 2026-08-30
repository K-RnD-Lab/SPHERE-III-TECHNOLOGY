from __future__ import annotations

from evidence_gap_navigator.config import get_settings
from evidence_gap_navigator.evaluation import (
    evaluate_rag,
    load_evaluation_questions,
    write_evaluation_artifacts,
)
from evidence_gap_navigator.rag import RAGService
from evidence_gap_navigator.retrieval import EvidenceSearchEngine


def main() -> None:
    settings = get_settings()
    engine = EvidenceSearchEngine(
        settings.documents_path,
        settings.index_dir,
        settings.embedding_model,
        settings.reranker_model,
    )
    service = RAGService(settings, engine)
    questions = load_evaluation_questions(settings.data_dir / "evaluation" / "questions.json")
    summary, details = evaluate_rag(settings, service, questions)
    write_evaluation_artifacts(settings.artifact_dir / "evaluation", "rag", summary, details)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()

