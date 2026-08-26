---
name: geography-literature-review-skill
description: Distills how top geography/earth-science journals structure literature reviews (from a Reference Review Benchmark Corpus) and runs an evidence-first multi-agent pipeline to produce a new review on any user-specified topic: Google Scholar API-only discovery, legal full-text acquisition with a human pause gate when key PDFs are missing, evidence matrix + argument map + synthesis-driven drafting, Zotero-verified citations with zero hallucination policy, draft figures, independent review and audit. Use when the user asks to write/scaffold a literature review, systematic/scoping/narrative/conceptual review, or "geo-review" commands.
license: MIT
metadata:
  version: 1.0.0
  corpus: 60 benchmark reviews (Nature Reviews Earth & Environment et al.)
  hard-rules: google-scholar-only-discovery; missing-fulltext-pause-gate; zero-hallucinated-citations; benchmark-HOW-vs-task-WHAT
---

# Geography Literature Review Research Skill

Two corpora, two jobs — never confuse them:

| | Reference Review Benchmark Corpus | Task-specific Evidence Corpus |
|---|---|---|
| Lives in | `benchmark_corpus/` (distilled patterns) | `runs/<run-id>/` (built fresh per topic) |
| Teaches / provides | **HOW** to write a high-quality geography review | **WHAT** is true about the user's topic |
| May supply facts to the manuscript? | **NEVER** | Yes — only source of facts/gaps/citations |

## When to use what

- Compile-time (ingest/distill/update benchmark): `workflows/benchmark-distillation.md`, `workflows/benchmark-update.md`.
- Runtime (user gives a NEW topic): follow `workflows/full-review-workflow.md` stage by stage.

## Runtime non-negotiables (read before any search)

1. **Google Scholar API only.** External discovery for a new topic must go through
   the configured Google-Scholar-compatible provider (`GOOGLE_SCHOLAR_API_PROVIDER/_KEY/_ENDPOINT`).
   Run `python scripts/google_scholar_preflight.py` first. If unavailable ⇒ set state
   `PAUSED_GOOGLE_SCHOLAR_API_NOT_READY`, report, stop searching. Never fall back to
   WoS/Scopus/OpenAlex/Semantic Scholar/web scraping.
2. **MissingFullTextGate.** If an included/high-priority paper has no legally
   obtainable full text: generate `missing_fulltext_literature.txt` (+ `.xlsx`),
   save checkpoint, state `PAUSED_WAITING_FOR_USER_FULLTEXT`, ask the user for PDFs
   or explicit skip. Do not synthesize results from title/abstract guesses.
3. **Zero hallucinated citations.** Every citation needs Zotero item / DOI /
   authoritative metadata; unsupported claims ⇒ `INSUFFICIENT EVIDENCE`;
   unresolvable refs leave the bibliography into `unresolved_citations.csv`.
4. **Synthesis > summary.** No paper-by-paper enumeration as primary mode;
   organize around propositions, consensus, controversy, conditions.
5. **Geography reasoning is conditional.** Apply spatial explanations only when task
   evidence triggers them (`references/geography-reasoning-rules.md`).
6. **Gaps come from task evidence**, never from the benchmark corpus content.

## Stage map (runtime)

```
topic → preflight → interpret → mode → search-plan → parallel Scout retrieval
→ screen/dedupe → full-text acquisition ⟂ MissingFullTextGate → extract evidence
→ evidence-matrix → synthesize → argument-map → outline → draft (placeholders)
→ cite (Zotero) → figures → reviewer → revise → audit → benchmark-QA → final
```

Detailed per-stage instructions live in `workflows/*.md`; agent contracts in
`agents/runtime/*.md`; distilled method knowledge in `benchmark_corpus/*.md`.

## Commands

Natural language or `/geo-review <cmd>`:

Compile-time: `benchmark-ingest <folder>` · `benchmark-update <folder>` · `benchmark-audit` · `benchmark-profile`
Runtime: `scholar-check` · `start "<topic>"` · `search` · `screen` · `evidence` · `synthesize` · `outline` · `draft` · `cite` · `figures` · `review` · `audit` · `missing-fulltext` · `resume` · `full`

If the host lacks slash commands, these map to the same workflows via intent matching.

## Setup requirements (before runtime)

```bash
export GOOGLE_SCHOLAR_API_PROVIDER=serpapi      # any compatible gateway
export GOOGLE_SCHOLAR_API_KEY=...               # keep out of git
export GOOGLE_SCHOLAR_API_ENDPOINT=https://...
pip install pypdf pyyaml openpyxl requests       # optional: mermaid-cli for figure rendering
```

Zotero optional but recommended (Web API key or local Zotero 7 running). See
`docs/google-scholar-setup.md`, `docs/zotero-setup.md`.

## Priority order when anything conflicts

citation truth > claim–evidence consistency > provenance > accuracy > completeness >
synthesis quality > logic > style. If evidence is thin, say so
(`INSUFFICIENT EVIDENCE`) instead of writing beautifully about nothing.
