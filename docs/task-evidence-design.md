# Task Evidence Design

## Principle
Evidence-first writing. Nothing enters the manuscript that did not pass:

```
Semantic Scholar/OpenAlex discovery → normalization → deduplication → screening
→ citation snowballing → legal fulltext (gate!)
→ Evidence Literature Card → evidence units (with source_page)
→ Evidence Matrix → Synthesis notes → Argument Map → Outline → Draft
```

## Task Literature Card (`templates/task-literature-card.yaml`)
Per included paper: bibliographic identity (+zotero_key/citation_key), scope
(geography/scale/time), concepts/framework, data/methods/spatial methods,
claims/findings, author-stated limitations, atomic **evidence_units**
(claim/result/context/method/geography/scale/source_page/confidence),
relationship to topic, supporting/contradicting themes, acquisition provenance.

Physically separate from benchmark pattern cards — different directories,
different schemas, different lifecycles.

## Evidence Matrix (`evidence/evidence-matrix.csv`)
Row = claim×paper×conditions with theme, support_or_contradict, confidence,
source_location, doi/zotero_key. Integrity rules enforced before synthesis:
unique evidence_ids · paper_ids ∈ registry · source_location non-empty ·
confidence ∈ {high,medium,low}.

## Argument Map (`evidence/argument-map.md`)
Proposition table: statement | supporting ids | contradicting ids | conditions |
evidence strength | unresolved uncertainty. This is the contract between
synthesis and drafting — writers may not invent propositions absent from it.

## Caching & reuse
Validated task corpora may be stored under `task_corpora/<topic>/` for later
updates of the SAME topic. They remain task artifacts: never merged into
`benchmark_corpus/`, never consulted as evidence for other topics.

## Gap derivation chain (hard rule)
documented limitation → repeated blind spot → unresolved contradiction → missing
geography/scale/period → method/data weakness → underexplored mechanism → gap
candidate → evidence validation → gap statement. Any link missing ⇒
INSUFFICIENT EVIDENCE FOR GAP CLAIM.
