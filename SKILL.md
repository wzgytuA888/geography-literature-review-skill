---
name: geography-literature-review-skill
description: Produces deep, source-traceable, near-submission literature reviews for geography, Earth science, ecology, remote sensing, climate and environmental research. Use when the user provides a research topic or asks for a critical, narrative, systematic, scoping, methodological or bibliometric review; evidence map; field-progress/gap analysis; or `/geo-review`. It plans the protocol, searches current literature, screens and appraises studies, analyzes geographic and scale heterogeneity, synthesizes claims with certainty ratings, drafts the manuscript, verifies citations and runs independent publication-readiness audits. Do not use for explaining a single paper or answering a concept question that needs no literature search.
license: MIT
metadata:
  version: 4.0.0
  corpus: 60 benchmark reviews (Nature Reviews Earth & Environment et al.)
  hard-rules: evidence-first; reproducible-search-log; design-matched-appraisal; claim-ledger; no-invented-metadata; benchmark-HOW-vs-task-WHAT
---

# Geography Literature Review Research Skill v4

## Outcome contract

Turn a topic into the strongest defensible, **full-text-grounded** review the
available evidence permits. For Earth and environmental review requests, default
to the NREE-derived critical-review profile unless the user names another venue.
NREE-shaped means its argument architecture and prose pass the corpus-derived
rules; it never guarantees editorial acceptance or licenses copying source prose.

Run a topic-specificity gate before protocol freeze. A broad label such as
“water scarcity”, “climate change” or “urbanization” first receives a bounded
orientation search. If the evidence separates into materially different review
questions, present 3-5 evidence-informed direction cards and pause for one user
choice. Do not silently choose a publishable question for the user.

“Near-submission” means a complete manuscript and audit package, not guaranteed
acceptance. Never label a review systematic, exhaustive or meta-analytic unless
its search coverage, screening, appraisal and synthesis meet that method's gates.

## Corpus firewall

| Corpus | Purpose | May supply manuscript facts/citations? |
|---|---|---|
| `benchmark_corpus/` | teaches **HOW** strong reviews reason and write | Never |
| `runs/<run-id>/` | establishes **WHAT** is known about this topic | Yes, after screening and extraction |

## Read before acting

- Every new review: `workflows/full-review-workflow.md` and
  `references/multi-agent-orchestration.md`.
- Protocol/mode selection: `references/review-methods.md` and
  `references/reporting-standards.md`.
- Discovery: `workflows/literature-search.md` and `references/search-strategy.md`.
- Broad or ambiguous topics: `workflows/scope-convergence.md`.
- Full-text acquisition and handoff: `workflows/fulltext-acquisition.md`.
- Extraction/appraisal: `workflows/evidence-synthesis.md` and
  `references/critical-appraisal.md`.
- Synthesis/drafting: `references/synthesis-rules.md`,
  `references/geography-reasoning-rules.md`, and
  `references/publication-package.md`. For NREE-profile outputs also read
  `references/nree-review-writing.md`.
- Benchmark ingest/update: read only its matching workflow.

## One-topic default behavior

When the user supplies a topic without a protocol:

1. Create a run with `scripts/review_scaffold.py init`.
2. Run the specificity gate. If the topic is broad, perform orientation discovery,
   save `protocol/direction-options.md`, set state to
   `PAUSED_WAITING_FOR_SCOPE_SELECTION`, ask the user to choose, and stop.
3. Frame 1 primary question and at most 4 secondary questions; write a provisional
   contribution statement and a scope table (concept, geography, period, evidence
   type, outcomes).
4. Select the review mode by fitness, not prestige. Use `critical_narrative` by
   default; use `systematic` only when the question and accessible databases make
   exhaustive, reproducible coverage credible.
5. Search and screen, then acquire every included report used by the manuscript
   as a legal local full-text file. Metadata/abstracts may support orientation and
   screening only; they are excluded from the manuscript evidence set.
6. If any included full text remains unavailable after bounded legal routes, run
   `scripts/missing_fulltext_gate.py`. Deliver its XLSX file, set state to
   `PAUSED_WAITING_FOR_USER_FULLTEXT`, tell the user the exact upload directory,
   and stop all extraction, synthesis, outline and drafting work until resolved.
7. Extract, appraise and synthesize from local full text before outlining. Draft
   against the NREE architecture contract when that profile applies.
8. Produce the full publication package and run `scripts/review_quality_gate.py`.
   If a hard gate fails, revise or label the output `RESEARCH DRAFT — NOT
   SUBMISSION READY` with the exact unresolved items.

## Evidence invariants

1. **Search adequacy, not API convenience.** Semantic Scholar and OpenAlex are
   strong open discovery layers; Crossref validates metadata. For a claimed
   systematic review, use field-appropriate bibliographic databases available to
   the user and report every source/platform exactly. Public-API-only coverage is
   normally a critical/narrative or scoping evidence base, not proof of exhaustion.
2. **Reproducibility.** Preserve verbatim user terms, generated and translated
   queries, database/platform, fields searched, filters, dates, counts, errors,
   deduplication and search-update date. Validate search sensitivity against known
   sentinel papers when available.
3. **Conservative records.** Never invent abstracts, DOIs, findings, methods,
   locations or quality judgments. Unknown fields are `null` or `not_reported`.
   Separate source fact, extraction and inference; inference is flagged.
4. **Independent decisions.** Systematic/scoping modes require two independent
   screening judgments and adjudication, or an explicit single-reviewer/AI-assisted
   limitation. Never imply human dual screening when agents performed it.
5. **Design-matched appraisal.** Select an appraisal tool/domain set by study
   design and review question. Do not replace risk-of-bias judgments with citation
   counts, journal rank or a generic numeric quality score.
6. **Local full text before writing.** Every report admitted to the manuscript
   evidence set must have identity-verified local PDF/HTML/text and a checksum.
   Abstract-only records may map the field or justify a recorded exclusion, but
   cannot support manuscript claims or citations. Any screened-in missing text
   triggers the XLSX handoff and pause. The run clears only after a verified file
   arrives or a documented protocol-valid screening revision excludes the report.
   A filename match is never identity verification; require readable content plus
   DOI, or title with author/year corroboration, and retain the extracted text.
7. **Unit-of-analysis control.** Track shared datasets, overlapping samples,
   reused models and author teams so dependent studies are not counted as
   independent replication.
8. **Claim ledger.** Every material manuscript claim records supporting and
   contradicting evidence IDs, conditions, appraisal, geographic applicability,
   confidence and verified citations. Absence of evidence is not evidence of a gap.
9. **Geographic validity.** Examine scale, zoning, spatial dependence, sampling
   footprint, regional imbalance, environmental gradient, boundary mismatch and
   transferability whenever triggered by the evidence.
10. **Citation truth.** Resolve references from the run registry through DOI,
    Zotero or authoritative provider metadata. Unverifiable references are removed
    or left explicitly unresolved; never fabricate them.

## Multi-agent execution

The Orchestrator runs specialists in dependency-aware waves. Use real parallel
subagents when the host supports them; otherwise execute the same roles serially.
No two agents edit the same authoritative artifact. Independent reviewers receive
the frozen protocol/evidence/draft but not the writer's private reasoning.

The Python CLI supplies deterministic acquisition, scaffold and integrity tools;
it is not the multi-agent runtime. On Codex/agent hosts, actually dispatch the role
contracts and record them in `reporting/agent-manifest.csv`. Never claim the CLI
alone executed extraction, appraisal, synthesis or writing stages it does not own.

Core roles: Protocol Architect · Domain/Mechanism Theorist · Search Strategist ·
Search Peer Reviewer · parallel Literature Scouts · Screening Reviewers A/B ·
Adjudicator · Research Landscape Cartographer · Legal Full-text Acquisition Agent ·
Full-text Verifier · Extraction Reviewers A/B · Critical Appraisal
Specialist · Geospatial Heterogeneity Analyst · Quantitative/Qualitative Synthesis
Specialist · Contradiction Red Team · Outline Architect · Writing Agent · Citation
Verifier · Figure/Table Agent · NREE Architecture Editor · Journal Editor ·
Reproducibility Auditor.

Read `references/multi-agent-orchestration.md` for role contracts, wave ordering,
conflict resolution and minimum-role fallbacks.

## Standard pipeline

```text
topic → specificity gate → orientation search → [user scope choice when broad]
→ protocol + contribution test → peer-reviewed search strategy
→ multi-source discovery + sentinel recall → deduplicate
→ dual screen/adjudicate → legal local full text for every included report
→ [missing-fulltext XLSX + pause when unresolved] → duplicate extraction checks
→ design-matched appraisal → dependency map + spatial representativeness audit
→ proposition clusters + certainty → contradiction/gap tests
→ argument map → NREE-shaped outline → full-text-bound draft
→ verified citations + figures/tables → red-team/reviewer/reproducibility audits
→ revision → submission-readiness gate → manuscript + supplements
```

Every downstream agent and executable must pass `scripts/run_state_guard.py`
before writing. Exit code 9 is a hard pause boundary, not an advisory warning.

## Commands

Natural language or `/geo-review <cmd>`:

`start` · `protocol` · `search-review` · `search` · `screen` · `adjudicate` ·
`snowball` · `fulltext` · `extract` · `appraise` · `geo-audit` · `synthesize` ·
`certainty` · `outline` · `draft` · `cite` · `figures` · `red-team` · `review` ·
`audit` · `package` · `resume` · `full`

## Deliverables

The default final package includes manuscript (Markdown; DOCX when the document
toolchain is available), structured abstract, keywords, methods, main text,
limitations, conclusions, verified bibliography, evidence/profile tables,
search strings and log, screening/flow counts, appraisal table, claim ledger,
figures/tables with provenance, reporting checklist, author query list and a
readiness report. When access blocks the run, the package instead includes
`missing_fulltext_literature.xlsx`, the expected upload path and a resumable
checkpoint. See `references/publication-package.md`.

## Priority

citation truth > claim–evidence consistency > search/appraisal transparency >
geographic validity > synthesis depth > completeness > prose polish. Thin or
inaccessible evidence must be reported as such, never filled with plausible text.
