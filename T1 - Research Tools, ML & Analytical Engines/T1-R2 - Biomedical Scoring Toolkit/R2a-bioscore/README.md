# bioscore

Biomedical scoring toolkit — reproducibility, data quality, and model readiness metrics for computational biology.

## Install

```bash
pip install bioscore
```

## Quick Start

```python
from bioscore import reproducibility, data_quality, model_readiness

# Score a notebook for reproducibility
reproducibility("analysis.ipynb")
# → {"score": 0.65, "issues": ["missing seed", "no version pinning"], "level": "partial"}

# Assess dataset quality
data_quality("dataset.csv", domain="oncology")
# → {"completeness": 0.8, "consistency": 0.9, "overall": 0.85}

# Check ML model readiness for deployment
model_readiness("model.pkl")
# → {"score": 0.72, "ready": false, "gaps": ["no validation split", "no bias audit"]}
```

## API

### `reproducibility(source: str) -> dict`
Evaluates a notebook or script for reproducibility best practices.

Checks: random seed, package version pinning, data source documentation, output preservation.

Returns `{"score": float, "issues": list[str], "level": str}`.

### `data_quality(source: str, domain: str = "general") -> dict`
Assesses a dataset for completeness, consistency, and domain-specific quality.

Returns `{"completeness": float, "consistency": float, "overall": float}`.

### `model_readiness(source: str) -> dict`
Evaluates an ML model artifact for production readiness.

Returns `{"score": float, "ready": bool, "gaps": list[str]}`.

## License

MIT © K-RnD Lab
