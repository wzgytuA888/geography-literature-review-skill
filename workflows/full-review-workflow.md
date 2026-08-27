# Full Review Workflow v4

Read `references/multi-agent-orchestration.md` before starting.

```text
[0] scaffold + verbatim request + automation manifest
[1] topic-specificity gate + orientation search
[2] if broad: 3-5 direction cards + PAUSED_WAITING_FOR_SCOPE_SELECTION
[3] selected question + review-mode triage + protocol + contribution test
[4] concept blocks + source plan + independent search peer review
[5] multi-source search + sentinel recall + raw snapshots/Search Log
[6] report dedup + study/site family linkage
[7] independent title/abstract screening + adjudication
[8] legal local full-text acquisition for every included report
[9] if missing: XLSX handoff + PAUSED_WAITING_FOR_USER_FULLTEXT
[10] full-text screening + piloted extraction + second-pass verification
[11] design-matched appraisal + dependency map
[12] geography/scale/representativeness audit
[13] method-appropriate synthesis + certainty profile
[14] contradiction, causal, transferability and gap red team
[15] claim ledger + argument map + NREE-shaped outline and visual argument
[16] full-text-bound manuscript + tables/figures/Boxes
[17] citation, NREE-architecture, scientific, journal and reproducibility audits
[18] revision + quality gate + submission package
```

Checkpoint every stage in `state.json`; record protocol amendments rather than
overwriting history. Agents write staging artifacts and the Orchestrator merges
canonical files. A provider failure logs degraded coverage; whether work can
continue depends on the review label and source plan, not merely whether one API
returned results.

## Completion behavior

- `SUBMISSION_CANDIDATE`: all hard gates pass; manuscript and supplements complete;
  remaining author sign-offs listed.
- `RESEARCH_DRAFT_NOT_READY`: useful complete draft, but access, human verification,
  appraisal, freshness or journal-fit items remain.
- `INSUFFICIENT_EVIDENCE`: evidence cannot support the planned primary conclusion;
  deliver the evidence map, limitations and a precise next-step acquisition plan.

Pause exactly at two user-owned gates: a material scope choice after orientation
search, or any unresolved screened-in full text after the legal acquisition pass.
Do not continue drafting around either gate.

