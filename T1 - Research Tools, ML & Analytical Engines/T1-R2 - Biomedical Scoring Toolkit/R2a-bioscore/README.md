# bioscore

**Biomedical scoring toolkit** — reproducibility, data quality, and model readiness metrics for computational biology.

[![PyPI](https://img.shields.io/pypi/v/bioscore.svg)](https://pypi.org/project/bioscore/)
[![CI](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY/actions/workflows/test-bioscore.yml/badge.svg)](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why this exists

Most computational biology teams have **no automated quality gates**. A researcher finishes a notebook, shares it — and nobody can reproduce it. A data scientist trains a model — and it silently fails on edge cases. A team deploys to production — and there's no bias audit.

**bioscore** closes these gaps with three one-command checks that plug into any workflow.

## Install

```bash
pip install bioscore
```

Requires Python 3.9+. No external dependencies for core functions.

## Quick Start

```python
from bioscore import reproducibility, data_quality, model_readiness

# 1. Check if your notebook is reproducible
reproducibility("analysis.ipynb")
# → {"score": 0.65, "issues": ["missing seed", "no version pinning"], "level": "partial"}

# 2. Assess dataset quality before training
data_quality("dataset.csv", domain="oncology")
# → {"completeness": 0.8, "consistency": 0.9, "overall": 0.85}

# 3. Verify model is ready for production
model_readiness("model.pkl")
# → {"score": 0.72, "ready": false, "gaps": ["no validation split", "no bias audit"]}
```

---

## Target Audience & Daily Use

### 🧬 Computational Biology Researcher

**Their morning:** Opens Jupyter, runs yesterday's analysis on new data. Shares notebook with labmates. Submits paper.

**The problem:** Six months later, nobody — including themselves — can reproduce the results. Random seeds weren't set. Package versions weren't pinned. The data source was a colleague's Dropbox link that's now dead.

**How bioscore helps:**
```python
from bioscore import reproducibility

result = reproducibility("my_analysis.ipynb")
if result["level"] != "full":
    print("Fix before sharing:", result["issues"])
```
They run this **before sharing any notebook**. It catches missing seeds, unpinned versions, undocumented data sources. The `level` field (`full` / `partial` / `minimal`) gives a quick pass/fail.

**Install:** `pip install bioscore` in their notebook environment (conda, venv, or Colab).

---

### 📊 Data Scientist in Pharma/Biotech

**Their morning:** Pulls clinical trial data. Checks for missing values. Trains a survival model. Sends to review.

**The problem:** Datasets have silent gaps — 30% missing in one column, inconsistent row counts, domain-specific quality rules nobody checks automatically.

**How bioscore helps:**
```python
from bioscore import data_quality

result = data_quality("clinical_data.csv", domain="oncology")
if result["overall"] < 0.7:
    print(f"Quality too low ({result['overall']}), fix before training")
```
They run this **as the first cell in every analysis notebook**. Domain-aware checks (`oncology`, `agriculture`, `general`) apply different quality thresholds. Prevents garbage-in-garbage-out silently.

**Install:** `pip install bioscore` in their data science environment.

---

### 🚀 ML Engineer / MLOps

**Their morning:** Reviews model PR. Checks metrics. Approves deployment to staging. Monitors production.

**The problem:** Models reach production without validation splits, bias audits, or input schemas. Issues surface only in production — expensive and risky.

**How bioscore helps:**
```python
from bioscore import model_readiness

result = model_readiness("model_v2.pkl")
if not result["ready"]:
    print("Block deployment:", result["gaps"])
```
They add this to **CI/CD pipeline** as a deployment gate. If `ready` is `false`, the pipeline blocks. Gaps like "no validation split" or "no bias audit" are surfaced as actionable items.

**Install:** Add `bioscore` to `requirements.txt` or `pyproject.toml` in the ML pipeline project.

---

## API Reference

### `reproducibility(source: str) -> dict`

Evaluates a notebook or script for reproducibility best practices.

**Checks:** random seed, package version pinning, data source documentation, output preservation, environment specification, comments, docstrings, logging.

**Returns:** `{"score": float, "issues": list[str], "level": "full"|"partial"|"minimal"}`

### `data_quality(source: str, domain: str = "general") -> dict`

Assesses a CSV dataset for completeness and consistency.

**Domains:** `"general"`, `"oncology"`, `"agriculture"` — each applies domain-specific quality weights.

**Returns:** `{"completeness": float, "consistency": float, "overall": float}`

### `model_readiness(source: str) -> dict`

Evaluates a pickled ML model artifact for production readiness.

**Checks:** validation split, bias audit, performance metrics, version tag, input schema, error handling, documentation, test coverage.

**Returns:** `{"score": float, "ready": bool, "gaps": list[str]}`

---

## Innovation

bioscore is **the first lightweight, zero-dependency Python toolkit** that unifies three critical pre-deployment checks for computational biology:

1. **Reproducibility scoring** — not just linting, but a weighted score with actionable issues
2. **Domain-aware data quality** — oncology and agriculture have different quality standards than general data
3. **Model readiness gate** — a binary pass/fail with specific gaps, designed for CI/CD integration

No other package combines all three. Most teams cobble together custom scripts. bioscore makes it `pip install bioscore` and one function call.

---

## License

MIT © K-RnD Lab
