#!/usr/bin/env python3
"""Zotero adapter — Reference Source of Truth integration layer.

Capability detection at import/run time; never assumes an unavailable backend.
Resolution chain for a reference:
    Zotero item → Better BibTeX key/CSL → DOI metadata (Crossref) →
    authoritative metadata record (fallback, flagged unresolved if none)

Backends used:
  * Zotero Web API v3   https://api.zotero.org  (needs ZOTERO_API_KEY + ZOTERO_USER_ID)
  * Zotero local server http://localhost:23119/api/users/0/...  (Zotero 7 desktop)
  * Better BibTeX JSON-RPC http://localhost:23119/better-bibtex/json-rpc

This module NEVER performs topic discovery — that is forbidden (Scholar-only).
"""
from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("requests required: pip install requests")

WEB_API = "https://api.zotero.org"
LOCAL_API = "http://localhost:23119/api"
BBT_RPC = "http://localhost:23119/better-bibtex/json-rpc"


@dataclass
class ZoteroCaps:
    web_api: bool = False
    local_api: bool = False
    better_bibtex: bool = False


class ZoteroAdapter:
    def __init__(self, timeout: int = 20):
        self.timeout = timeout
        self.api_key = os.environ.get("ZOTERO_API_KEY", "").strip()
        self.user_id = os.environ.get("ZOTERO_USER_ID", "").strip()
        self.caps = self.detect_capabilities()

    # ---------------- capability detection ----------------
    def detect_capabilities(self) -> ZoteroCaps:
        caps = ZoteroCaps()
        if self.api_key and self.user_id:
            try:
                r = requests.get(
                    f"{WEB_API}/users/{self.user_id}/items",
                    params={"limit": 1},
                    headers=self._web_headers(),
                    timeout=self.timeout,
                )
                caps.web_api = r.status_code == 200
            except requests.RequestException:
                pass
        try:
            r = requests.get(f"{LOCAL_API}/users/0/items", params={"limit": 1},
                             timeout=5)
            caps.local_api = r.status_code == 200
        except requests.RequestException:
            pass
        if not (caps.web_api or caps.local_api):
            caps.local_api = False
        try:
            payload = {"jsonrpc": "2.0", "method": "item.search",
                       "params": ["capability-probe"], "id": 1}
            r = requests.post(BBT_RPC, json=payload, timeout=5)
            caps.better_bibtex = r.status_code == 200
        except requests.RequestException:
            pass
        return caps

    def _base(self) -> str | None:
        """Pick best available API base."""
        if self.caps.web_api:
            return f"{WEB_API}/users/{self.user_id}"
        if self.caps.local_api:
            return f"{LOCAL_API}/users/0"
        return None

    def _web_headers(self) -> dict:
        h = {}
        if self.api_key:
            h["Zotero-API-Key"] = self.api_key
        h["Zotero-API-Version"] = "3"
        return h

    def available(self) -> bool:
        return bool(self._base())

    # ---------------- core operations ----------------
    def search(self, query: str, limit: int = 25) -> list[dict]:
        base = self._base()
        if not base:
            return []
        r = requests.get(f"{base}/items/top", params={"q": query, "limit": limit,
                                                      "format": "json"},
                         headers=self._web_headers(), timeout=self.timeout)
        r.raise_for_status()
        return [it["data"] for it in r.json()]

    def search_collection(self, collection_key: str, query: str = "",
                          limit: int = 50) -> list[dict]:
        base = self._base()
        if not base:
            return []
        params = {"limit": limit, "format": "json"}
        if query:
            params["q"] = query
        r = requests.get(f"{base}/collections/{collection_key}/items/top",
                         params=params, headers=self._web_headers(),
                         timeout=self.timeout)
        r.raise_for_status()
        return [it["data"] for it in r.json()]

    def get_metadata(self, zotero_key: str) -> dict | None:
        base = self._base()
        if not base:
            return None
        r = requests.get(f"{base}/items/{zotero_key}",
                         params={"format": "json"},
                         headers=self._web_headers(),
                         timeout=self.timeout)
        if r.status_code != 200:
            return None
        return r.json().get("data")

    def get_fulltext(self, zotero_key: str) -> bytes | None:
        """Return attachment file bytes if a PDF child exists."""
        base = self._base()
        if not base:
            return None
        r = requests.get(f"{base}/items/{zotero_key}/children",
                         params={"format": "json"},
                         headers=self._web_headers(), timeout=self.timeout)
        if r.status_code != 200:
            return None
        for child in r.json():
            d = child.get("data", {})
            if d.get("contentType") == "application/pdf" or str(d.get("filename", "")).endswith(".pdf"):
                link_mode = d.get("linkMode")
                if link_mode == "imported_file":
                    dl = requests.get(
                        f"{base}/items/{child['key']}/file",
                        headers=self._web_headers(), timeout=120)
                    if dl.status_code == 200:
                        return dl.content
                elif link_mode == "imported_url":
                    return None  # remote URL handled by caller if legal
        return None

    def resolve_doi(self, doi: str) -> dict | None:
        base = self._base()
        if not base:
            return None
        r = requests.get(f"{base}/items", params={"format": "json",
                                                  "q": f'doi:"{doi}"', "limit": 5},
                         headers=self._web_headers(), timeout=self.timeout)
        if r.status_code != 200:
            return None
        items = r.json()
        for it in items:
            d = it.get("data", {})
            if str(d.get("DOI", "")).lower().rstrip("/") == doi.lower().rstrip("/"):
                return d
        return None

    def get_citation_key(self, zotero_data: dict) -> str | None:
        """Better BibTeX citekey when available; falls back to zotero key."""
        if self.caps.better_bibtex:
            try:
                payload = {"jsonrpc": "2.0", "method": "citationkey",
                           "params": [[f"{self.user_id}:{zotero_data.get('key')}"]]
                           if self.caps.web_api else
                           [["0:" + zotero_data.get("key", "")]],
                           "id": 2}
                r = requests.post(BBT_RPC, json=payload, timeout=10)
                if r.status_code == 200:
                    res = r.json().get("result")
                    if isinstance(res, list) and res:
                        first = res[0]
                        if isinstance(first, dict):
                            return first.get("citationKey") or first.get("citekey")
                        if isinstance(first, str):
                            return first
            except requests.RequestException:
                pass
        return zotero_data.get("key")

    def bibliography_csl(self, zotero_keys: list[str], style: str = "apa") -> str | None:
        base = self._base()
        if not base or not zotero_keys:
            return None
        r = requests.post(f"{base}/items",
                          params={"format": "bib", "style": style,
                                  "contentType": "text/html"},
                          headers={**self._web_headers(),
                                   "Content-Type": "application/json"},
                          json=zotero_keys, timeout=self.timeout)
        if r.status_code == 200:
            return r.text
        return None

    # explicit no-op guards for docx live-field writing
    def insert_docx_citation(self) -> tuple[bool, str]:
        return False, ("Live Zotero Word-field insertion requires the Zotero Word "
                       "plugin GUI; not reliably scriptable. Use pandoc+CSL fallback "
                       "(workflows/zotero-citation.md) and report the limitation.")

    def update_docx_bibliography(self) -> tuple[bool, str]:
        return False, self.insert_docx_citation()[1]


# ---------------- Crossref metadata validation (NOT discovery) ----------------
def crossref_metadata(doi: str, timeout: int = 30) -> dict | None:
    """Metadata validation only. Forbidden as a discovery backend by policy."""
    try:
        r = requests.get(f"https://api.crossref.org/works/{doi}",
                         headers={"User-Agent": "geo-review-skill/1.0 (mailto:user@example.com)"},
                         timeout=timeout)
        if r.status_code == 200:
            return r.json().get("message")
    except requests.RequestException:
        pass
    return None


def main() -> None:
    """CLI probe: prints detected capabilities as JSON."""
    ad = ZoteroAdapter()
    print(json.dumps({
        "web_api": ad.caps.web_api,
        "local_api": ad.caps.local_api,
        "better_bibtex": ad.caps.better_bibtex,
        "usable": ad.available(),
        "note": "If usable=false, citation work falls back to DOI/Crossref metadata; "
                "unresolvable references are reported UNRESOLVED, never invented.",
    }, indent=2))


if __name__ == "__main__":
    main()
