# Quality Rubric — runtime-checkable criteria derived from benchmark quality signals

consolidated: 2026-08-26, N=60
Each criterion: WHAT to check, PASS test (measurable), evidence that benchmarks exhibit it.
Apply at review-draft time; a draft passing <12 of 16 items needs revision before release.

## Q1. Roadmap fidelity
Check: extract itinerary sentences from Introduction; compare with delivered heading order.
PASS: announced sequence == delivered sequence, 1:1 verb-to-section mapping.
Evidence: verifiable in B031-B037,B041,B042,B044-B048,B050,B051,B054,B056,B058-B060 (~20/60 verified;
testable in nearly all). [corpus-consensus principle]

## Q2. Quantified stakes opening
Check: first two Introduction paragraphs.
PASS: >=1 number with units tied to stakes/impacts present; abstract also carries >=1 concrete
finding or number (no scope-only abstract).
Evidence: batch-4/5 10/10 first-paragraph rule; batch-6 10/10 abstract rule. [consensus]

## Q3. Key-points checkability (if box present)
Check: each bullet standalone.
PASS: each bullet is a defensible claim; majority quantified or directional; bullets mirror body
findings.
Evidence: B021-B030 quantified-bullet form 7/10+; B011-B018,B020; B031,B034-B037; B041,B054,B057,
B059,B060. [common]

## Q4. Proposition density / no enumeration
Check: sample 10 consecutive body paragraphs.
PASS: >=8 advance exactly one proposition with clustered support; ZERO chains of >=3 consecutive
single-study narrations.
Evidence: study-by-study ratio low in ~55/60. [corpus-consensus]

## Q5. Citation cluster calibration
Check: evidential vs conceptual sentences.
PASS: empirical/trend claims carry >=2 refs OR an explicit single-source justification; zero-
citation text confined to roadmaps/previews/definitions/figure walk-throughs/author views.
Evidence: cluster/singles house style all batches; zero-cite share median 0.263 structural.
[corpus-consensus]

## Q6. Interval reporting
Check: every synthesized/recomputed quantity.
PASS: range, mean±SD with n, bounds, or explicit order-of-magnitude declaration present; point
estimates without provenance fail.
Evidence: B023,B025,B029,B030,B052,B053,B058 + number-provenance convention B045-B049. [common]

## Q7. Discrepancy diagnosis
Check: every reported disagreement between studies/datasets/models.
PASS: named cause within same paragraph (metric, method, resolution, missing process); bare
"results disagree" fails.
Evidence: ladder step 1 documented in ~25/60. [corpus-consensus]

## Q8. Regional differentiation contract
Check: each named-region contrast.
PASS: mechanism/evidence condition for the difference appears in the same paragraph (R1 rule);
region names never organize sections unless the review is a single-place deep synthesis.
Evidence: R1 in ~38/60. [corpus-consensus]

## Q9. Gap derivation
Check: each declared gap.
PASS: preceded by demonstrated deficit inside the body (mapped coverage, quantified share,
divergent estimates, audited inventory) — not asserted from topic absence.
Evidence: derived-gap pattern ~38/60. [corpus-consensus]

## Q10. Agenda specificity
Check: each closing agenda item.
PASS: names instrument/platform/network/model/action AND agent; zero bare "more research needed"
items.
Evidence: imperative+instrument style ~35/60; vague closings absent in captured set. [consensus]

## Q11. Term discipline
Check: key constructs across sections.
PASS: operational definition at first use; no silent synonym drift; borrowed consensus definitions
get author-operationalized restatement when needed.
Evidence: B003,B005,B007,B010,B011,B017,B020,B043,B046,B047,B052,B055,B057. [common]

## Q12. Uncertainty language calibration
Check: confidence qualifiers vs scope of evidence.
PASS: qualifier strength tracks evidence scope ("unequivocal" only where multi-source convergence;
"inconclusive" where regional records thin); hedges located AT thin-evidence claims.
Evidence: B001,B005,B006,B010,B012,B015,B016,B020,B024,B025,B028,B030. [common]

## Q13. Negative/non-significant results displayed
Check: mixed or null findings.
PASS: retained as explicit category (legend entries, significance masks, power caveats), not
dropped.
Evidence: B027,B029,B031,B032,B037,B038. [variant-to-common]

## Q14. Dataset audit
Check: compared datasets/products.
PASS: version/vintage/known-limitation noted at first mention; audit section or run-in exists when
comparison is central; supplementary pointers given for extended methods.
Evidence: B006,B007,B010,B013,B017,B019,B020,B022,B024,B027,B028,B053,B058. [common]

## Q15. Scope honesty
Check: Introduction scope statements.
PASS: inclusion list + at least one justified exclusion with reason stated early; numeric criteria
where applicable.
Evidence: B002,B009,B011,B012,B022,B024,B025,B028,B041,B044,B048,B049,B054,B055,B059. [common]

## Q16. Figure-text integration and caption craft
Check: figure-supported claims and captions.
PASS: major claims cite specific panels "(Fig. Xa)"; captions self-contained (sources/thresholds/
panel logic); takeaway sentence ends caption; epistemic encoding declared when used.
Evidence: B021-B030 10/10 self-contained; panel-inline citation >=7/10 batch-6. [consensus/common]

## Scoring guidance
- Consensus-tier failures (Q1,Q2,Q4,Q5,Q7,Q8,Q9): any failure blocks release without revision note.
- Common-tier failures: >=2 failures trigger revision.
- Record per-item pass/fail in the run's quality log for benchmark matching.
