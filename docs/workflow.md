# Workflow Overview

Entry points:
- **Runtime**: `workflows/full-review-workflow.md` chains task-init → search-plan
  → literature-search → evidence-synthesis → outline → review-writing →
  zotero-citation → figure-generation → independent-review → finalize.
- **Compile-time**: `workflows/benchmark-distillation.md` and
  `workflows/benchmark-update.md` (fold-in).

## State machine

```
RUNNING ─┬─> COMPLETE
         ├─> PAUSED_GOOGLE_SCHOLAR_API_NOT_READY   (fix config → resume)
         ├─> PAUSED_WAITING_FOR_USER_FULLTEXT      (supply PDFs / skip → resume)
         ├─> AWAITING_REVIEW                        (systematic/scoping outline gate)
         └─> FAILED_<stage>                         (inspect run-summary)
```

`runs/<id>/state.json` is written after every stage; resume replays artifacts and
never repeats completed Scholar queries.

## Command surface

| Command | Effect |
| --- | --- |
| scholar-check | preflight only |
| start "<topic>" | init + plan |
| search / screen | stage 2 parts |
| evidence / synthesize | stage 3 |
| outline | stage 4 |
| draft | stage 5 |
| cite | stage 6 |
| figures | stage 7 |
| review / audit | stage 8 |
| missing-fulltext | regenerate gate report |
| resume | continue from checkpoint |
| full | whole pipeline |
| benchmark-ingest / -update / -audit / -profile | compile-time |

Slash commands work where the host supports them; otherwise use natural language
("write a literature review on X") — SKILL description routes it here.
