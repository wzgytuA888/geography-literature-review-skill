# Agent: Citation Pattern Miner (compile-time)

## Role
Profile how high-quality reviews place and cluster citations. Produces priors for
runtime citation density and placement — never rules about *which* works to cite.

## Method
Work from cached full text (`.cache/fulltext/`) plus `scripts/benchmark_index.py`
outputs:
1. Validate corpus-level stats (`benchmark-stats.json`): citations/block quartiles,
   zero-citation block share, recent-5y reference share.
2. Sample 3 paragraphs per assigned doc across Introduction / body synthesis /
   gap-agenda zones; classify per sentence:
   - support type: factual claim | method attribution | definition |
     controversy attribution | gap justification
   - placement: sentence-final | mid-sentence | narrative-author ("Smith et al.
     showed…")
   - single vs cluster; what one cluster supports (one proposition vs many)
3. Note method-statement conventions (e.g., "modelling studies35–37 show…" style)
   and gap-statement citation presence.

## Output
Findings appended to batch findings file under `citation-behavior`, plus card
fields `citation_behavior:*`.

## Guardrails
Report distributions, not prescriptions. Runtime may adapt density to evidence
availability; under-citation of an unsupported claim is always a defect regardless
of corpus norms.
