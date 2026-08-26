# Search Strategy (Google Scholar API only)

## Non-negotiables
1. Discovery backend = configured Google-Scholar-compatible provider. Nothing else.
2. Preflight (`scripts/google_scholar_preflight.py`) must pass before the first query.
3. Provider failure ⇒ PAUSED_GOOGLE_SCHOLAR_API_NOT_READY. No WoS/Scopus/OpenAlex/
   Semantic Scholar/PubMed/web-search/scraping fallback — ever.
4. Crossref/DOI.org/OA resolvers: metadata validation, DOI resolution, availability
   checks ONLY — never discovery.
5. Every query and every result row lands in `search/google-scholar-search-log.csv`.

## Query construction
From `search-plan.yaml` concept table build families:
- **broad-recall**: core synonyms OR-ed, no year cap, first pages only;
- **high-precision**: exact phrases ANDed, tighter years;
- **seminal**: early window (e.g., ≤2005) or highest cited-by probes;
- **recent**: last ~5y (`as_ylo`), possibly date-sort if provider supports;
- **methods**: method-term × topic pairs;
- **regional/spatial**: region terms × topic (only when spatially framed);
- **controversy probes**: opposing-term pairs ("increases" vs "decreases" framings,
  "uncertainty", "contradictory").

Map to provider params strictly: q, num≤20, start/page, as_ylo/as_yhi, hl/lr.
Never assume undocumented fields.

## Snowballing within policy
- Forward: cited-by via provider fields (`cites_id` on SerpAPI-class providers) —
  log as qid family FWD-*.
- Related: no direct array on verified providers — emulate via variant queries;
  record this limitation rather than scraping.
- Backward: parse reference lists from legally obtained seed PDFs; verify each via
  Scholar queries; add through normal screening.

## Stopping rules (predefined in plan)
- page/result budget per family; global result cap;
- saturation: two consecutive expansion rounds adding no new themes/high-quality
  candidates (log which themes stopped appearing);
- quota guard: stop at provider threshold minus safety margin, checkpoint, resume
  after refill.

## Logging schema (search/google-scholar-search-log.csv)
query_id, query, provider, timestamp, page, rank, title, authors, year,
publication, scholar_result_id, doi, result_url, pdf_or_fulltext_url,
cited_by_count, cited_by_id, related_id, retrieval_status, dedup_status,
screening_status, notes
