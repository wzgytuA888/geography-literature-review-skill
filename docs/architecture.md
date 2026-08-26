# Architecture

## The one idea that organizes everything

**Benchmark teaches HOW; task literature provides WHAT.**
A corpus of 60 high-quality geography reviews (mostly *Nature Reviews Earth &
Environment*) is distilled into transferable review-method knowledge
(architecture, rhetoric moves, synthesis patterns, citation behavior,
conditional geography reasoning, gap/agenda logic, figure grammar, quality
rubric). At runtime, a user-specified topic triggers a fresh evidence pipeline:
Google Scholar API discovery → legal full-text acquisition (with a mandatory
human pause when key PDFs cannot be obtained) → structured evidence → synthesis
→ outline → drafting → Zotero-verified citations → figures → independent
review/audit → final manuscript. Benchmark content never becomes runtime facts.

## Compile-time vs Runtime

| | Compile-time | Runtime |
| --- | --- | --- |
| Input | benchmark PDFs | user topic |
| Output | `benchmark_corpus/*.md` method files + archetypes + rubric | `runs/<run-id>/` full manuscript package |
| Data structure | Review Pattern Card (`templates/review-pattern-card.yaml`) | Task Literature Card + Evidence Matrix |
| Frequency | once + incremental fold-ins | per topic |

## Agents

Compile-time (agents/compiletime/): curator · review/citation/geography/figure
pattern miners · consolidator.
Runtime (agents/runtime/): orchestrator · librarian · strategist · scouts A–E ·
extractor · synthesizer · outline · writer · citation · figure · reviewer ·
auditor · revision.

## Hard policy spine (non-negotiable)

1. Google Scholar-compatible API = only discovery backend; preflight required;
   failures pause, never switch backends.
2. MissingFullTextGate: included/high-priority paper without legal full text ⇒
   TXT(+XLSX) report + checkpoint + PAUSED_WAITING_FOR_USER_FULLTEXT; resume via
   validated PDFs or explicit skip recorded forever.
3. Zero hallucinated citations: Zotero item / verifiable DOI / authoritative
   metadata only; claim-support verified; unresolved ⇒ removed + reported.
4. Evidence-first: search→screen→extract→matrix→synthesis→outline→draft.
5. Gaps & geography reasoning conditional on task evidence.
6. Copyright: PDFs/full-text caches git-ignored; repo carries code, prompts,
   generic rules, statistics — never source text.

## Diagrams

See `assets/*.mmd` (+ .svg where rendered):
overall-architecture · compiletime-workflow · runtime-multi-agent-workflow ·
runtime-scholar-gate · evidence-citation-lineage.
