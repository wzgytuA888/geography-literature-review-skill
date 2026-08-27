from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from legal_fulltext_fetch import merge_results_into_run


def write_csv(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class V4FulltextMergeTests(unittest.TestCase):
    def test_acquisition_failure_provenance_merges_into_registry_and_screening(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            write_csv(run_dir / "fulltext/fulltext-registry.csv",
                      ["report_id", "fulltext_status", "identity_verified"],
                      [{"report_id": "R1", "fulltext_status": "", "identity_verified": ""}])
            write_csv(run_dir / "screening/adjudicated.csv",
                      ["report_id", "decision"],
                      [{"report_id": "R1", "decision": "include"}])
            merge_results_into_run(run_dir, [{
                "report_id": "R1", "title": "Paper", "doi": "10.1/x",
                "status": "MISSING_FULLTEXT", "route": "", "final_url": "",
                "local_path": "", "sha256": "", "bytes": "0",
                "attempts": "openalex:https://example.invalid/a.pdf",
                "failure_reason": "connection failed",
            }])
            with (run_dir / "fulltext/fulltext-registry.csv").open(
                    encoding="utf-8-sig", newline="") as handle:
                registry = next(csv.DictReader(handle))
            self.assertEqual(registry["fulltext_status"], "MISSING_FULLTEXT")
            self.assertIn("openalex", registry["access_attempts"])
            self.assertEqual(registry["failure_reason"], "connection failed")
            with (run_dir / "screening/adjudicated.csv").open(
                    encoding="utf-8-sig", newline="") as handle:
                screening = next(csv.DictReader(handle))
            self.assertEqual(screening["fulltext_status"], "MISSING_FULLTEXT")

    def test_downloaded_file_stays_pending_content_identity_verification(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            write_csv(run_dir / "fulltext/fulltext-registry.csv",
                      ["report_id", "fulltext_status", "identity_verified"],
                      [{"report_id": "R1", "fulltext_status": "", "identity_verified": ""}])
            merge_results_into_run(run_dir, [{
                "report_id": "R1", "title": "Paper", "doi": "10.1/x",
                "status": "DOWNLOADED_LEGAL", "route": "openalex",
                "final_url": "https://example.org/a.pdf", "local_path": "a.pdf",
                "sha256": "a" * 64, "bytes": "1000", "attempts": "openalex",
                "failure_reason": "",
            }])
            with (run_dir / "fulltext/fulltext-registry.csv").open(
                    encoding="utf-8-sig", newline="") as handle:
                row = next(csv.DictReader(handle))
            self.assertEqual(row["identity_verified"], "pending_content_verification")
            self.assertEqual(row["text_quality"], "pending_extraction")


if __name__ == "__main__":
    unittest.main()
