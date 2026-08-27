# Workflow Overview v3

1. `review_scaffold.py init` creates the run and disclosure manifest.
2. Protocol Architect and Domain Theorist frame and freeze the question/scope.
3. Search Strategist drafts the source plan; Search Peer Reviewer validates it.
4. Scouts search/import complementary sources and test sentinel recall.
5. Librarian links reports to studies/sites and preserves uncertain duplicates.
6. Independent screeners and an adjudicator produce final eligibility decisions.
7. Full-text Verifier applies importance tiers and the legal-access gate.
8. Extractors, Appraisal Specialist and Geospatial Analyst construct the evidence
   base, dependency map and external-validity audit.
9. Synthesis Methodologist and Certainty Agent create the claim ledger; Red Team
   tests contradictions, causal claims, transfer and gaps.
10. Outline/Lead Writing/Citation/Figure agents create a unified manuscript.
11. Scientific Reviewer, Journal Editor and Reproducibility Auditor report defects;
    Revision Agent closes them.
12. `review_quality_gate.py` issues the readiness verdict and final package status.

The open-discovery CLI implements `preflight`, `search`, `sentinel-check`, `screen`
and `snowball`.
Other named stages are orchestrated by the skill using their artifact contracts.
