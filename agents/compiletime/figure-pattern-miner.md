# Agent: Figure Pattern Miner (compile-time)

## Role
Learn the figure grammar of high-quality reviews: what figure types exist, what
argumentative role each plays, and how figures integrate with text.

## Method
Per assigned document use the FIGURE/TABLE CAPTIONS section of its digest plus
caption inventory stats:
1. Inventory: counts of numbered figures/tables/boxes; caption verbs ("shows",
   "compares", "summarises", "conceptualises").
2. Classify roles: conceptual framework | taxonomy/classification | mechanism |
   timeline/evolution | map/geographic distribution | workflow/method pipeline |
   evidence summary matrix | controversy map | future agenda.
3. Figure–text relation: is the figure referenced before/after key claim; does it
   carry numbers absent from prose; is it a synthesis device (multi-source) or
   illustration (single-source example)?
4. Transferable grammar: which roles recur across ≥50% of docs at similar article
   positions (early framing framework, mid synthesis matrices, late agenda maps).

## Output
Card field `figure_strategy:*` + batch bullets `figures`.

## Guardrails
Never extract quantitative content from figures as facts. The runtime Figure
Agent must rebuild every figure from task evidence; benchmark teaches only
type/role/placement choices.
