# studyreg

**Study Registry client** — register, search, and manage reproducible computational studies.

[![PyPI](https://img.shields.io/pypi/v/studyreg.svg)](https://pypi.org/project/studyreg/)
[![CI](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY/actions/workflows/test-studyreg.yml/badge.svg)](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why this exists

Computational studies die silently. A researcher runs an experiment, gets results, publishes — and the study details vanish into a PDF that nobody can search, filter, or build on. Pre-registration (declaring your study design before running it) is the gold standard for preventing p-hacking and publication bias — but existing registries are clunky, domain-specific, and not programmable.

**studyreg** makes study registration as easy as a Python function call, with built-in validation and search.

## Install

```bash
pip install studyreg
```

Requires Python 3.9+. No external dependencies for core functions.

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
results = search(domain="oncology", status="completed")
# → [Study(...), Study(...)]

# Validate a study registration
validate(study)
# → {"valid": true, "warnings": []}
```

---

## Target Audience & Daily Use

### 🔬 Computational Researcher

**Their morning:** Designs a new experiment. Writes the hypothesis. Prepares the dataset. Starts coding.

**The problem:** Without pre-registration, it's tempting to tweak the hypothesis after seeing results. Reviewers can't verify that the analysis plan was decided upfront. The study becomes unreproducible by design.

**How studyreg helps:**
```python
from studyreg import register, validate

study = register(
    title="Effect of soil microbiome diversity on crop yield under drought",
    repo="https://github.com/mylab/soil-microbiome-study",
    tags=["agriculture", "microbiome", "drought"],
    sphere="S",
    domain="agriculture",
)

# Validate before submitting
check = validate(study)
if not check["valid"]:
    print("Missing:", check["warnings"])
```
They run this **before writing any analysis code**. The registration timestamp and ID serve as proof of pre-registration. The `validate()` call catches missing fields before submission. When they publish, they cite the study ID — reviewers verify the plan was set upfront.

**Install:** `pip install studyreg` in their research project's environment.

---

### 📊 Meta-Analyst / Systematic Reviewer

**Their morning:** Needs to find all studies on a topic. Currently Googles, checks PubMed, emails authors. Most computational studies aren't indexed anywhere.

**The problem:** Computational studies are invisible to traditional literature search. No central registry. No tags. No way to filter by domain, status, or methodology.

**How studyreg helps:**
```python
from studyreg import search

# Find all completed oncology studies using XGBoost
results = search(domain="oncology", tags=["xgboost"], status="completed")
for study in results:
    print(study["id"], study["title"], study["repo"])
```
They use `search()` to **discover studies programmatically**. Filter by domain, status, tags, or SET sphere. Export results for systematic review. No more manual searching.

**Install:** `pip install studyreg` in their review analysis environment.

---

### 🏗️ Open Infrastructure Builder

**Their morning:** Building a platform for open science. Needs a study registry backend that's lightweight, programmable, and doesn't require a full database team.

**The problem:** Existing registries (ClinicalTrials.gov, OSF) are heavy, domain-locked, or require web UI interaction. No simple Python API for programmatic registration and search.

**How studyreg helps:**
```python
from studyreg import register, search, validate

# Your platform's registration endpoint calls this
study = register(title=user_input, repo=github_url, tags=auto_tags, sphere="S")

# Your search page calls this
results = search(domain=filter_domain, sphere=filter_sphere)

# Your validation step calls this
check = validate(study)
```
They embed studyreg as the **registry layer** in their platform. No database setup — studyreg manages storage internally. The API is three function calls. They focus on the UI, not the backend.

**Install:** Add `studyreg` to the platform's backend dependencies.

---

## API Reference

### `register(title, repo, tags, sphere, domain) -> dict`

Register a new computational study.

**Parameters:** `title` (str), `repo` (URL str), `tags` (list[str]), `sphere` (`S`/`E`/`T`), `domain` (str, default `"general"`)

**Returns:** dict with `id`, `status`, `date`, and all registration metadata.

### `search(domain=None, status=None, tags=None, sphere=None) -> list[dict]`

Search registered studies by domain, status, tags, or sphere.

**Returns:** list of matching study dicts.

### `validate(study: dict) -> dict`

Validate a study registration for completeness.

**Checks:** required fields (`title`, `repo`, `sphere`), valid sphere code, valid repo URL.

**Returns:** `{"valid": bool, "warnings": list[str]}`

---

## Innovation

studyreg is **the first lightweight, programmable study registry client** for computational science:

1. **Pre-registration as code** — register studies with a function call, not a web form
2. **Built-in validation** — catch missing fields and invalid entries before they propagate
3. **SET-aware** — every study is tagged with its sphere (Science/Entrepreneurship/Technology), enabling cross-domain discovery
4. **Zero infrastructure** — no database, no server, just Python

Existing registries require web UIs and manual entry. studyreg makes registration scriptable, searchable, and CI/CD-friendly.

---

## License

MIT © K-RnD Lab
