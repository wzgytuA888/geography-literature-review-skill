# Review Methods & Mode Router

## Available modes and what changes between them

| Mode | Search completeness | Screening rigor | Methods section | Reporting | Synthesis style |
| --- | --- | --- | --- | --- | --- |
| Narrative | targeted, saturation-based | light (documented) | brief | prose-led | argumentative |
| Conceptual | concept-driven lanes | light-medium | brief | framework-centric | theory-building |
| Systematic | exhaustive per protocol | strict PRISMA-like flow + counts | full protocol | flow diagram + tables | structured |
| Scoping | broad, bounded | medium; counts kept | full | range-mapping tables | descriptive-analytic |
| Bibliometric | database-driven | algorithmic + spot checks | full | metrics + maps | quantitative |
| Methodological | method families | inclusion by method relevance | full | capability/comparison tables | evaluative |
| Geography-thematic | thematic + spatial lanes | medium | full | region/scale matrices | thematic-spatial |

## Router procedure (runtime start)
1. If user named a mode → use it; record in `review-mode.yaml`.
2. Else infer from topic phrasing:
   - "what do we know / state of knowledge" → narrative or conceptual;
   - "systematic mapping of X effects" → systematic or scoping;
   - "how has method M evolved" → methodological;
   - "bibliometric landscape" → bibliometric;
   - explicitly spatial framing ("regional patterns of…") → geography-thematic.
3. Record decision + one-line rationale + consequences for search stopping rule.
4. Proceed without interrupting the user unless the inferred mode would materially
   change deliverable expectations (e.g., they asked "quick overview" but router
   infers systematic).

## Mode-specific hard notes
- Systematic/scoping: pre-register search strings + inclusion/exclusion BEFORE the
  first query; log every screen decision; deviations need explicit_user approval
  recorded in run state.
- Narrative/conceptual: evidence saturation allowed as stopping rule but must be
  logged with concrete observations ("no new themes across last N results/pages").
