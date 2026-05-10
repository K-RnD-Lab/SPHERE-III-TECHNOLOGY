"""Study Registry — register, search, and validate computational studies."""
from __future__ import annotations
import json
from datetime import date
from pathlib import Path

_DB: list[dict] = []
_DB_PATH: Path | None = None
_COUNTER = 0


def _load_db(path: str | None = None) -> list[dict]:
    global _DB, _DB_PATH, _COUNTER
    if path:
        _DB_PATH = Path(path)
        if _DB_PATH.exists():
            _DB = json.loads(_DB_PATH.read_text(encoding="utf-8"))
            _COUNTER = len(_DB)
    return _DB


def _save_db() -> None:
    if _DB_PATH:
        _DB_PATH.write_text(json.dumps(_DB, indent=2), encoding="utf-8")


def _next_id() -> str:
    global _COUNTER
    _COUNTER += 1
    return f"STU-{_COUNTER:04d}"


def register(
    title: str,
    repo: str,
    tags: list[str] | None = None,
    sphere: str = "S",
    domain: str = "general",
) -> dict:
    """Register a new computational study.

    Returns dict with ``id``, ``status``, and registration metadata.
    """
    study = {
        "id": _next_id(),
        "title": title,
        "repo": repo,
        "tags": tags or [],
        "sphere": sphere.upper(),
        "domain": domain,
        "status": "registered",
        "date": date.today().isoformat(),
    }
    _DB.append(study)
    _save_db()
    return study


def search(
    domain: str | None = None,
    status: str | None = None,
    tags: list[str] | None = None,
    sphere: str | None = None,
) -> list[dict]:
    """Search registered studies by domain, status, tags, or sphere.

    Returns list of matching study dicts.
    """
    results = _DB
    if domain:
        results = [s for s in results if s.get("domain") == domain]
    if status:
        results = [s for s in results if s.get("status") == status]
    if tags:
        results = [s for s in results if any(t in s.get("tags", []) for t in tags)]
    if sphere:
        results = [s for s in results if s.get("sphere") == sphere.upper()]
    return results


def validate(study: dict) -> dict:
    """Validate a study registration for completeness.

    Returns ``{"valid": bool, "warnings": list[str]}``.
    """
    warnings = []
    required = ["title", "repo", "sphere"]
    for field in required:
        if not study.get(field):
            warnings.append(f"missing required field: {field}")

    if study.get("sphere", "").upper() not in ("S", "E", "T"):
        warnings.append("sphere must be S, E, or T")

    if study.get("repo") and not study["repo"].startswith("http"):
        warnings.append("repo should be a valid URL")

    return {"valid": len(warnings) == 0, "warnings": warnings}
