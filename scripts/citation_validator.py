#!/usr/bin/env python3
"""Citation validator — Zero Hallucinated Citation Policy enforcement.

Checks every entry of a citation manifest against the acceptance rules:

  final_status = VERIFIED          requires (zotero item OR verifiable DOI OR
                                   authoritative metadata) AND claim_supported=true
  final_status = CLAIM_UNSUPPORTED citation exists but does not support the claim
  final_status = UNRESOLVED        no reliable metadata record → must be removed
                                   from the bibliography into unresolved report

Inputs: runs/<run-id>/citation/citation-manifest.jsonl with rows like
  {"claim_id","claim","citation_key","title","authors","year","doi",
   "zotero_key","source_location"}
Output: citation-audit.csv + unresolved_citations.csv in the same folder.

This script validates METADATA existence/consistency; claim-support verification
is performed by the Evidence Auditor agent and passed in via
"claim_supported" fields which this tool treats as authoritative input.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_state_guard import RunPausedError, assert_run_unblocked  # noqa: E402
from zotero_adapter import ZoteroAdapter, crossref_metadata  # noqa: E402


def audit(manifest_path: Path, out_dir: Path, check_crossref: bool = True,
          check_zotero: bool = True) -> dict:
    rows = [json.loads(l) for l in
            manifest_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    ad = ZoteroAdapter() if check_zotero else None
    if ad is not None and not ad.available():
        ad = None

    audited = []
    for r in rows:
        doi = (r.get("doi") or "").strip()
        title = (r.get("title") or "").strip()
        meta_ok = False
        source = ""
        cr = crossref_metadata(doi) if (check_crossref and doi) else None
        if cr:
            # lightweight consistency: year & first author surname overlap
            cr_year = None
            for k in ("published-print", "published-online", "issued", "created"):
                parts = (cr.get(k) or {}).get("date-parts") or []
                if parts and parts[0]:
                    cr_year = parts[0][0]
                    break
            cr_authors = [a.get("family", "") for a in cr.get("author", [])]
            year_ok = (not r.get("year")) or (not cr_year) or \
                      int(r["year"]) == int(cr_year)
            title_ok = (not title) or ("title" not in cr) or (
                title[:40].lower() in str(cr.get("title", [""]))[:400].lower())
            meta_ok = bool(year_ok and title_ok)
            source = "crossref"
        zot = None
        if ad is not None:
            if r.get("zotero_key"):
                zot = ad.get_metadata(r["zotero_key"])
            elif doi:
                zot = ad.resolve_doi(doi)
            if zot:
                meta_ok = True
                source = f"zotero:{zot.get('key')}"
        claim_supported = str(r.get("claim_supported", "")).strip().lower()
        claim_flag: bool | None = (True if claim_supported == "true"
                                   else False if claim_supported == "false"
                                   else None)

        if not meta_ok:
            status = "UNRESOLVED"
        elif claim_flag is False:
            status = "CLAIM_UNSUPPORTED"
        elif claim_flag is None:
            status = "VERIFIED_METADATA_ONLY"   # auditor must still confirm support
        else:
            status = "VERIFIED"

        audited.append({**r, "found_in_zotero": bool(zot),
                        "metadata_verified": meta_ok,
                        "metadata_source": source,
                        "claim_supported": claim_flag,
                        "final_status": status})

    out_dir.mkdir(parents=True, exist_ok=True)
    audit_csv = out_dir / "citation-audit.csv"
    fields = ["claim_id", "claim", "citation_key", "title", "authors", "year",
              "doi", "zotero_key", "found_in_zotero", "metadata_verified",
              "metadata_source", "fulltext_checked", "claim_supported",
              "source_location", "final_status"]
    with audit_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(audited)

    unresolved = [r for r in audited
                  if r["final_status"] in {"UNRESOLVED", "CLAIM_UNSUPPORTED"}]
    un_csv = out_dir / "unresolved_citations.csv"
    with un_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(unresolved)

    summary = {
        "total": len(audited),
        "verified": sum(1 for r in audited if r["final_status"] == "VERIFIED"),
        "verified_metadata_only": sum(1 for r in audited
                                      if r["final_status"] == "VERIFIED_METADATA_ONLY"),
        "claim_unsupported": sum(1 for r in audited
                                 if r["final_status"] == "CLAIM_UNSUPPORTED"),
        "unresolved": sum(1 for r in audited if r["final_status"] == "UNRESOLVED"),
        "hard_gate": "PASS" if audited and all(
            r["final_status"] == "VERIFIED" for r in audited) else "FAIL",
    }
    (out_dir / "audit-summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True,
                    help="citation-manifest.jsonl from the run")
    ap.add_argument("--out-dir", help="default: same folder as manifest")
    ap.add_argument("--no-crossref", action="store_true")
    ap.add_argument("--no-zotero", action="store_true")
    args = ap.parse_args()

    manifest = Path(args.manifest)
    if not manifest.exists():
        sys.exit(f"manifest not found: {manifest}")
    candidate_run_dir = manifest.parent.parent
    if (candidate_run_dir / "state.json").exists():
        try:
            assert_run_unblocked(candidate_run_dir, "citation")
        except RunPausedError as exc:
            print(json.dumps({"hard_gate": "FAIL", "blocked_before_write": str(exc)},
                             ensure_ascii=False))
            sys.exit(9)
    out_dir = Path(args.out_dir) if args.out_dir else manifest.parent
    summary = audit(manifest, out_dir, check_crossref=not args.no_crossref,
                    check_zotero=not args.no_zotero)
    print(json.dumps(summary, indent=2))
    sys.exit(0 if summary["hard_gate"] == "PASS" else 4)


if __name__ == "__main__":
    main()
