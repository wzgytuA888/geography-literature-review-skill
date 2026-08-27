from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .models import PaperRecord, SearchLogEntry
from .pipeline import build_theme_table


LIST_FIELDS = {name for name, field in PaperRecord.__dataclass_fields__.items()
               if "list" in str(field.type)}


def _flat(record: PaperRecord) -> dict[str, Any]:
    out = record.to_dict()
    for key, value in list(out.items()):
        if isinstance(value, (list, dict)):
            out[key] = json.dumps(value, ensure_ascii=False)
    return out


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or (list(rows[0]) if rows else [])
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def export_review(out_dir: Path, records: list[PaperRecord], logs: list[SearchLogEntry],
                  citation_edges: list[dict] | None = None,
                  dedup_log: list[dict] | None = None) -> dict[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = [r.to_dict() for r in records]
    (out_dir / "literature.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    flat = [_flat(r) for r in records]
    fields = list(PaperRecord.__dataclass_fields__)
    _write_csv(out_dir / "literature.csv", flat, fields)
    _write_csv(out_dir / "search_log.csv",
               [{**log.to_dict(), "filters": json.dumps(log.filters, ensure_ascii=False)} for log in logs],
               list(SearchLogEntry.__dataclass_fields__))
    if dedup_log is not None:
        _write_csv(out_dir / "deduplication_log.csv", dedup_log)

    try:
        from openpyxl import Workbook
        wb = Workbook()
        wb.remove(wb.active)

        def sheet(name: str, rows: list[dict], headers: list[str] | None = None) -> None:
            ws = wb.create_sheet(name)
            headers = headers or (list(rows[0]) if rows else [])
            ws.append(headers)
            for row in rows:
                ws.append([row.get(key) for key in headers])
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions

        sheet("Papers", flat, fields)
        evidence_fields = [
            "report_id", "paper_id", "study_id", "site_ids", "outcome_ids",
            "title", "authors", "year", "journal", "publisher", "volume",
            "issue", "publication_date", "doi", "citation_count",
            "abstract", "research_question", "study_objective", "study_area", "study_location",
            "country", "region", "latitude", "longitude", "climate_zone", "ecosystem_type",
            "data_source", "remote_sensing_dataset", "environmental_dataset", "climate_dataset",
            "method", "statistical_method", "model", "machine_learning_method",
            "environmental_variables", "dependent_variables", "independent_variables",
            "sample_size", "spatial_scale", "spatial_resolution", "temporal_scale",
            "temporal_resolution", "study_period", "main_findings", "mechanism", "limitations",
            "future_research", "research_gap", "include", "exclude_reason", "theme", "notes",
            "extraction_source", "inference", "confidence",
        ]
        sheet("Evidence_Matrix", flat, evidence_fields)
        sheet("Included", [r for r in flat if r.get("include") is True], fields)
        sheet("Excluded", [r for r in flat if r.get("include") is False], fields)
        themes = build_theme_table(records)
        for row in themes:
            row["paper_ids"] = json.dumps(row["paper_ids"], ensure_ascii=False)
        sheet("Themes", themes, ["theme", "paper_count", "paper_ids"])
        sheet("Search_Log", [{**log.to_dict(), "filters": json.dumps(log.filters, ensure_ascii=False)}
                             for log in logs], list(SearchLogEntry.__dataclass_fields__))
        sheet("Citation_Network", citation_edges or [],
              ["seed_paper_id", "paper_id", "direction", "source_database"])
        wb.save(out_dir / "literature_review.xlsx")
    except ImportError:
        pass
    return {"json": str(out_dir / "literature.json"),
            "csv": str(out_dir / "literature.csv"),
            "xlsx": str(out_dir / "literature_review.xlsx")}
