#!/usr/bin/env python3
"""MissingFullTextGate — mandatory human-in-the-loop pause for missing PDFs.

Trigger condition (all must hold):
  1. a concrete review topic exists,
  2. API-first literature search has been executed for this run,
  3. at least one paper is screened INCLUDED_PENDING_FULLTEXT or
     HIGH_PRIORITY_PENDING_FULLTEXT,
  4. no legal full-text channel succeeded (Zotero / local / OA / publisher /
     user-provided).

Effects:
  * writes runs/<run-id>/missing_fulltext_literature.txt  (always)
  * writes .xlsx when openpyxl is available               (best effort)
  * updates state.json → PAUSED_WAITING_FOR_USER_FULLTEXT
  * downstream stages (synthesis/outline/draft/cite/final) MUST NOT run.

Resume: scripts/resume_helper.py validates newly provided PDFs against the
missing list and clears the gate (or keeps it if high-priority items remain).
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

BLOCKING_STATUSES = {"INCLUDED_PENDING_FULLTEXT", "HIGH_PRIORITY_PENDING_FULLTEXT"}
NON_BLOCKING = {
    "EXCLUDED_TITLE_ABSTRACT", "DUPLICATE", "OUT_OF_SCOPE",
    "LOW_PRIORITY_BACKGROUND", "NOT_REQUIRED_FOR_CURRENT_CLAIM",
}

XLSX_FIELDS = [
    "priority", "paper_id", "title", "authors", "year", "journal_or_source",
    "doi", "google_scholar_result_url", "scholar_result_id", "citation_count",
    "relevance_reason", "screening_status", "fulltext_status",
    "access_attempts", "failure_reason", "recommended_user_action",
    "zotero_status", "notes",
]
TXT_FIELDS = ["priority", "title", "authors", "year", "doi",
              "google_scholar_result_url", "relevance_reason",
              "fulltext_status", "failure_reason", "recommended_user_action"]


def load_screening(run_dir: Path) -> list[dict]:
    """Collect candidate rows from screening.csv and/or literature-registry.jsonl."""
    rows: list[dict] = []
    sc = run_dir / "screening.csv"
    if sc.exists():
        with sc.open(encoding="utf-8-sig") as fh:
            rows.extend(dict(r) for r in csv.DictReader(fh))
    reg = run_dir / "literature-registry.jsonl"
    if reg.exists() and not rows:
        for line in reg.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    return rows


def blocking_rows(rows: list[dict]) -> list[dict]:
    out = []
    for r in rows:
        st = (r.get("screening_status") or "").strip()
        ft = (r.get("fulltext_status") or "").strip()
        skipped = str(r.get("explicit_user_skip", "")).lower() in {"true", "1", "yes"}
        if st in BLOCKING_STATUSES and ft not in {
            "AVAILABLE_LOCAL", "AVAILABLE_ZOTERO", "DOWNLOADED_LEGAL",
            "OPEN_ACCESS_FOUND"} and not skipped:
            out.append({**r, "_blocking": True})
    # order: HIGH first, then by citation_count desc
    out.sort(key=lambda r: (
        0 if r.get("screening_status") == "HIGH_PRIORITY_PENDING_FULLTEXT" else 1,
        -int(r.get("citation_count") or 0)))
    for i, r in enumerate(out, 1):
        r["priority"] = ("HIGH" if r.get("screening_status") == "HIGH_PRIORITY_PENDING_FULLTEXT"
                         else f"P{i}")
        if not r.get("recommended_user_action"):
            r["recommended_user_action"] = (
                "Please provide the PDF (or import it into Zotero), "
                "confirm skip, or confirm exclude.")
    return out


def write_txt(rows: list[dict], path: Path) -> None:
    lines = [
        "MISSING FULL-TEXT LITERATURE — ACTION REQUIRED",
        f"generated: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        "",
        "These papers passed initial screening as important candidates but no legal",
        "full text could be obtained. The workflow is PAUSED.",
        "Provide PDFs into the run folder or Zotero, then resume;",
        "or explicitly confirm skip/exclude per item.",
        "=" * 78, "",
    ]
    for r in rows:
        lines.append(f"[{r.get('priority','?')}] {r.get('title') or '(no title)'}")
        for k in TXT_FIELDS[1:]:
            v = r.get(k)
            if v not in (None, "", []):
                lines.append(f"    {k}: {v}")
        lines.append("-" * 78)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_xlsx(rows: list[dict], path: Path) -> bool:
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
    except ImportError:
        return False
    wb = Workbook()
    ws = wb.active
    ws.title = "Missing Full-text"
    ws.append(XLSX_FIELDS)
    for c in ws[1]:
        c.font = Font(bold=True)
    for r in rows:
        ws.append([r.get(f, "") for f in XLSX_FIELDS])
    widths = {1: 8, 2: 10, 3: 60, 4: 30, 5: 6, 6: 24, 7: 22, 8: 40, 9: 20,
              10: 10, 11: 34, 12: 16, 13: 16, 14: 20, 15: 26, 16: 34, 17: 14, 18: 18}
    for col, w in widths.items():
        ws.column_dimensions[ws.cell(row=1, column=col).column_letter].width = w
    wb.save(path)
    return True


def update_state(run_dir: Path, extra: dict) -> None:
    sp = run_dir / "state.json"
    state = {}
    if sp.exists():
        try:
            state = json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            state = {}
    state.update({
        "run_id": run_dir.name,
        **extra,
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    sp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        print(json.dumps({"error": f"run dir not found: {run_dir}"}))
        return 2

    rows = blocking_rows(load_screening(run_dir))
    if not rows:
        update_state(run_dir, {
            "stage": "fulltext_acquisition",
            "status": "RUNNING",
            "missing_fulltext_gate": "CLEAR",
        })
        print(json.dumps({"gate": "CLEAR", "message": "No blocking missing full texts."}))
        return 0

    txt_path = run_dir / "missing_fulltext_literature.txt"
    xlsx_path = run_dir / "missing_fulltext_literature.xlsx"
    if not args.dry_run:
        write_txt(rows, txt_path)
        xlsx_ok = write_xlsx(rows, xlsx_path)
        update_state(run_dir, {
            "stage": "fulltext_acquisition",
            "status": "PAUSED_WAITING_FOR_USER_FULLTEXT",
            "missing_fulltext_gate": "TRIGGERED",
            "missing_count": len(rows),
            "missing_report_txt": txt_path.name,
            "missing_report_xlsx": xlsx_path.name if xlsx_ok else None,
            "paused_because": (
                "Important included literature lacks legally obtainable full text; "
                "final synthesis/outline/draft/gap-finalization/citation are blocked."),
        })
    print(json.dumps({
        "gate": "TRIGGERED",
        "state": "PAUSED_WAITING_FOR_USER_FULLTEXT",
        "missing_count": len(rows),
        "report_txt": str(txt_path),
        "report_xlsx": str(xlsx_path) if xlsx_path.with_suffix('.xlsx').exists() or True else None,
        "user_options": [
            "Upload PDFs into the run folder or import into Zotero, then run resume",
            "Mark explicit_user_skip=true for items you allow to skip",
            "Confirm exclude for irrelevant items",
        ],
        "note": "Downstream synthesis/writing stages are blocked until the gate clears.",
    }, indent=2))
    return 5  # distinctive pause exit code


if __name__ == "__main__":
    sys.exit(main())
