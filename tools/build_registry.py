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


def infer_status(lower_text: str, entry_type: str) -> str:
    if "starter scaffold" in lower_text or "scaffold" in lower_text:
        return "scaffold"
    if entry_type in {"repository", "lane", "public case"}:
        return "active"
    return "active"


def build_tags(title: str, summary: str, sphere: str, track: str) -> list[str]:
    tags: list[str] = [sphere, track.lower()]
    for token in TOKEN_RE.findall(f"{title} {summary}".lower()):
        if token in STOPWORDS or token in tags:
            continue
        tags.append(token)
        if len(tags) >= 5:
            break
    return tags[:5]


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


def build_entry(repo_name: str, sphere: str, repo_path: Path, readme_path: Path) -> dict:
    rel = readme_path.relative_to(repo_path)
    text = read_text(readme_path)
    title = extract_title(text, rel.parent.name if rel.parent.name else repo_name)
    summary = extract_summary(text)
    lower_text = text.lower()
    track = "Root sphere repo" if rel.as_posix() == "README.md" else extract_track(rel.parts)
    entry_type = infer_entry_type(rel.parts, lower_text)
    status = infer_status(lower_text, entry_type)
    description = repo_description(repo_name) if entry_type == "repository" else ""
    summary = description or summary or title
    links = [
        {"label": "README", "href": github_readme_url(repo_name, rel)},
    ]
    if entry_type == "repository":
        links.insert(0, {"label": "Repo", "href": f"https://github.com/K-RnD-Lab/{repo_name}"})
    elif rel.parent.as_posix():
        links.append({"label": "Folder", "href": github_folder_url(repo_name, rel)})

    return {
        "title": title,
        "sphere": sphere,
        "track": track,
        "entryType": entry_type,
        "status": status,
        "summary": summary,
        "tags": build_tags(title, summary, sphere, track),
        "links": links,
    }


def sort_key(entry: dict) -> tuple:
    sphere_index = REPO_ORDER.index(entry["sphere"])
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
