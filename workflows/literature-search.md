# Workflow: Literature Search → Screen → Full-text

Mandatory order: Google Scholar API Search → Screening → Full-text Acquisition.
(Discovery backend is non-negotiable; see references/search-strategy.md.)

## 1. Search execution
- Strategist emits `search/search-plan.yaml`; Scouts A–E run lanes in parallel via
  adapter; every hit appended to `search/google-scholar-search-log.csv`.
- Provider 401/403/429/schema errors → Orchestrator pauses (preflight states).
- Stopping rules from plan (budgets/saturation/quota guard).

## 2. Screening
Librarian dedupes (DOI > result_id > title≥0.9) then screens:
| status | meaning |
| --- | --- |
| INCLUDED_PENDING_FULLTEXT | passes title/abstract bar; needs text |
| HIGH_PRIORITY_PENDING_FULLTEXT | clearly central; blocking priority |
| EXCLUDED_TITLE_ABSTRACT / OUT_OF_SCOPE / DUPLICATE | logged, non-blocking |
All decisions land in `screening.csv` with one-line reasons.

## 3. Full-text acquisition (legal channels only)
Order: Zotero/local PDFs → provider-returned legal links → DOI/publisher open
access → OA resolvers → institution-accessible copies → ask user.
Track `fulltext_status` enum honestly; never bypass paywalls/CAPTCHA.

## 4. MissingFullTextGate (mandatory human gate)
`python scripts/missing_fulltext_gate.py --run-dir runs/<id>`
- CLEAR → proceed to evidence extraction;
- TRIGGERED → TXT (+XLSX) report generated, checkpoint saved, state=
  PAUSED_WAITING_FOR_USER_FULLTEXT, downstream stages BLOCKED.
Resume path: user supplies PDFs → `scripts/resume_helper.py validate-pdf` →
matched items updated; gate clears only when no blocking item remains OR user
marks explicit_user_skip (recorded in audit + limitations forever).
