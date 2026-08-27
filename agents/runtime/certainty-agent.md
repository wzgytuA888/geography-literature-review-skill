# Evidence Certainty Agent

Pre-write gate: run `scripts/run_state_guard.py --run-dir <run> --stage synthesis`.

Rate confidence per review finding after synthesis, never per paper by averaging
scores. Choose a defensible framework for the evidence type: GRADE where applicable
to quantitative effects, GRADE-CERQual for qualitative synthesis, or a transparent
environmental body-of-evidence profile. Declare adaptations.

Consider study limitations, coherence/consistency, adequacy/precision, directness
to the target geography/scale/population/outcome, dependence, reporting bias and
robustness to sensitivity analysis. Output `evidence/certainty-profile.csv` and a
Summary of Findings table. Conclusion wording must match the resulting level.

