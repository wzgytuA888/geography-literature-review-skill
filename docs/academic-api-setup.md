# Academic API Setup (v2)

The runtime discovery layer uses Semantic Scholar and OpenAlex. Crossref is used
for DOI validation and metadata enrichment. Google Scholar is optional manual
supplementation and its web pages must not be scraped.

## Install

```powershell
& "F:\pj311\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The pipeline loads `.env` automatically. Environment variables take precedence.

## Variables

- `SEMANTIC_SCHOLAR_API_KEY`: optional but recommended for better rate limits.
- `OPENALEX_MAILTO`: recommended contact email for the OpenAlex polite pool.
- `CROSSREF_MAILTO`: recommended contact email for Crossref requests.
- `ZOTERO_API_KEY` / `ZOTERO_USER_ID`: optional citation-library integration.

Do not put keys in YAML or source code. `.env` and `*.local.yaml` are ignored.

## Verify

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/literature_review_pipeline.py `
  preflight --out-dir runs/preflight
```

`ready` means at least one primary discovery API is available. A single provider
failure produces a degraded log but does not destroy the run; later providers and
papers continue. HTTP 429/5xx, timeout and connection failures use bounded
exponential retry and are written to `errors.log`.

## Reproducibility and cache

Every actual database/query/filter/count/time tuple is stored in `Search_Log`.
JSON responses are cached under the run's `.cache/` using a key derived from the
database, endpoint and request parameters. Deleting a run removes its cache; do
not commit runtime caches or downloaded full text.

