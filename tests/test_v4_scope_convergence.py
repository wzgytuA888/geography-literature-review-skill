from __future__ import annotations

import argparse
import json
import sys
import tempfile
import unittest
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

from review_scaffold import init_run
from scope_convergence import checkpoint, select, start


def populated_cards(count: int = 3) -> str:
    cards = ["# Evidence-informed direction options\n"]
    for number in range(1, count + 1):
        cards.append(f"""
## Option {number} — Direction {number}

- Primary review question: Question {number}?
- Proposed contribution: Contribution {number}
- Inclusion boundary: Boundary {number}
- Expected NREE progression: Mechanism ladder {number}
- Evidence density and recency: Adequate and current
- Geographic/scale coverage: Global with regional tests
- Full-text feasibility: Most representative reports appear accessible
- Main risk or saturation issue: Existing-review saturation
- Representative verified papers: 10.1000/example{number}
""")
    cards.append("\n## User decision\n\nPending.\n")
    return "".join(cards)


class V4ScopeConvergenceTests(unittest.TestCase):
    def create_run(self, root: Path) -> Path:
        run_dir = root / "run"
        args = argparse.Namespace(topic="水资源短缺", out_dir=str(run_dir),
                                  mode="critical_narrative", language=["zh", "en"],
                                  target_journal="NREE", writing_profile="nree")
        self.assertEqual(init_run(args), 0)
        return run_dir

    def test_scaffold_starts_at_orientation_not_protocol(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = self.create_run(Path(td))
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "ORIENTATION_PENDING")
            self.assertEqual(state["current_stage"], "orientation")
            self.assertEqual(state["stages"]["orientation"], "in_progress")
            self.assertEqual(state["stages"]["protocol"], "pending")
            self.assertTrue((run_dir / "search/search_log.csv").exists())
            self.assertTrue((run_dir / "staging").is_dir())

    def test_broad_checkpoint_validates_cards_and_pauses_atomically(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = self.create_run(Path(td))
            self.assertEqual(start(run_dir), 0)
            (run_dir / "protocol/direction-options.md").write_text(
                populated_cards(5), encoding="utf-8")
            self.assertEqual(checkpoint(run_dir, "broad", ["phenomenon"], None), 0)
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "PAUSED_WAITING_FOR_SCOPE_SELECTION")
            self.assertEqual(state["current_stage"], "scope_selection")
            self.assertEqual(state["topic_specificity"], "broad_1_of_5_anchors")
            protocol = yaml.safe_load((run_dir / "protocol/protocol.yaml").read_text(
                encoding="utf-8"))
            self.assertEqual(protocol["scope_selection_status"], "pending")
            self.assertFalse(any((run_dir / "writing").iterdir()))

    def test_select_resumes_protocol_with_exact_user_question(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = self.create_run(Path(td))
            (run_dir / "protocol/direction-options.md").write_text(
                populated_cards(3), encoding="utf-8")
            self.assertEqual(checkpoint(run_dir, "broad", ["phenomenon"], None), 0)
            question = "When does irrigation efficiency reduce basin-scale consumptive use?"
            self.assertEqual(select(run_dir, 2, question), 0)
            state = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["current_stage"], "protocol")
            protocol = yaml.safe_load((run_dir / "protocol/protocol.yaml").read_text(
                encoding="utf-8"))
            self.assertEqual(protocol["primary_question"], question)

    def test_checkpoint_rejects_premature_manuscript(self):
        with tempfile.TemporaryDirectory() as td:
            run_dir = self.create_run(Path(td))
            (run_dir / "protocol/direction-options.md").write_text(
                populated_cards(3), encoding="utf-8")
            (run_dir / "writing/manuscript.md").write_text("premature", encoding="utf-8")
            self.assertEqual(checkpoint(run_dir, "broad", ["phenomenon"], None), 7)


if __name__ == "__main__":
    unittest.main()
