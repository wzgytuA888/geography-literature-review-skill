#!/usr/bin/env python3
"""API-first, reproducible literature-review acquisition pipeline (v2)."""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))

from geo_review.clients import CrossrefClient, OpenAlexClient, SemanticScholarClient  # noqa: E402
from geo_review.export import export_review  # noqa: E402
from geo_review.http import APIRequestError, load_environment  # noqa: E402
from geo_review.models import PaperRecord, SearchLogEntry, utc_now  # noqa: E402
from geo_review.pipeline import (apply_screening, build_queries, deduplicate,
                                 merge_records, score_relevance)  # noqa: E402


def allocate_per_query_limit(max_papers: int, query_count: int,
                             provider_count: int = 2,
                             candidate_pool_multiplier: float = 4.0,
                             override: int | None = None) -> int:
    if override is not None:
        return max(1, min(1000, override))
    return max(10, min(100, math.ceil(
        max_papers * candidate_pool_multiplier /
        max(1, query_count * provider_count))))


def run_search(args: argparse.Namespace) -> int:
    load_environment(REPO)
    out = Path(args.out_dir)
    cache = out / ".cache"
    errors = out / "errors.log"
    queries = build_queries(args.topic, args.keywords, args.boolean_query, args.max_queries)
    execution_queries = [" ".join(part for part in
                         [query, f'"{args.journal}"' if args.journal else "",
                          f'"{args.author}"' if args.author else ""] if part)
                         for query in queries]
    (out / "search_strategy.json").parent.mkdir(parents=True, exist_ok=True)
    provider_count = 2
    per_query = allocate_per_query_limit(
        args.max_papers, len(queries), provider_count,
        args.candidate_pool_multiplier, args.per_query_limit)
    (out / "search_strategy.json").write_text(json.dumps({
        "topic": args.topic, "keywords": args.keywords, "boolean_query": args.boolean_query,
        "generated_queries": queries, "actual_queries": execution_queries,
        "year_range": [args.year_lo, args.year_hi],
        "language": args.language, "maximum_number_of_papers": args.max_papers,
        "candidate_pool_multiplier": args.candidate_pool_multiplier,
        "per_query_per_provider_limit": per_query,
        "providers": ["Semantic Scholar", "OpenAlex"],
        "coverage_label": "open_discovery_not_exhaustive",
        "generated_at": utc_now(),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    s2 = SemanticScholarClient(cache, errors)
    oa = OpenAlexClient(cache, errors)
    crossref = CrossrefClient(cache, errors)
    records: list[PaperRecord] = []
    logs: list[SearchLogEntry] = []
    for query in execution_queries:
        for database, operation in [
            ("Semantic Scholar", lambda: s2.search(query, per_query, args.year_lo, args.year_hi)),
            ("OpenAlex", lambda: oa.search(query, per_query, args.year_lo, args.year_hi, args.language)),
        ]:
            try:
                found = operation()
                records.extend(found)
                logs.append(SearchLogEntry(database, query,
                    {"language": args.language, "journal": args.journal, "author": args.author},
                    f"{args.year_lo or ''}-{args.year_hi or ''}", len(found)))
            except APIRequestError as exc:
                logs.append(SearchLogEntry(database, query,
                    {"language": args.language, "journal": args.journal, "author": args.author},
                    f"{args.year_lo or ''}-{args.year_hi or ''}", 0, status="error", error=str(exc)))

    if args.doi:
        for doi in args.doi:
            for database, operation in [
                ("Semantic Scholar", lambda d=doi: s2.get_paper(d)),
                ("OpenAlex", lambda d=doi: oa.get_work(d)),
                ("Crossref", lambda d=doi: crossref.get_work(d)),
            ]:
                try:
                    item = operation()
                    if item:
                        records.append(item)
                    logs.append(SearchLogEntry(database, f"doi:{doi}", {}, None, int(bool(item))))
                except APIRequestError as exc:
                    logs.append(SearchLogEntry(database, f"doi:{doi}", {}, None, 0,
                                               status="error", error=str(exc)))

    unique, decisions = deduplicate(records)
    enriched = 0
    for rec in unique[:args.crossref_enrich_limit]:
        if not rec.doi:
            continue
        try:
            meta = crossref.get_work(rec.doi)
            if meta:
                merge_records(rec, meta)
                enriched += 1
            logs.append(SearchLogEntry("Crossref", f"doi:{rec.doi}",
                                       {"role": "metadata_validation"}, None, int(bool(meta))))
        except APIRequestError as exc:
            logs.append(SearchLogEntry("Crossref", f"doi:{rec.doi}",
                                       {"role": "metadata_validation"}, None, 0,
                                       status="error", error=str(exc)))
    score_relevance(unique, args.topic, args.year_hi)
    unique.sort(key=lambda r: (r.relevance_score or 0, r.citation_count or 0), reverse=True)
    unique = unique[:args.max_papers]
    for number, rec in enumerate(unique, 1):
        rec.paper_id = f"P{number:04d}"
        rec.report_id = rec.report_id or f"R{number:04d}"
    paths = export_review(out, unique, logs, dedup_log=decisions)
    print(json.dumps({"status": "complete", "records": len(unique), "queries": len(queries),
                      "crossref_enriched": enriched,
                      "outputs": paths, "errors_logged": errors.exists()}, indent=2, ensure_ascii=False))
    return 0 if unique else 2


def run_snowball(args: argparse.Namespace) -> int:
    load_environment(REPO)
    out = Path(args.out_dir)
    source = Path(args.input)
    records = [PaperRecord.from_dict(row) for row in json.loads(source.read_text(encoding="utf-8"))]
    logs = _load_logs(source.parent / "search_log.csv")
    s2 = SemanticScholarClient(out / ".cache", out / "errors.log")
    expanded: list[PaperRecord] = list(records)
    edges: list[dict] = []
    for seed in records:
        if not seed.semantic_scholar_id:
            continue
        for direction in ("backward", "forward"):
            try:
                found = s2.snowball(seed.semantic_scholar_id, direction, args.limit_per_seed)
                logs.append(SearchLogEntry("Semantic Scholar", f"{direction}:{seed.semantic_scholar_id}",
                                           {"seed_paper_id": seed.paper_id}, None, len(found)))
            except APIRequestError as exc:
                logs.append(SearchLogEntry("Semantic Scholar", f"{direction}:{seed.semantic_scholar_id}",
                                           {"seed_paper_id": seed.paper_id}, None, 0,
                                           status="error", error=str(exc)))
                continue
            expanded.extend(found)
            edges.extend({"seed_paper_id": seed.paper_id, "paper_id": item.semantic_scholar_id,
                          "direction": direction, "source_database": "Semantic Scholar"}
                         for item in found)
    unique, decisions = deduplicate(expanded)
    score_relevance(unique, args.topic)
    s2_to_pid = {r.semantic_scholar_id: r.paper_id for r in unique if r.semantic_scholar_id}
    for edge in edges:
        edge["paper_id"] = s2_to_pid.get(edge["paper_id"], edge["paper_id"])
    export_review(out, unique, logs, citation_edges=edges, dedup_log=decisions)
    print(json.dumps({"status": "complete", "records": len(unique), "edges": len(edges)}, indent=2))
    return 0


def _load_logs(path: Path) -> list[SearchLogEntry]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        try:
            filters = json.loads(row.get("filters") or "{}")
        except json.JSONDecodeError:
            filters = {}
        out.append(SearchLogEntry(
            database=row.get("database", ""), query=row.get("query", ""), filters=filters,
            year_range=row.get("year_range") or None,
            retrieved_count=int(row.get("retrieved_count") or 0),
            retrieved_at=row.get("retrieved_at") or utc_now(), status=row.get("status") or "ok",
            error=row.get("error") or None))
    return out


def run_screen(args: argparse.Namespace) -> int:
    source = Path(args.input)
    records = [PaperRecord.from_dict(row) for row in json.loads(source.read_text(encoding="utf-8"))]
    decisions = json.loads(Path(args.decisions).read_text(encoding="utf-8"))
    if isinstance(decisions, list):
        decisions = {row["paper_id"]: row for row in decisions}
    apply_screening(records, decisions)
    out = Path(args.out_dir)
    export_review(out, records, _load_logs(source.parent / "search_log.csv"))
    summary = {"included": sum(r.include is True for r in records),
               "excluded": sum(r.include is False for r in records),
               "undecided": sum(r.include is None for r in records)}
    print(json.dumps({"status": "complete", **summary}, indent=2))
    return 0


def run_preflight(args: argparse.Namespace) -> int:
    load_environment(REPO)
    out = Path(args.out_dir)
    checks = {}
    for name, operation in [
        ("semantic_scholar", lambda: SemanticScholarClient(out / ".cache", out / "errors.log").search("geography", 1)),
        ("openalex", lambda: OpenAlexClient(out / ".cache", out / "errors.log").search("geography", 1)),
    ]:
        try:
            checks[name] = {"status": "ok", "results": len(operation())}
        except Exception as exc:
            checks[name] = {"status": "error", "error": str(exc)}
    status = "ready" if any(v["status"] == "ok" for v in checks.values()) else "degraded"
    print(json.dumps({"status": status, "checks": checks}, indent=2))
    return 0 if status == "ready" else 2


def run_sentinel_check(args: argparse.Namespace) -> int:
    from difflib import SequenceMatcher
    from geo_review.models import normalize_doi, normalize_title

    literature = json.loads(Path(args.input).read_text(encoding="utf-8"))
    sentinel_path = Path(args.sentinels)
    if sentinel_path.suffix.lower() == ".csv":
        with sentinel_path.open(encoding="utf-8-sig") as handle:
            sentinels = list(csv.DictReader(handle))
    else:
        sentinels = json.loads(sentinel_path.read_text(encoding="utf-8"))
    dois = {normalize_doi(row.get("doi")) for row in literature if row.get("doi")}
    titles = [(row.get("report_id") or row.get("paper_id"),
               normalize_title(row.get("title"))) for row in literature if row.get("title")]
    results = []
    for sentinel in sentinels:
        doi = normalize_doi(sentinel.get("doi"))
        title = normalize_title(sentinel.get("title"))
        matched = bool(doi and doi in dois)
        match_id = None
        score = 1.0 if matched else 0.0
        if not matched and title:
            for candidate_id, candidate in titles:
                candidate_score = SequenceMatcher(None, title, candidate).ratio()
                if candidate_score > score:
                    score, match_id = candidate_score, candidate_id
            matched = score >= args.title_threshold
        results.append({"title": sentinel.get("title"), "doi": doi,
                        "matched": matched, "match_id": match_id,
                        "title_similarity": round(score, 3)})
    retrieved = sum(row["matched"] for row in results)
    recall = retrieved / len(results) if results else 0.0
    report = {"retrieved": retrieved, "total": len(results),
              "recall": round(recall, 4), "minimum_recall": args.minimum_recall,
              "hard_gate": "PASS" if results and recall >= args.minimum_recall else "FAIL",
              "results": results}
    output = Path(args.out) if args.out else Path(args.input).parent / "sentinel-recall.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["hard_gate"] == "PASS" else 8


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    pf = sub.add_parser("preflight")
    pf.add_argument("--out-dir", default="runs/preflight")
    pf.set_defaults(func=run_preflight)
    search = sub.add_parser("search")
    search.add_argument("--topic", required=True)
    search.add_argument("--keywords", nargs="*", default=[])
    search.add_argument("--boolean-query")
    search.add_argument("--year-lo", type=int)
    search.add_argument("--year-hi", type=int)
    search.add_argument("--language")
    search.add_argument("--journal")
    search.add_argument("--author")
    search.add_argument("--doi", nargs="*", default=[])
    search.add_argument("--max-papers", type=int, default=200)
    search.add_argument("--max-queries", type=int, default=8)
    search.add_argument("--candidate-pool-multiplier", type=float, default=4.0,
                        help="Retrieve a larger candidate pool before relevance triage")
    search.add_argument("--per-query-limit", type=int,
                        help="Override records requested per query per provider")
    search.add_argument("--crossref-enrich-limit", type=int, default=25)
    search.add_argument("--out-dir", required=True)
    search.set_defaults(func=run_search)
    snow = sub.add_parser("snowball")
    snow.add_argument("--input", required=True)
    snow.add_argument("--topic", required=True)
    snow.add_argument("--limit-per-seed", type=int, default=50)
    snow.add_argument("--out-dir", required=True)
    snow.set_defaults(func=run_snowball)
    screen = sub.add_parser("screen")
    screen.add_argument("--input", required=True)
    screen.add_argument("--decisions", required=True,
                        help="JSON object keyed by paper_id, or list of decision objects")
    screen.add_argument("--out-dir", required=True)
    screen.set_defaults(func=run_screen)
    sentinel = sub.add_parser("sentinel-check")
    sentinel.add_argument("--input", required=True, help="literature.json")
    sentinel.add_argument("--sentinels", required=True, help="JSON or CSV with title/doi")
    sentinel.add_argument("--minimum-recall", type=float, default=0.8)
    sentinel.add_argument("--title-threshold", type=float, default=0.9)
    sentinel.add_argument("--out")
    sentinel.set_defaults(func=run_sentinel_check)
    return ap


if __name__ == "__main__":
    cli_args = parser().parse_args()
    sys.exit(cli_args.func(cli_args))
