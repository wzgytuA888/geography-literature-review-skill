# Architecture v4

Version 4 retains the benchmark/task corpus firewall and adds evidence-informed
scope convergence, verified local full text and an NREE-profile release gate to
the protocol-to-publication artifact graph.

## Layers

1. **Method priors** — benchmark corpus teaches review architecture and rhetoric,
   never topic facts.
2. **Deterministic runtime** — scaffold, API clients, cache/retry, normalization,
   report deduplication, screening imports, exports, full-text/citation/readiness
   gates.
3. **Specialist agents** — protocol, search review, selection, extraction,
   appraisal, spatial analysis, synthesis, certainty, writing and auditing.
4. **Canonical run artifacts** — protocol, registries, evidence units, appraisal,
   dependency map, claim ledger, manuscript and publication supplements.

## Control flow

```text
topic → specificity/orientation gate → user scope choice when broad
→ protocol/source plan → independent query review → discovery/imports
→ report/study/site linkage → independent screen/adjudication
→ verified legal local full text for every included report (XLSX pause if missing)
→ verified extraction → appraisal/dependency/spatial audit → synthesis/certainty
→ red team → claim ledger/NREE outline/draft → citations/figures → independent audits
→ revision → deterministic readiness verdict
```

The Orchestrator owns state and merges canonical files. Parallel workers write
staging artifacts. Reviewers never directly edit the draft. Provider success does
not determine the review label; protocol coverage and method gates do.

## Failure behavior

Any included missing or identity-unverified local text, invalid coverage for the chosen label and hard
lineage/citation failures stop or downgrade the run. Other provider/access gaps are
logged and reflected in certainty. The system prefers a qualified research draft
over a fluent but unsupported submission claim.

