# Figure Design Rules

## When a figure exists
A figure earns its place when prose complexity collapses into structure:
multi-concept frameworks, taxonomies, mechanisms, timelines, distributions,
evidence matrices, controversy maps, agendas. Typical top reviews carry ~4–7
numbered figures; padding to look visual is an anti-pattern.

## Role → tool mapping
| Role | Tool first choice |
| --- | --- |
| conceptual framework | Mermaid flowchart / Graphviz |
| literature taxonomy | Mermaid graph |
| research evolution timeline | Mermaid timeline / Python |
| mechanism schematic | Graphviz clusters / SVG-by-script |
| geographic distribution | GeoPandas (real geometries+data only) |
| evidence summary matrix | Table (markdown/docx) or heatmap via matplotlib |
| workflow / PRISMA-style flow | Mermaid |
| future agenda map | Mermaid mindmap/graph |

## Grounding law
Conceptual diagrams: nodes/edges trace to argument-map concepts (cite
propositions). Quantitative/map/statistical figures: numbers come from
`figures/data/*.csv` WITH provenance columns (paper_id, doi, page). Forbidden:
invented values, weights, trends, network edges, significance markers, guessed
geographies.

## Lifecycle
plan (`figures/figure-plan.md`) → source (.mmd/.py) → render (.svg/.png) →
watermark "DRAFT SCIENTIFIC FIGURE" → Reviewer+Auditor validation → watermark
removed → text-integration check (referenced paragraphs exist and agree).

## Rendering reality (2026-08 baseline)
mmdc v11.x needs your own Puppeteer/Chrome; Kroki (kroki.io) renders server-side.
If neither available: ship .mmd sources + note; .mmd remains authoritative.

## Caption discipline
Caption states the takeaway + reading guide + provenance ("synthesis of refs …"
or "data from files/..."), matching benchmark norms of epistemic encoding
(dashed=uncertain, shading=ranges) where applicable.
