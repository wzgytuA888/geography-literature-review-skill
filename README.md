# Geography Literature Review Research Skill

Version 4 is a full-text-first, NREE-profile multi-agent workflow designed to
produce a deeply synthesized, auditable **submission candidate** when the evidence,
access and human verification permit it.

Give the skill a research topic. If the direction is broad, it first searches the
landscape, offers 3-5 evidence-informed questions and pauses for your choice. It then
designs and peer-reviews the final search, downloads lawful full text locally,
screens and appraises studies, analyzes geographic/scale heterogeneity, synthesizes
claims with certainty ratings, drafts the article, verifies citations and runs
independent scientific and reproducibility gates.

It does not promise journal acceptance or disguise missing database access, full
text or human verification. When those constraints matter, it returns a complete
research draft plus a precise readiness report rather than polishing uncertainty
into false confidence.

## Quick use

Invoke the skill in Codex and provide a topic, for example:

```text
Use $geography-literature-review-skill to produce a deep review of how climate
change and irrigation expansion alter groundwater depletion across arid regions.
Target a journal-neutral English manuscript and include a geographic evidence map.
```

When a sufficiently specific topic is supplied, v4 defaults to a deep NREE-profile
critical narrative review. A broad topic triggers the scope-selection checkpoint.
It uses the word “systematic”
only when multi-source coverage, selection, appraisal and reporting gates justify it.

## What is new in v4

- Evidence-informed scope convergence: broad directions produce 3-5 review-question
  cards and `PAUSED_WAITING_FOR_SCOPE_SELECTION`.
- Mandatory local full text for every report used in manuscript claims; abstracts are
  limited to orientation and screening.
- Lawful acquisition routes across local/Zotero, OA APIs, publisher OA, recognized
  repositories, author manuscripts and library delivery.
- Automatic missing-full-text XLSX handoff and resumable
  `PAUSED_WAITING_FOR_USER_FULLTEXT` checkpoint.
- An NREE-derived architecture and paragraph contract distilled from 60 full review
  articles, plus an independent NREE Architecture Editor gate.
- Visual-argument planning and proposal-to-heading roadmap fidelity before drafting.

Version 4 retains the v3 foundations:

- Protocol and contribution test before final searching.
- Review-type routing: critical/integrative, systematic, scoping/map,
  methodological, bibliometric, realist, quantitative and qualitative synthesis.
- Source-plan-first search with independent query review and sentinel-paper recall.
- Report → study → site/outcome linkage to prevent double-counting one dataset.
- Independent A/B screening and adjudication contracts, with truthful AI/human
  disclosure.
- Design-matched critical appraisal, including remote-sensing and geospatial model
  validity domains.
- Geographic representativeness, scale, zoning, spatial dependence and
  transferability audits.
- Method selection for meta-analysis, SWiM-style structured synthesis, qualitative
  synthesis and realist context–mechanism–outcome analysis.
- Per-claim evidence certainty, contradiction testing and defensible gap derivation.
- 20+ specialist roles executed in dependency-aware waves.
- A deterministic run scaffold and a hard submission-readiness gate.
- Publication package with manuscript, search appendix, screening flow, appraisal,
  claim ledger, evidence profile, verified citations, figures/tables, reporting
  checklist, AI disclosure and reproducibility report.

## Multi-agent architecture

The Orchestrator owns state and merges artifacts. Specialists work in staged waves:

```text
Protocol Architect + Domain Theorist
  → Research Landscape Cartographer (when broad) → user scope choice
  → Search Strategist + independent Search Peer Reviewer
  → parallel database/language Scouts
  → Screeners A/B → Adjudicator
  → Legal Full-text Acquisition + Full-text Verifier → XLSX pause if missing
  → Extraction A/B + Appraisal Specialist
  → Geospatial Analyst + Synthesis Methodologist + Certainty Agent
  → Contradiction/Gap Red Team
  → Outline Architect → Lead Writer
  → Citation + Figure/Table verification
  → NREE Architecture Editor + Scientific Reviewer + Journal Editor + Reproducibility Auditor
  → Revision → readiness gate
```

Agents write separate staging artifacts; one owner merges canonical data and one
Lead Writer controls the manuscript voice. Multiple AI agents are not represented
as independent human reviewers.

## Evidence architecture

The benchmark/task firewall remains strict:

| Corpus | Role | Scientific facts/citations in the new manuscript? |
|---|---|---|
| `benchmark_corpus/` | form, reasoning and writing priors | Never |
| `runs/<run-id>/` | searched, screened, extracted topic evidence | Yes |

The v4 entity model separates reports, underlying studies, sites/outcomes,
evidence units and claims. Every material sentence must trace through:

```text
claim → evidence unit → report/study/site → source locator
      → appraisal/dependence → verified citation → manuscript sentence
```

## Standards

The router applies the current relevant guidance and records version/access date:
PRISMA 2020/PRISMA-S, PRISMA-ScR, ROSES and CEE environmental-evidence guidance,
SWiM for synthesis without meta-analysis, and GRADE-CERQual when appropriate.
These improve conduct/reporting; citing a checklist never substitutes for doing the
work.

## Installation

```powershell
& "F:\pj311\.venv\Scripts\python.exe" -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Optional keys identify polite/high-quota API access. Secrets and raw copyrighted
full text remain git-ignored.

## Start an auditable run

Codex normally starts this automatically. The deterministic scaffold can also be
called directly:

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/review_scaffold.py init `
  --topic "Permafrost degradation and vegetation response on the Tibetan Plateau" `
  --language en --language zh --out-dir runs/permafrost-vegetation
```

Open discovery utilities currently provide executable `preflight`, `search`,
`sentinel-check`, `screen` and `snowball` commands through
`scripts/literature_review_pipeline.py`.
The remaining `/geo-review` actions are skill-orchestrated agent stages, not
misrepresented as standalone CLI commands.

## Search example

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/literature_review_pipeline.py search `
  --topic "Permafrost degradation and vegetation response on the Tibetan Plateau" `
  --keywords "permafrost degradation" vegetation NDVI "Tibetan Plateau" `
  --year-lo 2000 --year-hi 2026 --language en --max-papers 200 `
  --out-dir runs/permafrost-vegetation/search/open-discovery
```

Semantic Scholar and OpenAlex are open discovery layers; Crossref validates DOI
metadata. A formal systematic review additionally needs the field/grey/regional
sources in its frozen protocol. Open APIs alone are not treated as exhaustive.
The search command retrieves a candidate pool larger than the final paper cap so
that spreading work across several queries does not collapse each lane to only a
few records. `sentinel-check` blocks progression when the planned search misses too
many known eligible seed papers.

## Full-text acquisition and resume

After screening, populate `fulltext/acquisition-queue.csv` and run the bounded
lawful acquisition pass:

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/legal_fulltext_fetch.py `
  --run-dir runs/permafrost-vegetation
& "F:\pj311\.venv\Scripts\python.exe" scripts/missing_fulltext_gate.py `
  --run-dir runs/permafrost-vegetation
```

If the second command pauses the run, give the generated XLSX to the researcher.
After matching PDFs are placed in `fulltext/user_uploads/`, validate and resume:

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/resume_helper.py validate-pdf `
  --run-dir runs/permafrost-vegetation `
  --pdf runs/permafrost-vegetation/fulltext/user_uploads/R001.pdf `
        runs/permafrost-vegetation/fulltext/user_uploads/R002.pdf
```

## Readiness check

After the manuscript and supplements are assembled:

```powershell
& "F:\pj311\.venv\Scripts\python.exe" scripts/review_quality_gate.py `
  --run-dir runs/permafrost-vegetation
```

The verdict is one of:

- `SUBMISSION_CANDIDATE`
- `RESEARCH_DRAFT_NOT_READY`
- `INSUFFICIENT_EVIDENCE`

Hard failures include an empty/unverified citation manifest, unsupported claims or
figures, any included report without verified local full text, a failed NREE
architecture review, false systematic/global/causal labels,
hidden contradictions and automation described as human review.

## Tests

```powershell
$env:PYTHONUTF8=1
& "F:\pj311\.venv\Scripts\python.exe" -m unittest discover -s tests -v
& "F:\pj311\.venv\Scripts\python.exe" evals/run_scripted.py
```

## Limits and researcher responsibility

- Database coverage, subscriptions, API quotas and full-text rights constrain what
  the system can conclude.
- High-quality systematic review decisions and statistical/causal conclusions need
  accountable human/domain review before submission.
- The benchmark corpus is a writing/reasoning prior dominated by one journal
  family; task evidence and target-journal instructions always take precedence.
- Live Zotero Word fields are not scriptable through a stable public API; generated
  DOCX citations are static unless the researcher refreshes them in Zotero.

Code and prompts are MIT licensed. Review outputs belong to their authors.
