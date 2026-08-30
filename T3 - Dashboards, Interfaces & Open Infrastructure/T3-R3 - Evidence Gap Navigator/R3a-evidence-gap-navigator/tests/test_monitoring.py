from pathlib import Path

from evidence_gap_navigator.models import RAGResponse
from evidence_gap_navigator.monitoring import MonitoringStore


def test_monitoring_roundtrip(tmp_path: Path):
    store = MonitoringStore(tmp_path / "monitoring.db")
    response = RAGResponse(
        question="What is evaluated?",
        answer="Evidence [1]",
        sources=[],
        retrieval_method="hybrid",
        latency_ms=12.5,
        provider="test",
        model="test-model",
    )
    interaction_id = store.log_interaction(response)
    store.add_feedback(interaction_id, 1, "Useful")
    assert len(store.interactions()) == 1
    assert len(store.feedback()) == 1

