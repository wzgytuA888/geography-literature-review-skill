from __future__ import annotations

import argparse
import csv
import hashlib
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


def write_text_pdf(path: Path, lines: list[str]) -> None:
    escaped = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
               for line in lines]
    stream_text = "BT\n/F1 10 Tf\n72 740 Td\n12 TL\n" + "\nT*\n".join(
        f"({line}) Tj" for line in escaped) + "\nET\n"
    stream = stream_text.encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
         b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>"),
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n"
        + stream + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    payload = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for number, obj in enumerate(objects, 1):
        offsets.append(len(payload))
        payload.extend(f"{number} 0 obj\n".encode("ascii"))
        payload.extend(obj)
        payload.extend(b"\nendobj\n")
    xref = len(payload)
    payload.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    payload.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        payload.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    payload.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref}\n%%EOF\n".encode("ascii"))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


class ReleaseIntegrityTests(unittest.TestCase):
    def test_search_budget_keeps_recall_pool(self):
        self.assertEqual(allocate_per_query_limit(60, 8, 2, 4.0), 15)
        self.assertEqual(allocate_per_query_limit(60, 8, override=30), 30)

    def test_release_version_is_consistent(self):
        skill = (REPO / "SKILL.md").read_text(encoding="utf-8")
        citation = (REPO / "CITATION.cff").read_text(encoding="utf-8")
        from geo_review import __version__
        self.assertIn("version: 4.0.0", skill)
        self.assertIn("version: 4.0.0", citation)
        self.assertEqual(__version__, "4.0.0")

    def test_chinese_slug_is_preserved(self):
        self.assertIn("水资源", slugify("全球 水资源：综述"))

    def test_scaffold_records_verbatim_topic_and_mode(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "run"
            args = argparse.Namespace(topic="青藏高原冻土与植被响应", out_dir=str(out),
                                      mode="critical_narrative", language=["zh", "en"],
                                      target_journal=None, writing_profile="nree")
            self.assertEqual(init_run(args), 0)
            protocol = yaml.safe_load((out / "protocol/protocol.yaml").read_text(encoding="utf-8"))
            self.assertEqual(protocol["topic_verbatim"], args.topic)
            self.assertEqual(protocol["scope"]["languages"], ["zh", "en"])
            self.assertTrue((out / "reporting/agent-manifest.csv").exists())
            self.assertEqual(protocol["writing_profile"], "nree")
            self.assertTrue((out / "fulltext/acquisition-queue.csv").exists())

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
                "writing_profile": "nree",
                "contribution": {"this_review_adds": "A spatially explicit synthesis"}}), encoding="utf-8")
            (root / "search").mkdir(parents=True, exist_ok=True)
            (root / "search/search-plan.yaml").write_text(yaml.safe_dump({
                "sources": [{"database": "OpenAlex"}],
                "peer_review": {"status": "passed"},
                "sentinel_recall": {"status": "passed", "retrieved": 4, "total": 4}}), encoding="utf-8")
            write_csv(root / "screening/adjudicated.csv", ["report_id", "decision", "title", "doi"],
                      [{"report_id": "R1", "decision": "include",
                        "title": "Evidence grounded review", "doi": "10.1234/x"}])
            local_pdf = root / "fulltext/pdfs/R1.pdf"
            local_pdf.parent.mkdir(parents=True, exist_ok=True)
            source_text = "10.1234/x " + "Evidence grounded synthesis with methods and results. " * 40
            write_text_pdf(local_pdf, [source_text])
            local_sha256 = hashlib.sha256(local_pdf.read_bytes()).hexdigest()
            extracted_text = root / "fulltext/text/R1.txt"
            extracted_text.parent.mkdir(parents=True, exist_ok=True)
            extracted_text.write_text(source_text, encoding="utf-8")
            write_csv(root / "fulltext/fulltext-registry.csv",
                      ["report_id", "importance_tier", "fulltext_status", "local_path", "sha256",
                       "identity_verified", "identity_basis", "page_count", "text_quality",
                       "extracted_text_path"],
                      [{"report_id": "R1", "importance_tier": "critical", "fulltext_status": "AVAILABLE_LOCAL",
                        "local_path": "fulltext/pdfs/R1.pdf", "sha256": local_sha256,
                        "identity_verified": "verified_automatic", "identity_basis": "doi_in_pdf_text",
                        "page_count": "1", "text_quality": "good",
                        "extracted_text_path": "fulltext/text/R1.txt"}])
            write_csv(root / "appraisal/study-appraisal.csv",
                      ["report_id", "domain", "judgment"],
                      [{"report_id": "R1", "domain": "sampling", "judgment": "low"}])
            write_csv(root / "reporting/agent-manifest.csv", ["role"], [
                {"role": "Search Peer Reviewer"},
                {"role": "Critical Appraisal Specialist"},
                {"role": "Geospatial Heterogeneity Analyst"},
                {"role": "Contradiction and Gap Red Team"},
                {"role": "Reproducibility Auditor"},
                {"role": "NREE Architecture Editor"},
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
            (root / "evaluation/nree-architecture-report.md").write_text(
                "# NREE architecture review\n\nVerdict: PASS\n", encoding="utf-8")
            (root / "evaluation/nree-architecture-gate.yaml").write_text(
                yaml.safe_dump({"status": "pass", "score_total": 90,
                                "hard_blockers": []}), encoding="utf-8")
            result = quality_audit(root)
            self.assertEqual(result["verdict"], "SUBMISSION_CANDIDATE")


if __name__ == "__main__":
    unittest.main()
