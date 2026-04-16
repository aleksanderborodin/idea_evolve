#!/usr/bin/env python3
"""Opt-in tool: submit a solution to Kaggle for real-leaderboard scoring.

Used for Class C problems (hidden test labels) to periodically calibrate
the local holdout score against the public leaderboard. Never called by
evaluate.py — Kaggle rate-limits submissions (typically 5/day) and they
must stay under operator control.

Usage:
    python3 scripts/submit_to_kaggle.py <problem_id> <solution.py> [--message TEXT]

The problem must implement `helpers.core.write_submission(predictions, path)`
to translate the dict from `entrypoint()` into Kaggle's required CSV format.

Records each submission to runs/<problem>/<latest_attempt>/kaggle_submissions.jsonl
so we can track local-vs-public score drift over time.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBLEMS_DIR = REPO_ROOT / "problems"
RUNS_DIR = REPO_ROOT / "runs"

sys.path.insert(0, str(REPO_ROOT))
from problems._shared.constants import (  # noqa: E402
    KAGGLE_API_TOKEN_ENV,
    DATA_SUBDIR,
    KAGGLE_SPEC_FILENAME,
)


def _check_token():
    if not os.environ.get(KAGGLE_API_TOKEN_ENV):
        print(f"ERROR: {KAGGLE_API_TOKEN_ENV} not set", file=sys.stderr)
        sys.exit(2)


def _load_spec(problem_id: str) -> dict:
    import yaml
    spec_path = PROBLEMS_DIR / problem_id / DATA_SUBDIR / KAGGLE_SPEC_FILENAME
    if not spec_path.exists():
        print(f"ERROR: {spec_path} missing", file=sys.stderr)
        sys.exit(1)
    return yaml.safe_load(spec_path.read_text()) or {}


def _load_helpers(problem_id: str):
    helpers_path = PROBLEMS_DIR / problem_id / "helpers" / "core.py"
    spec = importlib.util.spec_from_file_location(f"{problem_id}_helpers", helpers_path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(PROBLEMS_DIR / problem_id))
    spec.loader.exec_module(mod)
    return mod


def _load_solution(solution_path: str):
    spec = importlib.util.spec_from_file_location("solution", solution_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if not hasattr(mod, "entrypoint"):
        raise ValueError(f"{solution_path} missing entrypoint()")
    return mod.entrypoint


def _latest_attempt(problem_id: str) -> Path | None:
    p = RUNS_DIR / problem_id
    if not p.exists():
        return None
    attempts = sorted([d for d in p.iterdir() if d.is_dir()])
    return attempts[-1] if attempts else None


def _poll_score(comp_id: str, message: str, deadline_s: int = 120) -> float | None:
    """Poll `kaggle competitions submissions` for our submission's public score."""
    deadline = time.time() + deadline_s
    while time.time() < deadline:
        res = subprocess.run(
            ["kaggle", "competitions", "submissions", comp_id, "-q"],
            capture_output=True, text=True,
        )
        if res.returncode == 0:
            for line in res.stdout.splitlines():
                if message in line:
                    parts = [c for c in line.split() if c]
                    for c in parts:
                        try:
                            return float(c)
                        except ValueError:
                            continue
        time.sleep(10)
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("problem_id")
    ap.add_argument("solution")
    ap.add_argument("--message", default=None, help="Submission tag (default: solution filename + utc).")
    args = ap.parse_args()

    _check_token()
    spec = _load_spec(args.problem_id)
    if spec.get("classification") not in ("C",):
        print(
            f"WARNING: classification={spec.get('classification')!r}. submit_to_kaggle is intended\n"
            f"for Class C problems (hidden test set). Class A/B problems already have\n"
            f"perfect-fidelity local scoring.",
            file=sys.stderr,
        )
    comp_id = spec["competition_id"]

    helpers = _load_helpers(args.problem_id)
    if not hasattr(helpers, "write_submission"):
        print(
            f"ERROR: {args.problem_id}/helpers/core.py must define\n"
            f"  write_submission(predictions, path) -> None\n"
            f"to translate entrypoint() output into Kaggle's submission format.",
            file=sys.stderr,
        )
        return 1

    entrypoint = _load_solution(args.solution)
    print(f"Running {args.solution} entrypoint() ...")
    # Some entrypoints accept an optional `full=True` to force the full test
    # set; others ignore kwargs. Inspect the signature and pass when accepted.
    import inspect
    sig = inspect.signature(entrypoint)
    if "full" in sig.parameters:
        predictions = entrypoint(full=True)
    else:
        predictions = entrypoint()
    sub_path = Path("/tmp") / f"submission_{args.problem_id}_{int(time.time())}.csv"
    helpers.write_submission(predictions, sub_path)
    print(f"Wrote {sub_path}")

    msg = args.message or f"{Path(args.solution).name} {datetime.now(timezone.utc).isoformat(timespec='seconds')}"
    print(f"Submitting to {comp_id} with message: {msg!r}")
    res = subprocess.run(
        ["kaggle", "competitions", "submit", "-c", comp_id, "-f", str(sub_path), "-m", msg],
        capture_output=True, text=True,
    )
    print(res.stdout)
    if res.returncode != 0:
        print(res.stderr, file=sys.stderr)
        return 1

    print("Polling for score (up to 2 min) ...")
    score = _poll_score(comp_id, msg)
    print(f"Public LB score: {score}")

    attempt_dir = _latest_attempt(args.problem_id)
    if attempt_dir:
        log_path = attempt_dir / "kaggle_submissions.jsonl"
        log_path.write_text(
            (log_path.read_text() if log_path.exists() else "")
            + json.dumps({
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "solution": args.solution,
                "message": msg,
                "public_score": score,
            }) + "\n"
        )
        print(f"Logged to {log_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
