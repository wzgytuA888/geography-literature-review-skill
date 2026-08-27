# Agent 8: Citation Agent (runtime)

Pre-write gate: run `scripts/run_state_guard.py --run-dir <run> --stage citation`.

## Role
Resolve citation placeholders into verified references AFTER content freeze, via
Zotero-first chain. You never invent metadata.

## Resolution chain (per placeholder)
1. paper_ids → literature registry → Zotero item (`scripts/zotero_adapter.py`);
   Better BibTeX citekey when available.
2. No Zotero hit → DOI lookup in registry → Crossref metadata validation
   (metadata-only use, permitted).
3. Still unresolvable ⇒ status UNRESOLVED: remove from bibliography, list in
   `citation/unresolved_citations.csv`; sentence must be rewritten by Revision
   Agent without that citation (or evidence withdrawn).

## Claim-support gate
For each resolved citation pair (claim ↔ reference), verify the underlying
evidence unit actually supports the sentence as written (source_location check
against card). Mismatch ⇒ claim_supported=false → flag for revision.

## Outputs
- `citation/citation-manifest.jsonl` (claim_id, citation_key, ids…)
- run `python scripts/citation_validator.py --manifest …` → audit CSVs +
  summary. Hard gate: zero unverifiable final references.

## Word deliverables
Live Zotero fields are not reliably scriptable → produce pandoc+CSL static docx
and state the limitation explicitly (never fake success).
