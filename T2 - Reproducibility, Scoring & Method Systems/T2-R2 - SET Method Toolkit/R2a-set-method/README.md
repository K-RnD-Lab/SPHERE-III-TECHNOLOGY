# set-method

Python toolkit for the **SET methodology** — classify, score, and recommend across Science, Entrepreneurship, and Technology spheres.

## Install

```bash
pip install set-method
```

## Quick Start

```python
from set_method import classify, score, recommend

# Classify a project or idea into SET spheres
classify("We're building an AI diagnostic tool for crop disease")
# → {"science": 0.7, "entrepreneurship": 0.8, "technology": 0.9, "primary": "T"}

# Score a venture idea against the SET framework
score("startup_idea.md", framework="orbit")
# → 0.73

# Get recommended quests based on personality type
recommend(personality="engineer", sphere="T")
# → ["T-1", "T-3", "E-2"]
```

## API

### `classify(text: str) -> dict`
Classifies input text into SET spheres using keyword matching and heuristics.

Returns a dict with `science`, `entrepreneurship`, `technology` scores (0–1) and `primary` sphere label.

### `score(source, framework="set") -> float`
Scores a project, document, or idea against a framework.

Supported frameworks: `"set"` (default), `"orbit"`.

Returns a float 0–1.

### `recommend(personality: str, sphere: str) -> list[str]`
Returns recommended quest IDs based on personality type and sphere.

Personality types: `fighter`, `operator`, `accomplisher`, `leader`, `engineer`, `developer`.

Sphere codes: `S`, `E`, `T`.

## License

MIT © K-RnD-Lab
