# Reporting Standards Router

Standards are reporting/conduct aids, not badges. Record the selected standard,
version, applicable items, deviations and location of each item in
`reporting/checklist.md`.

| Review/output | Primary framework | Use when |
|---|---|---|
| Systematic review | PRISMA 2020 + PRISMA-S | reproducible exhaustive search and eligibility workflow |
| Scoping review | PRISMA-ScR + PRISMA-S | map concepts, evidence types and gaps rather than estimate one answer |
| Environmental evidence review/map | ROSES + CEE Guidelines v5.1 | environment, conservation or management evidence synthesis |
| Quantitative synthesis without meta-analysis | SWiM | effect data are too heterogeneous for valid meta-analysis |
| Qualitative evidence synthesis | explicit QES method; GRADE-CERQual if applicable | synthesized qualitative findings and confidence |
| Narrative/conceptual/methodological | SANRA-inspired transparency plus this skill's protocol | exhaustive systematic claims are not intended |
| Bibliometric | reproducible database/query/export and analytic workflow | network/productivity/topic structure is itself the object |

Primary sources and access dates belong in the method log:

- PRISMA 2020: https://www.prisma-statement.org/prisma-2020
- PRISMA-S: https://www.prisma-statement.org/prisma-search
- ROSES: https://www.roses-reporting.com/
- CEE Guidelines v5.1: https://collaborationenvironmentalevidence.github.io/CEE_guidelines/
- SWiM: https://doi.org/10.1136/bmj.l6890
- GRADE-CERQual: https://www.cerqual.org/
- CEE AI reporting guidance: https://environmentalevidence.org/artificial-intelligence-reporting-guidance/

## Hard interpretation rules

- PRISMA describes transparent reporting; citing PRISMA does not repair an
  incomplete search, biased screening or inappropriate synthesis.
- Open discovery APIs alone rarely justify the word “exhaustive.” State database
  coverage limits and downgrade the review label when necessary.
- A flow diagram count must be computed from the registry/deduplication/screening
  tables, never estimated from prose.
- Search updates are required for a submission candidate when the last search is
  stale relative to a fast-moving field; record the update date and new records.
- Report automation/AI use according to the target journal, including which
  stages were automated and what was independently checked. Record system/model,
  version, developer, purpose, prompts/contracts, parameters, inputs/outputs,
  agreement/validation, errors, limitations, privacy/copyright and human sign-off.
