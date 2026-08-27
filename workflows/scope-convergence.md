# Workflow: Evidence-informed scope convergence

Use this workflow when the user's direction names a broad phenomenon but does not
identify a reviewable relationship, mechanism, population/system, scale or intended
contribution. The purpose is to let the literature inform the choice without letting
the agent silently choose the user's scientific question.

## Specificity gate

Initialize or resume this stage with
`python scripts/scope_convergence.py start --run-dir <run>`. The scaffold begins in
`ORIENTATION_PENDING`, never in protocol drafting.

Score five anchors as present/absent: phenomenon; focal relationship or mechanism;
geography/population/system; time or change window; intended contribution or decision.
Treat the topic as broad when fewer than two anchors are present, when an orientation
search yields three or more weakly connected research fronts, or when plausible scopes
would lead to different inclusion criteria and conclusions.

## Orientation search

1. Preserve the verbatim topic and translate it into broad concept blocks.
2. Search at least two discovery sources plus recent review articles; use metadata and
   abstracts only for clustering, not for manuscript claims.
   Use `literature_review_pipeline.py search --orientation-mode` so simultaneous
   OpenAlex/Semantic Scholar errors trigger the bounded Crossref orientation fallback;
   record the degraded coverage rather than treating errors as zero results.
3. Record queries, dates, counts and access errors in the normal search log.
4. Cluster the field by research question, not keyword frequency. Candidate directions
   must differ in mechanism, outcome, scale or intervention—not merely wording.
5. Test each direction against evidence density, recency, geographic coverage, likely
   full-text availability, existing-review saturation and a plausible original synthesis.

## Direction cards and pause

Write `protocol/direction-options.md` using the template. Offer 3-5 options. Each card
contains: precise primary question; contribution; inclusion boundary; expected NREE
architecture; evidence base and access feasibility; main risk; representative verified
papers. Do not recommend a direction solely because it has more papers.

Ask one concise user question requesting a choice or modification. Set:

```json
{"status":"PAUSED_WAITING_FOR_SCOPE_SELECTION","current_stage":"scope_selection"}
```

Do not start the final search, mass full-text acquisition, protocol freeze, extraction,
synthesis, outline or manuscript until the user chooses. On resume, preserve rejected
directions in the audit trail and freeze the selected scope. Use the atomic checkpoint:

```text
python scripts/scope_convergence.py checkpoint --run-dir <run> --specificity broad --anchor phenomenon
python scripts/scope_convergence.py select --run-dir <run> --option <1-5> --primary-question "<question>"
```

The checkpoint validates 3–5 complete cards and refuses to pause if manuscript,
full-text or evidence artifacts were produced prematurely.
