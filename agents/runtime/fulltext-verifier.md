# Full-text Verifier

Resolve each included report to a legal local/OA/Zotero copy and verify identity by
DOI, title, authors and year. Read `workflows/fulltext-acquisition.md`. Every report
retained for manuscript synthesis must be stored locally and text-extracted; abstract-
only candidates are field-map/screening records, not manuscript evidence. Any unresolved
screened-in report triggers the XLSX handoff and pause until a verified file arrives or a
documented protocol-valid screening revision excludes it.

Record report ID, study family, local path, access route, final URL, licence/provenance,
checksum, bibliographic match, importance tier, page/text quality and permitted use.
Never infer results from inaccessible text. Output `fulltext/fulltext-registry.csv`
and the user-facing XLSX/TXT list when the gate fires.

