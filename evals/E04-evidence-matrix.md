# E04 — Evidence Matrix Integrity
Fixture evidence-matrix-bad.csv contains seeded defects (duplicate evidence_id, missing source_location, invalid confidence).
Procedure: run integrity checks (run_scripted.py e04); validator must catch all seeded classes.
Pass: detection rate 100% on seeded defects.
