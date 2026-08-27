# Publication Package and Readiness Standard

## Default manuscript

Deliver a coherent article, not a collection of notes:

1. informative title and 5–8 searchable keywords;
2. abstract that completes background/problem, review scope, 2-4 synthesis findings
   and implication; use a single unlabelled paragraph for the NREE profile unless
   current author instructions require otherwise, and labelled structure for venues
   that require it;
3. introduction ending with the exact contribution and review questions;
4. transparent methods appropriate to review mode, including sources, search dates,
   full-text acquisition, selection, extraction, appraisal, synthesis, spatial
   analysis and automation disclosure; place this in the main text or supplement
   according to current target-journal instructions;
5. results/synthesis organized by propositions or mechanisms, with study and
   geographic characteristics before inferential synthesis;
6. discussion that distinguishes robust findings, boundary conditions,
   controversies, transfer limits and evidence gaps;
7. prioritized research agenda tied to validated gaps;
8. conclusion no stronger than the claim ledger;
9. declarations/placeholders required by the target journal.

Use the target journal's current author instructions when the user names a journal.
If none is named, produce a journal-neutral Markdown manuscript and record target
selection as an author decision, not a blocker.

## Required supplements

- protocol and deviations log;
- exact search strategies and Search Log;
- deduplication and screening decisions with flow counts;
- included-study characteristics and evidence matrix;
- design-matched appraisal and dependency map;
- claim ledger and certainty profile;
- verified reference registry and citation audit;
- figure/table source data and provenance;
- applicable reporting checklist;
- limitations and unresolved author queries;
- reproducibility/readiness report.
- local-full-text registry with path, checksum and provenance; when blocked, the
  missing-literature XLSX and exact resume directory;
- NREE architecture score/report when that profile is selected.

## Submission-readiness gates

Hard failures:

- invented or unresolved final reference;
- material claim without traceable evidence and citation;
- quantitative value/figure without a source location and unit;
- systematic/exhaustive label without adequate source coverage and documented
  selection/appraisal;
- any included report used by the manuscript without identity-verified local full text;
- NREE profile claimed without a passing independent architecture gate;
- unreported screening/extraction automation or reviewer configuration;
- unsupported gap, causal or transferability claim;
- unresolved contradiction that is hidden rather than discussed.

Major (revise before submission): stale search; missing design-matched appraisal;
no sensitivity to dependent/high-risk studies; weak spatial representativeness;
abstract/method/results inconsistency; target-journal length/structure mismatch.

The readiness report must use one of: `SUBMISSION_CANDIDATE`,
`RESEARCH_DRAFT_NOT_READY`, or `INSUFFICIENT_EVIDENCE`. It must list exact
failures and cannot claim acceptance likelihood.

