from __future__ import annotations

import math
import re
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Iterable

from .models import PaperRecord, normalize_title


EXCLUDE_REASONS = {
    "wrong_topic", "wrong_region", "wrong_method", "wrong_population",
    "wrong_time_period", "no_relevant_outcome", "review_article",
    "conference_abstract", "duplicate", "no_abstract", "other",
}


def build_queries(topic: str, keywords: list[str] | None = None,
                  boolean_query: str | None = None, max_queries: int = 8) -> list[str]:
    """Create bounded, reproducible query variants while preserving user input."""
    topic = " ".join(topic.split())
    keys = [" ".join(k.split()) for k in (keywords or []) if k.strip()]
    candidates = [q for q in [boolean_query, topic] if q]
    if len(keys) >= 2:
        candidates.extend(f'"{keys[0]}" AND "{key}"' for key in keys[1:])
    if len(keys) >= 3:
        candidates.append(" AND ".join(f'"{key}"' for key in keys[:3]))
    if keys and topic.lower() not in {k.lower() for k in keys}:
        candidates.append(f'"{topic}" AND "{keys[0]}"')
    out: list[str] = []
    seen: set[str] = set()
    for query in candidates:
        norm = query.casefold()
        if norm not in seen:
            seen.add(norm)
            out.append(query)
        if len(out) >= max_queries:
            break
    return out


def merge_records(primary: PaperRecord, incoming: PaperRecord) -> PaperRecord:
    """Merge provider records without overwriting known values with missing ones."""
    list_fields = {
        "authors", "source_database", "search_query", "topics", "institutions",
        "countries", "data_source", "remote_sensing_dataset", "environmental_dataset",
        "climate_dataset", "method", "statistical_method", "model",
        "machine_learning_method", "environmental_variables", "dependent_variables",
        "independent_variables", "main_findings", "mechanism", "limitations",
        "future_research", "research_gap", "theme",
    }
    for name in primary.__dataclass_fields__:
        current = getattr(primary, name)
        other = getattr(incoming, name)
        if name in list_fields:
            combined = list(current or [])
            for value in other or []:
                if value not in combined:
                    combined.append(value)
            setattr(primary, name, combined)
        elif current in (None, "") and other not in (None, ""):
            setattr(primary, name, other)
    if incoming.citation_count is not None:
        primary.citation_count = max(primary.citation_count or 0, incoming.citation_count)
    if incoming.reference_count is not None:
        primary.reference_count = max(primary.reference_count or 0, incoming.reference_count)
    return primary


def deduplicate(records: Iterable[PaperRecord], title_threshold: float = 0.94
                ) -> tuple[list[PaperRecord], list[dict]]:
    """Deduplicate DOI → S2 ID → OpenAlex ID → normalized title.

    Exact identifiers merge. Borderline title matches remain and are marked as
    possible duplicates instead of being silently deleted.
    """
    unique: list[PaperRecord] = []
    index: dict[tuple[str, str], PaperRecord] = {}
    decisions: list[dict] = []

    for rec in records:
        match = None
        reason = None
        keys = [("doi", rec.doi), ("semantic_scholar_id", rec.semantic_scholar_id),
                ("openalex_id", rec.openalex_id)]
        for kind, value in keys:
            if value and (kind, value.casefold()) in index:
                match, reason = index[(kind, value.casefold())], kind
                break
        title_norm = normalize_title(rec.title)
        if match is None and title_norm and ("title", title_norm) in index:
            match, reason = index[("title", title_norm)], "normalized_title"
        if match is not None:
            merge_records(match, rec)
            decisions.append({"action": "merged", "reason": reason,
                              "kept": match.paper_id, "removed_title": rec.title})
            continue

        # Only flag strong fuzzy matches; keep both records.
        best = None
        best_score = 0.0
        if title_norm:
            for prior in unique:
                score = SequenceMatcher(None, title_norm, normalize_title(prior.title)).ratio()
                if score > best_score:
                    best, best_score = prior, score
        if best is not None and best_score >= 0.86:
            rec.possible_duplicate = True
            rec.duplicate_of = best.paper_id or best.title
            decisions.append({"action": "flagged", "reason": "fuzzy_title",
                              "score": round(best_score, 3), "title": rec.title,
                              "possible_duplicate_of": best.title})

        unique.append(rec)
        for kind, value in keys:
            if value:
                index[(kind, value.casefold())] = rec
        if title_norm:
            index[("title", title_norm)] = rec

    for number, rec in enumerate(unique, 1):
        if not rec.paper_id:
            rec.paper_id = f"P{number:04d}"
    return unique, decisions


def score_relevance(records: list[PaperRecord], topic: str, year_hi: int | None = None) -> None:
    """Transparent triage score, not a quality or authority score.

    55% title/abstract token overlap, 20% recency, 15% log-scaled citation
    count, 10% metadata completeness. It is only a screening aid.
    """
    topic_tokens = {t for t in re.findall(r"\w+", topic.casefold()) if len(t) > 2}
    max_cites = max([r.citation_count or 0 for r in records] + [1])
    newest = year_hi or max([r.year or 0 for r in records] + [1])
    for rec in records:
        text_tokens = set(re.findall(r"\w+", f"{rec.title} {rec.abstract or ''}".casefold()))
        overlap = len(topic_tokens & text_tokens) / max(1, len(topic_tokens))
        recency = max(0.0, 1.0 - max(0, newest - (rec.year or newest - 20)) / 20)
        citation = math.log1p(rec.citation_count or 0) / math.log1p(max_cites)
        completeness = sum(bool(v) for v in [rec.abstract, rec.doi, rec.journal,
                                              rec.authors, rec.open_access_pdf]) / 5
        rec.relevance_score = round(0.55 * overlap + 0.20 * recency +
                                    0.15 * citation + 0.10 * completeness, 4)
        rec.relevance_score_method = (
            "0.55 token_overlap + 0.20 recency_20y + 0.15 log_citations + "
            "0.10 metadata_completeness; triage only, not paper quality")


def apply_screening(records: list[PaperRecord], decisions: dict[str, dict]) -> None:
    for rec in records:
        decision = decisions.get(rec.paper_id)
        if not decision:
            continue
        include = decision.get("include")
        reason = decision.get("exclude_reason")
        if include is False and reason not in EXCLUDE_REASONS:
            raise ValueError(f"Invalid exclude_reason for {rec.paper_id}: {reason}")
        rec.include = bool(include) if include is not None else None
        rec.exclude_reason = reason if include is False else None
        rec.screening_status = "included" if include is True else (
            "excluded" if include is False else decision.get("screening_status", "retrieved"))


def build_theme_table(records: list[PaperRecord]) -> list[dict]:
    groups: dict[str, list[str]] = defaultdict(list)
    for rec in records:
        for theme in rec.theme or rec.topics:
            groups[theme].append(rec.paper_id)
    return [{"theme": theme, "paper_count": len(ids), "paper_ids": ids}
            for theme, ids in sorted(groups.items(), key=lambda item: (-len(item[1]), item[0]))]
