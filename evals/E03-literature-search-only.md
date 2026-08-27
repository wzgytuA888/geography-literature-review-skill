# E03 — API-first Literature Discovery

Offline normalization checks cover Semantic Scholar and OpenAlex provider payloads.
Policy check: Crossref is metadata-only, Google Scholar is manual supplementation,
and no HTML scraper exists in the v4 acquisition path.

Pass: both primary-provider schemas normalize correctly, provenance is retained,
and one provider failure does not erase results/logs from another.
