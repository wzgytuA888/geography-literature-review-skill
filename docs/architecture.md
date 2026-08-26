# Architecture v2

The project keeps v1's compile-time/runtime boundary and dual-corpus isolation.
Version 2 changes only the runtime discovery and structured-review layer.

## Compile time

Benchmark PDFs are converted into form-only review pattern cards and consolidated
method knowledge. These resources teach architecture, rhetoric, synthesis,
geography reasoning, gap derivation and figure design. They never supply topic
facts or citations to a new review.

## Runtime

```
user question
  → bounded search strategy
  → Semantic Scholar ┐
                     ├→ normalized PaperRecord → dedup → screen → Search Log
  → OpenAlex         ┘
  → Crossref DOI validation/enrichment
  → core seeds → backward/forward snowballing → re-screen
  → legal full text / MissingFullTextGate
  → evidence matrix → themes → traceable claims/argument map
  → outline/draft → Zotero/DOI citations → figures → independent audit
  → CSV + JSON + XLSX + manuscript package
```

`src/geo_review/http.py` owns request throttling, retries, caching and error logs.
Provider clients normalize to `PaperRecord`; pipeline code owns query generation,
deduplication, explicit screening and transparent triage scoring. Deterministic
exports are generated independently of the writing agents.

Google Scholar is no longer a runtime dependency. Researcher-supplied manual
records may be added with full provenance, but result-page scraping is prohibited.

## Failure behavior

Individual provider/query failures are logged and do not erase other results. A
complete primary-provider outage pauses discovery. Missing important full text and
unverified citations remain hard gates. State and cached requests make runs resumable.
