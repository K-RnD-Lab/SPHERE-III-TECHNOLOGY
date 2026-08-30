from evidence_gap_navigator.openalex import normalize_work, reconstruct_abstract


def test_reconstruct_abstract_uses_positions():
    inverted = {"RAG": [0], "needs": [1], "evaluation": [2]}
    assert reconstruct_abstract(inverted) == "RAG needs evaluation"


def test_normalize_work_filters_missing_abstract():
    assert normalize_work({"id": "https://openalex.org/W1", "display_name": "Paper"}) is None

