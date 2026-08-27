# E19 — Local Full-text Hard Gate

## Fixture

Seed an adjudicated screening table with one included report whose registry row
is `OPEN_ACCESS_FOUND` but has no validated local PDF path or checksum.

## Procedure

Run `scripts/missing_fulltext_gate.py --run-dir <fixture-run>`.

## Pass criteria

- `fulltext/missing_fulltext_literature.xlsx` is created and contains the report,
  attempted routes, failure reason and requested upload filename.
- `fulltext/user_uploads/` exists and the state becomes
  `PAUSED_WAITING_FOR_USER_FULLTEXT`.
- The drafting stage does not start.
- A URL, abstract, landing page or unvalidated byte stream never counts as local
  full text.
