from __future__ import annotations

import time
from collections.abc import Iterator

import httpx

OPENALEX_WORKS_URL = "https://api.openalex.org/works"


def reconstruct_abstract(inverted_index: dict[str, list[int]] | None) -> str:
    if not inverted_index:
        return ""
    positioned = [
        (position, word)
        for word, positions in inverted_index.items()
        for position in positions
    ]
    return " ".join(word for _, word in sorted(positioned))


def normalize_work(raw: dict) -> dict | None:
    abstract = reconstruct_abstract(raw.get("abstract_inverted_index"))
    title = (raw.get("display_name") or raw.get("title") or "").strip()
    if not title or len(abstract) < 120:
        return None

    primary_location = raw.get("primary_location") or {}
    source = primary_location.get("source") or {}
    authors = [
        authorship.get("author", {}).get("display_name", "")
        for authorship in raw.get("authorships", [])
    ]
    concepts = [
        topic.get("display_name", "")
        for topic in raw.get("topics", [])[:8]
        if topic.get("display_name")
    ]
    return {
        "work_id": raw["id"].rsplit("/", 1)[-1],
        "title": title,
        "abstract": abstract,
        "year": raw.get("publication_year"),
        "authors": [author for author in authors if author],
        "cited_by_count": raw.get("cited_by_count", 0),
        "doi": raw.get("doi"),
        "url": primary_location.get("landing_page_url") or raw.get("id"),
        "source_name": source.get("display_name"),
        "concepts": concepts,
    }


def fetch_works(
    query: str,
    max_works: int = 240,
    email: str | None = None,
    from_year: int = 2020,
) -> Iterator[dict]:
    headers = {"User-Agent": f"EvidenceGapNavigator/0.1 ({email or 'public-research'})"}
    cursor = "*"
    yielded = 0
    with httpx.Client(timeout=45, headers=headers, follow_redirects=True) as client:
        while cursor and yielded < max_works:
            params = {
                "search": query,
                "filter": f"from_publication_date:{from_year}-01-01,has_abstract:true",
                "select": (
                    "id,display_name,abstract_inverted_index,publication_year,authorships,"
                    "cited_by_count,doi,primary_location,topics"
                ),
                "per-page": min(100, max_works - yielded),
                "cursor": cursor,
            }
            if email:
                params["mailto"] = email
            response = client.get(OPENALEX_WORKS_URL, params=params)
            response.raise_for_status()
            payload = response.json()
            for raw in payload.get("results", []):
                work = normalize_work(raw)
                if work:
                    yield work
                    yielded += 1
                    if yielded >= max_works:
                        break
            cursor = payload.get("meta", {}).get("next_cursor")
            time.sleep(0.12)

