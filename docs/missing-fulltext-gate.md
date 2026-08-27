# Missing Full-text Gate (Human-in-the-Loop)

## Why
Fabricating findings from titles/abstracts is the cardinal sin of automated
reviews. When any screened-in paper retained for synthesis cannot be obtained legally, the
workflow MUST stop and ask you.

## Trigger
All of: selected review question exists · final search and screening executed · item
decision is include · no legal channel
succeeded (Zotero/local/legal link/OA resolver/institution copy/user upload).

## What happens
1. `python scripts/missing_fulltext_gate.py --run-dir runs/<id>` runs after the
   bounded legal acquisition pass.
2. Outputs `fulltext/missing_fulltext_literature.txt` and `.xlsx`, ordered HIGH
   first then citation-weight. The spreadsheet records legal attempts, failure,
   evidence need, expected filename, exact upload directory and user decision.
3. All completed state checkpointed; `state.json` =
   PAUSED_WAITING_FOR_USER_FULLTEXT.
4. Blocked until gate clears: extraction, appraisal, synthesis, outline, draft, gap finalization,
   final citations, manuscript. No silent continuation possible.

## Your options per item
- Upload PDF into `runs/<id>/fulltext/user_uploads/` (or import into Zotero) → resume;
- if the item was included in error, record a protocol-valid exclusion and its reason.

## Resume
```bash
python scripts/resume_helper.py validate-pdf --run-dir runs/<id> --pdf file1.pdf file2.pdf
python scripts/resume_helper.py status --run-dir runs/<id>
```
PDFs are matched by DOI first, then fuzzy title (≥0.72) against the missing list,
copied into `runs/<id>/fulltext/user_uploads/`, screening and full-text rows updated,
and extraction continues from the checkpoint. Partial uploads keep the gate closed
while any included item remains unresolved. A skip flag cannot bypass this gate.

## Severity tiers
Blocking: every included report without an identity-verified local copy.
Non-blocking (logged only): EXCLUDED_TITLE_ABSTRACT, DUPLICATE, OUT_OF_SCOPE,
LOW_PRIORITY_BACKGROUND, NOT_REQUIRED_FOR_CURRENT_CLAIM.
