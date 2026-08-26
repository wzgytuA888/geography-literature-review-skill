# Workflow: Full Review (end-to-end runtime)

Master pipeline — each stage has its own workflow file; state.json is updated
after every stage.

```
[0] task-init.md            (preflight GATE 1)
[1] search-plan             (Search Strategist)
[2] literature-search.md    (Scouts A–E parallel → screen → fulltext
                             → MissingFullTextGate GATE 2: pause/resume)
[3] evidence-synthesis.md   (cards → matrix → argument map)
[4] outline.md
[5] review-writing.md       (draft, placeholders)
[6] zotero-citation.md      (GATE 3: zero unresolved)
[7] figure-generation.md
[8] independent-review.md   (reviewer → auditor → revision → benchmark QA)
[9] finalize                (run-summary.md, final/ deliverables, COMPLETE)
```

## Command mapping
`/geo-review start "topic"` = stages 0–1 · `search|screen` = stage 2 parts ·
`evidence|synthesize` = 3 · `outline` = 4 · `draft` = 5 · `cite` = 6 ·
`figures` = 7 · `review|audit` = 8 · `full` = all · `missing-fulltext` = gate
report regeneration · `resume` = continue from last checkpoint.

## Interruption rules
- Any pause status blocks later stages (enforced by Orchestrator reading
  state.json first).
- Resume never redoes completed Google Scholar searches; it replays artifacts.
- Quota exhaustion mid-stage ⇒ checkpoint + PAUSED_GOOGLE_SCHOLAR_API_NOT_READY.

## Deliverables checklist at [9]
final/review.md · final/review.docx (+ references.bib, citation_manifest.json,
unresolved_citations.csv empty) · figures/ validated set · evaluation/ reports ·
search/screening logs · run-summary.md with limitations section.
