# E20 — NREE Architecture Release Gate

## Procedure

Apply the independent NREE Architecture Editor to a complete synthetic review
package using `templates/nree-architecture-gate.yaml` and then run
`scripts/review_quality_gate.py`.

## Pass criteria

- The manuscript has an evidence-led title and abstract, a five-move
  introduction, a content-named conceptual progression, diagnostic treatment of
  disagreements, an argumentative visual plan and a derived future agenda.
- Paragraphs synthesize claims across studies instead of enumerating papers.
- Geography and scale operate as explanatory variables where warranted.
- The architecture score is at least 80/100, the status is `PASS`, and there are
  no hard blockers.
- The independent editor is recorded in `reporting/agent-manifest.csv`; otherwise
  release is blocked.
