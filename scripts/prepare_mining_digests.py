#!/usr/bin/env python3
"""Prepare compact per-document digests for LLM pattern mining (compile-time).

For every manifest record, writes .cache/digests/<doc_id>.txt containing:
  * bibliographic header (from manifest) + structural stats (from index)
  * heading tree
  * opening pages (title/abstract/introduction)
  * N evenly spaced body slices (defaulting around section boundaries)
  * closing part (conclusion / outlook / future directions)
  * all figure & table captions

Digest size is capped so that one agent can mine ~10 documents per context.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "benchmark_corpus" / "manifest.jsonl"
INDEX = REPO / "benchmark_corpus" / "benchmark-index.jsonl"
DIGESTS = REPO / ".cache" / "digests"

FIG_CAPTION_LINE = re.compile(r"^(Fig\w*\.?\s*\d+\s*\|.{0,400}|Table\s*\d+\s*\|.{0,300}|Box\s*\d+\s*\|.{0,300})", re.M)


def slice_text(text: str, start_frac: float, end_frac: float, cap: int) -> str:
    n = len(text)
    seg = text[int(n * start_frac):int(n * end_frac)]
    return seg[:cap]


def make_digest(rec: dict, idx_row: dict | None, n_slices: int = 5,
                open_chars: int = 6000, close_chars: int = 3500,
                slice_chars: int = 2200) -> str:
    path = REPO / rec["cache_file"]
    raw = unicodedata.normalize("NFKC", path.read_text(encoding="utf-8", errors="ignore"))
    ref_split = max(raw.rfind("\nReferences\n"), int(len(raw) * 0.85))
    body, refs_head = raw[:ref_split], raw[ref_split:ref_split + 1500]

    parts: list[str] = []
    parts.append(f"### DOCUMENT {rec['document_id']} — {rec.get('title')}")
    parts.append(f"year={rec.get('year')} doi={rec.get('doi')}")
    if idx_row:
        heads = idx_row.get("headings") or []
        parts.append("HEADINGS_DETECTED:\n" + "\n".join(f"  - {h}" for h in heads[:45]))
        parts.append(
            f"STATS paragraphs~{idx_row.get('n_paragraph_blocks')} "
            f"cit/block(q25|med|p75)={idx_row.get('citations_per_block_q25_50_75')} "
            f"figs={idx_row.get('figures_numbered')} tables={idx_row.get('tables_numbered')} "
            f"boxes={idx_row.get('boxes_numbered')} refs~{idx_row.get('reference_entry_count_estimate')} "
            f"recent5y_share={idx_row.get('recent5y_reference_share')}")
        if idx_row.get("n_paragraph_blocks", 99) < 25:
            parts.append("WARNING: poor text extraction quality — mark confidence low.")
    pages = [p for p in raw.split("\f") if p.strip()]
    parts.append("OPENING (page 1-2, title/abstract/intro):\n" +
                 " ".join(pages[1][:open_chars].split()) if len(pages) > 1 else "")
    # fix join precedence explicitly
    parts[-1] = "OPENING (page 1-2, title/abstract/intro):\n" + \
        " ".join((pages[1] if len(pages) > 1 else pages[0])[:open_chars].split())

    n = len(body)
    for i in range(n_slices):
        a = (i + 1) / (n_slices + 1)
        seg = body[int(n * a): int(n * a) + slice_chars]
        parts.append(f"BODY_SLICE_{i + 1}@{a:.0%}:\n" + " ".join(seg.split()))
    tail = body[-close_chars:]
    parts.append("CLOSING (conclusion/outlook/future):\n" + " ".join(tail.split()))

    caps = FIG_CAPTION_LINE.findall(raw)
    if caps:
        parts.append("FIGURE/TABLE CAPTIONS:\n" + "\n".join(
            " ".join(c.split())[:260] for c in caps[:20]))
    parts.append("REFERENCES_HEAD_SAMPLE:\n" + " ".join(refs_head[:900].split()))
    return "\n\n".join(parts)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", help="comma-separated document_id filter, e.g. B001,B002")
    ap.add_argument("--slices", type=int, default=5)
    args = ap.parse_args()

    records = [json.loads(l) for l in MANIFEST.read_text(encoding="utf-8").splitlines()]
    try:
        idx_rows = {json.loads(l)["document_id"]: json.loads(l)
                    for l in INDEX.read_text(encoding="utf-8").splitlines()}
    except FileNotFoundError:
        idx_rows = {}
    if args.docs:
        keep = {d.strip() for d in args.docs.split(",")}
        records = [r for r in records if r["document_id"] in keep]
    DIGESTS.mkdir(parents=True, exist_ok=True)
    for rec in records:
        d = make_digest(rec, idx_rows.get(rec["document_id"]), n_slices=args.slices)
        out = DIGESTS / f"{rec['document_id']}.txt"
        out.write_text(d, encoding="utf-8")
        print(f"{rec['document_id']} -> {out.name} ({len(d)} chars)")


if __name__ == "__main__":
    main()
