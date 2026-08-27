# Workflow: Task Init (v4 runtime)

1. Run `scripts/review_scaffold.py init` to create the full protocol-to-publication
   artifact tree and `state.json`.
2. Preserve the verbatim input, start `workflows/scope-convergence.md`, and run the
   bounded provider preflight (`--timeout-seconds 8 --max-retries 0`). It always
   writes `preflight.json` and exits; never leave initialization hanging.
3. If the
   direction is broad, do orientation discovery, present 3-5 direction cards and
   pause for the user's selection.
4. For the selected/sufficiently specific direction, interpret the topic into
   research object, outcome, region and bounded candidate terms.
5. Protocol Architect records the review mode, questions, scope, contribution
   test, eligibility, source plan, appraisal/synthesis plan, target inference
   geography and requested deliverables. Default to deep critical narrative when
   only a topic is supplied.
6. Continue when at least one primary API is ready. During orientation only, if
   both primary providers fail, use the logged bounded Crossref bibliographic
   fallback; do not represent it as exhaustive and do not scrape Google Scholar.
7. Route the review mode using `references/review-methods.md`, create the automation
   disclosure manifest, and write the resulting scope/rationale to state.json.

Freeze the protocol only after scope selection. Pilot/orientation searches may precede the freeze but
must be labeled and logged. Checkpoint before significant query quota is spent.
