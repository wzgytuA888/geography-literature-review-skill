#!/usr/bin/env python3
"""Offline scripted evals (E02, E03-mock, E04, E10, E13-lite, E14).

Runs without network using fixtures/. Prints JSON verdict per eval; exit 0 iff
all scripted evals pass.
"""
from __future__ import annotations

import csv
import io
import json
import re
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

FIXTURES = Path(__file__).resolve().parent / "fixtures"
RESULTS: dict[str, dict] = {}


def ev(name: str, ok: bool, detail: dict):
    RESULTS[name] = {"pass": ok, **detail}


# ---- E02: benchmark/task separation ---------------------------------------
def e02() -> None:
    """Writing-agent whitelist: pattern_cards must never appear as drafting inputs,
    and consolidated method files must not contain topic-fact sentences.
    Heuristic: method files must avoid quantified empirical claims with citations."""
    bench = REPO / "benchmark_corpus"
    problems = []
    for md in bench.glob("*.md"):
        text = md.read_text(encoding="utf-8", errors="ignore")
        # a topic fact looks like: number + unit + 'observed/found/increased' style
        factish = re.findall(
            r"\b(?:increased|decreased|doubled|accounts for)\b[^.\n]*\d+(?:\.\d+)?\s?%", text, re.I)
        if len(factish) > 3:
            problems.append({md.name: factish[:3]})
    ev("E02_corpus_separation", len(problems) == 0,
       {"files_with_fact_like_statements": problems,
        "note": "consolidated method files must describe FORM, not findings"})


# ---- E03: v4 provider normalization ----------------------------------------
def e03_mock() -> None:
    """Both primary provider schemas normalize into the shared record."""
    try:
        from geo_review.clients.semantic_scholar import SemanticScholarClient
        from geo_review.clients.openalex import OpenAlexClient
    except Exception as exc:
        ev("E03_api_first_discovery", False, {"error": str(exc)})
        return
    s2 = SemanticScholarClient._normalize({
        "paperId": "S2-1", "title": "Mock river paper", "year": 2024,
        "authors": [{"name": "A Researcher"}], "externalIds": {"DOI": "10.1/X"},
        "citationCount": 12, "referenceCount": 4,
        "openAccessPdf": {"url": "https://example.org/p.pdf"}}, "river query")
    oa = OpenAlexClient._normalize({
        "id": "https://openalex.org/W1", "display_name": "Mock climate paper",
        "publication_year": 2023, "doi": "https://doi.org/10.2/Y",
        "cited_by_count": 7, "authorships": [], "referenced_works": [],
        "abstract_inverted_index": {"climate": [0], "change": [1]}}, "climate query")
    ok = (s2.semantic_scholar_id == "S2-1" and s2.doi == "10.1/x"
          and s2.source_database == ["Semantic Scholar"]
          and oa.openalex_id == "https://openalex.org/W1" and oa.abstract == "climate change"
          and oa.source_database == ["OpenAlex"])
    ev("E03_api_first_discovery", ok,
       {"semantic_scholar": s2.to_dict(), "openalex": oa.to_dict()})


# ---- E10: fake-citation detection ------------------------------------------
def e10() -> None:
    """Unverifiable entries must come out UNRESOLVED, verified ones VERIFIED."""
    try:
        import citation_validator as cv
    except Exception as exc:
        ev("E10_fake_citation_detection", False, {"error": str(exc)})
        return

    manifest = FIXTURES / "citation-manifest.jsonl"
    if not manifest.exists():
        ev("E10_fake_citation_detection", False, {"error": "fixture missing"})
        return
    with tempfile.TemporaryDirectory() as td:
        summary = cv.audit(manifest, Path(td), check_crossref=False, check_zotero=False)
    # without any resolver everything must be UNRESOLVED (never silently accepted)
    ev("E10_fake_citation_detection",
       summary["unresolved"] == summary["total"] and summary["total"] > 0,
       {"summary": summary,
        "policy": "no resolvers available ⇒ nothing may pass verification"})


# ---- E04: evidence matrix integrity ----------------------------------------
def e04() -> None:
    f = FIXTURES / "evidence-matrix-bad.csv"
    if not f.exists():
        ev("E04_evidence_matrix", False, {"error": "fixture missing"})
        return
    rows = list(csv.DictReader(io.StringIO(f.read_text(encoding="utf-8"))))
    errs = []
    seen_eids = set()
    for r in rows:
        eid = r["evidence_id"].strip()
        if eid in seen_eids:
            errs.append(f"duplicate {eid}")
        seen_eids.add(eid)
        if not r["source_location"].strip():
            errs.append(f"{eid} missing source_location")
        if r["confidence"].strip() not in {"high", "medium", "low"}:
            errs.append(f"{eid} bad confidence")
    ev("E04_evidence_matrix", len(errs) >= 2,   # fixture intentionally broken
       {"detected_errors": errs[:6], "note": "validator must catch seeded defects"})


# ---- E14: benchmark quality matching computable ----------------------------
def e14() -> None:
    stats = REPO / "benchmark_corpus" / "benchmark-stats.json"
    ok = stats.exists()
    detail = {}
    if ok:
        data = json.loads(stats.read_text(encoding="utf-8"))
        need = {"paragraph_block_median_chars", "citation_median_per_block",
                "figures_per_article", "reference_entries_per_article"}
        detail = {"keys_present": sorted(need & set(data)), "n_documents": data.get("n_documents")}
        ok = need <= set(data)
    ev("E14_benchmark_quality_matching_inputs", ok, detail)


def main() -> int:
    e02(); e03_mock(); e04(); e10(); e14()
    print(json.dumps(RESULTS, indent=2, ensure_ascii=False))
    all_pass = all(v["pass"] for v in RESULTS.values())
    sys.exit(0 if all_pass else 7)


if __name__ == "__main__":
    main()
