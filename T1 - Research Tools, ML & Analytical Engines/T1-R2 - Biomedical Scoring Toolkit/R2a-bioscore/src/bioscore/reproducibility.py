"""Evaluate reproducibility of notebooks and scripts."""
from __future__ import annotations
import json
import re
from pathlib import Path


_REPRO_CHECKS = {
    "seed_set": {"pattern": r"random_seed|seed\s*=\s*\d|np\.random\.seed|torch\.manual_seed", "weight": 0.15},
    "version_pinning": {"pattern": r"==\s*[\d.]+|>=\s*[\d.]+", "weight": 0.15},
    "data_source_doc": {"pattern": r"data\s*source|dataset\s*from|load.*from|read_csv|read_excel", "weight": 0.15},
    "output_preserved": {"pattern": r"output", "weight": 0.10},
    "env_spec": {"pattern": r"requirements|environment\.yml|Pipfile|pyproject", "weight": 0.15},
    "comments_present": {"pattern": r"#\s*\S", "weight": 0.10},
    "docstrings": {"pattern": r'"""|\'\'\'', "weight": 0.10},
    "logging": {"pattern": r"logging\.|logger\.|print\(", "weight": 0.10},
}


def _read_source(source: str) -> str:
    p = Path(source)
    if p.suffix == ".ipynb":
        try:
            nb = json.loads(p.read_text(encoding="utf-8"))
            cells = nb.get("cells", [])
            return "\n".join(
                "".join(c.get("source", [])) for c in cells if c.get("cell_type") == "code"
            )
        except Exception:
            return ""
    if p.exists():
        return p.read_text(encoding="utf-8")
    return source


def reproducibility(source: str) -> dict:
    """Evaluate a notebook or script for reproducibility best practices.

    Returns dict with ``score`` (0–1), ``issues`` (list of missing items),
    and ``level`` (``full``, ``partial``, ``minimal``).
    """
    content = _read_source(source)
    if not content:
        return {"score": 0.0, "issues": ["empty or unreadable source"], "level": "minimal"}

    score = 0.0
    issues = []

    for check_name, cfg in _REPRO_CHECKS.items():
        if re.search(cfg["pattern"], content, re.IGNORECASE):
            score += cfg["weight"]
        else:
            issues.append(check_name.replace("_", " "))

    score = round(min(score, 1.0), 2)
    level = "full" if score >= 0.8 else "partial" if score >= 0.5 else "minimal"

    return {"score": score, "issues": issues, "level": level}
