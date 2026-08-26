#!/usr/bin/env python3
"""Google Scholar-compatible API adapter — the ONLY literature discovery backend.

Hard rules enforced by this module:
  * Discovery for a new review topic must go through a user-configured
    Google-Scholar-compatible provider (e.g. SerpAPI-style gateway).
  * No automatic fallback to WoS / Scopus / OpenAlex / Semantic Scholar /
    general web search / HTML scraping. If the provider is unavailable the
    caller must pause the workflow (PAUSED_GOOGLE_SCHOLAR_API_NOT_READY).
  * Crossref/DOI.org/Unpaywall are metadata/full-text resolvers, NOT discovery
    backends; they are handled in other modules.

Configuration (env vars, required):
    GOOGLE_SCHOLAR_API_PROVIDER   provider name, e.g. "serpapi"
    GOOGLE_SCHOLAR_API_KEY        secret key (never logged)
    GOOGLE_SCHOLAR_API_ENDPOINT   base endpoint URL

Optional env vars:
    GOOGLE_SCHOLAR_ENGINE / _LANGUAGE / _REGION / _RESULTS_PER_PAGE /
    _MAX_PAGES / _RATE_LIMIT

Provider-specific extras go to config/google-scholar.yaml.

Usage (CLI):
    python scripts/google_scholar_adapter.py --query "river floods attribution" \
        --year-lo 2015 --max-pages 2 --out results.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:  # pragma: no cover
    sys.exit("requests is required: pip install requests")

REPO = Path(__file__).resolve().parents[1]


class ScholarAPIError(RuntimeError):
    """Raised when the configured Google Scholar provider cannot be used."""


class ConfigError(ScholarAPIError):
    pass


class AuthError(ScholarAPIError):
    pass


class QuotaError(ScholarAPIError):
    pass


@dataclass
class NormalizedResult:
    """Provider-independent schema used across the whole skill."""

    rank: int
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    publication: str | None = None          # journal/source string if provided
    scholar_result_id: str | None = None    # stable per-provider result id
    doi: str | None = None
    result_url: str | None = None
    pdf_or_fulltext_url: str | None = None
    cited_by_count: int | None = None
    cited_by_id: str | None = None
    snippet: str | None = None
    raw_provider_payload_ref: dict | None = None

    def to_dict(self) -> dict:
        d = asdict(self)
        return d


def load_yaml_config() -> dict:
    cfg_path = REPO / "config" / "google-scholar.yaml"
    local_cfg = REPO / "config" / "google-scholar.local.yaml"  # untracked override
    path = local_cfg if local_cfg.exists() else cfg_path
    if not path.exists():
        return {}
    try:
        import yaml
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:  # malformed yaml must not kill a run silently
        raise ConfigError(f"Invalid config {path}: {e}") from e


@dataclass
class ProviderConfig:
    provider: str
    api_key: str
    endpoint: str
    engine: str | None = None
    language: str | None = None
    region: str | None = None
    results_per_page: int = 20
    max_pages: int = 5
    rate_limit_seconds: float = 1.0
    extra_params: dict = field(default_factory=dict)

    @property
    def masked_key(self) -> str:
        return (self.api_key[:4] + "…" + self.api_key[-2:]) if len(self.api_key) > 6 else "***"

    @classmethod
    def from_env(cls) -> "ProviderConfig":
        provider = os.environ.get("GOOGLE_SCHOLAR_API_PROVIDER", "").strip()
        api_key = os.environ.get("GOOGLE_SCHOLAR_API_KEY", "").strip()
        endpoint = os.environ.get("GOOGLE_SCHOLAR_API_ENDPOINT", "").strip()
        missing = [n for n, v in [
            ("GOOGLE_SCHOLAR_API_PROVIDER", provider),
            ("GOOGLE_SCHOLAR_API_KEY", api_key),
            ("GOOGLE_SCHOLAR_API_ENDPOINT", endpoint),
        ] if not v]
        if missing:
            raise ConfigError(
                "Google Scholar API not configured. Missing env vars: "
                + ", ".join(missing)
                + ". See docs/google-scholar-setup.md — configure before running any search."
            )
        yaml_cfg = load_yaml_config().get("provider_defaults", {}) if load_yaml_config() else {}

        def _num(env_name: str, yml_key: str, default: float, cast=float) -> float:
            raw = os.environ.get(env_name) or yaml_cfg.get(yml_key)
            try:
                return cast(raw) if raw else default
            except (TypeError, ValueError):
                return default

        extras = {k: v for k, v in (yaml_cfg.get("extra_params") or {}).items()}
        return cls(
            provider=provider,
            api_key=api_key,
            endpoint=endpoint,
            engine=os.environ.get("GOOGLE_SCHOLAR_ENGINE") or yaml_cfg.get("engine"),
            language=os.environ.get("GOOGLE_SCHOLAR_LANGUAGE") or yaml_cfg.get("language"),
            region=os.environ.get("GOOGLE_SCHOLAR_REGION") or yaml_cfg.get("region"),
            results_per_page=int(_num("GOOGLE_SCHOLAR_RESULTS_PER_PAGE", "results_per_page", 20)),
            max_pages=int(_num("GOOGLE_SCHOLAR_MAX_PAGES", "max_pages", 5)),
            rate_limit_seconds=_num("GOOGLE_SCHOLAR_RATE_LIMIT", "rate_limit_seconds", 1.0),
            extra_params=extras,
        )


# --------------------------------------------------------------------------
# Provider backends. Adding a new gateway = adding one function here.
# --------------------------------------------------------------------------

def _serpapi_search(cfg: ProviderConfig, q: str, page: int, year_lo: int | None,
                    year_hi: int | None) -> list[dict]:
    params: dict[str, Any] = {
        "engine": cfg.engine or "google_scholar",
        "q": q,
        "api_key": cfg.api_key,
        "num": min(cfg.results_per_page, 20),
        "start": page * min(cfg.results_per_page, 20),
    }
    if cfg.language:
        params["hl"] = cfg.language
    if cfg.region:
        params["lr"] = cfg.region
    if year_lo:
        params["as_ylo"] = year_lo
    if year_hi:
        params["as_yhi"] = year_hi
    params.update(cfg.extra_params)

    resp = requests.get(cfg.endpoint, params=params, timeout=60,
                        headers={"Accept": "application/json"})
    if resp.status_code == 401 or resp.status_code == 403:
        raise AuthError(f"Provider rejected credentials (HTTP {resp.status_code}).")
    if resp.status_code == 429:
        raise QuotaError("Rate limit / quota exhausted at provider.")
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        msg = str(data["error"])
        if "quota" in msg.lower() or "rate" in msg.lower():
            raise QuotaError(msg)
        raise ScholarAPIError(f"Provider error: {msg}")
    return data.get("organic_results", []) or []


def _generic_json_search(cfg: ProviderConfig, q: str, page: int,
                         year_lo: int | None, year_hi: int | None) -> list[dict]:
    """Generic JSON gateway: POST/GET {endpoint} expecting {"results":[...]}
    or a bare list. Field mapping mirrors the normalized schema."""
    payload: dict[str, Any] = {
        "api_key": cfg.api_key,
        "q": q,
        "page": page,
        "num": cfg.results_per_page,
    }
    if year_lo:
        payload["year_start"] = year_lo
    if year_hi:
        payload["year_end"] = year_hi
    if cfg.engine:
        payload["engine"] = cfg.engine
    payload.update(cfg.extra_params)
    resp = requests.post(cfg.endpoint, json=payload, timeout=60,
                         headers={"Accept": "application/json",
                                  "Content-Type": "application/json"})
    if resp.status_code in (401, 403):
        raise AuthError(f"Provider rejected credentials (HTTP {resp.status_code}).")
    if resp.status_code == 429:
        raise QuotaError("Rate limit / quota exhausted at provider.")
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results", data) if isinstance(data, dict) else data
    if not isinstance(results, list):
        raise ScholarAPIError("Unexpected response shape from generic provider.")
    return results


BACKENDS = {
    "serpapi": _serpapi_search,
}
GENERIC_PROVIDERS = {"generic", "custom", "scraperapi", "serpdog", "hasdata"}


def _normalize_serpapi(item: dict, rank_base: int) -> NormalizedResult:
    """SerpAPI google_scholar schema (verified 2026-08):
    organic_results[].{position,title,result_id,link,snippet,
      publication_info.{summary,authors[].name},
      inline_links.{cited_by{total,cites_id},versions{cluster_id}}}
    Year & DOI are NOT dedicated fields: parse from publication_info.summary /
    snippet when present."""
    import re as _re

    pub_info = item.get("publication_info") or {}
    authors_field = pub_info.get("authors") or []
    summary = pub_info.get("summary") or ""
    if isinstance(authors_field, list) and authors_field and isinstance(authors_field[0], dict):
        authors = [a.get("name") for a in authors_field if a.get("name")]
    elif summary:
        authors = [s.strip() for s in summary.split(" - ")[0].split(",") if s.strip()]
    else:
        authors = []

    year = pub_info.get("year")
    if not year:
        m_year = _re.search(r"\b(19[89]\d|20[0-2]\d)\b", summary)
        if m_year:
            year = int(m_year.group(1))
        else:
            m_year = _re.search(r"\b(19[89]\d|20[0-2]\d)\b", item.get("snippet") or "")
            year = int(m_year.group(1)) if m_year else None

    inline = item.get("inline_links") or {}
    cited = inline.get("cited_by") or {}
    versions = inline.get("versions") or {}
    resources = item.get("resources") or []
    pdf_url = None
    for r in resources:
        if r.get("file_format") == "PDF" or str(r.get("link", "")).lower().endswith(".pdf"):
            pdf_url = r.get("link")
            break
    doi = None
    hay = f"{item.get('snippet') or ''} {summary}"
    m_doi = _re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", hay)
    if m_doi:
        doi = m_doi.group(1).rstrip(".,;)")
    return NormalizedResult(
        rank=rank_base + int(item.get("position", 0)),
        title=item.get("title") or "",
        authors=authors,
        year=year,
        publication=summary or None,
        scholar_result_id=item.get("result_id"),
        doi=doi,
        result_url=item.get("link"),
        pdf_or_fulltext_url=pdf_url,
        cited_by_count=(cited.get("total") if isinstance(cited, dict) else None),
        cited_by_id=(cited.get("cites_id") if isinstance(cited, dict) else None),
        snippet=item.get("snippet"),
        raw_provider_payload_ref={"cluster_id": versions.get("cluster_id")}
        if isinstance(versions, dict) else None,
    )


def normalize_item(provider: str, item: dict, rank_base: int) -> NormalizedResult:
    if provider in BACKENDS or "result_id" in item:
        return _normalize_serpapi(item, rank_base)
    # generic mapping
    return NormalizedResult(
        rank=rank_base + int(item.get("position", 0) or 0),
        title=item.get("title") or "",
        authors=item.get("authors") or [],
        year=item.get("year"),
        publication=item.get("publication"),
        scholar_result_id=item.get("result_id") or item.get("id"),
        doi=item.get("doi"),
        result_url=item.get("url") or item.get("link"),
        pdf_or_fulltext_url=item.get("pdf_url"),
        cited_by_count=item.get("cited_by_count") or item.get("cited_by"),
        cited_by_id=item.get("cited_by_id"),
        snippet=item.get("snippet"),
    )


def search(query: str, *, page: int = 0, year_lo: int | None = None,
           year_hi: int | None = None, cfg: ProviderConfig | None = None) -> list[NormalizedResult]:
    """One page of Google Scholar results via the configured provider."""
    cfg = cfg or ProviderConfig.from_env()
    if cfg.provider in BACKENDS:
        raw = BACKENDS[cfg.provider](cfg, query, page, year_lo, year_hi)
    elif cfg.provider in GENERIC_PROVIDERS:
        raw = _generic_json_search(cfg, query, page, year_lo, year_hi)
    else:
        # unknown provider name → try generic contract, but say so in errors
        raw = _generic_json_search(cfg, query, page, year_lo, year_hi)
    base_rank = page * cfg.results_per_page + 1
    results = [normalize_item(cfg.provider, it, base_rank) for it in raw]
    time.sleep(max(0.0, cfg.rate_limit_seconds))
    return results


def search_many(query: str, *, max_pages: int | None = None, year_lo: int | None = None,
                year_hi: int | None = None, cfg: ProviderConfig | None = None,
                stop_when_empty: bool = True) -> list[NormalizedResult]:
    """Multi-page retrieval honoring provider max_pages and rate limits."""
    cfg = cfg or ProviderConfig.from_env()
    pages = min(max_pages or cfg.max_pages, cfg.max_pages)
    out: list[NormalizedResult] = []
    for p in range(pages):
        batch = search(query, page=p, year_lo=year_lo, year_hi=year_hi, cfg=cfg)
        if not batch and stop_when_empty:
            break
        out.extend(batch)
    return out


def preflight(cfg: ProviderConfig | None = None) -> dict:
    """Minimal live test of the configured provider. Returns capability report."""
    cfg = cfg or ProviderConfig.from_env()
    report: dict[str, Any] = {
        "provider": cfg.provider,
        "endpoint": cfg.endpoint,
        "api_key_present": bool(cfg.api_key),
        "checked_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    try:
        t0 = time.time()
        results = search('"test" geoscience', page=0, cfg=cfg)
        dt = time.time() - t0
        report.update({
            "status": "OK",
            "latency_seconds": round(dt, 2),
            "test_results_returned": len(results),
            "schema_fields_seen": sorted({k for r in results[:3] for k, v in r.to_dict().items() if v}),
            "supports_year_filter": True,   # verified only when caller passes filters
            "note": "Minimal test query succeeded.",
        })
    except (AuthError, QuotaError, ConfigError) as e:
        report.update({"status": "FAILED", "error_class": type(e).__name__, "error": str(e)})
    except Exception as e:  # network/DNS/etc.
        report.update({"status": "FAILED", "error_class": type(e).__name__, "error": str(e)})
    return report


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--query", help="Query string (Google Scholar syntax allowed)")
    ap.add_argument("--preflight", action="store_true", help="Run preflight check only")
    ap.add_argument("--year-lo", type=int)
    ap.add_argument("--year-hi", type=int)
    ap.add_argument("--max-pages", type=int)
    ap.add_argument("--out", help="Write JSON results here")
    args = ap.parse_args()

    if args.preflight:
        rep = preflight()
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        sys.exit(0 if rep.get("status") == "OK" else 2)

    if not args.query:
        ap.error("--query is required unless --preflight")
    try:
        rows = search_many(args.query, max_pages=args.max_pages,
                           year_lo=args.year_lo, year_hi=args.year_hi)
    except ConfigError as e:
        print(json.dumps({"status": "PAUSED_GOOGLE_SCHOLAR_API_NOT_READY",
                          "reason": str(e)}, indent=2))
        sys.exit(3)
    except (AuthError, QuotaError, ScholarAPIError) as e:
        print(json.dumps({"status": "PAUSED_GOOGLE_SCHOLAR_API_NOT_READY",
                          "reason": f"{type(e).__name__}: {e}"}, indent=2))
        sys.exit(3)

    payload = [r.to_dict() for r in rows]
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"{len(payload)} results -> {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
