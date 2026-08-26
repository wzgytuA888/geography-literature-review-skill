# Zotero Integration

## Position in system
Zotero = Reference Source of Truth (management, metadata, full text, citekeys,
bibliography). It is NOT a discovery backend — topic search stays Scholar-only.

## Capability detection (run `python scripts/zotero_adapter.py`)
Probes in order: Web API v3 (needs ZOTERO_API_KEY + ZOTERO_USER_ID) · local HTTP
server localhost:23119/api (Zotero 7+, user id 0, needs desktop setting "allow
other applications") · Better BibTeX JSON-RPC (localhost:23119/better-bibtex).

## Adapter surface (scripts/zotero_adapter.py)
search() · search_collection() · get_metadata() · get_fulltext() · resolve_doi()
· get_citation_key() · bibliography_csl() · insert_docx_citation() (returns
explicit NOT-SUPPORTED guidance) · update_docx_bibliography() (same).
Fallback chain: Better BibTeX export → DOI/Crossref metadata → CSL/BibTeX output.

## Setup
1. Web API: create key at zotero.org/settings/keys/new (read enough for citations;
   write not required by this skill); export ZOTERO_API_KEY, ZOTERO_USER_ID.
2. Local: enable server access in Zotero settings; keep Zotero running during runs.
3. Better BibTeX: install extension; citekeys via JSON-RPC `item.citationkey`;
   exports via `item.export` (bibtex/biblatex/csljson).

## Rate limits / reliability
Web API: ≤4 concurrent requests; honor Backoff/Retry-After headers; bibliography
endpoint ≤150 items. Local endpoints require running desktop app.

## DOCX deliverables truth table
| Ability | Scripted? | Deliverable |
| --- | --- | --- |
| static CSL citations+bibliography in .docx | yes (pandoc --citeproc) | final/review.docx |
| live Zotero Word fields | NO public API | do not fake; report limitation |

## Env vars
ZOTERO_API_KEY · ZOTERO_USER_ID (never committed; see .env.example)
