# Workflow: Outline

Input: evidence matrix + argument map + synthesis notes + mode.
Process: Outline Agent (agents/runtime/outline-agent.md) builds
`writing/outline.md` with per-section purpose / propositions / evidence clusters /
rhetorical moves / planned figures.

Validation before drafting:
1. Every argument-map proposition has exactly one home section.
2. Every section cites ≥1 evidence cluster (no hollow headers).
3. Architecture logic recorded (thematic/mechanistic/scale/regional/mixed) with
   reason; archetype prior consulted from `benchmark_corpus/archetypes/`.
4. Gap/agenda sections reference validated gap candidates only.
5. User-visible checkpoint: outline saved + state.json updated; drafting may start
   automatically for narrative/conceptual modes, or after explicit user go-ahead
   when mode = systematic/scoping (protocol visibility matters there).
