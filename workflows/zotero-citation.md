# Workflow: Zotero Citation Resolution

Trigger: content freeze reached.

1. Citation Agent extracts all placeholders from `writing/draft.md` →
   `citation/citation-manifest.jsonl`.
2. Resolution chain per entry (Zotero → BBT citekey → DOI/Crossref validate →
   else UNRESOLVED) — see references/citation-policy.md.
3. Claim-support gate: sentence ↔ evidence unit ↔ source_location check;
   mismatches set claim_supported=false.
4. Run `python scripts/citation_validator.py --manifest citation/citation-manifest.jsonl`
   → citation-audit.csv, unresolved_citations.csv, audit-summary.json.
   Hard gate: unresolved=0 AND claim_unsupported=0 for delivery; else Revision
   Agent fixes and re-runs.
5. Bibliography build:
   - Zotero available: bibliography_csl() (≤150/batch) or BBT item.export → .bib;
   - pandoc --citeproc renders final/review.docx with static CSL citations;
   - live Zotero Word fields NOT scripted — limitation stated in run summary.
6. Deliverables to `final/`: review.md · review.docx · references.bib ·
   citation_manifest.json · unresolved_citations.csv (empty at gate-pass).
