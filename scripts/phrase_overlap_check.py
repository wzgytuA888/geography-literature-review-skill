#!/usr/bin/env python3
"""Near-copy / phrase-overlap checker.

Compares a draft manuscript against cached benchmark full text to enforce
"match quality and logic, not wording". Flags long shared n-grams; long
overlapping spans must be rewritten before final QA.

Usage:
    python scripts/phrase_overlap_check.py --draft runs/<id>/draft.md \
        [--n 8] [--threshold 12]

Exit codes: 0 = pass, 6 = violations found (list written next to draft as
phrase-overlap-report.json).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "benchmark_corpus" / "manifest.jsonl"

WORD = re.compile(r"[A-Za-z][A-Za-z\-']+")


def tokens(text: str) -> list[str]:
    return [w.lower() for w in WORD.findall(text)]


def ngrams(toks: list[str], n: int) -> dict[tuple, int]:
    out: dict[tuple, int] = {}
    for i in range(len(toks) - n + 1):
        g = tuple(toks[i:i + n])
        out[g] = out.get(g, 0) + 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", required=True)
    ap.add_argument("--corpus", default=str(MANIFEST),
                    help="manifest.jsonl of benchmark cache files")
    ap.add_argument("--n", type=int, default=8, help="n-gram size")
    ap.add_argument("--threshold", type=int, default=10,
                    help="flag if more than N distinct shared %d-grams" % 8)
    args = ap.parse_args()

    draft = Path(args.draft)
    if not draft.exists():
        sys.exit(f"draft not found: {draft}")
    dtoks = tokens(draft.read_text(encoding="utf-8", errors="ignore"))
    dgr = set(ngrams(dtoks, args.n))

    hits: dict[str, list] = {}
    total_shared = 0
    manifest = Path(args.corpus)
    for line in manifest.read_text(encoding="utf-8").splitlines():
        rec = json.loads(line)
        cache = REPO / rec.get("cache_file", "")
        if not cache.exists():
            continue
        btoks = tokens(cache.read_text(encoding="utf-8", errors="ignore"))
        bset = set(ngrams(btoks, args.n))
        shared = dgr & bset
        total_shared += len(shared)
        if shared:
            examples = [" ".join(g) for g in sorted(shared)[:5]]
            hits[rec["document_id"]] = {
                "shared_ngram_count": len(shared),
                "example_phrases": examples,
            }

    report = {
        "draft": str(draft),
        "n": args.n,
        "distinct_draft_ngrams": len(dgr),
        "total_shared_with_benchmark": total_shared,
        "per_document": hits,
        "policy": "Any document with >=%d shared %d-grams requires rewriting "
                  "(match logic, never wording)." % (args.threshold, args.n),
        "status": "VIOLATIONS" if any(v["shared_ngram_count"] > args.threshold
                                      for v in hits.values()) else "PASS",
    }
    out = draft.parent / "phrase-overlap-report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("total_shared_with_benchmark", "status")}, indent=2))
    sys.exit(6 if report["status"] == "VIOLATIONS" else 0)


if __name__ == "__main__":
    main()
