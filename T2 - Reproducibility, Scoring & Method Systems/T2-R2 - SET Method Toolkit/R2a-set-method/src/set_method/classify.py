"""Classify text into SET spheres."""
from __future__ import annotations

_SPHERE_KEYWORDS: dict[str, list[str]] = {
    "science": [
        "research", "study", "hypothesis", "experiment", "biology", "medicine",
        "oncology", "ecology", "neuroscience", "metabolomics", "agtech",
        "sustainability", "green", "clinical", "bio", "med", "life systems",
        "plant", "crop", "diagnostic", "genomic", "proteomic", "dataset",
    ],
    "entrepreneurship": [
        "venture", "startup", "mvp", "market", "validation", "founder",
        "business", "revenue", "customer", "product", "launch", "growth",
        "ecosystem", "ops", "operating", "canvas", "orbit", "fundraising",
        "investment", "pitch", "traction",
    ],
    "technology": [
        "code", "engineering", "dashboard", "infrastructure", "api",
        "analytics", "tool", "pipeline", "deployment", "software",
        "algorithm", "model", "ml", "ai", "data", "scoring", "reproducibility",
        "open source", "framework", "library", "package",
    ],
}


def _tokenize(text: str) -> list[str]:
    return text.lower().replace("-", " ").replace("_", " ").split()


def classify(text: str) -> dict[str, float | str]:
    """Classify input text into SET spheres.

    Returns dict with ``science``, ``entrepreneurship``, ``technology``
    scores (0–1) and ``primary`` sphere label (``S``, ``E``, or ``T``).
    """
    tokens = _tokenize(text)
    scores: dict[str, float] = {}
    for sphere, keywords in _SPHERE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in " ".join(tokens))
        scores[sphere] = min(hits / max(len(keywords) * 0.15, 1), 1.0)

    total = sum(scores.values()) or 1.0
    scores = {k: round(v / total, 2) for k, v in scores.items()}

    primary = max(scores, key=scores.get)  # type: ignore[arg-type]
    label = {"science": "S", "entrepreneurship": "E", "technology": "T"}[primary]

    return {**scores, "primary": label}
