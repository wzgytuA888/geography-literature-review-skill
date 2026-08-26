# E16 — Incremental Benchmark Fold-in
Add synthetic new review B061 (fixture PDF); run update workflow. Expect: only new doc processed; existing pattern files get frequency bumps not rewrites; CHANGELOG entry written.
Pass: no full reprocessing signal (mtimes/diff scope), CHANGELOG updated.
