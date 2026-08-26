# Eval Harness

Each `E##-*.md` defines purpose, setup, procedure, pass criteria for one capability.
Evals run against fixtures under `fixtures/` (synthetic only — no copyrighted text)
or recorded runs. LLM-judged items use the rubric dimensions from SKILL spec §27.

## Index

| id | name | type | hard metric |
| --- | --- | --- | --- |
| E01 | Benchmark pattern extraction quality | LLM-judge | ≥80% of sampled cards fields evidence-backed |
| E02 | Benchmark vs task corpus separation | scripted+judge | leakage count = 0 |
| E03 | Literature search only (Scholar) | scripted mock provider | 0 non-Scholar calls; log completeness 100% |
| E04 | Evidence matrix integrity | scripted | orphan ids = 0; source_location coverage = 100% |
| E05 | Controversy detection | fixture judge | diagnosis ladder applied before "inconsistent" |
| E06 | Geography conditional reasoning | fixture judge | no rule fired without trigger; missed triggers ≤1 |
| E07 | Outline generation | judge | every proposition homed; no hollow sections |
| E08 | Section drafting | judge | enumeration ceiling respected; placeholders used |
| E09 | Citation matching | scripted adapter mock | Zotero-first chain order respected |
| E10 | Fake citation detection | scripted | fabricated refs flagged = 100% |
| E11 | Claim-citation mismatch detection | fixture judge | mismatched pairs caught ≥90% |
| E12 | Research gap validation | scripted+judge | unsupported gap statements = 0 |
| E13 | Figure plan grounding | scripted+judge | ungrounded figures downgraded, not drawn |
| E14 | Benchmark quality matching | scripted stats compare | logic metrics computed vs benchmark-stats.json |
| E15 | Full workflow dry-run (mock provider) | e2e | gates fire in order; pause states correct |
| E16 | Incremental fold-in | scripted | no full reprocess; CHANGELOG entry produced |
| E17 | Resume from checkpoint | scripted | state restored; no duplicate searches |

## Hard red lines (any failure ⇒ release blocked)
hallucinated references >0 · benchmark content leakage >0 · unsupported quantitative
figures >0 · unsupported gaps >0 · unauthorized backend use >0 · silent skips >0 ·
final synthesis during PAUSED_WAITING_FOR_USER_FULLTEXT >0 · near-copy from
benchmark >0.

## Running
Scriptable evals: `python evals/run_scripted.py` (offline, uses fixtures).
Judge-based evals: run the referenced workflow on the named fixture topic, then
score with `templates/review-rubric.yaml`.
