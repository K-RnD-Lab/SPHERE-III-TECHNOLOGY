# Architecture notes

## Design decisions

- OpenAlex keeps the corpus public and reproducible.
- `dlt` provides explicit pipeline state and repeatable ingestion without a notebook-only workflow.
- A compact local NumPy vector index avoids requiring reviewers to provision a vector database.
- BM25 remains a first-class baseline rather than treating vector retrieval as automatically superior.
- Hybrid fusion and reranking are selected only after evaluation.
- SQLite keeps monitoring inspectable and portable; the schema can move to PostgreSQL without changing the UI contract.
- Retrieval-only preview mode lets reviewers inspect evidence even without an LLM key.

## Safety boundary

The assistant must cite retrieved sources and disclose insufficient evidence. It is a literature-navigation aid,
not a systematic-review engine and not a substitute for expert assessment.

