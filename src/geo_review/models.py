from __future__ import annotations

import re
import unicodedata
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    doi = value.strip().lower()
    doi = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", doi)
    doi = re.sub(r"^doi:\s*", "", doi).rstrip(".,;)")
    return doi or None


def normalize_title(value: str | None) -> str:
    text = unicodedata.normalize("NFKC", value or "").lower()
    text = re.sub(r"[^\w\s]|_", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


@dataclass
class PaperRecord:
    paper_id: str = ""
    title: str = ""
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    journal: str | None = None
    publisher: str | None = None
    volume: str | None = None
    issue: str | None = None
    publication_date: str | None = None
    doi: str | None = None
    semantic_scholar_id: str | None = None
    openalex_id: str | None = None
    citation_count: int | None = None
    reference_count: int | None = None
    abstract: str | None = None
    url: str | None = None
    open_access_pdf: str | None = None
    source_database: list[str] = field(default_factory=list)
    search_query: list[str] = field(default_factory=list)
    retrieved_at: str = field(default_factory=utc_now)
    discovery_method: str = "database_search"
    seed_paper_id: str | None = None
    possible_duplicate: bool = False
    duplicate_of: str | None = None
    screening_status: str = "retrieved"
    include: bool | None = None
    exclude_reason: str | None = None
    relevance_score: float | None = None
    relevance_score_method: str | None = None
    topics: list[str] = field(default_factory=list)
    institutions: list[str] = field(default_factory=list)
    countries: list[str] = field(default_factory=list)

    # Evidence Matrix fields. Keep unknowns null; never infer them from a title.
    research_question: str | None = None
    study_objective: str | None = None
    study_area: str | None = None
    study_location: str | None = None
    country: str | None = None
    region: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    climate_zone: str | None = None
    ecosystem_type: str | None = None
    data_source: list[str] = field(default_factory=list)
    remote_sensing_dataset: list[str] = field(default_factory=list)
    environmental_dataset: list[str] = field(default_factory=list)
    climate_dataset: list[str] = field(default_factory=list)
    method: list[str] = field(default_factory=list)
    statistical_method: list[str] = field(default_factory=list)
    model: list[str] = field(default_factory=list)
    machine_learning_method: list[str] = field(default_factory=list)
    environmental_variables: list[str] = field(default_factory=list)
    dependent_variables: list[str] = field(default_factory=list)
    independent_variables: list[str] = field(default_factory=list)
    sample_size: str | None = None
    spatial_scale: str | None = None
    spatial_resolution: str | None = None
    temporal_scale: str | None = None
    temporal_resolution: str | None = None
    study_period: str | None = None
    main_findings: list[dict[str, Any]] = field(default_factory=list)
    mechanism: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    future_research: list[str] = field(default_factory=list)
    research_gap: list[str] = field(default_factory=list)
    theme: list[str] = field(default_factory=list)
    notes: str | None = None
    extraction_source: str | None = None
    inference: bool = False
    confidence: str | None = None

    def __post_init__(self) -> None:
        self.doi = normalize_doi(self.doi)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "PaperRecord":
        allowed = cls.__dataclass_fields__.keys()
        return cls(**{key: value[key] for key in allowed if key in value})


@dataclass
class SearchLogEntry:
    database: str
    query: str
    filters: dict[str, Any]
    year_range: str | None
    retrieved_count: int
    retrieved_at: str = field(default_factory=utc_now)
    status: str = "ok"
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
