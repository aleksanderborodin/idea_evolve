#!/usr/bin/env python3
"""Run a direct hamming-predictor Megaminx proxy experiment.

Tests exactly one independent variable: using cayleypy's built-in hamming
predictor in beam search instead of the unguided helper path. All other pieces
stay fixed: same proxy set, same fallback policy, same scoring function.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path("/home/sasha/Desktop/idea_evolve/idea-evolve")
PROBLEM_ROOT = ROOT / "problems" / "megaminx"
OUTPUT_ROOT = Path(
    "/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/"
    "workspace/gen002_experimentator_1/output"
)

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PROBLEM_ROOT) not in sys.path:
    sys.path.insert(0, str(PROBLEM_ROOT))

import cayleypy  # type: ignore
from cayleypy import Predictor  # type: ignore

from helpers.core import apply_path
from helpers.core import depth_bucket
from helpers.core import is_solved
from helpers.core import load_sample_submission_paths
from helpers.core import load_test
from helpers.core import score_predictions


def _inverse(move: str) -> str:
    if move.startswith("-"):
        return move[1:]
    return f"-{move}"


def cancel_moves(path: str) -> str:
    if not path:
        return path
    stack: list[str] = []
    for move in path.split("."):
        if not move:
            continue
        if stack and stack[-1] == _inverse(move):
            stack.pop()
        else:
            stack.append(move)
    return ".".join(stack)


def _to_kaggle_name(cname: str) -> str:
    s = cname[2:] if cname.startswith("M_") else cname
    if s.endswith("_inv"):
        return f"-{s[:-4]}"
    return s


def _result_to_path(result, generator_names: list[str]) -> str | None:
    if not getattr(result, "path_found", False):
        return None
    cay_path = result.path or []
    moves = [_to_kaggle_name(generator_names[idx]) for idx in cay_path]
    return ".".join(moves)


def run_experiment(beam_width: int = 2000, max_steps: int = 200) -> dict:
    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()
    compressed_sample = {sid: cancel_moves(path) for sid, path in sample_paths.items()}

    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef)
    predictor = Predictor(graph, "hamming")
    generator_names = list(gdef.generator_names)

    predictions: dict[int, str] = {}
    per_sid_rows: list[dict[str, object]] = []

    started = time.perf_counter()
    for sid, init_state in tests.items():
        bucket = depth_bucket(sid)
        fallback = compressed_sample[sid]
        fallback_len = 0 if not fallback else len(fallback.split("."))

        search_started = time.perf_counter()
        result = graph.beam_search(
            start_state=list(init_state),
            beam_width=beam_width,
            max_steps=max_steps,
            predictor=predictor,
            return_path=True,
        )
        search_elapsed = time.perf_counter() - search_started

        search_path = _result_to_path(result, generator_names)
        search_valid = False
        search_len = None
        used = "fallback"

        if search_path:
            search_valid = is_solved(apply_path(init_state, search_path))
            if search_valid:
                search_len = 0 if not search_path else len(search_path.split("."))
                if search_len < fallback_len:
                    predictions[sid] = search_path
                    used = "predictor"
                else:
                    predictions[sid] = fallback
            else:
                predictions[sid] = fallback
        else:
            predictions[sid] = fallback

        final_len = 0 if not predictions[sid] else len(predictions[sid].split("."))
        per_sid_rows.append(
            {
                "sid": sid,
                "bucket": bucket,
                "fallback_length": fallback_len,
                "search_found": bool(getattr(result, "path_found", False)),
                "search_valid": search_valid,
                "search_length": search_len,
                "used": used,
                "final_length": final_len,
                "saved_vs_fallback": fallback_len - final_len,
                "search_time_s": round(search_elapsed, 4),
            }
        )

    total_elapsed = time.perf_counter() - started
    fitness, is_valid, aux = score_predictions(predictions, proxy=True)

    improved_by_predictor = sum(1 for row in per_sid_rows if row["used"] == "predictor")
    summary = {
        "question": "Does the zero-cost hamming predictor beat the 46312 compression floor on the 101-puzzle proxy?",
        "beam_width": beam_width,
        "max_steps": max_steps,
        "fitness": fitness,
        "is_valid": is_valid,
        "runtime_s": round(total_elapsed, 4),
        "predictor_win_rows": improved_by_predictor,
        **aux,
    }
    return {
        "summary": summary,
        "predictions": predictions,
        "per_sid_rows": per_sid_rows,
    }


def write_outputs(result: dict) -> None:
    data_dir = OUTPUT_ROOT / "sandbox" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    (data_dir / "hamming_predictor_summary.json").write_text(
        json.dumps(result["summary"], indent=2)
    )
    (data_dir / "hamming_predictor_predictions.json").write_text(
        json.dumps(result["predictions"], indent=2)
    )

    rows = result["per_sid_rows"]
    with (data_dir / "hamming_predictor_per_sid.csv").open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "sid",
                "bucket",
                "fallback_length",
                "search_found",
                "search_valid",
                "search_length",
                "used",
                "final_length",
                "saved_vs_fallback",
                "search_time_s",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    result = run_experiment()
    write_outputs(result)
    print(json.dumps(result["summary"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
