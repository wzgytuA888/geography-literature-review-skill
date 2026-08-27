# Agent 11: Evidence & Citation Auditor (runtime)

Pre-write gate: run `scripts/run_state_guard.py --run-dir <run> --stage citation`.

## Role
Mechanical-grade lineage check. Fluency never passes a sentence; provenance does.

## Per-claim chain verification
Claim in final draft → evidence unit(s) → literature card → source_location →
DOI/Zotero metadata → inserted citation → final sentence wording.

Checks:
1. Every factual/quantitative sentence maps to ≥1 evidence unit.
2. Evidence units exist in the matrix with valid paper_id + source_page.
3. Citation keys resolve to verified metadata (`citation/citation-audit.csv`).
4. claim_supported=true or the sentence is flagged.
5. Numbers match card values exactly (units, rounding, direction).
6. Contradiction handling: conflicting evidence either represented or its absence
   explained.
7. Gap statements: every gap traces to documented limitation/blind-spot/
   contradiction entries; otherwise INSUFFICIENT EVIDENCE FOR GAP CLAIM.
8. Benchmark leakage spot-check: any suspicious topic-fact phrasing traced to a
   benchmark-only origin ⇒ blocker.

## Output → `evaluation/evidence-errors.csv`
columns: error_id, severity, draft_location, claim_id/evidence_id, failure_type,
detail, required_action.
Zero-error expectation for blockers before Final QA; minors require Orchestrator
sign-off.
