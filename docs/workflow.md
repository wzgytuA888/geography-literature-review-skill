# Workflow Overview v4

1. `review_scaffold.py init` creates the run and disclosure manifest.
2. The specificity gate performs orientation discovery. Broad directions produce
   3-5 cards and pause for user scope selection.
3. Protocol Architect and Domain Theorist frame and freeze the chosen question/scope.
4. Search Strategist drafts the source plan; Search Peer Reviewer validates it.
5. Scouts search/import complementary sources and test sentinel recall.
6. Librarian links reports to studies/sites and preserves uncertain duplicates.
7. Independent screeners and an adjudicator produce final eligibility decisions.
8. Legal Full-text Acquisition and Verification store every included report locally;
   unresolved items generate an XLSX and pause.
9. Extractors, Appraisal Specialist and Geospatial Analyst construct the evidence
   base, dependency map and external-validity audit.
10. Synthesis Methodologist and Certainty Agent create the claim ledger; Red Team
   tests contradictions, causal claims, transfer and gaps.
11. Outline/Lead Writing/Citation/Figure agents create an NREE-shaped manuscript.
12. NREE Architecture Editor, Scientific Reviewer, Journal Editor and Reproducibility Auditor report defects;
    Revision Agent closes them.
13. `review_quality_gate.py` issues the readiness verdict and final package status.

The deterministic CLI implements bounded `preflight`, atomic scope
`start/checkpoint/select`, `search`, `sentinel-check`, `screen`, `snowball`, legal
full-text acquisition, pause/resume and final integrity gates.
Other named stages are orchestrated by the skill using their artifact contracts.
