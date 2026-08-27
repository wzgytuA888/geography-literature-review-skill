# Agent 6: Outline Agent (runtime)

Pre-write gate: run `scripts/run_state_guard.py --run-dir <run> --stage outline`.

## Role
Design the article skeleton from task reality, using benchmark architecture
patterns as priors — never as a fixed template.

## Inputs (all required)
- `task.md`, `review-mode.yaml`
- `evidence/evidence-matrix.csv` + `argument-map.md` + synthesis notes
- `benchmark_corpus/review-architecture.md` + relevant `archetypes/*.md`
- `references/nree-review-writing.md` when NREE profile applies

## Output → `writing/outline.md`

For every section/subsection:
```yaml
- section: 3.2 Scale-dependent responses
  purpose: <why this section exists for THIS review's question>
  key_propositions: [P3, P4]
  evidence_cluster: [E041, E044, E052, E058, E061]
  rhetorical_move: synthesis-with-comparison → geographic-condition explanation → boundary
  planned_figure_or_table: Fig2 (mechanism) | T1 (method matrix)
  open_questions: [...]
```

## Rules
1. Every major proposition in the argument map must live in exactly one home
   section; orphans ⇒ restructure, not discard silently.
2. Sections with no evidence cluster are cut or merged — no hollow headers.
3. Introduction must earn the review: fragmentation statement grounded in the
   corpus you actually screened; scope & contribution explicit.
4. Gap/agenda sections may only cite gap candidates validated by Orchestrator.
5. Choose a progression ladder that the argument map supports; record why. Generic
   topic lists and evidence-free headings fail the NREE architecture gate.
6. Plan the framework figure, evidence displays, synthesis figure/table and any Box
   before prose; every visual carries evidence IDs and a rhetorical job.

Stopping: outline complete when drafting needs no structural decisions left.
