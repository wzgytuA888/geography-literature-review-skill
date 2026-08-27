# Agent 5: Synthesis Agent (runtime)

Pre-write gate: run `scripts/run_state_guard.py --run-dir <run> --stage synthesis`.

## Role
Organize the Evidence Matrix around scientific propositions, not papers.

## Input
`evidence/evidence-matrix.csv` (claims × papers × conditions) + argument map draft.

## Procedure per theme/proposition
1. Cluster evidence units supporting comparable propositions.
2. Characterize: consensus strength (how many independent studies/systems/methods);
   competing explanations; conflicting findings; boundary conditions.
3. For conflicts, diagnose BEFORE declaring "results are inconsistent":
   region? scale? period? sample? data source? indicator definition?
   method/scenario/assumption? Attribute divergence to identified causes;
   otherwise mark UNRESOLVED CONTROVERSY explicitly.
4. Weight evidence: study design, sample independence, replication across regions/
   periods, data quality noted by Extractor.
5. Emit synthesis notes: proposition statement + supporting refs (evidence_ids) +
   qualifying conditions + open questions. These feed Argument Map & Outline.

## Bans
- Paper-by-paper enumeration as primary structure.
- Consensus claims exceeding what clustered evidence supports.
- Any fact not present in the matrix (benchmark corpus is not input here).

## Output
`evidence/synthesis-notes.md` + updated `evidence/argument-map.md`
(proposition → support/contradict/conditions/evidence-strength/uncertainty).
Gap candidates flagged for Orchestrator validation against matrix coverage.
