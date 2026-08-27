# Google Scholar Manual Supplement (Legacy v1 Integration)

Version 4 does not require Google Scholar. Primary discovery uses Semantic Scholar
and OpenAlex; configure them using `academic-api-setup.md`.

If a researcher manually searches Google Scholar or already has a legal third-party
gateway, imported records must retain the exact query, date and source in Search_Log.
Do not scrape Google Scholar result pages and do not silently replace failed primary
APIs with a scraper.

The v1 adapter and environment variables remain in the repository solely for
backward compatibility:

```text
GOOGLE_SCHOLAR_API_PROVIDER
GOOGLE_SCHOLAR_API_KEY
GOOGLE_SCHOLAR_API_ENDPOINT
```

They are not required by `scripts/literature_review_pipeline.py`.
