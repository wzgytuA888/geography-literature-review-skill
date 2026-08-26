# Runtime Orchestrator (v2)

Coordinate the staged workflow and keep `state.json` current. Delegate independent
API query lanes when the host supports parallel agents, but require workers to
write artifacts and return compact summaries.

Before discovery, confirm scope, provider readiness and query budget. A failed
provider is logged as degraded coverage; continue other approved APIs. If every
primary provider fails, pause as `PAUSED_ACADEMIC_APIS_NOT_READY`. Never substitute
Google Scholar page scraping.

Enforce stage order: search log → normalization → deduplication → screening →
snowballing/re-screening → full-text gate → evidence matrix → synthesis → writing
→ citation/figure/reviewer/audit gates → structured export.

Never treat retrieval as inclusion, metadata as findings, or benchmark facts as
task evidence. Resume from checkpoints without repeating cached requests.
