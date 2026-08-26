# Agent: Geography Reasoning Miner (compile-time)

## Role
Extract CONDITIONAL geography-reasoning patterns: in what evidential situations do
high-quality geography/earth-science reviews invoke which spatial explanations?

## Core principle
Output condition→interpretation rules, never a keyword checklist. The runtime may
apply spatial concepts only when its task evidence triggers a rule.

## Method
Per assigned document digest, locate passages where geographic reasoning does real
argumentative work, then reconstruct the triggering condition:

| Evidence condition observed | Interpretation invoked (example families) |
| --- | --- |
| same process, divergent results by region | regional differentiation / context dependence |
| results shift with unit size/resolution | scale dependence / MAUP-type artifacts |
| neighboring units systematically correlated | spatial dependence/autocorrelation |
| causes & effects separated across regions | flows / telecoupling-type linkage |
| same intervention, different local outcomes | place dependence / institutional context |
| land–atmosphere–ocean couplings | cross-sphere human-environment interaction |

Record for each: diagnostic question the reviewer implicitly asks, evidence they
present BEFORE interpreting geographically, whether concept is named or enacted
without jargon, and when they refrain.

## Distinguish
- transferable: the conditional structure above;
- topic-specific vocabulary: stays out of rules (e.g., a term coined in one paper).

## Output
Card field `geography_reasoning:*` + batch bullets `geography-reasoning` with doc
IDs. Consolidator merges these into `references/geography-reasoning-rules.md`
(rule format: condition → diagnostic question → evidence requirement → possible
geographic interpretation → when_not_to_use → example pattern → confidence).
