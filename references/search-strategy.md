# Reproducible API-first Search Strategy

## Inputs

Record the research topic/question, original keywords, Boolean query, year range,
language, journal, author, DOI and paper cap. Parse a short topic into research
object, outcome, region and a small synonym set, then show or log all generated
queries. Never expand without a fixed bound.

## Provider roles

1. Semantic Scholar: primary relevance search, abstracts, identifiers, citation
   and reference edges, OA PDF metadata.
2. OpenAlex: primary broad-coverage search and bibliometric context—topics,
   authorships, institutions, countries and referenced works. Use cursor paging.
3. Crossref: DOI validation and publication metadata enrichment.
4. Google Scholar: optional researcher-run manual supplementation. Log manually
   added records and queries; do not scrape result pages.

## Reproducibility

For each request, log database, exact query, actual filters, date range, returned
count, time and status/error. Cache identical requests within a run. Preserve
zero-result and failed-query rows rather than silently dropping them.

## Stopping

Stop at the user cap, query budget, quota guard or thematic saturation. Saturation
requires consecutive planned query rounds with no material new eligible themes;
do not claim exhaustive coverage from one database.

## Ranking

Use the disclosed relevance score only for triage. Citation count is neither
quality nor authority. Inclusion remains a criterion-based screening decision.
