# Workflow: Source Plan → Peer Review → Search → Link → Screen → Full-text

Read `references/search-strategy.md` before this stage.

## 1. Search strategy and independent review

Preserve user terms, build concept blocks and adapt syntax per source. Record exact
queries, fields, filters, date range, language and platform. A Search Peer Reviewer
must close blocker issues and test combined recall against sentinel papers before
the final search.

## 2. Discovery

Open discovery can run through `scripts/literature_review_pipeline.py search`:

- Semantic Scholar: metadata, abstracts, S2 IDs, citation/reference counts,
  open-access PDF links and later citation edges.
- OpenAlex: broad works coverage, topics, authorships, institutions, countries,
  referenced works and citation counts using cursor pagination.
- Crossref: DOI metadata validation/enrichment only.

For a formal systematic/map review, also import/search the field, grey-literature,
regional and multilingual sources specified in the protocol. S2/OpenAlex-only
coverage cannot silently satisfy an exhaustive source plan.

One provider failing does not discard successful results from another. Retry
429/5xx/timeouts with bounded exponential backoff, cache completed requests, log
permanent errors and continue with other query/provider pairs.

## 3. Record deduplication, study linkage and screening

Merge report records only after bibliographic checks; DOI → Semantic Scholar ID →
OpenAlex ID → exact normalized title are candidates, not permission to merge
conflicting years/authors. Preserve fuzzy matches for adjudication. Link multiple
reports to a common `study_id` and sites/outcomes below it so they are not counted
as independent studies.

Statuses: retrieved → deduplicated → title_abstract_screened → fulltext_screened →
included. Run independent A/B decisions and adjudicate conflicts for systematic/
scoping modes; disclose AI vs human reviewers. Every exclusion uses a controlled
reason. Never auto-include all retrieved papers or treat rank cutoffs as exclusions.

## 4. Snowballing

After selecting core seed papers, use the `snowball` command for backward and
forward Semantic Scholar citation expansion. Record direction and seed ID, merge,
deduplicate and screen all new papers under the same criteria.

## 5. Legal local full text for the manuscript evidence set

Read `workflows/fulltext-acquisition.md`. Acquisition order remains local/Zotero →
API-provided OA link → Unpaywall/publisher OA → recognized repository/author manuscript
→ institutional library or user-provided copy. Every report retained for manuscript
synthesis must end as an identity-verified local file; abstract-only candidates can be
mapped or excluded but cannot enter the claim ledger. Any unresolved screened-in report
triggers the XLSX pause gate until a verified file arrives or a protocol-valid screening
revision removes it from the included set.

Outputs: literature registry, report→study→site links, Search Appendix/Log,
sentinel-recall report, deduplication log, A/B/adjudicated screening tables, flow
counts, full-text registry, citation network, errors and permitted raw snapshots.
