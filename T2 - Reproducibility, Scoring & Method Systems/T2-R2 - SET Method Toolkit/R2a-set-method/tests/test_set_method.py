from set_method import classify, score, recommend


def test_classify_returns_three_scores():
    result = classify("Building an AI diagnostic tool for crop disease")
    assert "science" in result
    assert "entrepreneurship" in result
    assert "technology" in result
    assert "primary" in result


def test_classify_primary_is_set_label():
    result = classify("Research hypothesis experiment biology medicine")
    assert result["primary"] == "S"


def test_classify_technology_primary():
    result = classify("Deploying an open source API pipeline for analytics")
    assert result["primary"] == "T"


def test_classify_entrepreneurship_primary():
    result = classify("Startup MVP market validation founder launch growth")
    assert result["primary"] == "E"


def test_score_returns_float():
    result = score("Building an AI diagnostic tool for crop disease")
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_score_orbit_framework():
    result = score("Startup MVP market validation", framework="orbit")
    assert isinstance(result, float)
    assert 0 <= result <= 1


def test_recommend_returns_list():
    result = recommend("engineer", "T")
    assert isinstance(result, list)
    assert len(result) > 0


def test_recommend_invalid_personality():
    try:
        recommend("wizard", "T")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_recommend_invalid_sphere():
    try:
        recommend("engineer", "X")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
