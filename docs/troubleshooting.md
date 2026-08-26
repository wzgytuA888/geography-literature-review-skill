# Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| preflight exit 3, "Missing env vars" | Google Scholar provider not configured | see docs/google-scholar-setup.md; state stays PAUSED_GOOGLE_SCHOLAR_API_NOT_READY |
| preflight 401/403 | bad/expired API key | rotate key; re-run scholar-check |
| 429 / QuotaError | rate limit or monthly cap hit | wait/refill; runs checkpoint — resume later without redoing searches |
| Adapter "Unexpected response shape" | unknown provider contract | implement mapping in google_scholar_adapter.py BACKENDS; do NOT scrape |
| Zotero usable=false | desktop off / local server disabled / no web key | docs/zotero-setup.md; otherwise DOI/Crossref fallback (more UNRESOLVED risk) |
| Better BibTeX probe false | BBT not installed / wrong port | install extension; Juris-M uses port 24119 (unsupported by default) |
| Gate triggered unexpectedly many items | screening too inclusive | tighten inclusion criteria in search-plan; or provide PDFs / mark skips |
| resume_helper "no confident match" for a supplied PDF | title mismatch/scanned first page | ensure filename contains DOI, or first page has title text |
| mmdc render fails | Chrome path moved | edit ~/mmdc-env/puppeteer.json executablePath; or keep .mmd as source of truth |
| Kroki 500 | service outage | offline fallback: local mmdc; .mmd remains authoritative |
| pattern card confidence low | weak PDF extraction (e.g., B004/B008/B013/B014) | acceptable; consolidator downweights; consider OCR re-extraction |
| citation audit FAIL but refs look real | claim_supported=false entries | fix sentence↔evidence mismatch via Revision Agent, re-run validator |
| phrase_overlap VIOLATIONS | draft too close to benchmark wording | rewrite structurally (logic parity is the goal, not paraphrase) |

## Getting help inside a run
`python scripts/resume_helper.py status --run-dir runs/<id>` prints the current
state machine position; every pause writes its reason + user action into
state.json and run logs.
