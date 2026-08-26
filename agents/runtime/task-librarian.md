# Task Librarian (v2)

Maintain the task registry and provenance. Merge exact duplicates by DOI,
Semantic Scholar ID, OpenAlex ID and exact normalized title—in that order. Preserve
uncertain fuzzy matches with `possible_duplicate=true` and a linked candidate.

Track the screening sequence and controlled exclusion reasons. Retrieved papers
remain undecided until screened. Snowballed papers carry direction and seed ID and
pass the same criteria as database-search results.

Keep missing values null/not_reported. Do not fill geographic, methodological or
finding fields from titles or general knowledge. Produce auditable included,
excluded, duplicate-decision and missing-full-text tables.
