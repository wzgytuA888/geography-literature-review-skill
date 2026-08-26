# Quality Control

## Three independent gates before FINAL

### Gate 1 — Independent Reviewer (scholarly quality)
Round-1 findings-only pass across science/literature/synthesis/writing/citations/
figures (agents/runtime/reviewer.md). Verdict thresholds: any blocker ⇒ MAJOR
REVISION loop.

### Gate 2 — Evidence & Citation Auditor (lineage integrity)
claim→evidence→card→source→metadata→citation→sentence chain verified row by row
(`evaluation/evidence-errors.csv`). Zero blockers allowed. Numbers must match
cards exactly.

### Gate 3 — Benchmark Quality Matching (logic parity, NOT wording)
Compare draft metrics against `benchmark_corpus/benchmark-stats.json` &
consolidated patterns → `evaluation/corpus-quality-comparison.md`:
- section organization vs dominant archetype(s);
- argument density: propositions per major section;
- synthesis density: share of paragraphs making clustered claims (>enumeration);
- citation behavior vs corpus quartiles (median ~2–4/block);
- consensus/controversy balance present;
- geography reasoning conditional usage (rules fired logged);
- gap derivation: every gap traces to documented deficit;
- agenda specificity: concrete instruments/platforms/questions;
- figure-text integration: each figure referenced by ≥1 paragraph it supports.
Plus near-copy screen: `scripts/phrase_overlap_check.py` PASS required.

## Hard red lines (auto-fail)
hallucinated references >0 · benchmark leakage into task claims >0 · unsupported
quantitative figures >0 · unsupported gap statements >0 · non-Scholar discovery
use >0 · silent skips of high-priority missing full text >0 · continuing final
stages while PAUSED_WAITING_FOR_USER_FULLTEXT.

## Run-level QA artifacts
runs/<id>/run-summary.md consolidates: stage timeline, screening counts, gate
statuses, eval results, unresolved items, limitations declared (access limits,
language bias, provider quotas).
