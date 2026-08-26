# Zotero Setup

Optional at search time, required for the smoothest citation workflow.

## Option A — Web API (works without desktop app running)
1. zotero.org/settings/keys/new → create key (read access sufficient).
2. Note your numeric userID (shown on same page / `GET /keys/<key>`).
3.
```bash
export ZOTERO_API_KEY=...
export ZOTERO_USER_ID=12345678
```
Limits: ≤4 concurrent requests; honor Backoff headers; bibliography ≤150/batch.

## Option B — Local server (Zotero 7+)
1. Zotero → Settings → Advanced → "Allow other applications on this computer to
   communicate with Zotero".
2. Keep Zotero desktop running during runs; adapter probes localhost:23119/api.

## Better BibTeX (recommended)
Install BBT → adapter gains citekey resolution (`item.citationkey`) and exports
(bibtex/biblatex/csljson via JSON-RPC or pull endpoint).

## Probe everything
```bash
python scripts/zotero_adapter.py
# {"web_api":..,"local_api":..,"better_bibtex":..,"usable":..}
```

## What if nothing is available?
Citation work degrades gracefully: registry DOI → Crossref metadata validation →
CSL/BibTeX output. Anything unresolvable becomes UNRESOLVED CITATION and leaves
the bibliography with a report — never invented, never silently dropped.

## Word deliverables truth table
| Deliverable | Scriptable? |
| --- | --- |
| .docx with static CSL citations + bibliography (pandoc --citeproc) | ✅ |
| .docx with live Zotero fields | ❌ no public API — plugin GUI only; limitation reported, never faked |
