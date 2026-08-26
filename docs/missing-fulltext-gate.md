# Missing Full-text Gate (Human-in-the-Loop)

## Why
Fabricating findings from titles/abstracts is the cardinal sin of automated
reviews. When an important screened-in paper cannot be obtained legally, the
workflow MUST stop and ask you.

## Trigger
All of: real topic exists · Scholar search executed · item status ∈
{INCLUDED_PENDING_FULLTEXT, HIGH_PRIORITY_PENDING_FULLTEXT} · no legal channel
succeeded (Zotero/local/legal link/OA resolver/institution copy/user upload).

## What happens
1. `python scripts/missing_fulltext_gate.py --run-dir runs/<id>` runs
   automatically at stage 2 end.
2. Outputs `missing_fulltext_literature.txt` (always) and `.xlsx` (when openpyxl
   installed), ordered HIGH first then citation-weight, each row carrying title/
   DOI/Scholar URL/relevance/failure reason/recommended action.
3. All completed state checkpointed; `state.json` =
   PAUSED_WAITING_FOR_USER_FULLTEXT.
4. Blocked until gate clears: final synthesis, outline, draft, gap finalization,
   final citations, manuscript. No silent continuation possible.

## Your options per item
- Upload PDF into the run folder (or import into Zotero) → resume;
- mark `explicit_user_skip=true` (recorded in audit + limitations permanently);
- confirm exclusion.

## Resume
```bash
python scripts/resume_helper.py validate-pdf --run-dir runs/<id> --pdf file1.pdf file2.pdf
python scripts/resume_helper.py status --run-dir runs/<id>
```
PDFs are matched by DOI first, then fuzzy title (≥0.72) against the missing list,
copied into `runs/<id>/user_pdfs/`, screening rows updated, extraction continues
from the checkpoint. Partial uploads keep the gate closed while any
high-priority item remains unresolved (unless you explicitly allowed skips).

## Severity tiers
Blocking: INCLUDED_PENDING_FULLTEXT, HIGH_PRIORITY_PENDING_FULLTEXT.
Non-blocking (logged only): EXCLUDED_TITLE_ABSTRACT, DUPLICATE, OUT_OF_SCOPE,
LOW_PRIORITY_BACKGROUND, NOT_REQUIRED_FOR_CURRENT_CLAIM.
