from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..http import ResilientClient
from ..models import PaperRecord


FIELDS = ",".join([
    "paperId", "title", "abstract", "authors", "year", "venue",
    "externalIds", "citationCount", "referenceCount", "url", "openAccessPdf",
    "publicationTypes", "publicationDate",
])


class SemanticScholarClient:
    base_url = "https://api.semanticscholar.org/graph/v1"

    def __init__(self, cache_dir: Path, error_log: Path, **kwargs: Any):
        self.http = ResilientClient("Semantic Scholar", cache_dir, error_log,
                                    min_interval=float(os.getenv("SEMANTIC_SCHOLAR_RATE_LIMIT", "1")),
                                    **kwargs)
        key = os.getenv("SEMANTIC_SCHOLAR_API_KEY", "").strip()
        self.headers = {"x-api-key": key} if key else {}

    def search(self, query: str, limit: int = 100, year_lo: int | None = None,
               year_hi: int | None = None) -> list[PaperRecord]:
        rows: list[PaperRecord] = []
        offset = 0
        while len(rows) < limit:
            page_size = min(100, limit - len(rows))
            params: dict[str, Any] = {"query": query, "limit": page_size,
                                      "offset": offset, "fields": FIELDS}
            if year_lo or year_hi:
                params["year"] = f"{year_lo or ''}-{year_hi or ''}"
            data = self.http.request_json("GET", f"{self.base_url}/paper/search",
                                          params=params, headers=self.headers)
            batch = data.get("data", []) if isinstance(data, dict) else []
            rows.extend(self._normalize(item, query=query) for item in batch)
            if not batch or len(batch) < page_size:
                break
            offset += len(batch)
        return rows[:limit]

    def get_paper(self, paper_id_or_doi: str) -> PaperRecord | None:
        identifier = paper_id_or_doi
        if paper_id_or_doi.lower().startswith("10."):
            identifier = f"DOI:{paper_id_or_doi}"
        data = self.http.request_json("GET", f"{self.base_url}/paper/{identifier}",
                                      params={"fields": FIELDS}, headers=self.headers)
        return self._normalize(data, query=f"id:{paper_id_or_doi}") if data else None

    def snowball(self, paper_id: str, direction: str, limit: int = 100) -> list[PaperRecord]:
        endpoint = "references" if direction == "backward" else "citations"
        data = self.http.request_json(
            "GET", f"{self.base_url}/paper/{paper_id}/{endpoint}",
            params={"fields": FIELDS, "limit": min(1000, limit)}, headers=self.headers)
        out: list[PaperRecord] = []
        for edge in data.get("data", []) if isinstance(data, dict) else []:
            item = edge.get("citedPaper" if direction == "backward" else "citingPaper") or {}
            rec = self._normalize(item, query=f"{direction}:{paper_id}")
            rec.discovery_method = "backward_citation" if direction == "backward" else "forward_citation"
            rec.seed_paper_id = paper_id
            out.append(rec)
        return out[:limit]

    @staticmethod
    def _normalize(item: dict[str, Any], query: str) -> PaperRecord:
        ext = item.get("externalIds") or {}
        oa = item.get("openAccessPdf") or {}
        return PaperRecord(
            title=item.get("title") or "",
            authors=[a.get("name", "") for a in item.get("authors") or [] if a.get("name")],
            year=item.get("year"), journal=item.get("venue") or None,
            publication_date=item.get("publicationDate"),
            doi=ext.get("DOI"), semantic_scholar_id=item.get("paperId"),
            citation_count=item.get("citationCount"), reference_count=item.get("referenceCount"),
            abstract=item.get("abstract"), url=item.get("url"),
            open_access_pdf=oa.get("url"), source_database=["Semantic Scholar"],
            search_query=[query],
        )
