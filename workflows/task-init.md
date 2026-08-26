# Workflow: Task Init (v2 runtime)

1. Create `runs/<YYYYMMDD>-<slug>/` with search, evidence, writing, citation,
   figures and evaluation folders.
2. Interpret the user's topic into research object, outcome, region and bounded
   candidate terms. Preserve the verbatim input.
3. Record review mode, research question, year/language/journal/author/DOI filters,
   maximum papers, inclusion/exclusion criteria and requested deliverables.
4. Run `scripts/literature_review_pipeline.py preflight`. Continue when at least
   one primary API is ready. Record unavailable providers as degraded capability;
   do not replace them with a Google Scholar scraper.
5. Route the review mode using `references/review-methods.md` and write the
   resulting scope and rationale to state.json.

Checkpoint before any search quota is spent.
