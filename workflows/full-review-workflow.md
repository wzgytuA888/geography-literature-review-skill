# Workflow: Full Review v2

```
[0] task-init                 scope + multi-API readiness
[1] bounded search strategy
[2] Semantic Scholar/OpenAlex search + Crossref validation + Search Log
[3] normalize + deduplicate + title/abstract screening
[4] core-paper selection + backward/forward snowballing + re-screen
[5] legal full text + MissingFullTextGate
[6] evidence matrix + iterative themes + traceable synthesis
[7] outline + evidence-grounded draft
[8] Zotero/DOI citations + figures
[9] independent review + evidence audit + benchmark QA
[10] CSV/JSON/XLSX/manuscript final package + run summary
```

State is checkpointed after every stage. A provider error logs degraded coverage
and permits other APIs to continue; a complete discovery outage pauses the run.
Full-text and citation hard gates retain their v1 behavior.

Final review sections should cover search overview, included-study characteristics,
temporal development, spatial distribution, themes, data/methods, main findings,
consensus, conflicts, limitations, evidence-grounded gaps, future directions, key
papers and evidence limitations.
