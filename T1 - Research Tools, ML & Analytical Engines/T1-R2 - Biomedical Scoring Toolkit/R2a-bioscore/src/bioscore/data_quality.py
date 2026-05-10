"""Assess dataset quality for completeness and consistency."""
from __future__ import annotations
from pathlib import Path


_DOMAIN_WEIGHTS: dict[str, dict[str, float]] = {
    "oncology": {"completeness": 0.4, "consistency": 0.3, "domain_specific": 0.3},
    "agriculture": {"completeness": 0.35, "consistency": 0.35, "domain_specific": 0.3},
    "general": {"completeness": 0.5, "consistency": 0.5, "domain_specific": 0.0},
}


def _check_csv(source: str) -> dict:
    try:
        import csv
        p = Path(source)
        if not p.exists():
            return {"completeness": 0.0, "consistency": 0.0}

        with open(p, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

        if len(rows) < 2:
            return {"completeness": 0.0, "consistency": 0.0}

        headers = rows[0]
        data_rows = rows[1:]
        total_cells = len(headers) * len(data_rows)

        empty_cells = sum(
            1 for row in data_rows for cell in row if not cell.strip()
        )
        completeness = round(1 - (empty_cells / max(total_cells, 1)), 2)

        col_lengths = [len(row) for row in data_rows]
        consistent = sum(1 for l in col_lengths if l == len(headers))
        consistency = round(consistent / max(len(data_rows), 1), 2)

        return {"completeness": completeness, "consistency": consistency}
    except Exception:
        return {"completeness": 0.0, "consistency": 0.0}


def data_quality(source: str, domain: str = "general") -> dict:
    """Assess a dataset for completeness, consistency, and domain-specific quality.

    Returns dict with ``completeness``, ``consistency``, and ``overall`` (0–1).
    """
    checks = _check_csv(source)
    weights = _DOMAIN_WEIGHTS.get(domain, _DOMAIN_WEIGHTS["general"])

    overall = round(
        checks["completeness"] * weights.get("completeness", 0.5)
        + checks["consistency"] * weights.get("consistency", 0.5),
        2,
    )

    return {
        "completeness": checks["completeness"],
        "consistency": checks["consistency"],
        "overall": overall,
    }
