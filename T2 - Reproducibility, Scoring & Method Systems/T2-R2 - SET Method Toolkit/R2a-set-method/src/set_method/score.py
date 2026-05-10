"""Score a project or idea against SET-based frameworks."""
from __future__ import annotations
from .classify import classify


_ORBIT_WEIGHTS: dict[str, float] = {
    "science": 0.25,
    "entrepreneurship": 0.40,
    "technology": 0.35,
}

_SET_WEIGHTS: dict[str, float] = {
    "science": 0.33,
    "entrepreneurship": 0.33,
    "technology": 0.34,
}


def score(source: str, framework: str = "set") -> float:
    """Score a project, document, or idea against a framework.

    Parameters
    ----------
    source : str
        Project description text or path to a markdown file.
    framework : str
        ``"set"`` (default) or ``"orbit"``.

    Returns
    -------
    float
        Score between 0 and 1.
    """
    if framework == "orbit":
        weights = _ORBIT_WEIGHTS
    else:
        weights = _SET_WEIGHTS

    result = classify(source)
    total = 0.0
    for sphere, weight in weights.items():
        total += result.get(sphere, 0) * weight

    return round(total, 2)
