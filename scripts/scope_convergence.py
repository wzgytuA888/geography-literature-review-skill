#!/usr/bin/env python3
"""Atomically start, checkpoint, or resolve the v4 topic-specificity gate."""
from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml


REQUIRED_CARD_FIELDS = (
    "Primary review question", "Proposed contribution", "Inclusion boundary",
    "Expected NREE progression", "Evidence density and recency",
    "Geographic/scale coverage", "Full-text feasibility",
    "Main risk or saturation issue", "Representative verified papers",
)
ANCHORS = {"phenomenon", "mechanism", "geography_or_system", "time_window",
           "intended_contribution"}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def atomic_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    temporary.replace(path)


def write_json(path: Path, value: dict) -> None:
    atomic_text(path, json.dumps(value, indent=2, ensure_ascii=False))


def write_yaml(path: Path, value: dict) -> None:
    atomic_text(path, yaml.safe_dump(value, allow_unicode=True, sort_keys=False))


def ensure_orientation_artifacts(run_dir: Path) -> None:
    (run_dir / "staging").mkdir(parents=True, exist_ok=True)
    log = run_dir / "search/search_log.csv"
    if not log.exists():
        atomic_text(log, "database,query,filters,year_range,retrieved_count,retrieved_at,status,error,role\n")
    result = run_dir / "search/orientation-results.md"
    if not result.exists():
        atomic_text(result, "# Orientation discovery results\n\nPending.\n")


def csv_has_data(path: Path) -> bool:
    if not path.exists():
        return False
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return any(True for _ in csv.DictReader(handle))


def downstream_artifacts(run_dir: Path) -> list[str]:
    violations: list[str] = []
    for rel in ("evidence/evidence-units.csv", "fulltext/fulltext-registry.csv"):
        if csv_has_data(run_dir / rel):
            violations.append(rel)
    for folder in ("writing", "final"):
        root = run_dir / folder
        if root.exists():
            violations.extend(str(path.relative_to(run_dir)) for path in root.rglob("*")
                              if path.is_file() and path.stat().st_size > 0)
    return sorted(set(violations))


def parse_direction_cards(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    matches = list(re.finditer(r"(?m)^## Option\s+\d+\b.*$", text))
    cards: list[str] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        cards.append(text[match.start():end])
    return cards


def validate_cards(path: Path) -> list[str]:
    cards = parse_direction_cards(path)
    errors: list[str] = []
    if not 3 <= len(cards) <= 5:
        errors.append(f"direction card count must be 3–5, found {len(cards)}")
    for index, card in enumerate(cards, 1):
        for field in REQUIRED_CARD_FIELDS:
            match = re.search(rf"(?m)^- {re.escape(field)}:\s*(.+)$", card)
            if not match or not match.group(1).strip() or match.group(1).strip().startswith("<"):
                errors.append(f"option {index} missing populated field: {field}")
    return errors


def start(run_dir: Path) -> int:
    state_path = run_dir / "state.json"
    if not state_path.exists():
        raise SystemExit(f"state file not found: {state_path}")
    ensure_orientation_artifacts(run_dir)
    state = read_json(state_path)
    state.update({"status": "ORIENTATION_RUNNING", "current_stage": "orientation",
                  "topic_specificity": "orientation_in_progress", "updated_at": now()})
    state.pop("stage", None)
    stages = state.setdefault("stages", {})
    stages["orientation"] = "in_progress"
    stages["protocol"] = "pending"
    write_json(state_path, state)
    print(json.dumps({"status": state["status"], "run_dir": str(run_dir)}, ensure_ascii=False))
    return 0


def checkpoint(run_dir: Path, specificity: str, anchors: list[str],
               directions_file: Path | None) -> int:
    unknown = set(anchors) - ANCHORS
    if unknown:
        raise SystemExit(f"unknown anchors: {sorted(unknown)}")
    state_path = run_dir / "state.json"
    protocol_path = run_dir / "protocol/protocol.yaml"
    state = read_json(state_path)
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8")) or {}
    violations = downstream_artifacts(run_dir)
    if violations:
        print(json.dumps({"status": "FAIL", "premature_downstream_artifacts": violations},
                         ensure_ascii=False))
        return 7
    report = {"specificity": specificity, "anchors_present": sorted(set(anchors)),
              "anchor_count": len(set(anchors)), "checked_at": now()}
    stages = state.setdefault("stages", {})
    stages["orientation"] = "completed"
    if specificity == "broad":
        directions_file = directions_file or run_dir / "protocol/direction-options.md"
        errors = validate_cards(directions_file)
        if errors:
            print(json.dumps({"status": "FAIL", "errors": errors}, ensure_ascii=False))
            return 7
        report["direction_card_count"] = len(parse_direction_cards(directions_file))
        state.update({
            "status": "PAUSED_WAITING_FOR_SCOPE_SELECTION",
            "current_stage": "scope_selection",
            "topic_specificity": f"broad_{len(set(anchors))}_of_5_anchors",
            "pause_reason": "materially different evidence-informed review directions require user choice",
            "updated_at": now(),
        })
        stages["protocol"] = "pending"
        protocol.update({"status": "awaiting_scope_selection",
                         "topic_specificity": state["topic_specificity"],
                         "scope_selection_status": "pending"})
    else:
        state.update({"status": "RUNNING", "current_stage": "protocol",
                      "topic_specificity": "specific", "updated_at": now()})
        stages["protocol"] = "in_progress"
        protocol.update({"status": "draft", "topic_specificity": "specific",
                         "scope_selection_status": "not_required"})
    state.pop("stage", None)
    write_json(run_dir / "protocol/scope-convergence.json", report)
    write_yaml(protocol_path, protocol)
    write_json(state_path, state)
    print(json.dumps({"status": state["status"], **report}, ensure_ascii=False))
    return 0


def select(run_dir: Path, option: int, primary_question: str) -> int:
    state_path = run_dir / "state.json"
    protocol_path = run_dir / "protocol/protocol.yaml"
    state = read_json(state_path)
    if state.get("status") != "PAUSED_WAITING_FOR_SCOPE_SELECTION":
        print(json.dumps({"status": "FAIL", "error": "run is not awaiting scope selection"}))
        return 7
    cards = parse_direction_cards(run_dir / "protocol/direction-options.md")
    if option < 1 or option > len(cards):
        print(json.dumps({"status": "FAIL", "error": "selected option is out of range"}))
        return 7
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8")) or {}
    protocol.update({"status": "draft", "scope_selection_status": "selected",
                     "selected_direction_option": option,
                     "primary_question": primary_question})
    state.update({"status": "RUNNING", "current_stage": "protocol",
                  "topic_specificity": "selected_after_orientation",
                  "selected_direction_option": option, "updated_at": now()})
    state.pop("pause_reason", None)
    state.setdefault("stages", {})["protocol"] = "in_progress"
    write_yaml(protocol_path, protocol)
    write_json(state_path, state)
    report_path = run_dir / "protocol/scope-convergence.json"
    report = read_json(report_path) if report_path.exists() else {}
    report.update({"selected_option": option, "primary_question": primary_question,
                   "selected_at": now()})
    write_json(report_path, report)
    print(json.dumps({"status": "RUNNING", "selected_option": option,
                      "primary_question": primary_question}, ensure_ascii=False))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    start_parser = sub.add_parser("start")
    start_parser.add_argument("--run-dir", required=True)
    checkpoint_parser = sub.add_parser("checkpoint")
    checkpoint_parser.add_argument("--run-dir", required=True)
    checkpoint_parser.add_argument("--specificity", choices=["broad", "specific"], required=True)
    checkpoint_parser.add_argument("--anchor", action="append", default=[], choices=sorted(ANCHORS))
    checkpoint_parser.add_argument("--directions-file")
    select_parser = sub.add_parser("select")
    select_parser.add_argument("--run-dir", required=True)
    select_parser.add_argument("--option", type=int, required=True)
    select_parser.add_argument("--primary-question", required=True)
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    if args.command == "start":
        return start(run_dir)
    if args.command == "checkpoint":
        return checkpoint(run_dir, args.specificity, args.anchor,
                          Path(args.directions_file) if args.directions_file else None)
    return select(run_dir, args.option, args.primary_question)


if __name__ == "__main__":
    raise SystemExit(main())
