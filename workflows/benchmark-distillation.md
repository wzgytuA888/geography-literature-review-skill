# Workflow: Benchmark Distillation (Compile-time)

Purpose: turn the Reference Review Benchmark Corpus into transferable
**HOW-TO-REVIEW** method knowledge. This stage never produces topic facts.

## Pipeline

```
PDFs → extract_documents.py → manifest.jsonl (+ .cache/fulltext)
     → benchmark_index.py    → benchmark-index.jsonl + benchmark-stats.json
     → prepare_mining_digests.py → .cache/digests/B*.txt
     → Pattern Miners (agents/compiletime/*.md, run in parallel batches)
         each doc: benchmark_corpus/pattern_cards/B###.yaml
         each batch: .cache/mining/batch-N-findings.md
     → Consolidation (Benchmark Consolidator)
         benchmark_corpus/{review-architecture,section-patterns,
           paragraph-rhetoric,synthesis-patterns,argument-patterns,
           citation-patterns,geography-reasoning-patterns,
           gap-identification-patterns,future-agenda-patterns,
           figure-patterns,quality-rubric,anti-patterns}.md
         benchmark_corpus/archetypes/*.md
```

## Miner instructions (used by compile-time Review/Citation/Geography/Figure miners)

For each assigned document:

1. Read `.cache/digests/<doc>.txt` only (progressive disclosure; never re-read
   whole PDFs).
2. Fill `templates/review-pattern-card.yaml` schema exactly → save as
   `benchmark_corpus/pattern_cards/<doc>.yaml`.
3. Extraction rules:
   - **Form over content**: record the *move*, not the science.
   - Exemplar quotes ≤15 words, at most one per field.
   - `UNKNOWN` is a legal value; guessing is a defect.
   - Cite page/slice provenance in `source_provenance`; set `confidence`
     honestly (`low` when the digest warns of poor extraction).
4. Batch findings file `.cache/mining/batch-<N>-findings.md`: for each dimension
   (architecture / introduction / rhetoric / synthesis / citation / geography /
   gap-agenda / figures / rubric / anti-pattern) list recurring patterns as
   bullets tagged with document IDs and frequency (`k/N docs`). Only patterns
   observed in ≥2 documents may be called "recurring"; singles are "candidate".

## Consolidation rules

- Merge batch findings across all batches; keep frequency counts and document
  IDs as evidence lines in the consolidated files.
- Distinguish corpus-consensus rules (≥50% of scored docs), common variants
  (≥20%), and outliers (explicitly non-transferable).
- Archetypes: cluster documents by review mode; one archetype file per cluster
  with its signature architecture and rhetoric profile.
- Never copy long passages from source reviews into consolidated files.
- Update `quality-rubric.md` so every criterion is checkable at runtime.

## Incremental fold-in

See `workflows/benchmark-update.md`. Fold-in reprocesses only new documents,
compares against existing patterns (support / extend / contradict), updates
counts, versions, and CHANGELOG — no full reprocessing.
