# E15 — Full Workflow Dry-run (mock provider)
Execute workflows/full-review-workflow.md stages against mock Scholar provider + fixture PDFs. Verify gate order: preflight -> search -> screen -> MissingFullTextGate fires on seeded pending item -> pause blocks draft stage.
Pass: state transitions exactly as specified; deliverables produced after resume.
