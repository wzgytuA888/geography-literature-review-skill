# Workflow: Evidence Matrix, Themes and Traceable Synthesis

## Evidence extraction

For each included paper, extract only explicit abstract/full-text information into
`templates/task-literature-card.yaml`. Full-text evidence units require a page or
section location. Metadata-only records may inform screening or bibliometrics but
not findings/mechanisms.

Unknown fields are `null` or `not_reported`. Separate source fact, AI extraction
and inference. Necessary inference uses `inference=true` plus low/medium/high
confidence and may not be worded as an author conclusion.

Store main findings as arrays of finding/direction/variable/confidence objects.

## Iterative themes

Start with task-derived topics, code papers to one or more topics, merge overlapping
codes and freeze a final theme vocabulary. Do not impose a fixed geography theme
list before the evidence is seen.

## Synthesis

Build claim records containing:

```json
{"claim":"...","supporting_papers":[],"contradicting_papers":[],
 "conditions":[],"confidence":"low|medium|high","notes":""}
```

Analyze temporal development, spatial coverage, data/method evolution, scales,
consensus and disagreement. Diagnose disagreements through definition, data,
method, scale, period and geography before calling results inconsistent.

Derive data, methodological, spatial, temporal, mechanism, scale, theoretical and
validation gaps from the included matrix. Do not concatenate future-work sections.

The argument map remains the contract between evidence and drafting.
