#!/usr/bin/env python3
"""Resume helpers for paused runs.

Subcommands:
  validate-pdf   Match user-supplied PDFs against missing_fulltext_literature
                 entries (title/DOI fuzzy match), copy them into the run folder,
                 update screening state, and clear/weaken the pause gate.
  status         Print current run state summary.

Usage:
  python scripts/resume_helper.py status --run-dir runs/20260826-agricultural-vwt
  python scripts/resume_helper.py validate-pdf --run-dir runs/<id> --pdf a.pdf b.pdf
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
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

REPO = Path(__file__).resolve().parents[1]


def norm_title(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[^a-z0-9 ]", "", s)


def first_page_text(pdf: Path) -> str:
    try:
        from pypdf import PdfReader
        r = PdfReader(str(pdf))
        return " ".join((r.pages[0].extract_text() or "").split())[:4000]
    except Exception:
        return ""


def load_missing(run_dir: Path) -> list[dict]:
    rows = []
    sc = run_dir / "screening.csv"
    if sc.exists():
        with sc.open(encoding="utf-8-sig") as fh:
            rows = [dict(r) for r in csv.DictReader(fh)]
    have_fulltext = {"AVAILABLE_LOCAL", "AVAILABLE_ZOTERO", "DOWNLOADED_LEGAL",
                     "OPEN_ACCESS_FOUND"}
    return [r for r in rows
            if r.get("screening_status") in
            {"INCLUDED_PENDING_FULLTEXT", "HIGH_PRIORITY_PENDING_FULLTEXT"}
            and str(r.get("explicit_user_skip", "")).lower() not in {"true", "1", "yes"}
            and r.get("fulltext_status") not in have_fulltext]


def match_pdf(pdf: Path, missing: list[dict]) -> tuple[dict | None, float]:
    text = first_page_text(pdf)
    m_doi = re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", pdf.stem) or \
        re.search(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", text[:2000])
    if m_doi:
        doi = m_doi.group(1).rstrip(".,;)")
        for row in missing:
            if str(row.get("doi", "")).lower().rstrip("/") == doi.lower():
                return row, 1.0
    t = norm_title(text[:1500] or pdf.stem)
    best, score = None, 0.0
    for row in missing:
        cand = norm_title(row.get("title", ""))
        if not cand:
            continue
        s = SequenceMatcher(None, cand[:120], t[:120]).ratio()
        if s > score:
            best, score = row, s
    return (best, score) if score >= 0.72 else (None, score)


def cmd_validate_pdf(run_dir: Path, pdfs: list[Path]) -> int:
    missing = load_missing(run_dir)
    if not missing:
        update_state(run_dir, {
            "missing_fulltext_gate": "CLEAR",
            "status": "RUNNING",
            "resume_event": "validate-pdf",
        })
        print(json.dumps({"gate": "CLEAR", "message": "No pending missing items.",
                          "next": "resume evidence extraction from checkpoint"}))
        return 0
    inbox = run_dir / "user_pdfs"
    inbox.mkdir(exist_ok=True)
    matched, unmatched = [], []
    remaining = list(missing)
    for pdf in pdfs:
        if not pdf.exists():
            unmatched.append({"pdf": str(pdf), "reason": "file not found"})
            continue
        row, score = match_pdf(pdf, remaining)
        dest = inbox / f"{hashlib.sha256(pdf.read_bytes()).hexdigest()[:12]}_{pdf.name}"
        shutil.copy2(pdf, dest)
        if row is None:
            unmatched.append({"pdf": pdf.name, "best_match_score": round(score, 3),
                              "reason": "no confident match — check title/DOI"})
            continue
        row["fulltext_status"] = "AVAILABLE_LOCAL"
        row["local_pdf"] = str(dest)
        matched.append({"paper_id": row.get("paper_id"), "pdf": str(dest),
                        "score": round(score, 3)})
        remaining.remove(row)

    # rewrite screening.csv with updates
    sc = run_dir / "screening.csv"
    if matched and sc.exists():
        with sc.open(encoding="utf-8-sig") as fh:
            reader = csv.DictReader(fh)
            fields = reader.fieldnames or []
            all_rows = list(reader)
        matched_ids = {m.get("paper_id") for m in matched}
        pdf_by_pid = {m.get("paper_id"): m.get("pdf") for m in matched}
        for upd in all_rows:
            if upd.get("paper_id") in matched_ids:
                upd["fulltext_status"] = "AVAILABLE_LOCAL"
                upd["local_pdf"] = pdf_by_pid[upd.get("paper_id")]
        fields = list(fields)
        for extra_key in ("local_pdf",):
            if extra_key not in fields and any(extra_key in r for r in all_rows):
                fields.append(extra_key)
        with sc.open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            w.writerows(all_rows)

    still_blocking = bool(load_missing(run_dir))
    update_state(run_dir, {
        "resume_event": "validate-pdf",
        "matched_count": len(matched),
        "unmatched_count": len(unmatched),
        "status": ("PAUSED_WAITING_FOR_USER_FULLTEXT" if still_blocking
                   else "RUNNING"),
        "missing_fulltext_gate": "TRIGGERED" if still_blocking else "CLEAR",
    })
    print(json.dumps({
        "matched": matched,
        "unmatched": unmatched,
        "gate": "TRIGGERED" if still_blocking else "CLEAR",
        "next": ("provide remaining PDFs or mark explicit_user_skip"
                 if still_blocking else
                 "resume evidence extraction from checkpoint"),
    }, indent=2))
    return 0


def update_state(run_dir: Path, extra: dict) -> None:
    sp = run_dir / "state.json"
    try:
        state = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    except Exception:
        state = {}
    state.update(extra)
    sp.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_status(run_dir: Path) -> int:
    sp = run_dir / "state.json"
    state = json.loads(sp.read_text(encoding="utf-8")) if sp.exists() else {}
    print(json.dumps(state, indent=2, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p1 = sub.add_parser("validate-pdf")
    p1.add_argument("--run-dir", required=True)
    p1.add_argument("--pdf", nargs="*", default=[])
    p2 = sub.add_parser("status")
    p2.add_argument("--run-dir", required=True)
    args = ap.parse_args()

    run_dir = Path(args.run_dir)
    if not run_dir.exists():
        sys.exit(f"run dir not found: {run_dir}")
    if args.cmd == "validate-pdf":
        return cmd_validate_pdf(run_dir, [Path(p) for p in args.pdf])
    return cmd_status(run_dir)


if __name__ == "__main__":
    sys.exit(main())
