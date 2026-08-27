#!/usr/bin/env python3
"""Deterministic integrity checks for a v3 review package."""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import yaml


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
    available = {"AVAILABLE_LOCAL", "AVAILABLE_ZOTERO", "DOWNLOADED_LEGAL", "OPEN_ACCESS_FOUND"}
    for row in fulltexts:
        if (row.get("importance_tier") or "").lower() in {"critical", "seminal"} and (
                row.get("fulltext_status") or "") not in available:
            blockers.append(f"conclusion-critical full text missing: {row.get('report_id')}")

    manuscript_path = run_dir / "writing/manuscript.md"
    if manuscript_path.exists():
        manuscript = manuscript_path.read_text(encoding="utf-8", errors="ignore")
        if len(manuscript.strip()) < 3000:
            majors.append("manuscript is too short to assess as a full review")
        if re.search(r"<CITE\b|\bTODO\b|\bTBD\b", manuscript, re.I):
            blockers.append("manuscript contains unresolved placeholders")

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
