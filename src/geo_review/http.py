from __future__ import annotations

import hashlib
import json
import os
import random
import time
from pathlib import Path
from typing import Any

import requests

try:
    from dotenv import load_dotenv
except ImportError:  # optional convenience; environment variables still work
    load_dotenv = None


class APIRequestError(RuntimeError):
    pass


def load_environment(repo: Path | None = None) -> None:
    if load_dotenv is not None:
        load_dotenv((repo / ".env") if repo else None, override=False)


class ResilientClient:
    """JSON HTTP client with disk cache, throttling and bounded retries."""

    def __init__(self, database: str, cache_dir: Path, error_log: Path,
                 min_interval: float = 0.2, max_retries: int = 4,
                 timeout: int = 45, session: requests.Session | None = None):
        self.database = database
        self.cache_dir = cache_dir / database.lower().replace(" ", "_")
        self.error_log = error_log
        self.min_interval = max(0.0, min_interval)
        self.max_retries = max_retries
        self.timeout = timeout
        self.session = session or requests.Session()
        self._last_request = 0.0

    def _key(self, method: str, url: str, params: dict | None,
             payload: dict | None) -> str:
        raw = json.dumps([method, url, params or {}, payload or {}], sort_keys=True,
                         ensure_ascii=False, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _log_error(self, message: str, context: dict[str, Any]) -> None:
        self.error_log.parent.mkdir(parents=True, exist_ok=True)
        row = {"database": self.database, "message": message, **context,
               "logged_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with self.error_log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def request_json(self, method: str, url: str, *, params: dict | None = None,
                     payload: dict | None = None, headers: dict | None = None,
                     use_cache: bool = True) -> Any:
        key = self._key(method, url, params, payload)
        path = self.cache_dir / f"{key}.json"
        if use_cache and path.exists():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                pass

        retryable = {429, 500, 502, 503, 504}
        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            wait = self.min_interval - (time.monotonic() - self._last_request)
            if wait > 0:
                time.sleep(wait)
            try:
                response = self.session.request(
                    method, url, params=params, json=payload, headers=headers,
                    timeout=self.timeout,
                )
                self._last_request = time.monotonic()
                if response.status_code in retryable:
                    retry_after = response.headers.get("Retry-After")
                    delay = float(retry_after) if retry_after and retry_after.isdigit() \
                        else min(30.0, (2 ** attempt) + random.random())
                    if attempt < self.max_retries:
                        time.sleep(delay)
                        continue
                response.raise_for_status()
                try:
                    data = response.json()
                except ValueError as exc:
                    raise APIRequestError("Malformed JSON response") from exc
                if use_cache:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
                return data
            except (requests.RequestException, APIRequestError) as exc:
                last_error = exc
                if attempt < self.max_retries:
                    time.sleep(min(30.0, (2 ** attempt) + random.random()))
                    continue
        message = f"request failed after {self.max_retries + 1} attempts: {last_error}"
        self._log_error(message, {"url": url, "params": params or {}})
        raise APIRequestError(message) from last_error

