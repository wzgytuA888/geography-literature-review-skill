# Publication-readiness Quality Control

Run independent gates after content freeze and again after revision.

## Gate 1 — Scientific and contradiction review

Test scope, construct definitions, causal logic, missing/disconfirming evidence,
dependence, appraisal use, geographic transfer and conclusion strength. Reviewer
findings include location, severity, evidence and required action; reviewers do not
rewrite the draft.

## Gate 2 — Lineage and citation integrity

Verify every material sentence:
`claim → evidence unit → report/study/site → source locator → appraisal → verified
metadata/citation → final wording`. Numbers, units, directions and figure/table
values must match. Empty citation manifests cannot pass.

## Gate 3 — Method/reporting reproducibility

Reconstruct source plan, exact queries, counts, deduplication, screening and
adjudication, local full-text paths/checksums/provenance, extraction verification, appraisal, dependence,
synthesis, certainty, amendments and automation disclosure. Compute flow counts
from tables. Check the current applicable PRISMA/PRISMA-S/ROSES/SWiM/CERQual
version and record access date rather than assuming a frozen standard.

## Gate 4 — Journal and manuscript coherence

Check contribution, title/abstract/full-text agreement, section jobs, synthesis
over enumeration, target-journal fit, figure/table integration, limitations,
declarations and author queries. Benchmark patterns are optional style priors,
never factual or universal structure requirements.

For the NREE profile, add an independent Architecture Editor pass using
`references/nree-review-writing.md` and the YAML scorecard. Score >=80 is necessary
but not sufficient; any roadmap, full-text, proposition-synthesis, visual-argument,
gap-derivation or phrase-overlap hard blocker fails the profile.

## Hard red lines

hallucinated/unresolved final references >0 · unsupported material claims >0 ·
benchmark leakage >0 · unsupported quantitative figures >0 · unsupported gap,
causal or global-transfer statements >0 · included manuscript evidence without
verified local full text >0 · false systematic/exhaustive label >0 · automation presented as human
review >0 · unresolved protocol deviation affecting the primary conclusion >0.

Verdict: `SUBMISSION_CANDIDATE`, `RESEARCH_DRAFT_NOT_READY`, or
`INSUFFICIENT_EVIDENCE`. A submission candidate still requires author/domain
responsibility; the gate does not predict journal acceptance.

