# E17 — Runtime Resume From Checkpoint
Kill a run mid-stage-3 (simulated by truncating state.json stage marker), then resume. Expect artifacts replayed, no duplicate search-log rows, stage continues at next step.
Pass: duplicate searches = 0; state consistent.
