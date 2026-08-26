---
name: geography-literature-review-skill
description: Runs reproducible, traceable literature-review workflows for geography, Earth science, ecology, remote sensing, climate and environmental research. Use for literature, systematic, scoping or bibliometric reviews; research-progress/gap analysis; evidence matrices; citation networks; or `/geo-review` commands. Uses Semantic Scholar and OpenAlex for discovery, Crossref for DOI metadata validation, conservative screening, evidence-grounded synthesis and structured exports. Do not use for explaining one paper, ordinary knowledge questions, or concept explanations that need no external literature search.
license: MIT
metadata:
  version: 2.0.0
  corpus: 60 benchmark reviews (Nature Reviews Earth & Environment et al.)
  hard-rules: evidence-first; reproducible-search-log; no-invented-metadata; uncertain-duplicates-preserved; benchmark-HOW-vs-task-WHAT
---

# Geography Literature Review Research Skill

Keep the two corpora separate:

| | Benchmark corpus | Task evidence corpus |
|---|---|---|
| Location | `benchmark_corpus/` | `runs/<run-id>/` |
| Purpose | teaches **HOW** strong reviews are structured | establishes **WHAT** is known about this topic |
| May supply manuscript facts? | Never | Yes, after screening and evidence extraction |

## Route the request

- New review, evidence matrix, research-gap analysis, citation network or field-progress analysis: read `workflows/full-review-workflow.md`.
- Search/acquisition stage: read `workflows/literature-search.md` and `references/search-strategy.md`.
- Evidence extraction or synthesis: read `workflows/evidence-synthesis.md` and `references/synthesis-rules.md`.
- Benchmark ingest/update: read the matching workflow only.
- One-paper explanation or no-search concept question: do not invoke this skill.

## Runtime invariants

1. **API-first discovery.** Search Semantic Scholar and OpenAlex. Crossref validates
   and enriches DOI metadata; it is not the primary discovery engine. Google
   Scholar is optional manual supplementation only—never scrape its result pages.
2. **Reproducibility.** Preserve the user's terms, generated queries, filters,
   database, counts and retrieval time in `Search_Log`. Bound query expansion.
3. **Conservative records.** Never invent abstracts, DOIs, findings, methods or
   geographic fields. Unknown evidence fields are `null` or `not_reported`.
   Distinguish source facts, AI extraction and inference; inference requires an
   explicit flag and confidence.
4. **Deduplication order.** DOI → Semantic Scholar ID → OpenAlex ID → exact
   normalized title. Keep uncertain fuzzy matches and set `possible_duplicate=true`.
5. **Screening is explicit.** Retrieved results are not automatically included.
   Track retrieved → deduplicated → title → abstract → full-text → included, plus
   `include` and a controlled `exclude_reason`.
6. **Full-text gate.** Important included papers without legally available full
   text trigger `PAUSED_WAITING_FOR_USER_FULLTEXT`; do not infer results from titles
   or abstracts.
7. **Traceable synthesis.** Every claim records supporting and contradicting paper
   IDs, conditions, confidence and notes. Gaps must emerge from included evidence,
   not copied future-work sentences or benchmark content.
8. **Citation truth.** Resolve references through the registry, Zotero/DOI and
   authoritative metadata. Unverifiable references remain unresolved, never invented.

## Standard workflow

```
question → bounded search strategy → Semantic Scholar + OpenAlex → normalize
→ Search Log → deduplicate → title/abstract screening → full-text gate
→ evidence matrix → core papers → backward/forward snowballing → re-screen
→ iterative theme coding → consensus/disagreement/gap synthesis
→ citation audit → structured exports → review/figure/final package
```

Use `scripts/literature_review_pipeline.py` for deterministic acquisition,
snowballing and exports. The evidence-first writing, Zotero, figure, independent
review and benchmark-QA stages remain available from v1.

## Commands

Natural language or `/geo-review <cmd>`:

`api-check` · `start` · `search` · `screen` · `snowball` · `evidence` ·
`themes` · `synthesize` · `outline` · `draft` · `cite` · `figures` · `review` ·
`audit` · `export` · `missing-fulltext` · `resume` · `full`

Legacy `scholar-check` remains an alias for an API readiness check, not a mandate
to use Google Scholar.

## Setup

```bash
pip install -r requirements.txt
python scripts/literature_review_pipeline.py preflight --out-dir runs/preflight
```

`SEMANTIC_SCHOLAR_API_KEY` is optional; the public endpoint is attempted without
it. `OPENALEX_MAILTO` and `CROSSREF_MAILTO` identify polite-pool requests. `.env`
is supported and ignored by git. Read `docs/academic-api-setup.md` when configuring.

## Priority

citation truth > claim–evidence consistency > provenance > accuracy > completeness
> synthesis quality > logic > style. Thin evidence must be reported as
`INSUFFICIENT EVIDENCE`, not filled with plausible prose.
