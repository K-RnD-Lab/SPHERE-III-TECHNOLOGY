# studyreg

Study Registry client — register, search, and manage reproducible computational studies.

## Install

```bash
pip install studyreg
```

## Quick Start

```python
from studyreg import register, search, validate

# Register a new study
study = register(
    title="Oncology survival analysis with XGBoost",
    repo="https://github.com/example/oncology-study",
    tags=["oncology", "survival", "xgboost"],
    sphere="S",
)
# → {"id": "STU-0042", "status": "registered", ...}

# Search existing studies
results = search(domain="agriculture", status="completed")
# → [Study(...), Study(...)]

# Validate a study registration
validate(study)
# → {"valid": true, "warnings": []}
```

## API

### `register(title, repo, tags, sphere) -> dict`
Register a new computational study.

Returns dict with `id`, `status`, and registration metadata.

### `search(domain=None, status=None, tags=None, sphere=None) -> list[dict]`
Search registered studies by domain, status, tags, or sphere.

Returns list of matching study dicts.

### `validate(study: dict) -> dict`
Validate a study registration for completeness.

Returns `{"valid": bool, "warnings": list[str]}`.

## License

MIT © K-RnD-Lab
