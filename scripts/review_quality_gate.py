#!/usr/bin/env python3
"""Deterministic integrity checks for a v4 review package."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path

import yaml

from resume_helper import MIN_READABLE_ALNUM_CHARS, identity_from_content, inspect_pdf


def csv_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def jsonl_rows(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip()]


def audit(run_dir: Path) -> dict:
    blockers: list[str] = []
    majors: list[str] = []
    required = [
        "state.json", "protocol/protocol.yaml", "search/search-plan.yaml",
        "search/search_log.csv", "screening/adjudicated.csv",
        "fulltext/fulltext-registry.csv",
        "evidence/evidence-units.csv", "appraisal/study-appraisal.csv",
        "appraisal/dependency-map.csv", "evidence/claim-ledger.csv",
        "evidence/certainty-profile.csv", "evidence/geospatial-audit.md",
        "writing/manuscript.md",
        "citation/citation-manifest.jsonl", "citation/citation-audit.csv",
        "citation/audit-summary.json", "reporting/agent-manifest.csv",
        "reporting/checklist.md", "evaluation/contradiction-and-gap-audit.md",
        "evaluation/reproducibility-report.md",
    ]
    for rel in required:
        if not (run_dir / rel).exists():
            blockers.append(f"missing required artifact: {rel}")

    protocol_path = run_dir / "protocol/protocol.yaml"
    if protocol_path.exists():
        protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8")) or {}
        if not str(protocol.get("primary_question") or "").strip():
            blockers.append("protocol primary question is not defined")
        contribution = protocol.get("contribution") or {}
        if not str(contribution.get("this_review_adds") or "").strip():
            majors.append("protocol contribution test is incomplete")
        if not protocol.get("frozen_at"):
            blockers.append("protocol is not frozen")

    search_plan_path = run_dir / "search/search-plan.yaml"
    if search_plan_path.exists():
        search_plan = yaml.safe_load(search_plan_path.read_text(encoding="utf-8")) or {}
        if not search_plan.get("sources"):
            blockers.append("source plan has no executed sources")
        peer = search_plan.get("peer_review") or {}
        if str(peer.get("status") or "").lower() not in {"pass", "passed"}:
            blockers.append("independent search peer review has not passed")
        sentinel = search_plan.get("sentinel_recall") or {}
        sentinel_status = str(sentinel.get("status") or "").lower()
        total = int(sentinel.get("total") or 0)
        retrieved = int(sentinel.get("retrieved") or 0)
        if sentinel_status not in {"pass", "passed", "not_available"}:
            blockers.append("sentinel recall gate has not passed")
        elif sentinel_status == "not_available" and not str(
                sentinel.get("rationale_if_unavailable") or "").strip():
            blockers.append("sentinel set unavailable without rationale")
        elif total and retrieved / total < 0.8:
            blockers.append("sentinel recall is below 0.80")

    screening = csv_rows(run_dir / "screening/adjudicated.csv")
    if not screening:
        blockers.append("adjudicated screening table has no decisions")

    claims = csv_rows(run_dir / "evidence/claim-ledger.csv")
    if not claims:
        blockers.append("claim ledger has no material claims")
    else:
        for row in claims:
            cid = row.get("claim_id") or "<missing-id>"
            if not (row.get("supporting_evidence_ids") or "").strip():
                blockers.append(f"{cid}: no supporting evidence IDs")
            if not (row.get("verified_citation_keys") or "").strip():
                blockers.append(f"{cid}: no verified citation keys")
            if (row.get("certainty") or "").strip() not in {
                    "very_low", "low", "moderate", "high"}:
                blockers.append(f"{cid}: invalid or missing certainty")

    evidence = csv_rows(run_dir / "evidence/evidence-units.csv")
    if not evidence:
        blockers.append("evidence-unit table is empty")
    for row in evidence:
        eid = row.get("evidence_id") or "<missing-id>"
        if not (row.get("source_location") or "").strip():
            blockers.append(f"{eid}: missing source location")
        if (row.get("extraction_basis") or "") == "abstract_limited" and (
                row.get("claim_type") or "") in {"causal_effect", "mechanism"}:
            blockers.append(f"{eid}: abstract-limited evidence used for detailed claim")

    manifest = jsonl_rows(run_dir / "citation/citation-manifest.jsonl")
    if not manifest:
        blockers.append("citation manifest is empty")
    citations = csv_rows(run_dir / "citation/citation-audit.csv")
    for row in citations:
        if row.get("final_status") != "VERIFIED":
            blockers.append(f"citation not verified: {row.get('citation_key') or row.get('doi')}")
        if str(row.get("claim_supported") or "").lower() != "true":
            blockers.append(f"citation support not confirmed: {row.get('claim_id')}")
    summary_path = run_dir / "citation/audit-summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        if summary.get("hard_gate") != "PASS" or not summary.get("total"):
            blockers.append("citation audit hard gate did not pass")

    fulltexts = csv_rows(run_dir / "fulltext/fulltext-registry.csv")
    if not fulltexts:
        blockers.append("full-text registry is empty")
    available = {"AVAILABLE_LOCAL", "AVAILABLE_ZOTERO", "DOWNLOADED_LEGAL"}
    verified_identity = {"true", "1", "yes", "verified", "verified_automatic",
                         "verified_manual", "pass", "passed"}
    accepted_text_quality = {"acceptable", "good"}
    fulltext_by_report = {row.get("report_id"): row for row in fulltexts}
    screening_by_report = {
        row.get("report_id") or row.get("record_id"): row for row in screening}
    included_reports = {
        row.get("report_id") or row.get("record_id")
        for row in screening
        if (row.get("decision") or "").lower() in {"include", "included"}
        or (row.get("screening_status") or "") in {
            "INCLUDED", "INCLUDED_PENDING_FULLTEXT", "HIGH_PRIORITY_PENDING_FULLTEXT"}
        or str(row.get("include") or "").lower() in {"true", "1", "yes"}
    }
    for report_id in sorted(r for r in included_reports if r):
        row = fulltext_by_report.get(report_id)
        if not row or row.get("fulltext_status") not in available:
            blockers.append(f"included report lacks verified local full text: {report_id}")
        elif not (row.get("local_path") or "").strip() or not (row.get("sha256") or "").strip():
            blockers.append(f"included report lacks local path/checksum: {report_id}")
        elif str(row.get("identity_verified") or "").strip().casefold() not in verified_identity:
            blockers.append(f"included report identity is not verified: {report_id}")
        elif not (row.get("identity_basis") or "").strip():
            blockers.append(f"included report lacks content-based identity evidence: {report_id}")
        elif str(row.get("text_quality") or "").strip().casefold() not in accepted_text_quality:
            blockers.append(f"included report full text is not readable: {report_id}")
        elif not str(row.get("page_count") or "").strip().isdigit() or int(row["page_count"]) < 1:
            blockers.append(f"included report page count is not verified: {report_id}")
        elif not (row.get("extracted_text_path") or "").strip():
            blockers.append(f"included report lacks extracted local text: {report_id}")
        else:
            local_path = Path(row["local_path"])
            if not local_path.is_absolute():
                local_path = run_dir / local_path
            if not local_path.is_file():
                blockers.append(f"included report local full text does not exist: {report_id}")
            else:
                actual_sha256 = hashlib.sha256(local_path.read_bytes()).hexdigest()
                if actual_sha256.casefold() != row["sha256"].strip().casefold():
                    blockers.append(f"included report checksum mismatch: {report_id}")
                if local_path.suffix.casefold() == ".pdf" or local_path.read_bytes()[:5] == b"%PDF-":
                    inspection = inspect_pdf(local_path)
                    if not inspection.get("ok"):
                        blockers.append(f"included report PDF has no readable full text: {report_id}")
                    elif int(row.get("page_count") or 0) != int(inspection.get("page_count") or 0):
                        blockers.append(f"included report page-count verification mismatch: {report_id}")
                    elif str(row.get("identity_verified") or "").strip().casefold() == "verified_automatic":
                        identity_row = {**screening_by_report.get(report_id, {}), **row}
                        matched, _, basis = identity_from_content(
                            identity_row, inspection.get("text", ""),
                            inspection.get("metadata_text", ""))
                        if not matched or basis != row.get("identity_basis"):
                            blockers.append(
                                f"included report automatic identity cannot be reproduced: {report_id}")
            text_path = Path(row["extracted_text_path"])
            if not text_path.is_absolute():
                text_path = run_dir / text_path
            if not text_path.is_file():
                blockers.append(f"included report extracted text does not exist: {report_id}")
            else:
                extracted = text_path.read_text(encoding="utf-8", errors="ignore")
                if sum(ch.isalnum() for ch in extracted) < MIN_READABLE_ALNUM_CHARS:
                    blockers.append(f"included report extracted text is too sparse: {report_id}")
    for row in fulltexts:
        if (row.get("importance_tier") or "").lower() in {"critical", "seminal"} and (
                row.get("fulltext_status") or "") not in available:
            blockers.append(f"conclusion-critical full text missing: {row.get('report_id')}")

    supported_ids = {
        item for claim in claims
        for item in (claim.get("supporting_evidence_ids") or "").split(";") if item
    }
    for row in evidence:
        if (row.get("evidence_id") or "") in supported_ids and (
                row.get("extraction_basis") or "").lower() in {
                    "abstract", "abstract_limited", "partial_abstract"}:
            blockers.append(f"manuscript claim relies on abstract-only evidence: {row.get('evidence_id')}")

    manuscript_path = run_dir / "writing/manuscript.md"
    if manuscript_path.exists():
        manuscript = manuscript_path.read_text(encoding="utf-8", errors="ignore")
        if len(manuscript.strip()) < 3000:
            majors.append("manuscript is too short to assess as a full review")
        if re.search(r"<CITE\b|\bTODO\b|\bTBD\b", manuscript, re.I):
            blockers.append("manuscript contains unresolved placeholders")

    if protocol_path.exists():
        profile = str(protocol.get("writing_profile") or "").lower()
        if profile == "nree":
            nree_report = run_dir / "evaluation/nree-architecture-report.md"
            nree_gate_path = run_dir / "evaluation/nree-architecture-gate.yaml"
            if not nree_report.exists():
                blockers.append("missing NREE architecture review")
            elif not re.search(r"\bPASS\b", nree_report.read_text(encoding="utf-8", errors="ignore")):
                blockers.append("NREE architecture review has not passed")
            if not nree_gate_path.exists():
                blockers.append("missing NREE architecture gate")
            else:
                nree_gate = yaml.safe_load(nree_gate_path.read_text(encoding="utf-8")) or {}
                if str(nree_gate.get("status") or "").lower() not in {"pass", "passed"}:
                    blockers.append("NREE architecture gate status is not PASS")
                if int(nree_gate.get("score_total") or 0) < 80:
                    blockers.append("NREE architecture score is below 80")
                if nree_gate.get("hard_blockers"):
                    blockers.append("NREE architecture gate has hard blockers")

    appraisal = csv_rows(run_dir / "appraisal/study-appraisal.csv")
    if not appraisal:
        blockers.append("design-matched appraisal table is empty")
    certainty = csv_rows(run_dir / "evidence/certainty-profile.csv")
    if not certainty:
        blockers.append("certainty profile is empty")
    agents = csv_rows(run_dir / "reporting/agent-manifest.csv")
    roles = {re.sub(r"[^a-z]", "", (row.get("role") or "").casefold()) for row in agents}
    for required_role in {"searchpeerreviewer", "criticalappraisalspecialist",
                          "geospatialheterogeneityanalyst", "contradictionandgapredteam",
                          "reproducibilityauditor"}:
        if required_role not in roles:
            blockers.append(f"required independent role missing from agent manifest: {required_role}")
    if protocol_path.exists() and str(protocol.get("writing_profile") or "").lower() == "nree":
        if "nreearchitectureeditor" not in roles:
            blockers.append("required independent role missing from agent manifest: nreearchitectureeditor")

    verdict = "SUBMISSION_CANDIDATE" if not blockers and not majors else (
        "RESEARCH_DRAFT_NOT_READY" if claims or manuscript_path.exists()
        else "INSUFFICIENT_EVIDENCE")
    return {"verdict": verdict, "blockers": sorted(set(blockers)),
            "majors": sorted(set(majors)), "hard_gate": "PASS" if not blockers else "FAIL"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out")
    args = ap.parse_args()
    run_dir = Path(args.run_dir)
    result = audit(run_dir)
    out = Path(args.out) if args.out else run_dir / "evaluation/readiness.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["verdict"] == "SUBMISSION_CANDIDATE" else 6


if __name__ == "__main__":
    raise SystemExit(main())
