# Paragraph Rhetoric — moves, topic sentences, mini-headings, zero-citation blocks, lengths

consolidated: 2026-08-26, N=60
Tiers: corpus-consensus >=30/60; common >=12/60; variant <12 multi-doc; outlier single-doc.
Length/density numbers come from benchmark-stats.json (block-level, corpus-wide).

## One-proposition-per-paragraph [corpus-consensus, ~55/60]
Paragraphs advance a proposition (a claim about how the system behaves), never narrate one paper.
Study-by-study chains are absent in every readable doc. (B001,B003,B005,B006,B007,B009,B010,
B011-B020 readable set,B021-B030,B031-B040 9/10 low ratio,B041-B050,B051-B060)

## Topic-sentence patterns [all observed; first two consensus-level]
- Proposition-led: finding or ranking stated first, support follows.
  (batch-wide; e.g. B021-B030 6/10 verified + batch-4/5/6 stats) [corpus-consensus]
- Named-object + behaviour assertion ("X. The X substantially ..."). (B021,B023,B024,B027,B029,B030) [common]
- Challenge/task statement openers for method-laden sections. (B047,B004) [variant]
- General-rule-then-named-exception contrast pattern. (B052,B056 and mirrored-pair docs B001) [common]
- Control-led physics openers (variable named with its control relation). (B058) [variant]

## Run-in bold mini-headings [common, ~15-25/60]
Bold run-in labels name one mechanism/variable/state and open a self-contained paragraph family
inside long sections; makes dense text skimmable without adding heading levels.
(B003,B010,B011,B016,B018,B020,B021,B023,B024,B026,B027,B029,B030)
Frequency varies by position in corpus (2/10 early batch vs 7/10 mid batch) — treat as optional
device, not house requirement.

## Typical move sequences (recurring templates)
1. claim -> citation cluster -> quantified exemplar -> regional contrast. (B001,B002,B005,B013,B041-B050 exemplar family) [consensus family]
2. event list -> impact tally -> pivot question. (B001 intro) [variant]
3. driver event -> geomorphic/physical consequence -> cited rates -> management relevance.
   (B023,B024,B026) [common]
4. expected-from-theory -> observed anomaly -> secondary-driver rescue. (B011,B014,B016) [variant]
5. competing-hypotheses list -> convergence clause retaining shared mechanism. (B023,B028,B029) [common]
6. physical law/definition -> observational support -> era trend -> residual uncertainty. (B058) [variant]

## Zero-citation structural blocks [corpus-consensus]
- Corpus zero-citation block share: min 0.10, median 0.263, max 0.71 per doc (benchmark-stats.json).
- These blocks are systematically connective tissue — roadmap sentences, section previews,
  definitions, figure walk-throughs, author-view statements — never evidential claims.
  (batch-6 10/10 via index stats; consistent with B032,B035,B037,B040 26-44% shares)

## Length profile (benchmark-stats.json, block medians per doc)
- p25=501 chars, median=623, p75=683; per-doc medians span 427-4350 (upper tail reflects merged-
  block extraction artifacts, not style).
- Working band for a single-proposition paragraph: ~450-850 chars; longer paragraphs demand
  explicit topic sentences or they collapse. (B047 card risk note, p75>1100 case)
- Per-doc examples inside the band: B001 q25=449/median=679/p75=976; B023 404/465/648;
  B047 490/714/1150; B058 451/565/778.

## Imitation risks recorded by miners
- Parallel templates turn mechanical when sibling paragraphs lack distinct mechanisms. (B046,B022,B028 risk notes)
- Long concept paragraphs need run-in labels or strong topic sentences. (B047 risk note)
