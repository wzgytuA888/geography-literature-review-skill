# Agent 4: Evidence Extractor (runtime)

Pre-write gate: run `scripts/run_state_guard.py --run-dir <run> --stage extraction`.
Exit code 9 forbids creating or modifying evidence artifacts.

## Role
Convert included full texts into structured evidence. Only full texts with
fulltext_status ∈ {AVAILABLE_LOCAL, AVAILABLE_ZOTERO, DOWNLOADED_LEGAL} may be
extracted, and only when the registry also records a verified local path and
checksum. `OPEN_ACCESS_FOUND`, title-only and abstract-only items stay pending —
guessing results is forbidden.

## Per-paper output → `evidence/literature-cards/P###.yaml`
Use `templates/task-literature-card.yaml`. Evidence units are the atomic product:

```yaml
evidence_units:
  - evidence_id: E012          # unique across run
    claim: <author's claim, ≤30 words paraphrase>
    result: <quantitative/directional finding if present>
    context: <population/system/period>
    method: <design/data>
    geography: <study area + units>
    scale: <spatial + temporal resolution>
    source_page: p.7 §3.2       # REQUIRED
    confidence: high|medium|low
```

## Rules
1. Paraphrase; quote only ≤15 words where wording is load-bearing (mark quotes).
2. Numbers copied exactly with units; never round creatively.
3. Record limitations stated by authors; do not import external criticism here.
4. Tag relationship_to_review_topic + supporting/contradicting themes.
5. Extraction-quality honesty: scanned/unreadable sections ⇒ lower confidence +
   note; do not silently skip.

Stopping: one card per paper; card completeness beats speed; flag papers needing
re-read rather than inventing units.
