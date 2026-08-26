# Geography Literature Review Research Skill

Version 2 turns the project from a Google-Scholar-gateway workflow into a
reproducible, API-first literature-review system. It retrieves and normalizes
research metadata, preserves search provenance, supports conservative screening
and citation snowballing, builds a geography-aware evidence matrix, and retains
the v1 evidence-to-claim audit and review-writing pipeline.

## What v2 does

1. Builds a bounded, reproducible search strategy from a topic, research
   question, keywords, Boolean query and filters.
2. Searches Semantic Scholar and OpenAlex. Semantic Scholar works without an API
   key where public quota permits; a key improves rate limits.
3. Uses Crossref to validate and enrich DOI metadata rather than as the primary
   discovery source.
4. Normalizes records and deduplicates by DOI → Semantic Scholar ID → OpenAlex ID
   → exact normalized title. Fuzzy matches are retained and flagged.
5. Records every database/query/filter/count/time tuple in `Search_Log`.
6. Supports title, abstract and full-text screening with controlled exclusion
   reasons. Retrieval never implies inclusion.
7. Performs backward and forward citation snowballing from Semantic Scholar seed
   papers while preserving `seed_paper_id` and discovery method.
8. Exports CSV, JSON and an Excel workbook with `Papers`, `Evidence_Matrix`,
   `Included`, `Excluded`, `Themes`, `Search_Log` and `Citation_Network` sheets.
9. Retains legal full-text gating, evidence units, traceable synthesis, Zotero/
   DOI citation validation, figure grounding and independent audit.

Google Scholar is now an optional manual supplement. This project does not scrape
Google Scholar result pages.

## Architecture

The original dual-corpus design remains unchanged:

| Corpus | Role | Can supply scientific facts? |
|---|---|---|
| `benchmark_corpus/` | teaches how high-quality geography reviews are structured | No |
| `runs/<run-id>/` | records the retrieved, screened and extracted topic evidence | Yes |

The v2 executable layer lives under `src/geo_review/`:

```text
models.py                  unified paper and search-log schemas
http.py                    caching, throttling, retry and error logging
clients/semantic_scholar.py
clients/openalex.py
clients/crossref.py
pipeline.py                query planning, deduplication, screening, scoring
export.py                  CSV, JSON and multi-sheet Excel exports
```

Existing `agents/`, `workflows/`, `references/`, `benchmark_corpus/`, Zotero,
full-text gate, figure and audit modules remain part of the full workflow.

## Installation

```powershell
& "F:\pj311\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Optional `.env` values:

```dotenv
SEMANTIC_SCHOLAR_API_KEY=
OPENALEX_MAILTO=researcher@example.org
CROSSREF_MAILTO=researcher@example.org
ZOTERO_API_KEY=
ZOTERO_USER_ID=
```

See [`docs/academic-api-setup.md`](docs/academic-api-setup.md). Secrets are read
from `.env` or process environment and must never be committed.

## Readiness check

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/literature_review_pipeline.py `
  preflight --out-dir runs/preflight
```

At least one working primary API yields `status: ready`. A provider failure is
logged and the other provider can continue; cached completed requests are reused.

## Search example

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/literature_review_pipeline.py search `
  --topic "Permafrost degradation and vegetation response on the Tibetan Plateau" `
  --keywords "permafrost degradation" vegetation NDVI "Tibetan Plateau" `
  --year-lo 2000 --year-hi 2026 --language en --max-papers 200 `
  --out-dir runs/permafrost-vegetation
```

The generated `search_strategy.json` shows both original inputs and every actual
query. Output records initially have `screening_status=retrieved` and
`include=null`; the workflow does not silently include all hits.

## Citation snowballing

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/literature_review_pipeline.py snowball `
  --input runs/permafrost-vegetation/literature.json `
  --topic "Permafrost degradation and vegetation response" `
  --limit-per-seed 50 --out-dir runs/permafrost-vegetation-expanded
```

Backward and forward additions are labeled and linked to their seed paper.

## Evidence model

Alongside identifiers, bibliographic metadata, API provenance and screening
status, the evidence matrix provides fields for research question, study area,
coordinates, climate zone, ecosystem, spatial/temporal scale and resolution,
remote-sensing/environmental/climate datasets, variables, methods, models,
sample size, structured findings, mechanism, limitations and gaps.

These evidence fields remain null until the abstract or full text explicitly
supports them. AI inference is not treated as a paper fact; any necessary
inference must carry `inference=true` and a confidence level.

## Relevance scoring

The optional score is a transparent screening aid, not a paper-quality score:

```text
0.55 topic-token overlap
+ 0.20 recency within a 20-year window
+ 0.15 log-scaled citation count
+ 0.10 metadata completeness
```

Citation count alone never establishes authority or inclusion.

## Full review workflow

Natural language or `/geo-review` commands support:

```text
api-check  start  search  screen  snowball  evidence  themes  synthesize
outline    draft  cite    figures review    audit     export  resume  full
```

A full run proceeds from search through screening and legal full-text acquisition,
then evidence extraction, iterative themes, consensus/controversy/gap synthesis,
outline, drafting, citation audit, figures, independent review and final exports.

## Tests

```powershell
& "F:\pj311\.venv\Scripts\python.exe" -m unittest discover -s tests -v
& "F:\pj311\.venv\Scripts\python.exe" evals/run_scripted.py
```

## Limitations

- Public API quotas and coverage differ; no database is complete.
- Abstract availability is uneven, and metadata-only fields cannot replace full
  text for extracting findings or mechanisms.
- Automated screening and theme coding require researcher review.
- The benchmark corpus is dominated by one journal family; it guides form, not facts.
- Live Zotero fields in Word remain a desktop-plugin action; generated DOCX files
  use static CSL citations.

## Privacy, copyright and license

API keys, raw PDFs, full text, caches and local runs are git-ignored. Only legally
available full text may be acquired. Code and prompts are MIT licensed; review
outputs belong to their authors.
