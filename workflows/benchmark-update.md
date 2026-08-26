# Workflow: Benchmark Update (Incremental Fold-in)

Trigger: new reviews added to `new_benchmark_reviews/` (or any folder the user
names) — applies to the Benchmark Corpus ONLY.

## Steps
1. **Curate**: `python scripts/extract_documents.py --source <new_folder> --out
   benchmark_corpus/manifest-incremental.jsonl` → dedupe vs existing manifest
   (SHA-256 + title similarity). Duplicates stop here.
2. **Digest & mine**: `python scripts/prepare_mining_digests.py --docs B061,B062,…`
   then run Review/Citation/Geography/Figure miners on the NEW docs only.
3. **Compare** each new pattern against consolidated files:
   - support (already-recorded pattern, bump frequency + doc ids)
   - extend (variant of known pattern; add as variant line)
   - contradict (challenge to a consensus rule ⇒ demote consensus→contested and
     flag in CHANGELOG for user review)
   - novel (candidate until it recurs)
4. **Consolidate**: re-run consolidator limited to affected files; keep version
   bump minor unless schema changed.
5. **Update**: archetypes membership, quality-rubric thresholds if warranted,
   `benchmark-stats.json` recomputation, CHANGELOG.md entry.
6. Never touch past runtime runs' scientific facts — fold-ins change HOW only.
7. Full reprocessing ONLY when schema or core algorithm changes (user-approved).

## Rollback safety
manifest is append-only; consolidation diffs recorded via git commit per update.
