# Changelog

## 2.0.0 — 2026-08-26

- Replaced mandatory Google-Scholar-gateway discovery with Semantic Scholar and
  OpenAlex primary APIs; Crossref now performs DOI validation/enrichment and
  Google Scholar is a logged manual supplement only.
- Added a reusable `src/geo_review` runtime package: unified PaperRecord and
  SearchLog schemas, resilient cached HTTP client, provider clients, bounded query
  generation, transparent relevance scoring, conservative screening and robust
  identifier/title deduplication.
- Added backward/forward Semantic Scholar citation snowballing with seed lineage.
- Added CSV, JSON and multi-sheet Excel outputs covering papers, evidence matrix,
  included/excluded studies, themes, search log and citation network.
- Expanded natural-geography evidence fields and enforced null/not_reported for
  unsupported facts; AI inference is explicitly labeled with confidence.
- Preserved v1 benchmark distillation, legal full-text gate, Zotero/DOI citation
  audit, evidence-to-claim lineage, figures, reviewer and checkpoint/resume design.
- Added `.env` loading, optional API keys, bounded retries/backoff, per-run cache,
  error logs, requirements and v2 unit tests.

## 1.1.0 — 2026-08-26

Benchmark consolidation pass (compile-time Benchmark Consolidator).

- Merged batch-1..6 mining findings into 12 consolidated pattern files under
  `benchmark_corpus/` (architecture, sections, paragraph rhetoric, synthesis,
  argument, citation, geography reasoning, gap identification, future agenda,
  figures, anti-patterns, quality rubric) — form-only knowledge, tiered
  (corpus-consensus >=30/60, common >=12, variant, outlier), every claim carrying
  doc-ID evidence; version stamp `consolidated: 2026-08-26, N=60`.
- Added `benchmark_corpus/archetypes/` (narrative, conceptual, systematic,
  scoping, methodological, geography-thematic) with honest corpus-coverage flags
  (scoping: zero corpus coverage; systematic: thin, semi-systematic hybrids noted).
- Quality rubric made runtime-checkable: 16 criteria Q1-Q16 with measurable PASS
  tests and blocking rules.
- Reconciled cross-batch contradictions: citation-density extraction artifacts
  (superscript loss, caption blocks) vs prose style; key-points box presence as
  year/format-dependent (not universal); recent-5y reference share reconciled as
  a field-speed + publication-year gradient.

## 1.0.0 — 2026-08-26

Initial release.

### Compile-time
- Benchmark ingest pipeline: `extract_documents.py` → `benchmark_index.py` →
  `prepare_mining_digests.py`.
- Distilled from 60 benchmark reviews (NREE-dominant, 2020–2026):
  60 Review Pattern Cards; consolidated pattern files (architecture, sections,
  rhetoric, synthesis, argument, citation, geography reasoning, gap, agenda,
  figure), quality rubric, anti-patterns, archetypes.
- Incremental fold-in workflow (`benchmark-update.md`).

### Runtime
- Google-Scholar-API-only discovery adapter + mandatory preflight;
  no-backend-switch policy enforced.
- Search planning/logging schema, screening states, legal full-text tracking.
- MissingFullTextGate: TXT (+XLSX) missing-literature report, checkpoint,
  PAUSED_WAITING_FOR_USER_FULLTEXT, validated resume (`resume_helper.py`).
- Evidence cards/matrix/argument map/synthesis; evidence-grounded drafting with
  structured citation placeholders; Zotero-first resolution chain +
  zero-hallucination audit (`citation_validator.py`).
- Figure plan/build workflow with DRAFT watermarking and data-provenance rules.
- Independent reviewer → revision → auditor → benchmark quality matching.
- Checkpoint/resume state machine (`runs/<id>/state.json`).

### Infrastructure
- 5 architecture diagrams (.mmd + .svg); docs set; evals E01–E17 with offline
  scripted suite; .gitignore/.env.example protecting keys & copyrighted text.
