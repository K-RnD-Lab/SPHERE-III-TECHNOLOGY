from bioscore import reproducibility, data_quality, model_readiness


def test_reproducibility_returns_dict():
    result = reproducibility("import numpy as np; np.random.seed(42)")
    assert "score" in result
    assert "issues" in result
    assert "level" in result
    assert 0 <= result["score"] <= 1


def test_reproducibility_levels():
    result = reproducibility("print('hello')")
    assert result["level"] in ("full", "partial", "minimal")


def test_data_quality_nonexistent():
    result = data_quality("nonexistent.csv")
    assert result["completeness"] == 0.0


def test_model_readiness_returns_dict():
    result = model_readiness("nonexistent_model.pkl")
    assert "score" in result
    assert "ready" in result
    assert "gaps" in result
