# Workflow: Task Init (runtime start)

Input: user gives topic / question / field / concept to review.

1. mkdir `runs/<YYYYMMDD>-<slug>/` with subfolders search/ evidence/ writing/
   citation/ figures/ evaluation/.
2. Run preflight: `python scripts/google_scholar_preflight.py`
   - exit 0 → continue;
   - exit 2/3 → state PAUSED_GOOGLE_SCHOLAR_API_NOT_READY + report + STOP.
3. Write `task.md`: interpreted topic, target audience/journal style hints,
   deliverables requested, language scope.
4. Router (`references/review-methods.md`) → `review-mode.yaml` (mode + rationale +
   consequences).
5. Scope definition: time window, geography/language coverage, exclusion defaults
   (non-scholarly sources), depth target (section count range).
6. Delegate Search Strategist; record all decisions in `state.json`
   (stage=init, status=RUNNING).

Checkpoint after this workflow = safe pause point before any quota spend.
