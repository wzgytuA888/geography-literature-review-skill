from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO / "src"))

from citation_validator import audit as citation_audit
from literature_review_pipeline import allocate_per_query_limit, run_sentinel_check
from review_quality_gate import audit as quality_audit
from review_scaffold import init_run, slugify


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class V3IntegrityTests(unittest.TestCase):
    def test_search_budget_keeps_recall_pool(self):
        self.assertEqual(allocate_per_query_limit(60, 8, 2, 4.0), 15)
        self.assertEqual(allocate_per_query_limit(60, 8, override=30), 30)

    def test_release_version_is_consistent(self):
        skill = (REPO / "SKILL.md").read_text(encoding="utf-8")
        citation = (REPO / "CITATION.cff").read_text(encoding="utf-8")
        from geo_review import __version__
        self.assertIn("version: 3.0.0", skill)
        self.assertIn("version: 3.0.0", citation)
        self.assertEqual(__version__, "3.0.0")

    def test_chinese_slug_is_preserved(self):
        self.assertIn("水资源", slugify("全球 水资源：综述"))

    def test_scaffold_records_verbatim_topic_and_mode(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "run"
            args = argparse.Namespace(topic="青藏高原冻土与植被响应", out_dir=str(out),
                                      mode="critical_narrative", language=["zh", "en"],
                                      target_journal=None)
            self.assertEqual(init_run(args), 0)
            protocol = yaml.safe_load((out / "protocol/protocol.yaml").read_text(encoding="utf-8"))
            self.assertEqual(protocol["topic_verbatim"], args.topic)
            self.assertEqual(protocol["scope"]["languages"], ["zh", "en"])
            self.assertTrue((out / "reporting/agent-manifest.csv").exists())

    def test_empty_citation_manifest_fails_hard_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            manifest = root / "citation-manifest.jsonl"
            manifest.write_text("", encoding="utf-8")
            summary = citation_audit(manifest, root, check_crossref=False, check_zotero=False)
            self.assertEqual(summary["total"], 0)
            self.assertEqual(summary["hard_gate"], "FAIL")

    def test_sentinel_recall_is_a_hard_gate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            literature = root / "literature.json"
            literature.write_text(json.dumps([
                {"report_id": "R1", "title": "Urban expansion and surface warming", "doi": "10.1/a"}
            ]), encoding="utf-8")
            sentinels = root / "sentinels.json"
            sentinels.write_text(json.dumps([
                {"title": "Urban expansion and surface warming", "doi": "10.1/a"},
                {"title": "A missing sentinel", "doi": "10.1/b"}
            ]), encoding="utf-8")
            args = argparse.Namespace(input=str(literature), sentinels=str(sentinels),
                                      minimum_recall=0.8, title_threshold=0.9,
                                      out=str(root / "sentinel-recall.json"))
            self.assertEqual(run_sentinel_check(args), 8)
            report = json.loads((root / "sentinel-recall.json").read_text(encoding="utf-8"))
            self.assertEqual(report["recall"], 0.5)
            self.assertEqual(report["hard_gate"], "FAIL")

    def test_quality_gate_accepts_complete_synthetic_package(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for rel in ["search/search_log.csv", "appraisal/dependency-map.csv",
                        "reporting/checklist.md",
                        "evidence/geospatial-audit.md",
                        "evaluation/contradiction-and-gap-audit.md",
                        "evaluation/reproducibility-report.md"]:
                path = root / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("x\n", encoding="utf-8")
            (root / "state.json").write_text("{}", encoding="utf-8")
            (root / "protocol").mkdir(parents=True, exist_ok=True)
            (root / "protocol/protocol.yaml").write_text(yaml.safe_dump({
                "primary_question": "What is the effect?", "frozen_at": "2026-08-27",
                "contribution": {"this_review_adds": "A spatially explicit synthesis"}}), encoding="utf-8")
            (root / "search").mkdir(parents=True, exist_ok=True)
            (root / "search/search-plan.yaml").write_text(yaml.safe_dump({
                "sources": [{"database": "OpenAlex"}],
                "peer_review": {"status": "passed"},
                "sentinel_recall": {"status": "passed", "retrieved": 4, "total": 4}}), encoding="utf-8")
            write_csv(root / "screening/adjudicated.csv", ["report_id", "decision"],
                      [{"report_id": "R1", "decision": "include"}])
            write_csv(root / "fulltext/fulltext-registry.csv",
                      ["report_id", "importance_tier", "fulltext_status"],
                      [{"report_id": "R1", "importance_tier": "critical", "fulltext_status": "AVAILABLE_LOCAL"}])
            write_csv(root / "appraisal/study-appraisal.csv",
                      ["report_id", "domain", "judgment"],
                      [{"report_id": "R1", "domain": "sampling", "judgment": "low"}])
            write_csv(root / "reporting/agent-manifest.csv", ["role"], [
                {"role": "Search Peer Reviewer"},
                {"role": "Critical Appraisal Specialist"},
                {"role": "Geospatial Heterogeneity Analyst"},
                {"role": "Contradiction and Gap Red Team"},
                {"role": "Reproducibility Auditor"},
            ])
            write_csv(root / "evidence/evidence-units.csv",
                      ["evidence_id", "source_location", "extraction_basis", "claim_type"],
                      [{"evidence_id": "E001", "source_location": "p. 3", "extraction_basis": "full_text", "claim_type": "association"}])
            write_csv(root / "evidence/claim-ledger.csv",
                      ["claim_id", "supporting_evidence_ids", "verified_citation_keys", "certainty"],
                      [{"claim_id": "C001", "supporting_evidence_ids": "E001", "verified_citation_keys": "key1", "certainty": "moderate"}])
            write_csv(root / "evidence/certainty-profile.csv", ["claim_id"], [{"claim_id": "C001"}])
            citation = root / "citation"
            citation.mkdir(parents=True, exist_ok=True)
            (citation / "citation-manifest.jsonl").write_text(json.dumps({"claim_id": "C001"}) + "\n", encoding="utf-8")
            write_csv(citation / "citation-audit.csv",
                      ["claim_id", "citation_key", "doi", "claim_supported", "final_status"],
                      [{"claim_id": "C001", "citation_key": "key1", "doi": "10.1/x", "claim_supported": "True", "final_status": "VERIFIED"}])
            (citation / "audit-summary.json").write_text(json.dumps({"total": 1, "hard_gate": "PASS"}), encoding="utf-8")
            manuscript = root / "writing/manuscript.md"
            manuscript.parent.mkdir(parents=True, exist_ok=True)
            manuscript.write_text("# Review\n\n" + "Evidence-grounded synthesis. " * 160, encoding="utf-8")
            result = quality_audit(root)
            self.assertEqual(result["verdict"], "SUBMISSION_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
