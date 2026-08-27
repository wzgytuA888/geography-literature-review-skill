from __future__ import annotations

import argparse
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from legal_fulltext_fetch import run as fetch_fulltext
from missing_fulltext_gate import main as missing_gate_main
from resume_helper import cmd_validate_pdf
from review_scaffold import init_run


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_text_pdf(path: Path, lines: list[str]) -> None:
    """Write a one-page, extractable PDF without optional test dependencies."""
    escaped = [line.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
               for line in lines]
    stream_text = "BT\n/F1 10 Tf\n72 740 Td\n12 TL\n" + "\nT*\n".join(
        f"({line}) Tj" for line in escaped
    ) + "\nET\n"
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
        f"startxref\n{xref}\n%%EOF\n".encode("ascii")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def make_paused_run(run_dir: Path, *, title: str = "A rigorous water review",
                    authors: str = "Alice Example; Bob Scholar", year: str = "2024",
                    doi: str = "10.1234/example.doi") -> Path:
    write_csv(
        run_dir / "screening/adjudicated.csv",
        ["report_id", "paper_id", "decision", "screening_status", "title",
         "authors", "year", "doi", "fulltext_status"],
        [{"report_id": "R001", "paper_id": "P001", "decision": "include",
          "screening_status": "HIGH_PRIORITY_PENDING_FULLTEXT", "title": title,
          "authors": authors, "year": year, "doi": doi,
          "fulltext_status": "MISSING_FULLTEXT"}],
    )
    write_csv(
        run_dir / "fulltext/fulltext-registry.csv",
        ["report_id", "fulltext_status", "local_path", "sha256",
         "identity_verified", "identity_basis", "page_count", "text_quality",
         "extracted_text_path"],
        [{"report_id": "R001", "fulltext_status": "MISSING_FULLTEXT",
          "local_path": "", "sha256": "", "identity_verified": "",
          "identity_basis": "", "page_count": "", "text_quality": "",
          "extracted_text_path": ""}],
    )
    state = {
        "status": "PAUSED_WAITING_FOR_USER_FULLTEXT",
        "current_stage": "fulltext_acquisition",
        "stage": "fulltext_acquisition",
        "missing_fulltext_gate": "TRIGGERED",
        "missing_count": 1,
        "missing_report_xlsx": "fulltext/missing_fulltext_literature.xlsx",
        "fulltext_upload_directory": str(run_dir / "fulltext/user_uploads"),
        "paused_because": "included report lacks verified local full text",
        "stages": {"fulltext": "in_progress", "extraction": "pending",
                   "synthesis": "pending", "drafting": "pending"},
    }
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "state.json").write_text(json.dumps(state), encoding="utf-8")
    inbox = run_dir / "fulltext/user_uploads"
    inbox.mkdir(parents=True, exist_ok=True)
    return inbox


class V4WorkflowTests(unittest.TestCase):
    def test_scaffold_creates_scope_and_fulltext_contract(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "run"
            args = argparse.Namespace(topic="水资源短缺", out_dir=str(out),
                                      mode="critical_narrative", language=["zh", "en"],
                                      target_journal="NREE", writing_profile="nree")
            self.assertEqual(init_run(args), 0)
            state = json.loads((out / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["schema_version"], "4.0")
            self.assertEqual(state["topic_specificity"], "pending_orientation_gate")
            self.assertTrue((out / "protocol/direction-options.md").exists())
            self.assertTrue((out / "fulltext/pdfs").is_dir())
            self.assertTrue((out / "fulltext/user_uploads").is_dir())

    def test_any_included_missing_fulltext_pauses_and_writes_xlsx(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            write_csv(run_dir / "screening/adjudicated.csv",
                      ["report_id", "decision", "title", "doi", "importance_tier"],
                      [{"report_id": "R001", "decision": "include", "title": "A paper",
                        "doi": "10.1/test", "importance_tier": "supplemental"}])
            write_csv(run_dir / "fulltext/fulltext-registry.csv",
                      ["report_id", "fulltext_status", "failure_reason"],
                      [{"report_id": "R001", "fulltext_status": "OPEN_ACCESS_FOUND",
                        "failure_reason": "URL found but PDF not stored locally"}])
            (run_dir / "state.json").write_text("{}", encoding="utf-8")
            with patch.object(sys, "argv", ["missing_fulltext_gate.py", "--run-dir", str(run_dir)]):
                self.assertEqual(missing_gate_main(), 5)
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "PAUSED_WAITING_FOR_USER_FULLTEXT")
            self.assertTrue((run_dir / "fulltext/missing_fulltext_literature.xlsx").exists())
            self.assertTrue((run_dir / "fulltext/user_uploads").is_dir())

    def test_legal_fetch_copies_user_pdf_and_records_checksum(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source.pdf"
            source.write_bytes(b"%PDF-1.4\n% minimal test fixture\n")
            queue = root / "queue.csv"
            write_csv(queue, ["report_id", "title", "doi", "local_path"],
                      [{"report_id": "R001", "title": "A paper", "doi": "10.1/test",
                        "local_path": str(source)}])
            results = fetch_fulltext(queue, root / "pdfs", root / "results.csv")
            self.assertEqual(results[0]["status"], "AVAILABLE_LOCAL")
            self.assertEqual(len(results[0]["sha256"]), 64)
            self.assertTrue(Path(results[0]["local_path"]).exists())

    def test_resume_rejects_blank_pdf_even_when_filename_matches(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            make_paused_run(run_dir)
            supplied = Path(td) / "A rigorous water review.pdf"
            from pypdf import PdfWriter
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            with supplied.open("wb") as handle:
                writer.write(handle)
            self.assertEqual(cmd_validate_pdf(run_dir, [supplied]), 5)
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "PAUSED_WAITING_FOR_USER_FULLTEXT")
            self.assertEqual(state["missing_fulltext_gate"], "TRIGGERED")
            with (run_dir / "fulltext/fulltext-registry.csv").open(
                    encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertNotEqual(row["identity_verified"], "verified_automatic")
            self.assertFalse((run_dir / "fulltext/text/R001.txt").exists())

    def test_resume_rejects_damaged_pdf_and_keeps_pause(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            make_paused_run(run_dir)
            damaged = Path(td) / "A rigorous water review.pdf"
            damaged.write_bytes(b"%PDF-1.4\nnot a parseable PDF")
            self.assertEqual(cmd_validate_pdf(run_dir, [damaged]), 5)
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["missing_fulltext_gate"], "TRIGGERED")

    def test_resume_does_not_use_filename_as_identity_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            make_paused_run(run_dir)
            wrong = Path(td) / "A rigorous water review.pdf"
            filler = " ".join(["readable unrelated scientific content"] * 80)
            write_text_pdf(wrong, ["A different paper", "Carol Other 2022", filler])
            self.assertEqual(cmd_validate_pdf(run_dir, [wrong]), 5)
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "PAUSED_WAITING_FOR_USER_FULLTEXT")

    def test_resume_auto_scans_and_accepts_doi_content(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            inbox = make_paused_run(run_dir)
            supplied = inbox / "arbitrary-upload-name.pdf"
            filler = " ".join(["hydrological mechanism evidence and methods"] * 80)
            write_text_pdf(supplied, ["10.1234/example.doi", filler])
            self.assertEqual(cmd_validate_pdf(run_dir, []), 0)

            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["missing_fulltext_gate"], "CLEAR")
            self.assertEqual(state["status"], "RUNNING")
            self.assertEqual(state["current_stage"], "extraction")
            self.assertNotIn("stage", state)
            self.assertEqual(state["stages"]["fulltext"], "completed")
            self.assertEqual(state["stages"]["extraction"], "in_progress")
            self.assertNotIn("paused_because", state)
            self.assertNotIn("missing_count", state)
            self.assertEqual(len(state["pause_history"]), 1)

            with (run_dir / "fulltext/fulltext-registry.csv").open(
                    encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["identity_verified"], "verified_automatic")
            self.assertEqual(row["identity_basis"], "doi_in_pdf_text")
            self.assertEqual(row["page_count"], "1")
            self.assertIn(row["text_quality"], {"acceptable", "good"})
            self.assertEqual(len(row["sha256"]), 64)
            self.assertEqual(Path(row["local_path"]).parent,
                             run_dir / "fulltext/pdfs")
            text_path = run_dir / row["extracted_text_path"]
            self.assertTrue(text_path.exists())
            self.assertIn("10.1234/example.doi", text_path.read_text(encoding="utf-8"))

    def test_resume_ignores_target_doi_when_it_appears_only_after_front_matter(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            make_paused_run(run_dir)
            supplied = Path(td) / "A rigorous water review.pdf"
            long_unrelated_body = " ".join(["unrelated readable analysis"] * 900)
            write_text_pdf(supplied, ["A different article", "Carol Other 2022",
                                      long_unrelated_body,
                                      "References 10.1234/example.doi"])
            self.assertEqual(cmd_validate_pdf(run_dir, [supplied]), 5)
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["missing_fulltext_gate"], "TRIGGERED")

    def test_resume_accepts_title_plus_author_and_year_content(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td) / "run"
            make_paused_run(run_dir, doi="")
            supplied = Path(td) / "not-the-title.pdf"
            filler = " ".join(["water evidence mechanism boundary condition"] * 80)
            write_text_pdf(supplied, ["A rigorous water review",
                                      "Alice Example and Bob Scholar", "2024", filler])
            self.assertEqual(cmd_validate_pdf(run_dir, [supplied]), 0)
            with (run_dir / "fulltext/fulltext-registry.csv").open(
                    encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertIn("title_in_pdf_text", row["identity_basis"])
            self.assertIn("author_in_pdf_text", row["identity_basis"])
            self.assertIn("year_in_pdf_text", row["identity_basis"])

    def test_nree_contract_and_piracy_boundary_are_explicit(self):
        skill = (REPO / "SKILL.md").read_text(encoding="utf-8")
        fulltext = (REPO / "workflows/fulltext-acquisition.md").read_text(encoding="utf-8")
        nree = (REPO / "references/nree-review-writing.md").read_text(encoding="utf-8")
        self.assertIn("PAUSED_WAITING_FOR_SCOPE_SELECTION", skill)
        self.assertIn("PAUSED_WAITING_FOR_USER_FULLTEXT", skill)
        self.assertIn("Never bypass authentication, paywalls", fulltext)
        self.assertIn("Sci-Hub, pirate repositories", fulltext)
        self.assertIn("NREE profile release gate", nree)


if __name__ == "__main__":
    unittest.main()
