# Multi-agent Orchestration

Use roles as independent cognitive passes, not decorative names. If the host has
few agent slots, execute the same contracts in waves. The Orchestrator alone owns
`state.json` and merges authoritative artifacts.

Before dispatching any extraction, appraisal, analysis, outline, drafting,
citation, figure, review or packaging role, the Orchestrator and the worker must
both run `scripts/run_state_guard.py --run-dir <run> --stage <stage>`. Exit code 9
is a hard pre-write stop. A prose instruction to pause is not a substitute for
this guard.

On a host with collaboration/subagent tools, the Orchestrator must actually spawn,
wait for and record the required independent roles. Merely reading the role files
or simulating all voices in one uninterrupted drafting pass does not satisfy the
multi-agent contract. Each dispatch/result enters `reporting/agent-manifest.csv`.

## Wave plan

| Wave | Parallel roles | Merge/gate |
|---|---|---|
| 0 Orientation | Research Landscape Cartographer when topic is broad | 3-5 direction cards; user scope choice or pause |
| 1 Framing | Protocol Architect; Domain/Mechanism Theorist | selected question, scope and provisional contribution agree |
| 2 Search design | Search Strategist; Search Peer Reviewer | PRESS-style query critique closed before final search |
| 3 Discovery | Scouts split by database/query family/language | normalized registry + complete Search Log |
| 4 Selection | Screeners A/B | Adjudicator resolves conflicts; agreement and exclusions logged |
| 5 Full text | Legal Acquisition Agent; Full-text Verifier | every included report local/verified or XLSX pause |
| 6 Evidence | Extraction A/B; Appraisal Specialist | critical fields and sampled evidence units double-checked |
| 7 Analysis | Synthesis Specialist; Geospatial Analyst; Quant/Qual Specialist | claim ledger + dependency map + certainty profile |
| 8 Challenge | Contradiction Red Team; Gap Auditor | rival explanations and negative/disconfirming evidence handled |
| 9 Manuscript | Outline Architect; Figure Agent; section writers where safe | NREE blueprint; Lead Writer unifies voice and freezes content |
| 10 Integrity | Citation Verifier; Figure/Table Agent | all claims and visual data have local provenance |
| 11 Review | NREE Architecture Editor; Scientific Reviewer; Journal Editor; Reproducibility Auditor | independent findings merged into revision ledger |

## Artifact ownership

- Workers write only to their assigned staging file, e.g.
  `search/scout-openalex.json` or `screening/reviewer-a.csv`.
- The Orchestrator or named merger writes the canonical registry/matrix/ledger.
- Never let parallel section writers invent cross-section claims. Give each writer
  a frozen evidence cluster and claim IDs; Lead Writer controls transitions,
  terminology and conclusion strength.
- Reviewer, Red Team and Auditor must not edit the manuscript. They report defects;
  the Revision Agent applies fixes and records each disposition.

## Independence and conflict resolution

Independent means the second pass does not see the first pass's decision before
making its own. After both are frozen, the Adjudicator sees record, criteria and
both rationales. It selects a decision with a written reason; it does not average
confidence scores. Persistent ambiguity is included at screening and resolved at
full text.

Agents are not human reviewers. Report automation truthfully as “two independent
AI-assisted passes” unless actual people performed the decisions.

## Minimum-role fallback

When only one agent is available, preserve role separation through fresh passes:

1. freeze the artifact;
2. clear writer-oriented notes from the review input;
3. apply the independent role rubric;
4. write findings to a separate file;
5. revise only after the critique is complete.

Never omit Search Peer Review, Full-text Verification, Appraisal, Geospatial Audit,
Contradiction Red Team, Citation Verification, NREE Architecture Review (for that
profile) or Reproducibility Audit from a near-submission run.

## Stop/escalate rules

- Search strategy rejected twice: narrow/reframe the question or ask for database
  access; do not endlessly expand queries.
- Screening disagreement remains after full text: include for sensitivity analysis
  and flag uncertainty.
- Any screened-in full text unavailable after lawful acquisition: deliver the XLSX,
  pause and request it; do not draft an abstract-supported workaround.
- Evidence certainty low/very low for the primary claim: deliver a qualified
  conclusion or evidence-map framing, not a confident review verdict.
- Any reviewer alleges unsupported text: the claim ledger, not majority vote,
  decides whether the sentence is retained.
