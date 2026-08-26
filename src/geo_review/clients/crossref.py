from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from ..http import ResilientClient
from ..models import PaperRecord


class CrossrefClient:
    base_url = "https://api.crossref.org"

    def __init__(self, cache_dir: Path, error_log: Path, **kwargs: Any):
        self.http = ResilientClient("Crossref", cache_dir, error_log,
                                    min_interval=float(os.getenv("CROSSREF_RATE_LIMIT", "0.2")),
                                    **kwargs)
        self.mailto = os.getenv("CROSSREF_MAILTO", "").strip()

    def get_work(self, doi: str) -> PaperRecord | None:
        headers = {"User-Agent": f"geography-literature-review-skill/2.0 ({self.mailto})"}
        data = self.http.request_json("GET", f"{self.base_url}/works/{doi}", headers=headers)
        item = data.get("message") if isinstance(data, dict) else None
        return self._normalize(item, doi) if item else None

    @staticmethod
    def _normalize(item: dict[str, Any], doi: str) -> PaperRecord:
        titles = item.get("title") or []
        containers = item.get("container-title") or []
        year = None
        for key in ("published-print", "published-online", "issued", "created"):
            parts = (item.get(key) or {}).get("date-parts") or []
            if parts and parts[0]:
                year = parts[0][0]
                break
        authors = [" ".join(filter(None, [a.get("given"), a.get("family")]))
                   for a in item.get("author") or []]
        return PaperRecord(
            title=titles[0] if titles else "", authors=authors, year=year,
            journal=containers[0] if containers else None, doi=item.get("DOI") or doi,
            publisher=item.get("publisher"), volume=item.get("volume"),
            issue=item.get("issue"),
            publication_date="-".join(str(v) for v in ((item.get("published") or {})
                                                      .get("date-parts") or [[]])[0]) or None,
            citation_count=item.get("is-referenced-by-count"),
            reference_count=item.get("reference-count"), abstract=item.get("abstract"),
            url=item.get("URL"), source_database=["Crossref"], search_query=[f"doi:{doi}"],
        )
