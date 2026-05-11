# set-method

**SET methodology toolkit** — classify, score, and recommend across Science, Entrepreneurship, and Technology spheres.

[![PyPI](https://img.shields.io/pypi/v/set-method.svg)](https://pypi.org/project/set-method/)
[![CI](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY/actions/workflows/test-set-method.yml/badge.svg)](https://github.com/K-RnD-Lab/SPHERE-III-TECHNOLOGY/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Why this exists

Every project lives at the intersection of **Science, Entrepreneurship, and Technology** — but most people can't articulate which sphere dominates their work. This matters because:

- **Mentors** need to direct people to the right starting point
- **Founders** need to understand their venture's DNA before building
- **Programs** need to score and compare ideas objectively

**set-method** gives you a programmatic way to classify, score, and recommend within the SET framework.

## Install

```bash
pip install set-method
```

Requires Python 3.9+. No external dependencies.

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

---

## Target Audience & Daily Use

### 🎓 Mentor / Program Coordinator

**Their morning:** A new member joins the community. They fill out an intro form: "I'm a biology grad, I want to build a startup around crop disease diagnostics." The mentor needs to direct them — learn first? build? research?

**The problem:** Without a framework, mentors give inconsistent advice. One says "go research", another says "start building". The new member gets lost.

**How set-method helps:**
```python
from set_method import classify, recommend

profile = classify("I'm a biology grad, I want to build a startup around crop disease diagnostics")
# → {"science": 0.6, "entrepreneurship": 0.7, "technology": 0.8, "primary": "T"}

quests = recommend(personality="engineer", sphere=profile["primary"])
# → ["T-1", "T-3", "E-2"]
```
They run this **during onboarding**. The classification tells them which sphere to start in. The recommendation gives specific quest IDs the new member should tackle first.

**Install:** `pip install set-method` in the program's onboarding tool or dashboard backend.

---

### 🚀 Startup Founder / Entrepreneur

**Their morning:** Wakes up with an idea. Writes a one-liner. Needs to validate — is this a tech play? a science project? a business? They need to know before committing time.

**The problem:** Most founders over-index on one dimension. A biotech founder thinks only about the science, ignoring go-to-market. A SaaS founder thinks only about code, ignoring research validation.

**How set-method helps:**
```python
from set_method import classify, score

profile = classify("AI-powered platform that matches patients to clinical trials using genomics")
# → {"science": 0.6, "entrepreneurship": 0.7, "technology": 0.8, "primary": "T"}

readiness = score("AI-powered platform that matches patients to clinical trials", framework="orbit")
# → 0.72
```
They paste their idea into a tool powered by set-method. It shows them: "Your idea is 60% science, 70% entrepreneurship, 80% technology — you're under-investing in science validation." The `orbit` framework weights entrepreneurship higher (40%), reflecting venture readiness.

**Install:** `pip install set-method` in their venture planning tool or CLI.

---

### 🧑‍💻 Community Platform Builder

**Their morning:** Building a platform that connects learners, builders, and researchers. Needs to auto-tag content, route users, and suggest next steps.

**The problem:** Manual tagging doesn't scale. Content sits in the wrong category. Users bounce because they can't find relevant material.

**How set-method helps:**
```python
from set_method import classify

# Auto-tag every new piece of content
tag = classify("New tutorial: deploying ML models on edge devices with TensorFlow Lite")
# → {"science": 0.1, "entrepreneurship": 0.2, "technology": 0.9, "primary": "T"}
```
They integrate `classify()` into their **content ingestion pipeline**. Every new article, project, or idea gets auto-tagged with SET sphere weights. Users filter by sphere. The `primary` field routes content to the right hub.

**Install:** Add `set-method` to the platform's backend API dependencies.

---

## API Reference

### `classify(text: str) -> dict`

Classifies input text into SET spheres using keyword matching and heuristics.

**Returns:** dict with `science`, `entrepreneurship`, `technology` scores (0–1) and `primary` sphere label (`S`, `E`, or `T`).

### `score(source: str, framework: str = "set") -> float`

Scores a project, document, or idea against a framework.

**Frameworks:** `"set"` (equal weights) or `"orbit"` (entrepreneurship-weighted).

**Returns:** float 0–1.

### `recommend(personality: str, sphere: str) -> list[str]`

Returns recommended quest IDs based on personality type and sphere.

**Personalities:** `fighter`, `operator`, `accomplisher`, `leader`, `engineer`, `developer`
**Spheres:** `S`, `E`, `T`

**Returns:** list of quest IDs.

---

## Innovation

set-method is **the first programmatic implementation of the SET methodology**:

1. **Automated sphere classification** — no manual tagging, NLP-based keyword matching with weighted scoring
2. **Dual framework scoring** — `set` for balanced assessment, `orbit` for venture-readiness emphasis
3. **Personality-quest mapping** — connects who you are (personality type) with what you should do (quest), grounded in the SET sphere

No other toolkit operationalizes the Science-Entrepreneurship-Technology framework as installable software.

---

## License

MIT © K-RnD Lab
