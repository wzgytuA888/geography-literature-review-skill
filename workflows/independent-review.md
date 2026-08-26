# Workflow: Independent Review & Audit & Benchmark QA

Sequence after draft (+figures):

## Round 1 — Reviewer (findings only)
Output evaluation/reviewer-report.md (severity-tagged findings). No rewriting in
this round by design (writer cannot grade its own work).

## Round 2 — Evidence & Citation Auditor
Row-by-row lineage verification → evaluation/evidence-errors.csv. Blockers listed
explicitly.

## Round 3 — Revision
Revision Agent resolves blockers→majors→minors; logs to
evaluation/revision-log.md; re-runs citation_validator + phrase_overlap_check.

## Round 4 — Benchmark Quality Matching
Compare against corpus stats/patterns (references/quality-control.md Gate 3) →
evaluation/corpus-quality-comparison.md. Logic metrics only; near-copy screen must
PASS.

## Final QA
All gates PASS + hard red lines zero + limitations declared → Orchestrator marks
COMPLETE, writes runs/<id>/run-summary.md, delivers final/ artifacts.
