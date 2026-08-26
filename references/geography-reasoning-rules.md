# Geography Reasoning Rules (conditional)

> HOW these rules work: the runtime checks the LEFT column against its task
> evidence. Only when a condition is met — and the evidence requirement is
> satisfiable — may the corresponding spatial interpretation enter the manuscript.
> Never insert the vocabulary to sound geographic. Consolidated corpus evidence:
> `benchmark_corpus/geography-reasoning-patterns.md`.

Rule format per spec §8:

```yaml
- id: GR1
  condition: same process yields divergent results across regions
  diagnostic_question: Do places differ in a stated mechanism, or only in outcomes?
  evidence_requirement: ≥2 regions compared + a named differentiating mechanism
    (climate regime, institutional setting, data coverage…)
  possible_interpretation: regional differentiation / place dependence
  when_not_to_use: differences explained by method/data heterogeneity alone
  example_pattern: benchmark docs compare belts/environments before claiming regionality
  confidence: high        # set by consolidator from corpus frequency
```

## Seed rule set (populated & frequency-scored during consolidation)

| id | Condition (evidence situation) | Interpretation family |
| --- | --- | --- |
| GR1 | Divergent results by region + known differentiating mechanism | regional differentiation / context dependence |
| GR2 | Results shift with spatial unit size or zoning | scale dependence / MAUP-type artifact check |
| GR3 | Neighboring units systematically correlated beyond chance | spatial dependence / autocorrelation |
| GR4 | Causes and effects separated across regions (production↔consumption, emission↔impact) | flow / telecoupling-type linkage |
| GR5 | Same policy/intervention, different local outcomes | place dependence / institutional context |
| GR6 | Coupled spheres (land–water–atmosphere–ocean) respond jointly | cross-sphere human–environment interaction |
| GR7 | Evidence density itself differs sharply by geography (data deserts) | geographic data imbalance — usable AS gap evidence |
| GR8 | Mechanisms differ across climatic/physical belts | environment-gradient explanation |

## Usage discipline at runtime
1. Scan synthesis notes for conditions; log which rules fired and on which
   evidence_ids.
2. Write the geographic reading ONLY with cited evidence for both outcome pattern
   AND differentiating mechanism.
3. Prefer enacting the reasoning over naming jargon; introduce a term once, with
   definition, if load-bearing.
4. If no rule fires, the review simply is not spatially framed that day — fine.

Named places calibrate examples but never organize the argument by themselves.
