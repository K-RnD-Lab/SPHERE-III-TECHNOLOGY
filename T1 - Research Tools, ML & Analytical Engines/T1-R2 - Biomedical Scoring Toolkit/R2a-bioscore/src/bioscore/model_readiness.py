"""Evaluate ML model readiness for production deployment."""
from __future__ import annotations
from pathlib import Path
import pickle
import re


_READINESS_CHECKS = {
    "validation_split": {"weight": 0.15},
    "bias_audit": {"weight": 0.15},
    "performance_metrics": {"weight": 0.15},
    "version_tag": {"weight": 0.10},
    "input_schema": {"weight": 0.15},
    "error_handling": {"weight": 0.10},
    "documentation": {"weight": 0.10},
    "test_coverage": {"weight": 0.10},
}


def _inspect_pickle(source: str) -> dict:
    p = Path(source)
    if not p.exists():
        return {"artifact_type": "unknown", "checks_passed": {}}

    try:
        with open(p, "rb") as f:
            obj = pickle.load(f)
        obj_str = str(obj)
    except Exception:
        return {"artifact_type": "unreadable", "checks_passed": {}}

    checks_passed: dict[str, bool] = {}
    checks_passed["validation_split"] = bool(re.search(r"val|valid|test_split", obj_str, re.IGNORECASE))
    checks_passed["bias_audit"] = bool(re.search(r"bias|fairness|parity", obj_str, re.IGNORECASE))
    checks_passed["performance_metrics"] = bool(re.search(r"accuracy|f1|auc|precision|recall|score", obj_str, re.IGNORECASE))
    checks_passed["version_tag"] = bool(re.search(r"version|v\d", obj_str, re.IGNORECASE))
    checks_passed["input_schema"] = bool(re.search(r"schema|feature_names|columns|input", obj_str, re.IGNORECASE))
    checks_passed["error_handling"] = bool(re.search(r"try|except|error|raise", obj_str, re.IGNORECASE))
    checks_passed["documentation"] = bool(re.search(r"doc|description|readme", obj_str, re.IGNORECASE))
    checks_passed["test_coverage"] = bool(re.search(r"test|coverage", obj_str, re.IGNORECASE))

    return {"artifact_type": type(obj).__name__, "checks_passed": checks_passed}


def model_readiness(source: str) -> dict:
    """Evaluate an ML model artifact for production readiness.

    Returns dict with ``score`` (0–1), ``ready`` (bool), and ``gaps`` (list of missing items).
    """
    result = _inspect_pickle(source)
    checks = result.get("checks_passed", {})

    score = 0.0
    gaps = []
    for check_name, cfg in _READINESS_CHECKS.items():
        if checks.get(check_name, False):
            score += cfg["weight"]
        else:
            gaps.append(check_name.replace("_", " "))

    score = round(min(score, 1.0), 2)
    ready = score >= 0.7

    return {"score": score, "ready": ready, "gaps": gaps}
