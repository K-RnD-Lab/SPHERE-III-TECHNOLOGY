"""Classify text into SET spheres."""
from __future__ import annotations

_SPHERE_KEYWORDS: dict[str, list[str]] = {
    "science": [
        "research", "study", "hypothesis", "experiment", "biology", "medicine",
        "oncology", "ecology", "neuroscience", "metabolomics", "agtech",
        "sustainability", "green", "clinical", "bio", "med", "life systems",
        "plant", "crop", "diagnostic", "genomic", "proteomic", "dataset",
        "brca", "mirna", "cancer", "tumor", "patient", "trial", "therapy",
        "biomarker", "drug", "pharmaceutical", "epidemiology", "cohort",
    ],
    "entrepreneurship": [
        "venture", "startup", "mvp", "market", "validation", "founder",
        "business", "revenue", "customer", "product", "launch", "growth",
        "ecosystem", "ops", "operating", "canvas", "orbit", "fundraising",
        "investment", "pitch", "traction", "saas", "platform", "monetize",
    ],
    "technology": [
        "code", "engineering", "dashboard", "infrastructure", "api",
        "analytics", "tool", "pipeline", "deployment", "software",
        "algorithm", "framework", "library", "package", "reproducibility",
        "open source", "scoring", "registry", "client",
    ],
}

# Strong science indicators that override technology overlap
_SCIENCE_STRONG = {
    "oncology", "clinical", "biomedical", "brca", "mirna", "cancer",
    "tumor", "patient", "therapy", "biomarker", "drug", "pharmaceutical",
    "epidemiology", "cohort", "trial", "diagnostic", "genomic", "proteomic",
    "medicine", "biology", "neuroscience", "metabolomics", "ecology",
}

# Technology indicators that are NOT also science
_TECH_STRONG = {
    "api", "framework", "library", "package", "deployment", "infrastructure",
    "dashboard", "software", "open source", "registry", "client", "scoring",
}


def _tokenize(text: str) -> list[str]:
    return text.lower().replace("-", " ").replace("_", " ").split()


def classify(text: str) -> dict[str, float | str]:
    """Classify input text into SET spheres.

    Returns dict with ``science``, ``entrepreneurship``, ``technology``
    scores (0–1) and ``primary`` sphere label (``S``, ``E``, or ``T``).
    """
    tokens = _tokenize(text)
    token_set = set(tokens)
    scores: dict[str, float] = {}
    for sphere, keywords in _SPHERE_KEYWORDS.items():
        hits = sum(1 for kw in keywords if kw in token_set or kw in " ".join(tokens))
        scores[sphere] = min(hits / max(len(keywords) * 0.15, 1), 1.0)

    # Boost: strong domain indicators override overlap
    science_strong_hits = sum(1 for kw in _SCIENCE_STRONG if kw in token_set)
    tech_strong_hits = sum(1 for kw in _TECH_STRONG if kw in token_set)
    if science_strong_hits > 0:
        scores["science"] = min(scores["science"] + science_strong_hits * 0.15, 1.0)
    if tech_strong_hits > 0:
        scores["technology"] = min(scores["technology"] + tech_strong_hits * 0.15, 1.0)

    total = sum(scores.values()) or 1.0
    scores = {k: round(v / total, 2) for k, v in scores.items()}

    primary = max(scores, key=scores.get)  # type: ignore[arg-type]
    label = {"science": "S", "entrepreneurship": "E", "technology": "T"}[primary]

    return {**scores, "primary": label}
