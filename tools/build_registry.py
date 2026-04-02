#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Iterable


REPO_ORDER = ["science", "entrepreneurship", "technology"]
SPHERE_CODES = {"science": "S", "entrepreneurship": "E", "technology": "T"}
IGNORE_PARTS = {
    ".git",
    ".github",
    "spaces",
    "docs",
    "tools",
    "dashboard",
    "data",
    "figures",
    "integrations",
    "trainer",
    "app_data",
    "__pycache__",
}
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9-]{2,}")
CODE_RE = re.compile(r"\b([SET]\d(?:-[A-Z])?(?:-R\d+)?)\b")
LINK_RE = re.compile(r"\[([^\]]+)\]\([^)]+\)")
METADATA_RE = re.compile(
    r"^## Registry Metadata\s+```(?:yaml|yml)?\s*(.*?)```",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "from",
    "this",
    "into",
    "across",
    "study",
    "starter",
    "research",
    "template",
    "report",
    "lane",
    "system",
    "systems",
    "sphere",
    "repo",
    "current",
    "question",
    "scope",
    "method",
    "status",
    "what",
    "which",
    "how",
}
SCIENCE_HINTS = {
    "agri",
    "agric",
    "assay",
    "bio",
    "biomedical",
    "biomarker",
    "cancer",
    "clinical",
    "delivery",
    "ecology",
    "environment",
    "genomic",
    "lab",
    "med",
    "metabol",
    "microbiome",
    "neuro",
    "oncology",
    "pathway",
    "plant",
    "rna",
    "soil",
    "therapeutic",
    "translational",
    "variant",
}
ENTREPRENEURSHIP_HINTS = {
    "audience",
    "commercial",
    "ecosystem",
    "founder",
    "growth",
    "market",
    "message",
    "mvp",
    "opportunity",
    "ops",
    "partnership",
    "positioning",
    "product",
    "public case",
    "stakeholder",
    "validation",
    "venture",
    "workflow",
}
TECHNOLOGY_HINTS = {
    "ai",
    "analytics",
    "app",
    "automation",
    "code",
    "dashboard",
    "demo",
    "engine",
    "infrastructure",
    "interface",
    "pipeline",
    "registry",
    "reproducibility",
    "score",
    "scoring",
    "template",
    "tool",
    "workflow",
}
DELIVERY_LABELS = {
    "github": "GitHub",
    "git_hub": "GitHub",
    "hf": "Hugging Face",
    "hugging face": "Hugging Face",
    "hugging_face": "Hugging Face",
    "notion": "Notion",
}


def default_repo_paths() -> dict[str, Path]:
    users_root = Path(__file__).resolve().parents[2]
    return {
        "science": users_root / "sp1repo",
        "entrepreneurship": users_root / "sp2repo",
        "technology": users_root / "sp3repo",
    }


def parse_args() -> argparse.Namespace:
    defaults = default_repo_paths()
    parser = argparse.ArgumentParser(description="Build the cross-sphere study registry JSON.")
    parser.add_argument("--science-path", default=str(defaults["science"]))
    parser.add_argument("--entrepreneurship-path", default=str(defaults["entrepreneurship"]))
    parser.add_argument("--technology-path", default=str(defaults["technology"]))
    parser.add_argument(
        "--output",
        default=str(
            defaults["technology"]
            / "T3 - Dashboards, Interfaces & Open Infrastructure"
            / "T3-R1 - Dashboard Templates & Public Interfaces"
            / "R1a-study-registry-dashboard-template"
            / "dashboard"
            / "data"
            / "registry.json"
        ),
    )
    return parser.parse_args()


def clean_markdown(text: str) -> str:
    text = LINK_RE.sub(r"\1", text)
    text = text.replace("`", "").replace("*", "").replace("_", "")
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def iter_registry_readmes(repo_path: Path, sphere_prefix: str) -> Iterable[Path]:
    for path in sorted(repo_path.rglob("README.md")):
        rel = path.relative_to(repo_path)
        if rel.as_posix() == "README.md":
            yield path
            continue
        if any(part in IGNORE_PARTS for part in rel.parts):
            continue
        if rel.parts and rel.parts[0].startswith(sphere_prefix):
            yield path


def extract_title(text: str, fallback: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return clean_markdown(line[2:])
    return fallback


def extract_summary(text: str) -> str:
    after_title = False
    in_code = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if raw_line.startswith("# "):
            after_title = True
            continue
        if line.startswith("```"):
            in_code = not in_code
            continue
        if not after_title or in_code or not line:
            continue
        if line.startswith(("#", "|", "- ", "* ", ">")) or re.match(r"^\d+\.", line):
            continue
        cleaned = clean_markdown(line)
        if cleaned:
            return cleaned
    return ""


def extract_track(rel_parts: tuple[str, ...]) -> str:
    matches: list[str] = []
    for part in rel_parts:
        matches.extend(CODE_RE.findall(part))
    if matches:
        return matches[-1]
    return rel_parts[0].split(" ")[0]


def infer_entry_type(rel_parts: tuple[str, ...], lower_text: str) -> str:
    if rel_parts == ("README.md",):
        return "repository"
    if "public case" in lower_text:
        return "public case"
    if len(rel_parts) == 2:
        return "lane"
    if any(part.startswith("R") for part in rel_parts):
        return "study"
    return "track"


def infer_status(text: str, entry_type: str) -> str:
    if entry_type in {"repository", "lane", "public case"}:
        return "active"

    status_match = re.search(
        r"^## Status\s+(.*?)(?:\n## |\Z)",
        text,
        re.IGNORECASE | re.MULTILINE | re.DOTALL,
    )
    status_text = status_match.group(1).lower() if status_match else text.lower()
    if "starter scaffold" in status_text or "scaffold" in status_text:
        return "scaffold"
    return "active"


def parse_metadata_value(raw_value: str) -> str | list[str]:
    value = raw_value.strip()
    if value.startswith("[") and value.endswith("]"):
        items = [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
        return items
    return value.strip("\"'")


def extract_registry_metadata(text: str) -> dict[str, str | list[str]]:
    match = METADATA_RE.search(text)
    if not match:
        return {}

    block = match.group(1).strip()
    metadata: dict[str, str | list[str]] = {}
    current_key: str | None = None
    for raw_line in block.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key:
            current_value = metadata.setdefault(current_key, [])
            if isinstance(current_value, list):
                current_value.append(stripped[2:].strip().strip("\"'"))
            continue
        if ":" not in stripped:
            continue
        key, raw_value = stripped.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value:
            metadata[key] = parse_metadata_value(value)
            current_key = None
        else:
            metadata[key] = []
            current_key = key
    return metadata


def normalize_sphere(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip().lower()
    mapping = {
        "s": "science",
        "science": "science",
        "e": "entrepreneurship",
        "entrepreneurship": "entrepreneurship",
        "t": "technology",
        "technology": "technology",
    }
    return mapping.get(cleaned)


def normalize_spheres(values: str | list[str] | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        raw_items = [values]
    else:
        raw_items = values

    normalized: list[str] = []
    for item in raw_items:
        sphere = normalize_sphere(item)
        if sphere and sphere not in normalized:
            normalized.append(sphere)

    return sorted(normalized, key=REPO_ORDER.index)


def normalize_delivery_layers(values: str | list[str] | None) -> list[str]:
    if values is None:
        return ["GitHub"]
    if isinstance(values, str):
        raw_items = [values]
    else:
        raw_items = values

    normalized: list[str] = []
    for item in raw_items:
        key = item.strip().lower().replace("-", " ").replace("_", " ")
        label = DELIVERY_LABELS.get(key, item.strip())
        if label and label not in normalized:
            normalized.append(label)

    return normalized or ["GitHub"]


def canonical_combo(primary_sphere: str, secondary_spheres: list[str]) -> str:
    spheres = sorted({primary_sphere, *secondary_spheres}, key=REPO_ORDER.index)
    return "+".join(SPHERE_CODES[sphere] for sphere in spheres)


def contains_any(signal_text: str, hints: set[str]) -> bool:
    return any(hint in signal_text for hint in hints)


def infer_secondary_spheres(
    sphere: str,
    entry_type: str,
    signal_text: str,
) -> list[str]:
    if entry_type == "repository":
        return []

    secondary: list[str] = []
    if sphere != "science" and contains_any(signal_text, SCIENCE_HINTS):
        secondary.append("science")
    if sphere != "entrepreneurship" and contains_any(signal_text, ENTREPRENEURSHIP_HINTS):
        secondary.append("entrepreneurship")
    if sphere != "technology" and contains_any(signal_text, TECHNOLOGY_HINTS):
        secondary.append("technology")
    return sorted(secondary, key=REPO_ORDER.index)


def infer_artifact_type(sphere: str, entry_type: str, signal_text: str) -> str:
    if entry_type == "repository":
        return "repository"
    if entry_type == "lane":
        return "lane"
    if entry_type == "track":
        return "track"
    if "public case" in signal_text:
        return "public_case"
    if sphere == "science":
        if contains_any(signal_text, TECHNOLOGY_HINTS):
            return "research_tool"
        return "hypothesis"
    if sphere == "entrepreneurship":
        return "venture_case"
    if "dashboard" in signal_text or "registry" in signal_text or "interface" in signal_text:
        return "dashboard"
    if "score" in signal_text or "scoring" in signal_text or "confidence" in signal_text:
        return "scoring_system"
    return "tool"


def infer_validation_stage(status: str, entry_type: str, artifact_type: str, signal_text: str) -> str:
    if "live" in signal_text or "running" in signal_text:
        return "live"
    if status == "scaffold":
        return "scaffold"
    if artifact_type == "hypothesis":
        return "exploratory"
    if artifact_type in {"tool", "research_tool", "scoring_system", "dashboard"}:
        return "prototype"
    if artifact_type in {"public_case", "venture_case"}:
        return "active_case"
    if entry_type in {"repository", "lane", "track"}:
        return "taxonomy"
    return "active"


def build_tags(
    title: str,
    summary: str,
    sphere: str,
    track: str,
    combo: str,
    artifact_type: str,
) -> list[str]:
    tags: list[str] = [sphere, track.lower(), combo.lower(), artifact_type.replace("_", "-")]
    for token in TOKEN_RE.findall(f"{title} {summary}".lower()):
        if token in STOPWORDS or token in tags:
            continue
        tags.append(token)
        if len(tags) >= 7:
            break
    return tags[:7]


def repo_description(repo_name: str) -> str:
    headers = {"User-Agent": "Codex", "Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"https://api.github.com/repos/K-RnD-Lab/{repo_name}"
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            data = json.load(response)
    except urllib.error.URLError:
        return ""
    return data.get("description") or ""


def github_readme_url(repo_name: str, rel_path: Path) -> str:
    base = f"https://github.com/K-RnD-Lab/{repo_name}/blob/main"
    if rel_path.as_posix() == "README.md":
        return f"{base}/README.md"
    return f"{base}/{urllib.request.pathname2url(rel_path.as_posix())}"


def github_folder_url(repo_name: str, rel_path: Path) -> str:
    folder = rel_path.parent.as_posix()
    base = f"https://github.com/K-RnD-Lab/{repo_name}/tree/main"
    return f"{base}/{urllib.request.pathname2url(folder)}"


def metadata_for_entry(
    sphere: str,
    entry_type: str,
    track: str,
    title: str,
    summary: str,
    rel: Path,
    text: str,
    status: str,
) -> dict[str, object]:
    raw_metadata = extract_registry_metadata(text)
    signal_text = clean_markdown(f"{title} {summary} {track} {rel.as_posix()}").lower()

    primary_sphere = normalize_sphere(raw_metadata.get("primary_sphere")) or sphere
    metadata_secondary = normalize_spheres(raw_metadata.get("secondary_spheres"))
    inferred_secondary = infer_secondary_spheres(primary_sphere, entry_type, signal_text)
    secondary_spheres = metadata_secondary or inferred_secondary
    secondary_spheres = [item for item in secondary_spheres if item != primary_sphere]
    secondary_spheres = sorted(secondary_spheres, key=REPO_ORDER.index)

    combo = str(raw_metadata.get("combo") or canonical_combo(primary_sphere, secondary_spheres)).upper()
    artifact_type = str(raw_metadata.get("artifact_type") or infer_artifact_type(primary_sphere, entry_type, signal_text))
    delivery_layers = normalize_delivery_layers(raw_metadata.get("delivery_layers"))
    validation_stage = str(
        raw_metadata.get("validation_stage")
        or infer_validation_stage(status, entry_type, artifact_type, signal_text)
    )

    return {
        "primarySphere": primary_sphere,
        "secondarySpheres": secondary_spheres,
        "combo": combo,
        "artifactType": artifact_type,
        "deliveryLayers": delivery_layers,
        "validationStage": validation_stage,
    }


def build_entry(repo_name: str, sphere: str, repo_path: Path, readme_path: Path) -> dict:
    rel = readme_path.relative_to(repo_path)
    text = read_text(readme_path)
    fallback_title = repo_name if rel.as_posix() == "README.md" else (rel.parent.name if rel.parent.name else repo_name)
    title = extract_title(text, fallback_title)
    if rel.as_posix() == "README.md":
        title = repo_name
    summary = extract_summary(text)
    lower_text = text.lower()
    track = "Root sphere repo" if rel.as_posix() == "README.md" else extract_track(rel.parts)
    entry_type = infer_entry_type(rel.parts, lower_text)
    status = infer_status(text, entry_type)
    description = repo_description(repo_name) if entry_type == "repository" else ""
    summary = description or summary or title
    metadata = metadata_for_entry(sphere, entry_type, track, title, summary, rel, text, status)

    links = [
        {"label": "README", "href": github_readme_url(repo_name, rel)},
    ]
    if entry_type == "repository":
        links.insert(0, {"label": "Repo", "href": f"https://github.com/K-RnD-Lab/{repo_name}"})
    elif rel.parent.as_posix():
        links.append({"label": "Folder", "href": github_folder_url(repo_name, rel)})

    return {
        "title": title,
        "sphere": metadata["primarySphere"],
        "track": track,
        "entryType": entry_type,
        "status": status,
        "summary": summary,
        "tags": build_tags(
            title,
            summary,
            str(metadata["primarySphere"]),
            track,
            str(metadata["combo"]),
            str(metadata["artifactType"]),
        ),
        "links": links,
        **metadata,
    }


def sort_key(entry: dict) -> tuple:
    sphere_index = REPO_ORDER.index(entry["primarySphere"])
    root_rank = 0 if entry["entryType"] == "repository" else 1
    return (sphere_index, root_rank, entry["track"], entry["title"])


def main() -> None:
    args = parse_args()
    repo_paths = {
        "science": Path(args.science_path),
        "entrepreneurship": Path(args.entrepreneurship_path),
        "technology": Path(args.technology_path),
    }
    repo_names = {
        "science": "SPHERE-I-SCIENCE",
        "entrepreneurship": "SPHERE-II-ENTREPRENEURSHIP",
        "technology": "SPHERE-III-TECHNOLOGY",
    }
    prefixes = {"science": "S", "entrepreneurship": "E", "technology": "T"}

    entries: list[dict] = []
    for sphere in REPO_ORDER:
        repo_path = repo_paths[sphere]
        repo_name = repo_names[sphere]
        for readme_path in iter_registry_readmes(repo_path, prefixes[sphere]):
            entries.append(build_entry(repo_name, sphere, repo_path, readme_path))

    entries.sort(key=sort_key)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(entries)} entries to {output_path}")


if __name__ == "__main__":
    main()
