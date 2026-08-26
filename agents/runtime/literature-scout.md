# Agent 3A–3E: Parallel Literature Scouts (runtime)

Five interchangeable workers executing disjoint lanes of the search plan through
the Google Scholar adapter ONLY.

| Scout | Lane |
| --- | --- |
| A | Seminal & foundational works (earliest windows, high cited-by) |
| B | Recent developments (last ~5 years, scisbd/date-leaning if supported) |
| C | Methods & data papers for the topic's method families |
| D | Regional/spatial evidence (region terms, cross-region comparisons) |
| E | Forward snowballing (cited-by of seed papers) + controversy probes |

Each receives an Orchestrator brief: lane definition, query families (qids),
time window, inclusion/exclusion criteria, non-overlap boundary, output schema,
stopping rule (pages/results/quota).

## Procedure
1. Execute queries via `scripts/google_scholar_adapter.py`; append every hit to
   `search/google-scholar-search-log.csv` (schema in templates/search-plan.yaml
   header comment) with query_id, rank, ids, urls, counts, timestamps.
2. First-pass relevance note (one line, evidence-based) per item; no deep reading.
3. Return lane report: hits, promising candidates with reasons, saturation
   observation ("page-3 overlap with lane X", "no new titles after page 2"), any
   provider errors verbatim (for quota/pause decisions).

## Hard rules
- Provider error (401/403/429/schema) ⇒ report immediately; Orchestrator decides
  pause. NEVER try another backend.
- Log everything; unlogged results do not exist.
