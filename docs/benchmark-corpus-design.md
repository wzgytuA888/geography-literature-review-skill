# Benchmark Corpus Design

## Role definition (memorize)

**Reference Review Benchmark Corpus = 高质量文献综述范例库 / method training set.**
It teaches HOW TO REVIEW. It is NOT: a research-question generator, an evidence
store for future topics, a source of quotable facts, or a constraint on which
concepts a new review may use. On any conflict, task evidence wins.

## Current composition
60 reviews (2020–2026 window), predominantly *Nature Reviews Earth &
Environment* (s43017 DOIs), spanning climate extremes, hydrology, coasts,
cryosphere–carbon–ecosystem topics. Structural stats live in
`benchmark_corpus/benchmark-stats.json`; per-doc structural records in
`benchmark-index.jsonl`; ingest manifest in `manifest.jsonl`.

## Data structures
- **Review Pattern Card** (`templates/review-pattern-card.yaml`) — one per doc;
  form-only fields across design/introduction/sections/argument/synthesis/
  rhetoric/citation/geography/figures/gap-agenda/quality/anti-patterns;
  UNKNOWN legal; provenance mandatory.
- **Consolidated pattern files** — cross-document tiers (consensus ≥50%, common
  ≥20%, variant, outlier) with document-ID evidence lines; anti-dominance rule:
  no single doc >30% of a file's consensus claims.
- **Archetypes** — clustered review modes with signature architecture/rhetoric.
- **Quality rubric & anti-patterns** — runtime-checkable criteria.

## Extraction pipeline
PDFs (local) → `scripts/extract_documents.py` (full text cached under `.cache/`,
git-ignored) → `scripts/benchmark_index.py` (objective structure stats) →
`scripts/prepare_mining_digests.py` (bounded digests for miners) → parallel
miners → consolidator. Weak-extraction docs (currently B004/B008/B013/B014) are
flagged so downstream confidence stays honest.

## Copyright posture
No raw PDFs, full text, or long excerpts in git. Consolidated files contain
patterns + ≤15-word exemplar fragments maximum. Public distribution carries only
code/templates/generic rules/statistics.

## Extending
Drop new reviews into a folder and run `workflows/benchmark-update.md`
(fold-in): dedupe → digest → mine → compare (support/extend/contradict/novel) →
consolidate → CHANGELOG. HOW-only updates; past runs' facts untouched.
