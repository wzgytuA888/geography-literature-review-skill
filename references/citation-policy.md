# Citation Policy (Zero Hallucination)

## Acceptance criteria for ANY final citation
At least one of:
- Zotero item exists (`found_in_zotero=true`), or
- verifiable DOI resolving to consistent metadata (Crossref check passes year/
  title consistency), or
- authoritative metadata record from the search log with provider result_id +
  URL.

Model memory alone is NEVER acceptance.

## Pipeline (after content freeze)
```
placeholders <CITE …> → resolve paper_ids → Zotero match → DOI/metadata validate
→ claim-support verify → insert → bibliography → audit CSVs
```
Tools: `scripts/zotero_adapter.py`, `scripts/citation_validator.py`.
Hard gate: `unresolved=0` AND `claim_unsupported=0` for final delivery;
otherwise deliverable is marked INCOMPLETE with the unresolved report attached.

## Claim–citation binding
- Every placeholder carries claim_id + evidence_ids + paper_ids.
- One cluster supports ONE proposition; multi-proposition clusters are split.
- If a real reference does not support the sentence → claim_supported=false →
  rewrite or drop. A true reference misused is still a citation error.

## Density priors (from benchmark corpus medians)
~2–4 citations per paragraph-block typical for top reviews; zero-citation
paragraphs legitimate for framing/transition/method notes only. Priors guide,
never force: unsupported claims fail regardless of density.

## Failure handling
UNRESOLVED → remove from references, list in `citation/unresolved_citations.csv`,
rewrite dependent sentences. Never keep an unverified entry "for completeness".

## Word/live-fields honesty
Live Zotero fields not reliably scriptable ⇒ deliver pandoc+CSL static docx +
state limitation; never simulate field success.
