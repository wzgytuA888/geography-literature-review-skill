from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..http import ResilientClient
from ..models import PaperRecord


def abstract_from_index(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    pairs = [(pos, word) for word, positions in index.items() for pos in positions]
    return " ".join(word for _, word in sorted(pairs)) or None


class OpenAlexClient:
    base_url = "https://api.openalex.org"

    def __init__(self, cache_dir: Path, error_log: Path, **kwargs: Any):
        self.http = ResilientClient("OpenAlex", cache_dir, error_log,
                                    min_interval=float(os.getenv("OPENALEX_RATE_LIMIT", "0.2")),
                                    **kwargs)
        self.mailto = os.getenv("OPENALEX_MAILTO", "").strip()

    def search(self, query: str, limit: int = 200, year_lo: int | None = None,
               year_hi: int | None = None, language: str | None = None) -> list[PaperRecord]:
        rows: list[PaperRecord] = []
        cursor = "*"
        while len(rows) < limit:
            filters = []
            if year_lo:
                filters.append(f"from_publication_date:{year_lo}-01-01")
            if year_hi:
                filters.append(f"to_publication_date:{year_hi}-12-31")
            if language:
                filters.append(f"language:{language}")
            params: dict[str, Any] = {"search": query, "per-page": min(200, limit - len(rows)),
                                      "cursor": cursor}
            if filters:
                params["filter"] = ",".join(filters)
            if self.mailto:
                params["mailto"] = self.mailto
            data = self.http.request_json("GET", f"{self.base_url}/works", params=params)
            batch = data.get("results", []) if isinstance(data, dict) else []
            rows.extend(self._normalize(item, query) for item in batch)
            next_cursor = (data.get("meta") or {}).get("next_cursor") if isinstance(data, dict) else None
            if not batch or not next_cursor or next_cursor == cursor:
                break
            cursor = next_cursor
        return rows[:limit]

    def get_work(self, identifier: str) -> PaperRecord | None:
        target = f"https://doi.org/{identifier}" if identifier.lower().startswith("10.") else identifier
        params = {"mailto": self.mailto} if self.mailto else None
        data = self.http.request_json("GET", f"{self.base_url}/works/{target}", params=params)
        return self._normalize(data, f"id:{identifier}") if data else None

    @staticmethod
    def _normalize(item: dict[str, Any], query: str) -> PaperRecord:
        primary = item.get("primary_location") or {}
        source = primary.get("source") or {}
        oa = item.get("best_oa_location") or item.get("open_access") or {}
        authorships = item.get("authorships") or []
        institutions = sorted({i.get("display_name") for a in authorships
                               for i in a.get("institutions") or [] if i.get("display_name")})
        countries = sorted({c for a in authorships for c in a.get("countries") or [] if c})
        return PaperRecord(
            title=item.get("display_name") or item.get("title") or "",
            authors=[(a.get("author") or {}).get("display_name", "") for a in authorships
                     if (a.get("author") or {}).get("display_name")],
            year=item.get("publication_year"), journal=source.get("display_name"),
            publication_date=item.get("publication_date"),
            doi=item.get("doi"), openalex_id=item.get("id"),
            citation_count=item.get("cited_by_count"),
            reference_count=len(item.get("referenced_works") or []),
            abstract=abstract_from_index(item.get("abstract_inverted_index")),
            url=primary.get("landing_page_url") or item.get("id"),
            open_access_pdf=oa.get("pdf_url"), source_database=["OpenAlex"],
            search_query=[query], topics=[t.get("display_name") for t in item.get("topics") or []
                                          if t.get("display_name")],
            institutions=institutions, countries=countries,
        )
