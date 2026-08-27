# Workflow: Extraction, Appraisal, Geography and Traceable Synthesis

## Evidence extraction

Pilot the extraction form, then extract explicit abstract/full-text information.
Critical results, effect values and appraisal fields receive an independent second
check. Track report, study, site and outcome IDs; full-text evidence units require a
page/table/figure/section locator. Metadata-only records may inform screening or
bibliometrics but not findings/mechanisms.

Unknown fields are `null` or `not_reported`. Separate source fact, AI extraction
and inference. Necessary inference uses `inference=true` plus low/medium/high
confidence and may not be worded as an author conclusion.

Store main findings as typed claims with original statistic/effect/uncertainty,
units, comparison, context, geography/scale and exact locator. Track shared data,
samples and models.

## Critical appraisal and geographic audit

Read `references/critical-appraisal.md`. Apply design-matched domain judgments;
separate internal validity, external validity/directness and reporting quality.
Appraisal must change certainty and sensitivity analyses. The Geospatial Analyst
then compares evidence footprint with target inference, checking scale, boundaries,
spatial dependence, non-stationarity and underrepresented regions/environments.

## Iterative themes

Start with task-derived topics, code papers to one or more topics, merge overlapping
codes and freeze a final theme vocabulary. Do not impose a fixed geography theme
list before the evidence is seen.

## Synthesis

Build claim-ledger records containing:

```json
{"claim_id":"C001","claim_type":"association","claim":"...",
 "supporting_evidence_ids":[],"contradicting_evidence_ids":[],
 "independent_study_families":[],"conditions":[],"applicability":{},
 "certainty":"very_low|low|moderate|high","notes":""}
```

Choose meta-analysis, structured/SWiM, qualitative, realist or mixed synthesis by
the protocol decision tree. Analyze time, space, scale, data/method evolution,
consensus and disagreement. Diagnose disagreements through definition, data,
design, dependence, method, scale, period and geography before calling results
inconsistent. Test whether conclusions survive high-risk/dependent evidence.

Derive data, methodological, spatial, temporal, mechanism, scale, theoretical and
validation gaps from the included matrix. Do not concatenate future-work sections.

The claim ledger and argument map are the contracts between evidence and drafting.
