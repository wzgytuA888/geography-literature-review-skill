# Google Scholar Setup (MANDATORY before runtime search)

> **使用本 Skill 前，请先配置 Google Scholar API provider。**
> **Before using this Skill, configure a Google Scholar API provider.**

Google Scholar itself has no official public developer API. This skill requires
a legally configured third-party gateway that exposes Scholar results as JSON
(verified compatible examples: SerpAPI `engine=google_scholar`; SearchApi;
SerpDog — see docs/technology-baseline.md for exact schemas and limits).

## 1. Environment variables (required)

```bash
export GOOGLE_SCHOLAR_API_PROVIDER=serpapi        # or your gateway's name
export GOOGLE_SCHOLAR_API_KEY=...                 # secret — never commit
export GOOGLE_SCHOLAR_API_ENDPOINT=https://serpapi.com/search
# optional
export GOOGLE_SCHOLAR_ENGINE=google_scholar
export GOOGLE_SCHOLAR_LANGUAGE=en
GOOGLE_SCHOLAR_REGION / _RESULTS_PER_PAGE / _MAX_PAGES / _RATE_LIMIT
```

Provider-specific non-secret options go in `config/google-scholar.yaml`
(copy from `config/google-scholar.yaml.example`). Secrets live ONLY in env vars
or an untracked `config/google-scholar.local.yaml`.

## 2. Verify with preflight

```bash
python scripts/google_scholar_preflight.py
# exit 0 = READY; exit 2/3 = fix config; JSON report printed (key never shown)
```

## 3. What the adapter guarantees
- Normalized results across providers (title/authors/year/result_id/doi-if-
  present/cited-by fields); year+DOI parsed from summary/snippet because no
  provider exposes dedicated fields.
- Strict error classes: ConfigError / AuthError / QuotaError → workflow pauses
  (PAUSED_GOOGLE_SCHOLAR_API_NOT_READY). **No automatic fallback to WoS, Scopus,
  OpenAlex, Semantic Scholar, PubMed, web search, or page scraping — by design.**
- Crossref/DOI.org/Unpaywall are used downstream for metadata validation, DOI
  resolution, availability checks — never for topic discovery.

## 4. Quota notes
Budgets differ wildly (e.g., SerpAPI free tier ≈250 searches/month). Plan query
families accordingly (`max_pages`, safety margin in yaml); runs checkpoint so
refilled quotas can resume without repeating searches.
