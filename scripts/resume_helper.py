#!/usr/bin/env python3
"""Validate user-supplied full texts and resume a paused review run.

``validate-pdf`` validates explicit ``--pdf`` paths. When no paths are supplied,
it scans ``fulltext/user_uploads``. A filename is never identity evidence: a PDF
must be parseable, contain enough extractable text, and match either the expected
DOI in its content or the expected title plus author/year content.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path


AVAILABLE_STATUSES = {"AVAILABLE_LOCAL", "AVAILABLE_ZOTERO", "DOWNLOADED_LEGAL"}
VERIFIED_IDENTITIES = {"verified_automatic", "verified_manual", "verified"}
ACCEPTABLE_TEXT_QUALITY = {"acceptable", "good"}
MIN_READABLE_ALNUM_CHARS = 500
MIN_TITLE_SCORE = 0.90
DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", re.I)
PAUSE_FIELDS = (
    "missing_count", "missing_report_txt", "missing_report_xlsx",
    "fulltext_upload_directory", "paused_because",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def norm_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value or "").casefold()
    return " ".join("".join(ch if ch.isalnum() else " " for ch in value).split())


def norm_title(value: str) -> str:
    return norm_text(value)


def norm_doi(value: str) -> str:
    value = (value or "").strip().casefold()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value)
    return value.rstrip(".,;)")


def safe_report_id(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", value or "report").strip("-.")
    return cleaned[:80] or "report"


def inspect_pdf(pdf: Path) -> dict:
    """Return extracted text and deterministic readability diagnostics."""
    try:
        from pypdf import PdfReader
        reader = PdfReader(str(pdf))
        if reader.is_encrypted:
            try:
                unlocked = reader.decrypt("")
            except Exception:
                unlocked = 0
            if not unlocked:
                return {"ok": False, "reason": "encrypted PDF cannot be read",
                        "page_count": 0, "text_quality": "unreadable"}
        page_count = len(reader.pages)
        if page_count < 1:
            return {"ok": False, "reason": "PDF has no pages", "page_count": 0,
                    "text_quality": "unreadable"}
        metadata = reader.metadata or {}
        metadata_text = " ".join(str(value) for value in metadata.values() if value)
        pages: list[str] = []
        failed_pages = 0
        for page in reader.pages:
            try:
                pages.append(page.extract_text() or "")
            except Exception:
                pages.append("")
                failed_pages += 1
    except Exception as exc:
        return {"ok": False, "reason": f"unparseable PDF: {type(exc).__name__}: {exc}",
                "page_count": 0, "text_quality": "unreadable"}

    normalized_pages = [" ".join(page.split()) for page in pages]
    text = "\n\f\n".join(normalized_pages).strip()
    readable_chars = sum(ch.isalnum() for ch in text)
    nonempty_pages = sum(
        sum(ch.isalnum() for ch in page) >= 40 for page in normalized_pages
    )
    if readable_chars < MIN_READABLE_ALNUM_CHARS or nonempty_pages < 1:
        return {
            "ok": False,
            "reason": (
                "insufficient extractable text; PDF may be blank, damaged, or scanned "
                "without OCR"
            ),
            "text": text,
            "metadata_text": metadata_text,
            "page_count": page_count,
            "readable_chars": readable_chars,
            "nonempty_pages": nonempty_pages,
            "failed_pages": failed_pages,
            "text_quality": "unreadable",
        }
    coverage = nonempty_pages / page_count
    quality = "good" if readable_chars >= 2000 and coverage >= 0.5 else "acceptable"
    return {
        "ok": True,
        "reason": "",
        "text": text,
        "metadata_text": metadata_text,
        "page_count": page_count,
        "readable_chars": readable_chars,
        "nonempty_pages": nonempty_pages,
        "failed_pages": failed_pages,
        "text_quality": quality,
    }


def title_score(expected: str, content: str) -> float:
    title = norm_title(expected)
    body = norm_text(content[:20000])
    if not title or not body:
        return 0.0
    if title in body:
        return 1.0
    title_tokens = title.split()
    body_tokens = body.split()
    if len(title_tokens) <= 1:
        return 0.0
    width = len(title_tokens)
    best = 0.0
    for start in range(0, min(len(body_tokens), 500)):
        window = " ".join(body_tokens[start:start + width + 3])
        best = max(best, SequenceMatcher(None, title, window).ratio())
        if best >= 0.98:
            break
    body_token_set = set(body_tokens[:800])
    coverage = sum(token in body_token_set for token in title_tokens) / len(title_tokens)
    return max(best, coverage)


def author_tokens(authors: str) -> list[str]:
    ignored = {"and", "the", "author", "authors", "et", "al"}
    tokens = [token for token in norm_text(authors).split()
              if len(token) >= 3 and token not in ignored and not token.isdigit()]
    return sorted(set(tokens), key=lambda item: (-len(item), item))


def identity_from_content(row: dict, text: str,
                          metadata_text: str = "") -> tuple[bool, float, str]:
    """Verify DOI-in-content or title plus author/year-in-content."""
    expected_doi = norm_doi(str(row.get("doi") or ""))
    # Restrict DOI matching to PDF metadata and front matter. Searching the full
    # document could falsely match a target DOI that appears only in references.
    doi_identity_zone = f"{metadata_text}\n{text[:12000]}"
    content_dois = {norm_doi(match.group(1))
                    for match in DOI_RE.finditer(doi_identity_zone)}
    if expected_doi and expected_doi in content_dois:
        return True, 1.0, "doi_in_pdf_text"

    score = title_score(str(row.get("title") or ""), text)
    if score < MIN_TITLE_SCORE:
        return False, score, "title_not_matched_in_pdf_text"

    front = norm_text(text[:12000])
    expected_authors = author_tokens(str(row.get("authors") or ""))
    matched_authors = [token for token in expected_authors if token in front]
    expected_year = str(row.get("year") or "").strip()
    year_match = bool(re.fullmatch(r"(?:19|20)\d{2}", expected_year)
                      and re.search(rf"\b{re.escape(expected_year)}\b", text[:12000]))
    if not matched_authors and not year_match:
        return False, score, "title_matched_but_author_or_year_not_found_in_pdf_text"
    details = ["title_in_pdf_text"]
    if matched_authors:
        details.append("author_in_pdf_text")
    if year_match:
        details.append("year_in_pdf_text")
    return True, score, "+".join(details)


def verify_pdf_against_missing(pdf: Path, missing: list[dict]) -> tuple[dict | None, dict]:
    inspection = inspect_pdf(pdf)
    if not inspection.get("ok"):
        return None, inspection
    best_row = None
    best_score = 0.0
    best_basis = "no_bibliographic_content_match"
    for row in missing:
        matched, score, basis = identity_from_content(
            row, inspection["text"], inspection.get("metadata_text", "")
        )
        if matched and score >= best_score:
            best_row, best_score, best_basis = row, score, basis
    inspection["identity_score"] = best_score
    inspection["identity_basis"] = best_basis
    if best_row is None:
        inspection["reason"] = (
            "readable PDF, but DOI or title plus author/year was not matched in PDF content"
        )
    return best_row, inspection


def match_pdf(pdf: Path, missing: list[dict]) -> tuple[dict | None, float]:
    """Compatibility wrapper; matching is content-based and never filename-based."""
    row, inspection = verify_pdf_against_missing(pdf, missing)
    return row, float(inspection.get("identity_score") or 0.0)


def resolve_run_path(run_dir: Path, value: str) -> Path:
    path = Path(value)
    return path if path.is_absolute() else run_dir / path


def registry_entry_is_verified(run_dir: Path, row: dict) -> bool:
    if str(row.get("fulltext_status") or "") not in AVAILABLE_STATUSES:
        return False
    if str(row.get("identity_verified") or "").strip().casefold() not in VERIFIED_IDENTITIES:
        return False
    if not str(row.get("identity_basis") or "").strip():
        return False
    if str(row.get("text_quality") or "").strip().casefold() not in ACCEPTABLE_TEXT_QUALITY:
        return False
    try:
        if int(row.get("page_count") or 0) < 1:
            return False
    except (TypeError, ValueError):
        return False
    local_value = str(row.get("local_path") or row.get("local_pdf") or "").strip()
    text_value = str(row.get("extracted_text_path") or "").strip()
    expected_sha = str(row.get("sha256") or "").strip().casefold()
    if not local_value or not text_value or not expected_sha:
        return False
    local_path = resolve_run_path(run_dir, local_value)
    text_path = resolve_run_path(run_dir, text_value)
    if not local_path.is_file() or not text_path.is_file():
        return False
    if hashlib.sha256(local_path.read_bytes()).hexdigest().casefold() != expected_sha:
        return False
    extracted = text_path.read_text(encoding="utf-8", errors="ignore")
    return sum(ch.isalnum() for ch in extracted) >= MIN_READABLE_ALNUM_CHARS


def load_missing(run_dir: Path) -> list[dict]:
    rows: list[dict] = []
    screening = (run_dir / "screening/adjudicated.csv"
                 if (run_dir / "screening/adjudicated.csv").exists()
                 else run_dir / "screening.csv")
    if screening.exists():
        with screening.open(encoding="utf-8-sig") as handle:
            rows = [dict(row) for row in csv.DictReader(handle)]
    registry_path = run_dir / "fulltext/fulltext-registry.csv"
    by_report: dict[str, dict] = {}
    if registry_path.exists():
        with registry_path.open(encoding="utf-8-sig") as handle:
            by_report = {str(row.get("report_id") or ""): dict(row)
                         for row in csv.DictReader(handle)}
    missing: list[dict] = []
    for row in rows:
        report_id = str(row.get("report_id") or row.get("record_id") or "")
        merged = {**row, **{key: value for key, value in by_report.get(report_id, {}).items()
                            if value not in (None, "")}}
        included = (
            merged.get("screening_status") in {
                "INCLUDED", "INCLUDED_PENDING_FULLTEXT", "HIGH_PRIORITY_PENDING_FULLTEXT"
            }
            or str(merged.get("decision") or "").casefold() in {"include", "included"}
            or str(merged.get("include") or "").casefold() in {"true", "1", "yes"}
        )
        if included and not registry_entry_is_verified(run_dir, merged):
            missing.append(merged)
    return missing


def unique_pdf_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique: list[Path] = []
    for path in paths:
        key = str(path.resolve(strict=False)).casefold()
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def update_csv_records(run_dir: Path, matched: list[dict]) -> None:
    if not matched:
        return
    by_report = {item["report_id"]: item for item in matched if item.get("report_id")}
    by_paper = {item["paper_id"]: item for item in matched if item.get("paper_id")}
    screening = (run_dir / "screening/adjudicated.csv"
                 if (run_dir / "screening/adjudicated.csv").exists()
                 else run_dir / "screening.csv")
    if screening.exists():
        with screening.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or [])
            rows = list(reader)
        for row in rows:
            item = by_report.get(row.get("report_id") or row.get("record_id")) \
                or by_paper.get(row.get("paper_id"))
            if item:
                row["fulltext_status"] = "AVAILABLE_LOCAL"
                row["local_pdf"] = item["pdf"]
        for field in ("fulltext_status", "local_pdf"):
            if field not in fields:
                fields.append(field)
        with screening.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    registry = run_dir / "fulltext/fulltext-registry.csv"
    registry.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    fields: list[str] = []
    if registry.exists():
        with registry.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = list(reader.fieldnames or [])
            rows = list(reader)
    existing = {row.get("report_id"): row for row in rows}
    for report_id, item in by_report.items():
        row = existing.get(report_id)
        if row is None:
            row = {"report_id": report_id}
            rows.append(row)
            existing[report_id] = row
        row.update({
            "fulltext_status": "AVAILABLE_LOCAL",
            "local_path": item["pdf"],
            "sha256": item["sha256"],
            "identity_verified": "verified_automatic",
            "identity_basis": item["identity_basis"],
            "page_count": str(item["page_count"]),
            "text_quality": item["text_quality"],
            "extracted_text_path": item["extracted_text_path"],
        })
    required_fields = [
        "report_id", "evidence_id", "importance_tier", "fulltext_status",
        "access_route", "final_url", "local_path", "sha256",
        "license_or_provenance", "identity_verified", "identity_basis",
        "page_count", "text_quality", "extracted_text_path", "claim_restriction",
    ]
    for field in required_fields:
        if field not in fields:
            fields.append(field)
    with registry.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_state(run_dir: Path) -> dict:
    path = run_dir / "state.json"
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except Exception:
        return {}


def write_state(run_dir: Path, state: dict) -> None:
    (run_dir / "state.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8"
    )


def update_resume_state(run_dir: Path, still_blocking: bool, missing_count: int,
                        matched_count: int, unmatched_count: int) -> None:
    state = read_state(run_dir)
    previous_pause = (
        state.get("status") == "PAUSED_WAITING_FOR_USER_FULLTEXT"
        or state.get("missing_fulltext_gate") == "TRIGGERED"
        or bool(state.get("paused_because"))
    )
    stages = dict(state.get("stages") or {})
    state.pop("stage", None)
    state.update({
        "resume_event": "validate-pdf",
        "matched_count": matched_count,
        "unmatched_count": unmatched_count,
        "updated_at": utc_now(),
    })
    if still_blocking:
        state.update({
            "status": "PAUSED_WAITING_FOR_USER_FULLTEXT",
            "missing_fulltext_gate": "TRIGGERED",
            "current_stage": "fulltext_acquisition",
            "missing_count": missing_count,
        })
        stages["fulltext"] = "in_progress"
    else:
        if previous_pause:
            event = {field: state.get(field) for field in PAUSE_FIELDS
                     if state.get(field) is not None}
            event.update({
                "status": "PAUSED_WAITING_FOR_USER_FULLTEXT",
                "resolved_at": utc_now(),
                "resolution": "validated_local_fulltext",
                "matched_count": matched_count,
            })
            history = list(state.get("pause_history") or [])
            history.append(event)
            state["pause_history"] = history
        for field in PAUSE_FIELDS:
            state.pop(field, None)
        state.update({
            "status": "RUNNING",
            "missing_fulltext_gate": "CLEAR",
            "current_stage": "extraction",
        })
        stages["fulltext"] = "completed"
        if stages.get("extraction") != "completed":
            stages["extraction"] = "in_progress"
    state["stages"] = stages
    write_state(run_dir, state)


def cmd_validate_pdf(run_dir: Path, pdfs: list[Path]) -> int:
    missing = load_missing(run_dir)
    if not missing:
        update_resume_state(run_dir, False, 0, 0, 0)
        print(json.dumps({
            "gate": "CLEAR",
            "message": "No pending missing items.",
            "next": "resume evidence extraction from checkpoint",
        }, indent=2))
        return 0

    inbox = run_dir / "fulltext/user_uploads"
    inbox.mkdir(parents=True, exist_ok=True)
    auto_scanned = not pdfs
    candidates = unique_pdf_paths(pdfs or sorted(inbox.glob("*.pdf")))
    matched: list[dict] = []
    unmatched: list[dict] = []
    remaining = list(missing)
    if not candidates:
        unmatched.append({"pdf": None, "reason": f"no PDF files found in {inbox}"})

    canonical_pdf_dir = run_dir / "fulltext/pdfs"
    canonical_pdf_dir.mkdir(parents=True, exist_ok=True)
    text_dir = run_dir / "fulltext/text"
    text_dir.mkdir(parents=True, exist_ok=True)
    for pdf in candidates:
        if not pdf.is_file():
            unmatched.append({"pdf": str(pdf), "reason": "file not found"})
            continue
        row, inspection = verify_pdf_against_missing(pdf, remaining)
        if row is None:
            unmatched.append({
                "pdf": str(pdf),
                "reason": inspection.get("reason"),
                "page_count": inspection.get("page_count", 0),
                "text_quality": inspection.get("text_quality", "unreadable"),
                "readable_chars": inspection.get("readable_chars", 0),
                "identity_score": round(float(inspection.get("identity_score") or 0.0), 3),
                "identity_basis": inspection.get("identity_basis", "not_verified"),
            })
            continue

        payload = pdf.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        report_id = str(row.get("report_id") or row.get("record_id") or "report")
        destination = canonical_pdf_dir / (
            f"{safe_report_id(report_id)}_{digest[:12]}_{safe_report_id(pdf.name)}"
        )
        if pdf.resolve() != destination.resolve():
            shutil.copy2(pdf, destination)
        text_path = text_dir / f"{safe_report_id(report_id)}.txt"
        text_path.write_text(inspection["text"] + "\n", encoding="utf-8")
        matched.append({
            "paper_id": row.get("paper_id"),
            "report_id": report_id,
            "pdf": str(destination),
            "sha256": digest,
            "identity_verified": "verified_automatic",
            "identity_basis": inspection["identity_basis"],
            "identity_score": round(float(inspection.get("identity_score") or 0.0), 3),
            "page_count": inspection["page_count"],
            "text_quality": inspection["text_quality"],
            "readable_chars": inspection["readable_chars"],
            "extracted_text_path": str(text_path.relative_to(run_dir)),
        })
        remaining.remove(row)

    update_csv_records(run_dir, matched)
    unresolved = load_missing(run_dir)
    still_blocking = bool(unresolved)
    update_resume_state(run_dir, still_blocking, len(unresolved), len(matched), len(unmatched))
    exact_resume = f'python scripts/resume_helper.py validate-pdf --run-dir "{run_dir}"'
    print(json.dumps({
        "matched": matched,
        "unmatched": unmatched,
        "auto_scanned_upload_directory": str(inbox) if auto_scanned else None,
        "gate": "TRIGGERED" if still_blocking else "CLEAR",
        "next": (
            f"provide readable identity-matching PDFs, then run: {exact_resume}"
            if still_blocking else "resume evidence extraction from checkpoint"
        ),
    }, indent=2, ensure_ascii=False))
    return 5 if still_blocking else 0


def cmd_status(run_dir: Path) -> int:
    print(json.dumps(read_state(run_dir), indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)
    validate = sub.add_parser("validate-pdf")
    validate.add_argument("--run-dir", required=True)
    validate.add_argument(
        "--pdf", nargs="*", default=[],
        help="PDF paths; omit to scan <run-dir>/fulltext/user_uploads/*.pdf",
    )
    status = sub.add_parser("status")
    status.add_argument("--run-dir", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        sys.exit(f"run dir not found: {run_dir}")
    if args.cmd == "validate-pdf":
        return cmd_validate_pdf(run_dir, [Path(path) for path in args.pdf])
    return cmd_status(run_dir)


if __name__ == "__main__":
    raise SystemExit(main())
