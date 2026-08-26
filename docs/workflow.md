# Workflow Overview v2

Runtime entry point: `workflows/full-review-workflow.md`.

```
RUNNING ─┬─> COMPLETE
         ├─> PAUSED_ACADEMIC_APIS_NOT_READY
         ├─> PAUSED_WAITING_FOR_USER_FULLTEXT
         ├─> AWAITING_REVIEW
         └─> FAILED_<stage>
```

Provider-specific failures normally produce degraded coverage and an `errors.log`
entry, not a failed run. The complete-API outage state is used only when neither
Semantic Scholar nor OpenAlex is usable.

Commands: `api-check`, `start`, `search`, `screen`, `snowball`, `evidence`,
`themes`, `synthesize`, `outline`, `draft`, `cite`, `figures`, `review`, `audit`,
`export`, `missing-fulltext`, `resume`, `full`, plus benchmark compile-time commands.

Legacy `scholar-check` maps to `api-check` for compatibility.
