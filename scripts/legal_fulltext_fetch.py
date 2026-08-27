#!/usr/bin/env python3
"""Download identity-linked open-access PDFs into a review run.

Input is a CSV queue (default: fulltext/acquisition-queue.csv). The script only
uses local files, explicit OA/repository URLs, OpenAlex OA locations and optional
Unpaywall OA locations. It never attempts authentication or paywall bypass.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path
from urllib.parse import quote

import requests


URL_FIELDS = ("open_access_pdf", "repository_pdf_url", "publisher_pdf_url", "pdf_url")
RESULT_FIELDS = (
    "report_id", "title", "doi", "status", "route", "final_url", "local_path",
    "sha256", "bytes", "attempts", "failure_reason",
)


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    if not path.exists():
        return [], []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def merge_results_into_run(run_dir: Path, results: list[dict[str, str]]) -> None:
    """Merge acquisition provenance; identity verification remains a later gate."""
    registry = run_dir / "fulltext/fulltext-registry.csv"
    fields, rows = _read_csv(registry)
    required = [
        "report_id", "fulltext_status", "access_route", "final_url", "local_path",
        "sha256", "identity_verified", "page_count", "text_quality",
        "access_attempts", "failure_reason", "bytes",
    ]
    for field in required:
        if field not in fields:
            fields.append(field)
    by_id = {str(row.get("report_id") or ""): row for row in rows}
    for result in results:
        rid = result["report_id"]
        row = by_id.get(rid)
        if row is None:
            row = {field: "" for field in fields}
            row["report_id"] = rid
            row["title"] = result.get("title", "")
            row["doi"] = result.get("doi", "")
            rows.append(row)
            by_id[rid] = row
            for field in ("title", "doi"):
                if field not in fields:
                    fields.append(field)
        row.update({
            "fulltext_status": result.get("status", ""),
            "access_route": result.get("route", ""),
            "final_url": result.get("final_url", ""),
            "local_path": result.get("local_path", ""),
            "sha256": result.get("sha256", ""),
            "access_attempts": result.get("attempts", ""),
            "failure_reason": result.get("failure_reason", ""),
            "bytes": result.get("bytes", ""),
        })
        if result.get("status") in {"AVAILABLE_LOCAL", "DOWNLOADED_LEGAL"}:
            row["identity_verified"] = "pending_content_verification"
            row["text_quality"] = "pending_extraction"
    _write_csv(registry, fields, rows)

    screening = (run_dir / "screening/adjudicated.csv"
                 if (run_dir / "screening/adjudicated.csv").exists()
                 else run_dir / "screening.csv")
    sc_fields, sc_rows = _read_csv(screening)
    if sc_rows:
        if "fulltext_status" not in sc_fields:
            sc_fields.append("fulltext_status")
        status_by_id = {row["report_id"]: row["status"] for row in results}
        for row in sc_rows:
            rid = row.get("report_id") or row.get("record_id")
            if rid in status_by_id:
                row["fulltext_status"] = status_by_id[rid]
        _write_csv(screening, sc_fields, sc_rows)


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "-", value or "paper").strip("-.")
    return value[:80] or "paper"


def oa_routes(row: dict[str, str], session: requests.Session,
              unpaywall_email: str | None) -> list[tuple[str, str]]:
    routes: list[tuple[str, str]] = []
    for field in URL_FIELDS:
        if row.get(field):
            routes.append((field, row[field]))
    doi = (row.get("doi") or "").removeprefix("https://doi.org/").strip()
    if doi:
        try:
            data = session.get(
                f"https://api.openalex.org/works/https://doi.org/{quote(doi, safe='')}",
                timeout=20,
            ).json()
            loc = data.get("best_oa_location") or {}
            if loc.get("pdf_url"):
                routes.append(("openalex", loc["pdf_url"]))
        except Exception:
            pass
        if unpaywall_email:
            try:
                data = session.get(
                    f"https://api.unpaywall.org/v2/{quote(doi, safe='')}?email={quote(unpaywall_email)}",
                    timeout=20,
                ).json()
                loc = data.get("best_oa_location") or {}
                if loc.get("url_for_pdf"):
                    routes.append(("unpaywall", loc["url_for_pdf"]))
            except Exception:
                pass
    seen, unique = set(), []
    for route, url in routes:
        if url and url not in seen and str(url).startswith(("https://", "http://")):
            seen.add(url)
            unique.append((route, url))
    return unique


def download_pdf(session: requests.Session, url: str, destination: Path,
                 max_bytes: int) -> tuple[bool, str, int]:
    try:
        with session.get(url, timeout=35, stream=True, allow_redirects=True) as response:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "").lower()
            data = bytearray()
            for chunk in response.iter_content(1024 * 64):
                if chunk:
                    data.extend(chunk)
                if len(data) > max_bytes:
                    return False, "file exceeds configured byte limit", len(data)
            if not bytes(data[:5]) == b"%PDF-":
                return False, f"response is not a PDF ({content_type or 'unknown content type'})", len(data)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            return True, "", len(data)
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}", 0


def run(queue: Path, out_dir: Path, result_path: Path,
        unpaywall_email: str | None = None, max_mb: int = 80) -> list[dict[str, str]]:
    with queue.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    session = requests.Session()
    session.headers["User-Agent"] = "geography-literature-review-skill/4.0 lawful-OA-fetch"
    results: list[dict[str, str]] = []
    for index, row in enumerate(rows, 1):
        rid = row.get("report_id") or f"R{index:04d}"
        attempts: list[str] = []
        local = row.get("local_path")
        if local and Path(local).exists() and Path(local).read_bytes()[:5] == b"%PDF-":
            source = Path(local)
            dest = out_dir / f"{safe_name(rid)}_{safe_name(source.name)}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            payload = dest.read_bytes()
            results.append({"report_id": rid, "title": row.get("title", ""),
                            "doi": row.get("doi", ""), "status": "AVAILABLE_LOCAL",
                            "route": "user_local", "final_url": "", "local_path": str(dest),
                            "sha256": hashlib.sha256(payload).hexdigest(), "bytes": str(len(payload)),
                            "attempts": "user_local", "failure_reason": ""})
            continue
        success = None
        last_reason = "no lawful OA PDF route discovered"
        for route, url in oa_routes(row, session, unpaywall_email):
            attempts.append(f"{route}:{url}")
            dest = out_dir / f"{safe_name(rid)}_{safe_name(row.get('title') or rid)}.pdf"
            ok, reason, size = download_pdf(session, url, dest, max_mb * 1024 * 1024)
            if ok:
                payload = dest.read_bytes()
                success = {"report_id": rid, "title": row.get("title", ""),
                           "doi": row.get("doi", ""), "status": "DOWNLOADED_LEGAL",
                           "route": route, "final_url": url, "local_path": str(dest),
                           "sha256": hashlib.sha256(payload).hexdigest(), "bytes": str(size),
                           "attempts": " | ".join(attempts), "failure_reason": ""}
                break
            last_reason = reason
        results.append(success or {"report_id": rid, "title": row.get("title", ""),
                                   "doi": row.get("doi", ""), "status": "MISSING_FULLTEXT",
                                   "route": "", "final_url": "", "local_path": "",
                                   "sha256": "", "bytes": "0", "attempts": " | ".join(attempts),
                                   "failure_reason": last_reason})
    result_path.parent.mkdir(parents=True, exist_ok=True)
    with result_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        writer.writerows(results)
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--input")
    parser.add_argument("--unpaywall-email")
    parser.add_argument("--max-mb", type=int, default=80)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    queue = Path(args.input) if args.input else run_dir / "fulltext/acquisition-queue.csv"
    if not queue.exists():
        raise SystemExit(f"acquisition queue not found: {queue}")
    results = run(queue, run_dir / "fulltext/pdfs",
                  run_dir / "fulltext/acquisition-results.csv",
                  args.unpaywall_email, args.max_mb)
    merge_results_into_run(run_dir, results)
    missing = sum(row["status"] == "MISSING_FULLTEXT" for row in results)
    print(json.dumps({"processed": len(results), "missing": missing,
                      "results": str(run_dir / 'fulltext/acquisition-results.csv')}, indent=2))
    return 5 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
