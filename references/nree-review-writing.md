# NREE-derived review architecture and writing contract

Derived from a local corpus of 60 *Nature Reviews Earth & Environment* review PDFs
(2020-2026). The corpus teaches form only. Never use benchmark scientific facts or copy
its prose. Verify current NREE author instructions at runtime because journal requirements
can change.

## Corpus profile

- Dominant skeleton: Abstract -> Introduction -> 3-6 content-named body sections ->
  Summary and future perspectives.
- Median article: about 6 numbered figures and 165 references; these are descriptive
  priors, not quotas.
- Typical single-proposition paragraph: roughly 450-850 extracted characters with a
  median of about three citations; extraction artefacts make exact word limits unreliable.
- Boxes isolate definitions, methods, taxonomies or regional cases so the main argument
  remains progressive.

## Architecture gate

Before drafting, choose one explicit progression supported by the evidence:

1. mechanism/causal funnel: framing -> processes/drivers -> observations/evidence ->
   consequences/projections -> responses;
2. temporal ladder: baseline/past -> observed transition -> future states;
3. spatial or scale ladder: site/process -> landscape/region -> global coupling;
4. framework mirror: sections map one-to-one to a new conceptual framework;
5. parallel classes: the same analytical template is repeated across comparable classes,
   followed by a cross-class synthesis.

Do not use a generic textbook catalogue. Headings state scientific content, not “Literature
review”, “Discussion” or “Theme 1”. Keep the hierarchy shallow. Every major section must own
a distinct proposition cluster and hand the argument to the next section.

## Introduction contract

Use five moves in order:

1. establish Earth/environment system stakes;
2. anchor the stakes with at least one situated and verified quantity;
3. diagnose a synthesis problem (fragmentation, contested mechanism, scale mismatch,
   outdated synthesis or decision failure), not the empty phrase “few studies exist”;
4. state exactly what this Review contributes;
5. give a roadmap whose verbs and order match the delivered headings one-to-one.

Include operational scope and justified exclusions early. Write the Introduction after the
body so it promises only what the full-text synthesis delivers.

## Paragraph contract

Each evidential paragraph advances one proposition:

`proposition -> multi-source evidence -> comparison/contrast -> diagnosis -> boundary or
uncertainty -> implication/transition`.

Open with the synthesis claim, not an author name. Avoid three consecutive study-by-study
sentences. General claims normally require multiple independent study families; a single
source is acceptable only when explicitly unique (official statistic, defining dataset or
seminal proposition). Diagnose disagreement in the same paragraph using metric, design,
resolution, region, period, missing process or dependency. Situate every number by unit,
denominator, period, geography and source. Place hedges at the exact thin-evidence clause.

## Figures, tables and Boxes

Plan the visual argument before prose:

- Fig. 1: conceptual orientation/framework, with entities, processes and feedbacks;
- evidence figures: spatial/temporal patterns or mechanism tests, not decorative icons;
- synthesis figure: reconciles evidence into a framework, typology or decision space;
- table: construct/method/evidence/condition comparison with provenance and uncertainty;
- Box: terminology, method primer, contested calculation or bounded regional case.

Every visual has a question, evidence lineage and a body paragraph that interprets specific
panels. Captions are self-contained and identify sources, thresholds, periods and uncertainty.

## Closing contract

“Summary and future perspectives” must answer the Introduction promise point-for-point,
separate robust conclusions from conditional propositions, and derive priorities from mapped
limitations. Each agenda item names a tractable question, data/method/instrument, responsible
research community or decision actor, relevant scale and expected discriminating observation.
Never end with a generic call for more research or a policy prescription stronger than the
evidence certainty.

## NREE profile release gate

Before prose, freeze five artifacts: one-sentence question/contribution contract;
argument map; section blueprint with one progression ladder; `figure-blueprint.md`
(Fig. 1 orientation, intermediate evidence figures, final synthesis figure); and
paragraph plans linking propositions to local full-text evidence clusters.

A manuscript cannot claim the NREE profile unless all are true:

- roadmap and delivered section order match;
- body follows one declared progression rather than a topic list;
- every body paragraph is traceable to locally stored full text;
- no abstract-only record supports a manuscript claim;
- no study-by-study chain of three or more sentences;
- disagreements, scales and geographic contrasts are diagnosed, not merely mentioned;
- gaps are derived from the evidence map;
- at least one framework/synthesis figure and two evidence-bearing tables/figures are planned
  and provenance-complete (unless the target article type explicitly differs);
- an independent NREE Architecture Editor and Journal Editor both pass the frozen draft;
- phrase-overlap testing confirms the benchmark corpus influenced form, not wording.

The Architecture Editor records the decision in
`evaluation/nree-architecture-gate.yaml`. Score title/abstract/introduction (20),
central progression and section coherence (25), paragraph synthesis (15), evidence/
uncertainty/geographic calibration (15), visual argument (15), and summary/future
agenda (10). A score below 80/100 or any hard blocker is FAIL; the score calibrates
revision and never overrides scientific/citation/full-text gates.
