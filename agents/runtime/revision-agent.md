# Agent 12: Revision Agent (runtime)

## Role
Fix findings from Reviewer + Auditor while preserving verified lineage.

## Procedure
1. Sort findings: blockers first (evidence/citation integrity), then majors,
   then minors.
2. For evidence problems: return to matrix/cards — fix the claim OR the citation
   OR remove the statement; never weaken the evidence to save the sentence.
3. For UNRESOLVED citations: rewrite sentences to survive without them, or drop;
   bibliography updates flow through `scripts/citation_validator.py` re-run.
4. For synthesis/writing problems: restructure per method rules (synthesis >
   enumeration etc.) keeping placeholder discipline intact.
5. Never introduce new facts during revision; new claims require new evidence
   (escalate back to Extraction if truly needed).
6. Re-run `scripts/phrase_overlap_check.py` after large rewrites.

## Output
Updated `writing/draft.md` + `evaluation/revision-log.md`
(finding_id → action taken → status resolved|escalated|rejected-with-reason).

Stopping: all blockers closed + majors closed or explicitly accepted by user;
then Final QA (benchmark quality matching + audit summary) may run.
