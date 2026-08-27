#!/usr/bin/env python3
"""Read-only guard that prevents downstream work while a review run is paused."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


PAUSED_STATUSES = {
    "PAUSED_WAITING_FOR_SCOPE_SELECTION",
    "PAUSED_WAITING_FOR_USER_FULLTEXT",
    "PAUSED_ACADEMIC_APIS_NOT_READY",
}
ALLOWED_BY_STATUS = {
    "PAUSED_WAITING_FOR_SCOPE_SELECTION": {
        "status", "orientation", "scope_selection", "quality_audit"},
    "PAUSED_WAITING_FOR_USER_FULLTEXT": {
        "status", "fulltext_acquisition", "resume", "quality_audit"},
    "PAUSED_ACADEMIC_APIS_NOT_READY": {
        "status", "preflight", "search_recovery", "quality_audit"},
}


class RunPausedError(RuntimeError):
    """Raised before a blocked stage can write artifacts."""


def read_state(run_dir: Path) -> dict:
    path = run_dir / "state.json"
    if not path.exists():
        raise FileNotFoundError(f"state file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def assert_run_unblocked(run_dir: Path, intended_stage: str) -> dict:
    """Return state when allowed; otherwise raise without changing the run."""
    state = read_state(run_dir)
    status = str(state.get("status") or "")
    if status in PAUSED_STATUSES and intended_stage not in ALLOWED_BY_STATUS[status]:
        reason = state.get("paused_because") or state.get("pause_reason") or status
        raise RunPausedError(
            f"run is {status}; stage '{intended_stage}' is blocked before write: {reason}")
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True)
    parser.add_argument("--stage", required=True)
    args = parser.parse_args()
    try:
        state = assert_run_unblocked(Path(args.run_dir), args.stage)
    except (RunPausedError, FileNotFoundError, json.JSONDecodeError) as exc:
        print(json.dumps({"allowed": False, "error": str(exc)}, ensure_ascii=False))
        return 9
    print(json.dumps({"allowed": True, "status": state.get("status"),
                      "stage": args.stage}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
