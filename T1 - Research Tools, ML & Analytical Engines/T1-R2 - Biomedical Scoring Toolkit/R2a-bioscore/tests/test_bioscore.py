from bioscore import reproducibility, data_quality, model_readiness
import pickle, tempfile, os


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


def test_model_readiness_sklearn_model():
    """Regression test: sklearn models should have score > 0 because
    vars(obj) inspection finds attributes like n_features, score, etc."""
    try:
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.datasets import make_classification
    except ImportError:
        return  # skip if sklearn not installed

    X, y = make_classification(n_samples=50, n_features=4, random_state=42)
    clf = RandomForestClassifier(n_estimators=5, random_state=42)
    clf.fit(X, y)

    pkl = os.path.join(tempfile.gettempdir(), "test_sklearn.pkl")
    with open(pkl, "wb") as f:
        pickle.dump(clf, f)

    result = model_readiness(pkl)
    assert result["score"] > 0, f"Expected score > 0, got {result['score']}"
    assert isinstance(result["gaps"], list)

