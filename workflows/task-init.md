# Workflow: Task Init (v3 runtime)

1. Run `scripts/review_scaffold.py init` to create the full protocol-to-publication
   artifact tree and `state.json`.
2. Interpret the user's topic into research object, outcome, region and bounded
   candidate terms. Preserve the verbatim input.
3. Protocol Architect records the review mode, questions, scope, contribution
   test, eligibility, source plan, appraisal/synthesis plan, target inference
   geography and requested deliverables. Default to deep critical narrative when
   only a topic is supplied.
4. Run `scripts/literature_review_pipeline.py preflight`. Continue when at least
   one primary API is ready. Record unavailable providers as degraded capability;
   do not replace them with a Google Scholar scraper.
5. Route the review mode using `references/review-methods.md`, create the automation
   disclosure manifest, and write the resulting scope/rationale to state.json.

Freeze the protocol before final search. Pilot searches may precede the freeze but
must be labeled and logged. Checkpoint before significant query quota is spent.
