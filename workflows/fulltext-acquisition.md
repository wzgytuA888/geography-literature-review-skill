# Workflow: Legal local full text before synthesis

The manuscript evidence base is full-text-only. Abstracts may support orientation,
deduplication and screening but never a scientific claim in the draft.

## Local storage contract

For every screened-in report create:

- `fulltext/pdfs/<report_id>_<safe-name>.pdf` or an identity-verified HTML file;
- `fulltext/text/<report_id>.txt` extracted from that local source;
- one registry row with DOI/title/authors/year match, acquisition route, final URL,
  access date, licence/provenance, SHA-256, page count/text quality and permitted use.

Do not draft from a remote landing page while claiming local full-text verification.

## Lawful acquisition order

1. user-provided project folders and Zotero attachments;
2. API-declared open-access PDF locations from OpenAlex/Semantic Scholar;
3. Unpaywall (when configured), publisher open-access PDF/HTML and Crossref licence links;
4. recognized repositories and author manuscripts: PubMed Central/Europe PMC, arXiv,
   EarthArXiv, ESSOAr, Zenodo, HAL, institutional repositories and author-hosted accepted
   manuscripts;
5. the user's institutional link resolver, library document delivery/interlibrary loan,
   or an author-copy request.

Use bounded retries, cache successful files and verify `%PDF`, readable pages and
bibliographic identity. A DOI resolving to a paywall is not a successful acquisition.
Never bypass authentication, paywalls, access controls or robots restrictions; never use
Sci-Hub, pirate repositories or credential-sharing services.

## Missing-full-text gate

After the acquisition pass, every `include` decision without verified local full text is
blocking. Generate `missing_fulltext_literature.xlsx` and TXT with one row per missing
report: priority, title, authors, year, journal, DOI, publisher URL, attempted legal routes,
failure reason, why it matters, claim/section need, expected filename, exact upload folder,
recommended action and user decision fields.

Set `PAUSED_WAITING_FOR_USER_FULLTEXT`, deliver the XLSX to the user and stop extraction,
appraisal, gap finalization, synthesis, outline, drafting and final citation work. Resume
only after `resume_helper.py validate-pdf` verifies the supplied files, or after the user
documents a protocol-valid screening revision showing that a report was incorrectly
included. Do not use a “skip” flag to bypass an included missing report.

Give the user this exact default recovery command with the run path filled in:

```text
python scripts/resume_helper.py validate-pdf --run-dir "<absolute-run-directory>"
```

With no `--pdf` argument, the command scans `fulltext/user_uploads/*.pdf`. Explicit
paths remain available as `--pdf <file1.pdf> <file2.pdf>`. `user_uploads` is only an
inbox; a validated canonical copy is stored in `fulltext/pdfs/`. A PDF clears the gate only
when it is parseable, contains sufficient extractable text and matches either the DOI
in PDF metadata/front matter (never a reference-list-only DOI), or the title plus
author/year in PDF content. A matching filename is
never identity evidence. Blank, damaged, encrypted, and scanned-without-OCR files remain
blocking. Successful validation records checksum, page count, text quality, identity
basis and `fulltext/text/<report_id>.txt`; it then archives the resolved pause metadata
to `pause_history` and resumes at extraction.
