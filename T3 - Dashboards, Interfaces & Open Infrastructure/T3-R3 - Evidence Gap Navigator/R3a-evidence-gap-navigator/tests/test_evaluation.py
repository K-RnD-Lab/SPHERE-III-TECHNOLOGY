import pytest

from evidence_gap_navigator.evaluation import ndcg_at_k, reciprocal_rank


def test_reciprocal_rank():
    assert reciprocal_rank(["A", "B", "C"], {"B"}) == 0.5
    assert reciprocal_rank(["A"], {"B"}) == 0.0


def test_ndcg_rewards_earlier_relevant_results():
    early = ndcg_at_k(["B", "A", "C"], {"B"}, 3)
    late = ndcg_at_k(["A", "C", "B"], {"B"}, 3)
    assert early == pytest.approx(1.0)
    assert early > late

