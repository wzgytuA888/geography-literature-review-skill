# Evaluation

Two layers: **scripted evals** (deterministic, offline) and **judge evals**
(LLM-as-judge against the rubric on fixture topics).

## Scripted (run now)
```bash
python evals/run_scripted.py
```
Covers: E02 separation heuristic · E03 backend-exclusivity with mock provider ·
E04 matrix integrity on broken fixture · E10 fake-citation handling · E14
benchmark-stats computability. Exit 0 = all pass.

## Judge-based procedure
1. Run the target workflow on the fixture named in each `evals/E##-*.md`
   (mock Scholar provider for search stages).
2. Score outputs against `templates/review-rubric.yaml` dimensions
   (0–2 per criterion) plus the eval's specific pass criteria.
3. Record verdicts into the run summary; hard red lines (see evals/README.md)
   are release blockers regardless of average scores.

## Hard metrics (must equal 0)
unverifiable final references · benchmark leakage into task claims · unsupported
quantitative figures · unsupported gap statements · unauthorized discovery
backends · silent skips of high-priority missing full text · synthesis while
paused · near-copy from benchmark.

## When to re-run
Any change to scripts/, workflows/, agents/, or benchmark corpus fold-ins.
E15–E17 (full dry-run, fold-in, resume) run after every major refactor.
