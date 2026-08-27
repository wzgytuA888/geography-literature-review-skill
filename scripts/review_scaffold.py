#!/usr/bin/env python3
"""Create a versioned, auditable v4 literature-review run."""
from __future__ import annotations

import argparse
import json
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

import yaml


REPO = Path(__file__).resolve().parents[1]
TEMPLATES = REPO / "templates"
DIRECTORIES = [
    "protocol", "search/raw", "screening", "fulltext/pdfs", "fulltext/text",
    "fulltext/user_uploads", "evidence/literature-cards",
    "appraisal", "writing", "citation", "figures/data", "reporting",
    "evaluation", "final", "logs", "staging",
]
TEMPLATE_TARGETS = {
    "protocol.yaml": "protocol/protocol.yaml",
    "search-plan.yaml": "search/search-plan.yaml",
    "sentinel-set.csv": "search/sentinel-set.csv",
    "claim-ledger.csv": "evidence/claim-ledger.csv",
    "study-appraisal.csv": "appraisal/study-appraisal.csv",
    "dependency-map.csv": "appraisal/dependency-map.csv",
    "certainty-profile.csv": "evidence/certainty-profile.csv",
    "agent-manifest.csv": "reporting/agent-manifest.csv",
    "direction-options.md": "protocol/direction-options.md",
    "acquisition-queue.csv": "fulltext/acquisition-queue.csv",
    "evidence-units.csv": "evidence/evidence-units.csv",
    "fulltext-registry.csv": "fulltext/fulltext-registry.csv",
    "nree-architecture-gate.yaml": "evaluation/nree-architecture-gate.yaml",
    "search-log.csv": "search/search_log.csv",
    "orientation-results.md": "search/orientation-results.md",
}


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def slugify(text: str) -> str:
    slug = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text.casefold(), flags=re.UNICODE).strip("-")
    return (slug[:60] or "review").rstrip("-")


def init_run(args: argparse.Namespace) -> int:
    run_dir = Path(args.out_dir) if args.out_dir else (
        REPO / "runs" / f"{datetime.now():%Y%m%d}-{slugify(args.topic)}")
    if run_dir.exists() and any(run_dir.iterdir()):
        raise SystemExit(f"Refusing to overwrite non-empty run directory: {run_dir}")
    for name in DIRECTORIES:
        (run_dir / name).mkdir(parents=True, exist_ok=True)
    for source, target in TEMPLATE_TARGETS.items():
        shutil.copy2(TEMPLATES / source, run_dir / target)

    protocol_path = run_dir / "protocol/protocol.yaml"
    protocol = yaml.safe_load(protocol_path.read_text(encoding="utf-8"))
    protocol["topic_verbatim"] = args.topic
    protocol["review_mode"] = args.mode
    protocol["scope"]["languages"] = args.language or ["en"]
    protocol["target_journal"] = args.target_journal
    protocol["writing_profile"] = args.writing_profile
    protocol["manuscript_architecture_profile"] = args.writing_profile
    protocol["status"] = "orientation_pending"
    if args.mode not in {"critical_narrative", "integrative", "conceptual"}:
        protocol["label_constraints"] = ["pending_method_gates"]
    protocol_path.write_text(yaml.safe_dump(protocol, allow_unicode=True,
                                             sort_keys=False), encoding="utf-8")

    task = (
        f"# Review task\n\n## Verbatim request\n\n{args.topic}\n\n"
        f"## Initial mode\n\n{args.mode}\n\n"
        "## Status\n\nTopic specificity, scope, question and contribution are provisional until scope selection and protocol freeze.\n"
    )
    (run_dir / "task.md").write_text(task, encoding="utf-8")
    state = {
        "schema_version": "4.0",
        "run_id": run_dir.name,
        "topic_verbatim": args.topic,
        "review_mode": args.mode,
        "status": "ORIENTATION_PENDING",
        "current_stage": "orientation",
        "topic_specificity": "pending_orientation_gate",
        "writing_profile": args.writing_profile,
        "protocol_version": "1.0",
        "created_at": now(),
        "updated_at": now(),
        "stages": {name: "pending" for name in [
            "orientation", "protocol", "search", "screening", "fulltext", "extraction",
            "appraisal", "geospatial_audit", "synthesis", "drafting",
            "citations", "figures", "review", "packaging"]},
    }
    state["stages"]["orientation"] = "in_progress"
    (run_dir / "state.json").write_text(json.dumps(
        state, indent=2, ensure_ascii=False), encoding="utf-8")
    (run_dir / "protocol/deviations.md").write_text(
        "# Protocol amendments\n\nNo amendments recorded.\n", encoding="utf-8")
    print(json.dumps({"status": "created", "run_dir": str(run_dir),
                      "mode": args.mode}, indent=2, ensure_ascii=False))
    return 0


def parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init")
    init.add_argument("--topic", required=True)
    init.add_argument("--out-dir")
    init.add_argument("--mode", default="critical_narrative", choices=[
        "critical_narrative", "integrative", "conceptual", "systematic_review",
        "systematic_map", "scoping", "methodological", "bibliometric",
        "realist", "meta_analysis", "qualitative_evidence_synthesis"])
    init.add_argument("--language", action="append")
    init.add_argument("--target-journal")
    init.add_argument("--writing-profile", default="nree", choices=["nree", "journal_neutral"])
    init.set_defaults(func=init_run)
    return ap


if __name__ == "__main__":
    parsed = parser().parse_args()
    raise SystemExit(parsed.func(parsed))
