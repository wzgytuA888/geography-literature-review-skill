#!/usr/bin/env python3
"""Google Scholar API preflight check — mandatory before any runtime search.

Exit codes:
  0  provider ready
  2  check failed (auth/quota/network/schema) → workflow must pause with
     state PAUSED_GOOGLE_SCHOLAR_API_NOT_READY
  3  configuration missing entirely

The report is JSON on stdout; never includes the raw API key.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from google_scholar_adapter import ProviderConfig, ScholarAPIError, preflight  # noqa: E402


def main() -> None:
    try:
        cfg = ProviderConfig.from_env()
    except ScholarAPIError as e:
        print(json.dumps({
            "status": "FAILED",
            "state": "PAUSED_GOOGLE_SCHOLAR_API_NOT_READY",
            "error_class": type(e).__name__,
            "message": str(e),
            "user_action": "Configure GOOGLE_SCHOLAR_API_PROVIDER / _KEY / _ENDPOINT "
                           "(see docs/google-scholar-setup.md) and re-run this check.",
        }, indent=2))
        sys.exit(3)

    rep = preflight(cfg)
    if rep.get("status") == "OK":
        rep["state"] = "READY"
        print(json.dumps(rep, indent=2))
        # persist capability snapshot into the current run if one exists
        sys.exit(0)
    else:
        rep["state"] = "PAUSED_GOOGLE_SCHOLAR_API_NOT_READY"
        rep.setdefault("user_action",
                       "Fix the Google Scholar API configuration/credentials/quota and re-run. "
                       "Do NOT switch to another discovery backend; that is forbidden by policy.")
        print(json.dumps(rep, indent=2))
        sys.exit(2)


if __name__ == "__main__":
    main()
