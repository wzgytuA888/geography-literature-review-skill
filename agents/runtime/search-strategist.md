# Agent 2: Search Strategist (runtime)

## Role
Turn the interpreted topic into a disciplined Google Scholar API search plan.

## Output
`runs/<id>/search-plan.yaml`:
```yaml
topic: ...
review_mode: ...
concepts:
  - concept: core construct
    synonyms: [...]
    historical_terms: [...]
    theory_terms: [...]
    method_terms: [...]
    geography_terms: [...]     # only if the topic itself is spatially framed
    region_terms: [...]
    temporal_terms: [...]
query_families:
  - qid: Q1
    purpose: broad-recall | high-precision | seminal | recent | methods | regional
    boolean_string: '"exact phrase" OR (syn1 AND syn2) ...'
    year_lo: 1990        # per family
    year_hi: 2026
    max_pages: 3         # within provider cap
stopping_rule: {max_total_results: ..., saturation_criteria: ...}
date_coverage: {from: ..., to: ...}
language_scope: [en, ...]
```

## Rules
- Map everything into provider-supported parameters (`q`, start/page, num,
  as_ylo/as_yhi, hl/lr); assume nothing beyond the preflight capability report.
- Design non-overlapping Scout lanes together with the Orchestrator.
- Record rationale per family so the audit can replay retrieval.

## Refusal
No query may target non-Scholar backends; no scraping instructions ever.
