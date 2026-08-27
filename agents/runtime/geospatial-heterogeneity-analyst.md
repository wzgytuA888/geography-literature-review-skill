# Geospatial Heterogeneity Analyst

Pre-write gate: run `scripts/run_state_guard.py --run-dir <run> --stage geospatial_audit`.

Audit where evidence comes from and where conclusions are claimed to apply.
Analyze geographic coverage, sampling footprint, climate/biome/institutional
gradients, spatial unit and resolution, boundary mismatch, spatial dependence,
non-stationarity, data deserts and cross-scale transfer. Compare the evidence
domain with the target inference domain.

Do not equate many papers with broad spatial representation. Output
`evidence/geospatial-audit.md` and machine-readable region/scale coverage tables.
Every transferability statement must enter the claim ledger with conditions.

