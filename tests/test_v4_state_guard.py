from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from run_state_guard import RunPausedError, assert_run_unblocked
from citation_validator import main as citation_main


class V4StateGuardTests(unittest.TestCase):
    def test_fulltext_pause_blocks_every_downstream_stage_without_writes(self):
        blocked = [
            "extraction", "appraisal", "geospatial_audit", "synthesis", "outline",
            "drafting", "citation", "figures", "review", "packaging",
        ]
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            state_path = run_dir / "state.json"
            state = {"status": "PAUSED_WAITING_FOR_USER_FULLTEXT",
                     "paused_because": "one included report is missing"}
            state_path.write_text(json.dumps(state), encoding="utf-8")
            before = state_path.read_bytes()
            for stage in blocked:
                with self.subTest(stage=stage), self.assertRaises(RunPausedError):
                    assert_run_unblocked(run_dir, stage)
            self.assertEqual(state_path.read_bytes(), before)
            self.assertEqual(list(run_dir.iterdir()), [state_path])

    def test_pause_allows_only_resolution_stages(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            (run_dir / "state.json").write_text(json.dumps({
                "status": "PAUSED_WAITING_FOR_USER_FULLTEXT"}), encoding="utf-8")
            for stage in ["status", "fulltext_acquisition", "resume", "quality_audit"]:
                self.assertEqual(assert_run_unblocked(run_dir, stage)["status"],
                                 "PAUSED_WAITING_FOR_USER_FULLTEXT")

    def test_scope_pause_blocks_final_search_and_drafting(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            (run_dir / "state.json").write_text(json.dumps({
                "status": "PAUSED_WAITING_FOR_SCOPE_SELECTION"}), encoding="utf-8")
            for stage in ["search", "screening", "drafting"]:
                with self.assertRaises(RunPausedError):
                    assert_run_unblocked(run_dir, stage)

    def test_citation_entrypoint_stops_before_writing_when_paused(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = Path(td)
            citation = run_dir / "citation"
            citation.mkdir(parents=True)
            manifest = citation / "citation-manifest.jsonl"
            manifest.write_text('{"claim_id":"C1"}\n', encoding="utf-8")
            (run_dir / "state.json").write_text(json.dumps({
                "status": "PAUSED_WAITING_FOR_USER_FULLTEXT"}), encoding="utf-8")
            with patch.object(sys, "argv", ["citation_validator.py", "--manifest", str(manifest)]):
                with self.assertRaises(SystemExit) as stopped:
                    citation_main()
            self.assertEqual(stopped.exception.code, 9)
            self.assertFalse((citation / "citation-audit.csv").exists())


if __name__ == "__main__":
    unittest.main()
