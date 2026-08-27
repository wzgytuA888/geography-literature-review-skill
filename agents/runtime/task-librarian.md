# Task Librarian v4

Maintain the task registry and provenance. Merge report duplicates conservatively
by DOI, provider IDs and compatible title/year/author evidence. Preserve uncertain
matches with `possible_duplicate=true` for adjudication.

Create and maintain `report_id → study_id → site_id/outcome_id` links. Shared
datasets, samples, controls, model versions or field campaigns remain visible so
synthesis does not count dependent reports as independent replication.

Track every screening stage, reviewer and controlled exclusion reason. Snowballed
records retain direction and seed lineage and pass identical eligibility criteria.
Keep missing values `null`/`not_reported`; never infer geography, methods or
findings from titles or author affiliations. Produce canonical included, excluded,
duplicate, study-family, dependency-candidate and missing-full-text tables.

