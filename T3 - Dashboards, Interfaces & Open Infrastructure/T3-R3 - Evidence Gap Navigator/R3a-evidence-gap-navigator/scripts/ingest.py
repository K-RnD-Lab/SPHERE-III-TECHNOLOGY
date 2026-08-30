from __future__ import annotations

import argparse
import json

from evidence_gap_navigator.config import get_settings
from evidence_gap_navigator.ingestion import run_ingestion
from evidence_gap_navigator.retrieval import EvidenceSearchEngine


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest OpenAlex works and build the dense index")
    parser.add_argument("--max-works", type=int, default=240)
    parser.add_argument("--skip-index", action="store_true")
    parser.add_argument("--force-index", action="store_true")
    args = parser.parse_args()

    settings = get_settings()
    result = run_ingestion(settings, max_works=args.max_works)
    if not args.skip_index:
        engine = EvidenceSearchEngine(
            settings.documents_path,
            settings.index_dir,
            settings.embedding_model,
            settings.reranker_model,
        )
        engine.build_dense_index(force=args.force_index)
        result["index_documents"] = len(engine.documents)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

