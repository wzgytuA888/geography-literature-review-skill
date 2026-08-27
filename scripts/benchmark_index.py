#!/usr/bin/env python3
"""Structural indexer for the Benchmark Corpus (compile-time pipeline).

Handles two-column journal PDF extractions (Nature Reviews style) where
paragraph breaks are lost: rebuilds the text flow, detects heading lines,
and derives paragraph-sized blocks for statistics. All outputs are
statistics/metadata only (no copyrighted prose enters the repository).

Outputs:
  benchmark_corpus/benchmark-index.jsonl   per-document structural record
  benchmark_corpus/benchmark-stats.json    corpus aggregate
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "benchmark_corpus" / "manifest.jsonl"
OUT_INDEX = REPO / "benchmark_corpus" / "benchmark-index.jsonl"
OUT_STATS = REPO / "benchmark_corpus" / "benchmark-stats.json"

NUM_CITE = re.compile(r"\[(\d{1,4}(?:[,–\-]\d{1,4})*)\]")
# Nature-style superscript citations survive extraction glued to words: "extremes35–37"
SUPERSCRIPT_CITE = re.compile(r"[a-z\)\.]((?:\d{1,3})(?:[,–\-](?:\d{1,3}))*)\b(?!\d)")
REF_PAREN = re.compile(r"\(refs?\.?\s*\d{1,3}(?:[,–\-]\d{1,3})*[^)]{0,60}\)", re.I)
AUTHOR_YEAR = re.compile(
    r"\((?:[A-Z][A-Za-zÀ-ÿ'’\-\.]+\s+(?:et al\.?,?\s*|and\s+|&\s*)?)+,?\s*(?:19|20)\d{2}[a-z]?(?:;\s*)*\)")
FIG_CAPTION = re.compile(r"^Fig\w*\.?\s*(\d+)\s*\|", re.M)
TAB_CAPTION = re.compile(r"^Table\s*(\d+)\s*\|", re.M)
BOX_CAPTION = re.compile(r"^Box\s*(\d+)\s*\|", re.M)
PAGE_HEADER = re.compile(
    r"Nature Reviews[^\n]*Volume[^\n]*\n?\s*\d+\n|^[A-Za-z &]+\s*\|\s*Volume.*$", re.M)
REF_LINE = re.compile(r"^\s{0,4}\d{1,3}\.\s+[A-Z]", re.M)

PROSE_STARTERS = {
    "the", "a", "an", "these", "this", "those", "such", "in", "on", "for",
    "however", "moreover", "therefore", "thus", "although", "while", "if",
    "when", "as", "it", "its", "their", "our", "we", "here", "notably",
    "importantly", "further", "furthermore", "additionally", "similarly",
    "by", "to", "with", "under", "across", "during", "despite", "given",
    "box", "fig", "figure", "table", "extended data", "equation", "ref",
}
SENT_END = re.compile(r"[.!?]\s*$")


def clean_lines(text: str) -> list[str]:
    """Remove running headers/footers/page numbers; keep content lines."""
    lines = []
    for ln in text.split("\n"):
        s = ln.rstrip()
        if PAGE_HEADER.search(s):
            continue
        if re.fullmatch(r"\s*\d{1,4}\s*", s):
            continue
        if "Nature Reviews Earth & Environment" in s and "|" in s:
            continue
        if "https://doi.org" in s or "www.nature.com" in s:
            continue
        lines.append(s)
    return lines


def is_heading(line: str) -> bool:
    s = line.strip()
    if not (3 <= len(s) <= 72):
        return False
    if NUM_CITE.search(s) or AUTHOR_YEAR.search(s):
        return False
    if SENT_END.search(s):
        return False
    words = s.split()
    if not (1 <= len(words) <= 10):
        return False
    # reject obvious sentence starts
    first = words[0].lower().strip(",.;:")
    if first in PROSE_STARTERS:
        return False
    # must look title-ish: starts uppercase, contains lowercase words
    if not s[0].isupper():
        return False
    letters = [c for c in s if c.isalpha()]
    upper_ratio = sum(c.isupper() for c in letters) / max(1, len(letters))
    if upper_ratio > 0.6:      # ALL CAPS junk
        return False
    if any(c in s for c in "()[]{}|=<>@#$%^*_~“”\""):
        return False
    # known generic sections pass immediately
    low = s.lower()
    generic = {
        "abstract", "introduction", "background", "main", "results",
        "discussion", "conclusion", "conclusions", "summary", "outlook",
        "methods", "references", "review article", "perspective", "perspectives",
        "data availability", "code availability", "acknowledgements",
        "acknowledgments", "author contributions", "competing interests",
        "search summary", "key points",
    }
    if low in generic:
        return True
    # otherwise require ≥3 words and no terminal preposition/conjunction
    if len(words) < 2:
        return False
    if words[-1].lower() in {"of", "in", "and", "the", "for", "on", "to", "with", "a"}:
        return False
    return sum(ch.isalpha() for ch in s) >= len(s) * 0.7


def build_blocks(lines: list[str]) -> tuple[list[str], list[int]]:
    """Return (blocks, heading_indices). A block ends at a heading or when it
    already holds ≥350 chars and reaches a sentence end."""
    blocks: list[str] = []
    heads_at: list[int] = []
    buf: list[str] = []
    cur = 0
    for i, ln in enumerate(lines):
        s = ln.strip()
        if not s:
            continue
        if is_heading(s):
            if buf:
                blocks.append(" ".join(buf))
                buf = []
            blocks.append(f"__HEADING__ {s}")
            heads_at.append(len(blocks) - 1)
            continue
        buf.append(s)
        joined = " ".join(buf)
        if len(joined) >= 350 and SENT_END.search(s):
            blocks.append(joined)
            buf = []
    if buf:
        blocks.append(" ".join(buf))
    return blocks, heads_at


def _span_count(spec: str) -> int:
    """Count citations represented by '35' or '35–37' or '2,3'."""
    if "–" in spec or "-" in spec:
        m = re.split(r"[–\-]", spec)
        try:
            lo, hi = int(m[0]), int(m[-1])
            return min(max(1, hi - lo + 1), 25)
        except ValueError:
            return 1
    return len([p for p in re.split(r",", spec) if p.strip()])


def cite_count(text: str) -> int:
    n = 0
    for m in NUM_CITE.finditer(text):
        n += _span_count(m.group(1))
    seen = set()
    for m in SUPERSCRIPT_CITE.finditer(text):
        spec = m.group(1)
        nums = [int(p) for p in re.split(r"[,–\-]", spec) if p.isdigit()]
        # keep only reference-like numbers (<300), drop equations/years fragments
        if not nums or max(nums) >= 300:
            continue
        key = m.start()
        if key not in seen:
            seen.add(key)
            n += _span_count(spec)
    n += len(REF_PAREN.findall(text))
    n += len(AUTHOR_YEAR.findall(text))
    return n


def ref_years(refs_text: str) -> tuple[int, float]:
    years = [int(y) for y in re.findall(r"\b(19[89]\d|20[0-2]\d)\b", refs_text)]
    if not years:
        return 0, 0.0
    recent5 = sum(1 for y in years if y >= 2021)
    return len(years), recent5 / len(years)


def analyze(rec: dict) -> dict:
    cache = rec.get("cache_file")
    path = REPO / cache if cache else None
    if not path or not path.exists():
        return {"document_id": rec["document_id"], "error": "cache missing"}
    raw = unicodedata.normalize("NFKC", path.read_text(encoding="utf-8", errors="ignore"))
    ref_split = max(raw.rfind("\nReferences\n"), raw.rfind("\nReferences\r"))
    if ref_split < len(raw) // 2:  # fallback: references near end
        ref_split = int(len(raw) * 0.85)
    body, refs = raw[:ref_split], raw[ref_split:]

    lines = clean_lines(body)
    blocks, head_idx = build_blocks(lines)
    headings = [b[len("__HEADING__ "):] for b in blocks if b.startswith("__HEADING__")]
    para_blocks = [
        b for b in blocks
        if not b.startswith("__HEADING__") and len(b) > 300 and not FIG_CAPTION.match(b[:12])
    ]
    dens = [cite_count(p) for p in para_blocks]
    lens = [len(p) for p in para_blocks]

    def q4(vals):
        vals = sorted(vals)
        if len(vals) < 4:
            return None
        return [int(statistics.quantiles(vals, n=4)[0]), int(statistics.median(vals)),
                int(statistics.quantiles(vals, n=4)[2])]

    figs = sorted({int(m) for m in FIG_CAPTION.findall(raw)})
    tabs = sorted({int(m) for m in TAB_CAPTION.findall(raw)})
    boxes = sorted({int(m) for m in BOX_CAPTION.findall(raw)})
    n_refs, frac_recent5 = ref_years(refs)
    n_ref_entries = len(REF_LINE.findall(refs))

    return {
        "document_id": rec["document_id"],
        "title": rec.get("title"),
        "year": rec.get("year"),
        "doi": rec.get("doi"),
        "headings": headings[:45],
        "n_paragraph_blocks": len(para_blocks),
        "block_len_chars_q25_50_75": q4(lens),
        "citations_per_block_q25_50_75": q4(dens),
        "zero_citation_block_share": round(sum(1 for d in dens if d == 0) / max(1, len(dens)), 3),
        "figures_numbered": figs,
        "tables_numbered": tabs,
        "boxes_numbered": boxes,
        "reference_entry_count_estimate": n_ref_entries or n_refs,
        "recent5y_reference_share": round(frac_recent5, 3) if frac_recent5 else None,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(MANIFEST))
    ap.add_argument("--out-index", default=str(OUT_INDEX))
    ap.add_argument("--out-stats", default=str(OUT_STATS))
    args = ap.parse_args()
    manifest = Path(args.manifest)
    out_index = Path(args.out_index)
    out_stats = Path(args.out_stats)
    if not manifest.exists():
        sys.exit(f"manifest missing: {manifest} — run extract_documents.py first")
    records = [json.loads(l) for l in manifest.read_text(encoding="utf-8").splitlines()]
    rows = [analyze(r) for r in records]
    out_index.parent.mkdir(parents=True, exist_ok=True)
    out_stats.parent.mkdir(parents=True, exist_ok=True)
    out_index.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n", encoding="utf-8")

    med_dens = [r["citations_per_block_q25_50_75"][1] for r in rows if r.get("citations_per_block_q25_50_75")]
    med_len = [r["block_len_chars_q25_50_75"][1] for r in rows if r.get("block_len_chars_q25_50_75")]
    fig_counts = [len(r["figures_numbered"]) for r in rows if r.get("figures_numbered") is not None]
    ref_counts = [r["reference_entry_count_estimate"] for r in rows if r.get("reference_entry_count_estimate")]

    hc: Counter[str] = Counter()
    for r in rows:
        for h in (r.get("headings") or [])[:20]:
            hc[h.title()] += 1

    def q(vals):
        vals = sorted(v for v in vals if v)
        if not vals:
            return None
        out = {"min": vals[0], "median": int(statistics.median(vals)), "max": vals[-1]}
        if len(vals) > 3:
            qs = statistics.quantiles(vals, n=4)
            out.update({"p25": int(qs[0]), "p75": int(qs[2])})
        return out

    stats = {
        "n_documents": len(rows),
        "paragraph_block_median_chars": q(med_len),
        "citation_median_per_block": q(med_dens),
        "figures_per_article": q(fig_counts),
        "reference_entries_per_article": q(ref_counts),
        "most_common_headings": [{"heading": h, "count": c} for h, c in hc.most_common(30)],
    }
    out_stats.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")

    ok = sum(1 for r in rows if "error" not in r)
    print(f"indexed {ok}/{len(rows)} docs")
    for r in rows[:6]:
        print(r["document_id"], "blocks:", r.get("n_paragraph_blocks"),
              "cit/block:", r.get("citations_per_block_q25_50_75"),
              "heads:", len(r.get("headings") or []))
    print(f"-> {out_index}\n-> {out_stats}")


if __name__ == "__main__":
    main()
