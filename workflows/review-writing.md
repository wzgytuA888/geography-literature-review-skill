# Workflow: Evidence-grounded Review Writing

Preconditions: scope selected; protocol/search/screening gates passed; every report in
the manuscript evidence set has verified local full text; extraction/appraisal/
geographic/synthesis gates passed; claim ledger, visual argument and outline frozen.

## Drafting loop (Writing Agent)
Per section: load ONLY that section's approved claim/evidence cluster, local full-text
locations and relevant method files → draft with placeholder citations
(`<CITE claim_id=… >`) → self-check against `references/nree-review-writing.md` and
`benchmark_corpus/paragraph-rhetoric.md` → append to `writing/draft.md`.

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
- one governing proposition per evidential paragraph; proposition first, then clustered
  multi-source evidence, diagnosis, boundary and transition;
- “global”, causal, mechanism and gap statements require their dedicated gates;
- report automation truthfully and never call independent AI passes human review.
- no manuscript sentence may cite an abstract-only or remotely inspected source.
