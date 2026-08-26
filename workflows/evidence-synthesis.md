# Workflow: Evidence Extraction & Synthesis

Precondition: gate CLEAR; ≥1 full text AVAILABLE_*.

## Extraction pass
For each available paper → Evidence Extractor produces
`evidence/literature-cards/P###.yaml` (schema templates/task-literature-card.yaml);
every evidence unit gets global E### id, source_page REQUIRED.

## Matrix assembly
Append rows to `evidence/evidence-matrix.csv` (columns exactly as template header):
claim_id, theme, paper_id, evidence_id, claim_text, evidence_summary, methodology,
geography, spatial_scale, temporal_scope, support_or_contradict, confidence,
source_location, doi, zotero_key.
Integrity checks: unique evidence_ids; paper_ids exist in registry; source_location
non-empty; confidence present.

## Argument map
`evidence/argument-map.md`: proposition table — statement | supporting evidence_ids |
contradicting evidence_ids | conditions | evidence strength | unresolved uncertainty.

## Synthesis pass
Synthesis Agent walks themes per references/synthesis-rules.md →
`evidence/synthesis-notes.md`; conflict diagnosis ladder applied; gap candidates
flagged with their evidential basis (deficit counts, blind spots, contradictions).

Checkpoint: matrix+map saved = resumable before any drafting.
