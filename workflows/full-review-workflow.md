# Full Review Workflow v3

Read `references/multi-agent-orchestration.md` before starting.

```text
[0] scaffold + verbatim request + automation manifest
[1] review-mode triage + protocol + scope/contribution test
[2] concept blocks + source plan + independent search peer review
[3] multi-source search + sentinel recall + raw snapshots/Search Log
[4] report dedup + study/site family linkage
[5] independent title/abstract and full-text screening + adjudication
[6] legal full-text tiers + identity verification
[7] piloted extraction + second-pass verification
[8] design-matched appraisal + dependency map
[9] geography/scale/representativeness audit
[10] method-appropriate synthesis + certainty profile
[11] contradiction, causal, transferability and gap red team
[12] claim ledger + argument map + journal-shaped outline
[13] evidence-bound manuscript + tables/figures
[14] citation, scientific, journal and reproducibility audits
[15] revision + quality gate + submission package
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

Do not pause for every imperfect record. Pause only when missing access or a user
decision would change the primary conclusion, chosen review label or authorized
scope.

