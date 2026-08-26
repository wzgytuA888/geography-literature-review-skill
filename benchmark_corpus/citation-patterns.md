# Citation Patterns — density, clustering, placement, seminal-recent balance

consolidated: 2026-08-26, N=60
Tiers: corpus-consensus >=30/60; common >=12/60; variant <12 multi-doc; outlier single-doc.

## Density profile (benchmark-stats.json, citations-per-block quartiles per doc)
- Corpus-wide: p25=2, median=3, p75=4 citations per block; per-doc medians span 1-20.
- Two extraction artifacts MUST NOT be read as style:
  (a) author-manuscript PDFs lose superscripts -> medians depressed to 0-1 (batch-1 caveat);
  (b) figure/table-caption blocks included in counts depress medians toward 0 (batch-3 caveat).
- Prose-level working profile after artifacts: evidential sentences carry ~2-8-reference clusters;
  conceptual sentences run 0-1. (batch-2 8/10 readable; batch-4 p75 up to 8; batch-6 p25/median/
  p75 = 0-2 | 2-5 | 5-8)

## Cluster behavior [corpus-consensus, all batches]
- Clusters (~2-6 refs, extremes to 8+) anchor empirical/trend claims.
- Single citations reserved for landmark papers, definitions, datasets, equations-at-first-use,
  policy documents.
- Polarisation is deliberate: zero-citation blocks are connective tissue (roadmaps, previews,
  definitions), never evidence claims. See paragraph-rhetoric.md.

## Placement [corpus-consensus]
- Sentence-final numbered superscript clusters dominate house style (batch-4 10/10; batch-5 10/10).
- Mid-sentence placement after named regions/datasets/methods for attribution precision.
- Narrative-author mentions in prose are rare and reserved for canon-defining works.
  (batch-4,batch-5; e.g. B045 canon-naming convention)

## Method/dataset citation discipline [common, ~20/60 pooled]
Methods, datasets, instruments cited at exact first mention with resolution, vintage, version, or
known limitation attached. (B001 equations,B006 methods-with-limits,B007 dataset biases,B010 metric
origins,B013,B017,B019,B020,B053 platforms,B058 networks/models,B052 dataset Box)
Method/definition citations concentrate in Boxes/Glossaries/methods sections rather than
scattering through analytic prose. (B033,B035,B036,B037,B038) [variant]

## Seminal-recent balance [corpus-consensus, index-wide]
- Recent-5y reference share: min 0.013, median 0.235, max 0.70 (benchmark-stats.json over N=60).
- Layering rule: dated foundational works anchor theory/definitions/history; recent work carries
  projections/attribution/fast-moving applied findings.
- Share rises with field speed and with publication year (batch-3 reported modest shares early
  corpus; batch-5/6 report 0.17-0.60 late corpus). Reconcile as a gradient, not a contradiction.
- Reference volume: median 165 entries/article (p25=77, p75=213); annotated subsets below sit
  inside this budget.

## Gap/agenda citation register [variant-to-common, ~10/60 documented]
Gap assertions and closing agenda items are deliberately uncited — an author-judgement register
distinct from the evidence register; prior partial reviews are cited only to prove the absence.
(B001,B007,B010,B021,B022,B024,B026,B051)

## Annotated reference apparatus [common, ~11+/60 documented]
Selected key references carry one-line significance notes stating what the work showed; some docs
add a terminal highlighted-references end-matter. (B010,B011,B014,B015,B018,B020,B021,B022,B023,
B029,B030; digest truncation makes this a lower bound)

## Standards as evidence objects [variant, 2-4/60]
Protocol/standards documents and assessment reports cited as primary evidence, by code.
(B012,B019,B022-B026 policy/plan integration pattern)

## Exclusion transparency [outlier]
Unusable estimates dropped from synthesis tables WITH the reason stated. (B010)
