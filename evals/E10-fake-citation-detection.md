# E10 — Fake Citation Detection
Fixture citation-manifest.jsonl mixes plausible-but-fake entries with verifiable DOIs. With resolvers disabled everything must resolve UNRESOLVED; with Crossref enabled fakes stay UNRESOLVED.
Pass: fabricated refs flagged = 100%.
