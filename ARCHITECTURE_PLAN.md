# ARCHITECTURE_PLAN.md — Geography Literature Review Research Skill

> Status: v3.0 · protocol-first, source-plan-first, multi-agent publication workflow.
> This document fixes the architectural decisions for the whole repository.
> Technology evidence lives in `docs/technology-baseline.md`.

---

## 1. Technologies checked (summary)

Reconnaissance was executed live at build time against official sources; the full
evidence table is in `docs/technology-baseline.md`. Key conclusions:

- **Book-to-Skill**: methodology source (structure/procedure/decision-rules distillation,
  progressive disclosure, incremental fold-in). We adopt its *principles*, not its code.
- **Agent Skills open standard**: `SKILL.md` with YAML frontmatter (`name`, `description`),
  progressive disclosure L1 metadata → L2 SKILL.md → L3 on-demand resources. We follow
  agentskills.io / Anthropic conventions and keep SKILL.md < 500 lines.
- **Academic discovery v3**: source selection follows the protocol. Semantic
  Scholar/OpenAlex are open discovery layers and Crossref validates metadata;
  formal systematic reviews add field, grey and regional sources as required.
- **Zotero**: Web API v3 + local HTTP server (Zotero 7) + Better BibTeX JSON-RPC;
  adapter with capability detection and fallback chain.
- **Multi-agent**: orchestrator-worker pattern (Anthropic research-system practice);
  workers run in parallel where independent; reviewers are separate from writers.

## 2. Book-to-Skill version adopted

Principles distilled from the current public Book-to-Skill approach: convert a
reference corpus into transferable *procedure* (not summaries); store knowledge in
progressive-disclosure resource files; support incremental fold-in without full
reprocessing; keep provenance for every extracted pattern. Version pinning and
checked dates: see `docs/technology-baseline.md` §1.

## 3. Agent Skills specification followed

- `SKILL.md`: YAML frontmatter with `name` (lowercase-hyphen), `description`
  (third-person, includes trigger conditions, ≤1024 chars), optional
  `license`, `metadata`.
- Body: instructions only; heavy content pushed to `references/`, `workflows/`,
  `agents/`, `scripts/`, `templates/` loaded on demand (L3).
- No execution guarantees assumed from frontmatter alone; slash-command surface
  documented but natural-language triggers provided as equivalent.

## 4. Why Benchmark Corpus ≠ Task Evidence Corpus

The benchmark corpus (60 high-quality geography/earth-science reviews, mostly
*Nature Reviews Earth & Environment*) teaches **HOW to review**:
architecture, rhetoric, synthesis moves, citation behavior, geography-reasoning
conditions, gap derivation logic, figure strategy, quality rubric.

It must never supply WHAT is true about a new topic. Every runtime fact, number,
consensus/controversy claim, gap, and citation comes exclusively from the
task-specific Evidence Corpus built fresh via the protocol-approved sources and
legal full-text acquisition. On conflict, task evidence wins.

Enforcement mechanisms (defense in depth):
1. Physical separation: `benchmark_corpus/` vs `task_corpora/` vs `runs/<run-id>/`.
2. Different data structures: Review Pattern Card vs Evidence Literature Card.
3. Writing agent input whitelist: task evidence matrix + validated cards + method
   rules only — benchmark full text never enters the writing context.
4. Evals E02 (corpus separation) and hard metric "benchmark leakage = 0".
5. Phrase-overlap / near-copy check against benchmark text before final QA.

## 5. Compile-time / Runtime boundary

**Compile-time** (offline, one-time + incremental): Benchmark Distillation —
parse PDFs → structural metadata → Review Pattern Cards → pattern mining
(section / paragraph / synthesis / citation / geography / gap / agenda / figure)
→ consolidation → distilled method files under `benchmark_corpus/` → quality
rubric + anti-patterns. Agents: curator, miners (review/citation/geography/figure),
consolidator.

**Runtime** (per user topic): scaffold → protocol/review-mode routing → source plan
and independent search review → parallel retrieval/import → report/study/site
linkage → independent screening/adjudication → full-text tiers → verified
extraction → design-matched appraisal/dependency/geographic audits → synthesis and
certainty → contradiction/gap red team → claim ledger → outline/draft → verified
citations/figures → scientific/journal/reproducibility review → revision →
readiness verdict. All state lives under `runs/<run-id>/` with checkpoints.

Runtime reads distilled method rules (HOW) but no benchmark scientific content.

## 6. Why Review Pattern Card

Traditional literature cards would capture *content* of the reviews — exactly what
we must NOT transfer. A Review Pattern Card captures *form*: review design,
introduction moves, section logic, rhetorical sequences, citation density/cluster
behavior, geography reasoning triggers, figure roles, gap/agenda derivation,
quality features, anti-patterns, provenance. UNKNOWN values are recorded verbatim,
never guessed.

## 7. How "HOW TO REVIEW" is distilled

Pipeline: `workflows/benchmark-distillation.md`. Each dimension gets a dedicated
miner prompt (`agents/compiletime/*.md`) reading cached fulltext locally, emitting
pattern findings; a consolidator merges across documents into
`benchmark_corpus/*-patterns.md` + archetypes, keeping frequency counts and
document provenance so rules reflect corpus consensus rather than single papers.

## 8. Preventing benchmark content leakage into new articles

See §4 enforcement list. Additional guard: the phrase-overlap checker
(`scripts/phrase_overlap_check.py`) compares draft n-grams against cached benchmark
text; long overlaps force rewrite. Gap statements require evidence IDs from the
task matrix (`INSUFFICIENT EVIDENCE FOR GAP CLAIM` otherwise).

## 9. Multi-agent runtime construction

Lead Orchestrator + protocol/domain, search/peer-review, scout, screening/
adjudication, full-text, extraction, appraisal, geospatial, synthesis/certainty,
red-team, writing, citation/figure, journal/reproducibility and revision roles.
Each agent definition is an artifact contract. Parallelism is limited to independent
work; one owner merges canonical data and one writer owns the manuscript voice.

## 10. Skill ↔ MCP boundary

Skills provide procedural knowledge and file artifacts; MCP provides tool access.
Academic API calls go through the v2 REST clients (plain HTTPS, not an MCP
dependency). Zotero access uses Web API/local server/
Better BibTeX directly through `scripts/zotero_adapter.py`; if a Zotero MCP is
present in the host it may be used opportunistically, but is not required.

## 11–13. Zotero as reference source of truth; provenance; citation verification

Every final citation requires: Zotero item OR verifiable DOI OR authoritative
metadata record; model memory alone is forbidden. Chain: claim → evidence unit →
card → source location → DOI/Zotero → metadata verification → claim-support
verification → inserted citation. Failures become `UNRESOLVED CITATION` and are
removed from the final list into an unresolved report. Audit trail:
`citation/citation-audit.csv` per run.

## 14–16. Figures, reviewers/auditors, evals

Figures: plan first (`figure-plan.md`), then real drafts (Mermaid/Graphviz/
Python) marked DRAFT SCIENTIFIC FIGURE until validated; quantitative figures need
real data. Independent reviewer finds problems only (round 1); auditor traces
every claim→citation lineage; benchmark quality matching compares logic metrics,
not wording. Evals E01–E17 in `evals/` with hard gates (hallucinated refs = 0,
leakage = 0, silent skips = 0).

## 17. Long-running checkpointing

`runs/<run-id>/state.json` records stage, status enum
(`PAUSED_ACADEMIC_APIS_NOT_READY`, `PAUSED_WAITING_FOR_USER_FULLTEXT`, …),
artifacts, timestamps. Resume continues from last completed stage; completed
searches are never redone unless invalidated.

## 18–19. Copyright / privacy; GitHub release policy

Raw PDFs, extracted full text cache (`.cache/`), `.env`, keys, run artifacts stay
local via `.gitignore`. Public-safe repo contains code, prompts, templates, generic
rules, synthetic examples only. Default GitHub target: **private** repository
named `geography-literature-review-skill`.

## 20–24. Academic API abstraction & preflight; provider roles;
missing-fulltext gate; missing report schema; pause/resume machine

- Provider abstraction (`src/geo_review/clients`): Semantic Scholar and OpenAlex
  primary discovery, Crossref DOI validation/enrichment, shared normalized record.
- Preflight (`scripts/literature_review_pipeline.py preflight`): each primary API
  is probed independently. Complete outage pauses; partial failure logs degraded
  coverage and preserves successful results.
- Provider rule: Google Scholar is optional manual supplementation only; result
  pages are never scraped. Crossref is not the primary topical search engine.
- MissingFullTextGate: INCLUDED_PENDING_FULLTEXT /
  HIGH_PRIORITY_PENDING_FULLTEXT items without legal fulltext ⇒ generate
  `missing_fulltext_literature.txt` (+ .xlsx when openpyxl available), save all
  state, pause, request PDFs/Zotero uploads or explicit skip; resume validates
  paper↔PDF↔DOI↔Zotero mapping and continues extraction. Explicit user skip sets
  `explicit_user_skip=true` and keeps audit records.

## 25. Main risks & fallbacks

| Risk | Mitigation |
| --- | --- |
| Scholar provider quota exhausted mid-run | checkpoint + pause; resume after refill |
| Provider schema variance | adapter normalizes; unknown fields logged, not guessed |
| Zotero unavailable | fallback chain Better BibTeX → DOI metadata → CSL/BibTeX output; never fake success |
| Mermaid CLI rendering fails | keep .mmd sources; SVG/PNG rendered when toolchain available |
| Large-PDF extraction errors | per-page try/except; page-level gaps recorded in provenance |
| Pattern overfit to single journal | consolidator tracks cross-document frequency; outlier flagged |

Hard priority order (unchanged): citation truth > claim–evidence consistency >
provenance > accuracy > completeness > synthesis > style.
