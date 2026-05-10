"""Recommend quests based on personality type and sphere."""
from __future__ import annotations

_QUEST_MAP: dict[str, dict[str, list[str]]] = {
    "fighter": {
        "S": ["S-2", "S-4"],
        "E": ["E-1", "E-3"],
        "T": ["T-1", "T-4"],
    },
    "operator": {
        "S": ["S-3", "S-4"],
        "E": ["E-2", "E-4"],
        "T": ["T-2", "T-3"],
    },
    "accomplisher": {
        "S": ["S-1", "S-3"],
        "E": ["E-1", "E-4"],
        "T": ["T-1", "T-3"],
    },
    "leader": {
        "S": ["S-1", "S-2"],
        "E": ["E-3", "E-4"],
        "T": ["T-3", "T-4"],
    },
    "engineer": {
        "S": ["S-2", "S-3"],
        "E": ["E-1", "E-2"],
        "T": ["T-1", "T-2"],
    },
    "developer": {
        "S": ["S-1", "S-4"],
        "E": ["E-2", "E-3"],
        "T": ["T-2", "T-4"],
    },
}


def recommend(personality: str, sphere: str) -> list[str]:
    """Return recommended quest IDs based on personality type and sphere.

    Parameters
    ----------
    personality : str
        One of ``fighter``, ``operator``, ``accomplisher``, ``leader``,
        ``engineer``, ``developer``.
    sphere : str
        ``S``, ``E``, or ``T``.

    Returns
    -------
    list[str]
        Recommended quest IDs.
    """
    key = personality.lower()
    if key not in _QUEST_MAP:
        raise ValueError(
            f"Unknown personality '{personality}'. "
            f"Choose from: {', '.join(_QUEST_MAP)}"
        )
    sphere_upper = sphere.upper()
    if sphere_upper not in _QUEST_MAP[key]:
        raise ValueError(f"Unknown sphere '{sphere}'. Choose from: S, E, T")
    return _QUEST_MAP[key][sphere_upper]
