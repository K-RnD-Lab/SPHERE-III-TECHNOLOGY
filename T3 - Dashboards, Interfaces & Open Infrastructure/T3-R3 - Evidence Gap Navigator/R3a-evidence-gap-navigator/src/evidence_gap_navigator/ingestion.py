from __future__ import annotations

import json
from pathlib import Path

import dlt

from evidence_gap_navigator.chunking import chunk_work
from evidence_gap_navigator.config import Settings
from evidence_gap_navigator.openalex import fetch_works


@dlt.resource(name="openalex_works", write_disposition="replace", primary_key="work_id")
def openalex_resource(query: str, max_works: int, email: str | None):
    for work in fetch_works(query=query, max_works=max_works, email=email):
        # Keep list-valued metadata in the main warehouse table instead of dlt child tables.
        work["authors_json"] = json.dumps(work.pop("authors"), ensure_ascii=False)
        work["concepts_json"] = json.dumps(work.pop("concepts"), ensure_ascii=False)
        yield work


def run_ingestion(settings: Settings, max_works: int = 240) -> dict[str, int | str]:
    settings.documents_path.parent.mkdir(parents=True, exist_ok=True)
    pipeline_dir = settings.artifact_dir / "dlt"
    pipeline_dir.mkdir(parents=True, exist_ok=True)

    resource = openalex_resource(settings.openalex_query, max_works, settings.openalex_email)
    pipeline = dlt.pipeline(
        pipeline_name="evidence_gap_openalex",
        destination="duckdb",
        dataset_name="evidence_gap",
        pipelines_dir=str(pipeline_dir),
    )
    load_info = pipeline.run(resource)

    documents = []
    with pipeline.sql_client() as client:
        rows = client.execute_sql(
            """
            SELECT work_id, title, abstract, year, authors_json, cited_by_count,
                   doi, url, source_name, concepts_json
            FROM evidence_gap.openalex_works
            ORDER BY cited_by_count DESC
            """
        )
    columns = [
        "work_id", "title", "abstract", "year", "authors", "cited_by_count",
        "doi", "url", "source_name", "concepts",
    ]
    for row in rows:
        work = dict(zip(columns, row, strict=True))
        for field in ("authors", "concepts"):
            if isinstance(work[field], str):
                work[field] = json.loads(work[field])
        documents.extend(chunk.model_dump() for chunk in chunk_work(work))

    with settings.documents_path.open("w", encoding="utf-8") as output:
        for document in documents:
            output.write(json.dumps(document, ensure_ascii=False) + "\n")

    return {
        "works": len({document["work_id"] for document in documents}),
        "chunks": len(documents),
        "documents_path": str(settings.documents_path),
        "load_package": str(load_info.loads_ids[-1]) if load_info.loads_ids else "none",
    }


def load_documents(path: Path):
    from evidence_gap_navigator.models import EvidenceDocument

    with path.open(encoding="utf-8") as source:
        return [EvidenceDocument.model_validate_json(line) for line in source if line.strip()]
