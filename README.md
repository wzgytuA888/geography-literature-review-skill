# Geography Literature Review Research Skill

Version 3 upgrades the project from a literature-discovery pipeline into a
protocol-first, multi-agent review system designed to produce a deeply synthesized,
fully auditable **submission candidate** when the evidence and access permit it.

Give the skill a research topic. It will frame the question, choose a defensible
review type, design and peer-review the search, screen and appraise studies, analyze
geographic/scale heterogeneity, synthesize claims with certainty ratings, draft the
article, verify citations and run independent scientific and reproducibility gates.

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

When only a topic is supplied, v3 defaults to a deep critical narrative review.
It records inferred scope and continues autonomously. It uses the word “systematic”
only when multi-source coverage, selection, appraisal and reporting gates justify it.

## What is new in v3

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
  → Search Strategist + independent Search Peer Reviewer
  → parallel database/language Scouts
  → Screeners A/B → Adjudicator
  → Extraction A/B + Full-text Verifier + Appraisal Specialist
  → Geospatial Analyst + Synthesis Methodologist + Certainty Agent
  → Contradiction/Gap Red Team
  → Outline Architect → Lead Writer
  → Citation + Figure/Table verification
  → Scientific Reviewer + Journal Editor + Reproducibility Auditor
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

The v3 entity model separates reports, underlying studies, sites/outcomes,
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
figures, missing conclusion-critical text, false systematic/global/causal labels,
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
