from evidence_gap_navigator.chunking import chunk_text, chunk_work


def test_chunk_text_preserves_short_text():
    assert chunk_text("A short abstract.") == ["A short abstract."]


def test_chunk_work_keeps_source_metadata():
    work = {
        "work_id": "W1",
        "title": "Evaluation of RAG",
        "abstract": "Evidence " * 80,
        "year": 2025,
        "authors": ["A. Researcher"],
        "cited_by_count": 4,
        "doi": "https://doi.org/example",
        "url": "https://openalex.org/W1",
        "source_name": "Example Journal",
        "concepts": ["Retrieval augmented generation"],
    }
    documents = list(chunk_work(work, max_chars=250))
    assert len(documents) > 1
    assert all(document.work_id == "W1" for document in documents)
    assert documents[0].title == "Evaluation of RAG"

