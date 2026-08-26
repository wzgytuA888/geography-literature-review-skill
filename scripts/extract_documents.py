#!/usr/bin/env python3
"""Extract text and bibliographic metadata from Benchmark Corpus PDFs.

Part of the Compile-time pipeline (Benchmark Distillation).
Reads PDFs from a source folder, extracts per-page text into a local cache
(git-ignored: full text is copyrighted), and emits benchmark_corpus/manifest.jsonl
with structural metadata only (no copyrighted content).

Usage:
    python scripts/extract_documents.py --source <pdf_folder> [--out manifest_path]

Only structural/bibliographic metadata goes into the repository. Full text stays
in the local cache directory (.cache/fulltext/) which is git-ignored.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    sys.exit("pypdf is required: pip install pypdf")

REPO = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = REPO / ".cache" / "fulltext"

DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)", re.I)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")


def norm_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[ \t]+", " ", s)


def extract_pdf(pdf_path: Path, cache_dir: Path) -> dict:
    """Extract text per page; cache to disk; return metadata + cached paths."""
    sha = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:16]
    stem = pdf_path.stem.replace(" ", "_")[:60]
    cache_txt = cache_dir / f"{stem}__{sha}.txt"
    meta = {"sha256_16": sha}
    if cache_txt.exists():
        text = cache_txt.read_text(encoding="utf-8", errors="ignore")
        meta["cached"] = True
        n_pages = text.count("\f")
    else:
        reader = PdfReader(str(pdf_path))
        pages = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        text = "\f".join(pages)
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_txt.write_text(text, encoding="utf-8")
        meta["cached"] = False
        n_pages = len(pages)

    first = text.split("\f")[0] if text else ""
    dois = DOI_RE.findall(first[:6000]) + DOI_RE.findall(text[:2000])
    doi = None
    for d in dois:
        d = d.rstrip(".,;)")
        if "s43" in d.lower() or "/" in d:
            doi = d
            break

    years = [int(y) for y in YEAR_RE.findall(first)]
    return {
        **meta,
        "pages": n_pages,
        "chars": len(text),
        "doi_guess": doi,
        "year_guess": max(years) if years else None,
        "cache_file": str(cache_txt.relative_to(REPO)) if cache_txt.is_relative_to(REPO) else str(cache_txt),
    }


def infer_title_from_filename(name: str) -> tuple[str | None, int | None]:
    """Filenames follow 'NN_YYYY_Title words.pdf' — parse that convention."""
    m = re.match(r"^(\d+)_((19|20)\d{2})_(.+)$", name)
    if m:
        return m.group(4).replace("-", " ").strip(), int(m.group(2))
    return None, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True, help="Folder containing benchmark review PDFs")
    ap.add_argument("--out", default=str(REPO / "benchmark_corpus" / "manifest.jsonl"))
    args = ap.parse_args()

    src = Path(args.source)
    if not src.exists():
        sys.exit(f"Source folder not found: {src}")
    pdfs = sorted(src.rglob("*.pdf"))
    if not pdfs:
        sys.exit(f"No PDFs found under {src}")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    records = []
    with out.open("w", encoding="utf-8") as fh:
        for i, pdf in enumerate(pdfs, 1):
            info = extract_pdf(pdf, DEFAULT_CACHE)
            fn_title, fn_year = infer_title_from_filename(pdf.stem)
            rec = {
                "document_id": f"B{i:03d}",
                "filename": pdf.name,
                "source_path": str(pdf),
                "title_from_filename": fn_title,
                "title": fn_title,
                "year": fn_year or info.get("year_guess"),
                "doi": info.get("doi_guess"),
                **{k: v for k, v in info.items() if k not in {"doi_guess", "year_guess"}},
                "ingest_time": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            records.append(rec)
            print(f"[{i}/{len(pdfs)}] {rec['document_id']} {pdf.name[:60]} pages={info['pages']} doi={rec['doi']}")

    print(f"\nWrote {len(records)} records -> {out}")


if __name__ == "__main__":
    main()
