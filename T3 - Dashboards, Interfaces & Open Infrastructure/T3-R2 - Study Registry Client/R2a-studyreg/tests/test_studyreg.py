from studyreg import register, search, validate


def test_register_returns_study():
    result = register(
        title="Test study",
        repo="https://github.com/example/test",
        tags=["test"],
        sphere="S",
    )
    assert "id" in result
    assert result["status"] == "registered"
    assert result["sphere"] == "S"


def test_search_finds_registered():
    register(title="Oncology study", repo="https://github.com/example/onc", tags=["oncology"], sphere="S", domain="oncology")
    results = search(domain="oncology")
    assert len(results) >= 1


def test_search_by_sphere():
    register(title="Tech study", repo="https://github.com/example/tech", sphere="T")
    results = search(sphere="T")
    assert len(results) >= 1


def test_validate_good_study():
    study = {"title": "Good study", "repo": "https://github.com/example", "sphere": "S"}
    result = validate(study)
    assert result["valid"] is True
    assert len(result["warnings"]) == 0


def test_validate_missing_fields():
    result = validate({})
    assert result["valid"] is False
    assert len(result["warnings"]) > 0


def test_validate_invalid_sphere():
    study = {"title": "Test", "repo": "https://github.com/example", "sphere": "X"}
    result = validate(study)
    assert result["valid"] is False
