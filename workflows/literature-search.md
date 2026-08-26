# Workflow: API Search → Deduplicate → Screen → Snowball → Full-text

Read `references/search-strategy.md` before this stage.

## 1. Search strategy

Preserve user terms and generate no more than the configured query budget.
Record actual queries, filters, date range and language in `search_strategy.json`.

## 2. Discovery

Run `scripts/literature_review_pipeline.py search`:

- Semantic Scholar: metadata, abstracts, S2 IDs, citation/reference counts,
  open-access PDF links and later citation edges.
- OpenAlex: broad works coverage, topics, authorships, institutions, countries,
  referenced works and citation counts using cursor pagination.
- Crossref: DOI metadata validation/enrichment only.

One provider failing does not discard successful results from another. Retry
429/5xx/timeouts with bounded exponential backoff, cache completed requests, log
permanent errors and continue with other query/provider pairs.

## 3. Deduplication and screening

Merge exact identity matches by DOI → Semantic Scholar ID → OpenAlex ID → exact
normalized title. Preserve fuzzy matches with `possible_duplicate=true`.

Statuses: retrieved → deduplicated → title_screened → abstract_screened →
fulltext_screened → included. Every exclusion uses the controlled reason list in
`src/geo_review/pipeline.py`. Never auto-include all retrieved papers.

## 4. Snowballing

After selecting core seed papers, use the `snowball` command for backward and
forward Semantic Scholar citation expansion. Record direction and seed ID, merge,
deduplicate and screen all new papers under the same criteria.

## 5. Legal full text

Acquisition order remains Zotero/local files → API-provided OA link → DOI/
publisher OA → legal resolver → institutional/user-provided copy. Important
included papers still missing text trigger `MissingFullTextGate`; downstream
finding/mechanism synthesis remains blocked.

Outputs: literature.json/csv/xlsx, Search_Log, deduplication log, screening table,
citation network, errors.log and cached request payloads.
