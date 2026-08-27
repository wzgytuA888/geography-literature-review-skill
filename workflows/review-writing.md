# Workflow: Evidence-grounded Review Writing

Preconditions: protocol/search/screening/extraction/appraisal/geographic/synthesis
gates passed; claim ledger and outline frozen for the draft round.

## Drafting loop (Writing Agent)
Per section: load ONLY that section's approved claim/evidence cluster + relevant
method files → draft with placeholder citations (`<CITE claim_id=… >`) → self-check
paragraph moves against `benchmark_corpus/paragraph-rhetoric.md` priors → append
to `writing/draft.md`.

Section order strategy: hardest-synthesis sections first (they expose evidence
gaps while fixing them is cheap), Introduction last (it must promise only what the
review actually delivers).

## Content freeze
When draft covers outline: freeze text; citation resolution begins (citation-agent).
Post-freeze edits go through Revision Agent only, keeping placeholders/claims
consistent and re-running validator afterwards.

## Style enforcement during drafting
- enumeration ceiling (≤2 consecutive study-by-study sentences);
- conditional-conclusion pattern for conflicts after diagnosis ladder;
- geography rules fired only with logged triggers;
- no benchmark phrasing (spot-check via overlap checker at revision).
- claim wording must match type/certainty/applicability in the ledger;
- “global”, causal, mechanism and gap statements require their dedicated gates;
- report automation truthfully and never call independent AI passes human review.
