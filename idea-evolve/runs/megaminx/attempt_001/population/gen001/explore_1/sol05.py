"""Multi-restart beam search + compression for Megaminx.

Strategy:
1. Move cancellation on sample paths (free improvement)
2. Run beam search multiple times with different parameters
3. Keep the shortest valid path found
4. Compare against compressed sample and use whichever is shorter
"""

from __future__ import annotations

import random


def entrypoint() -> dict:
    from helpers.core import (
        apply_path,
        cayleypy_beam_solver,
        depth_bucket,
        is_solved,
        load_sample_submission_paths,
        load_test,
        solved_state,
    )

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()
    solved = solved_state()

    results = {}

    for sid, initial_state in tests.items():
        bucket = depth_bucket(sid)

        best_path = sample[sid]

        if bucket in ("special", "short", "medium"):
            beam_path = multi_restart_beam(initial_state, bucket)
            if beam_path:
                if len(beam_path.split(".")) < len(best_path.split(".")):
                    best_path = beam_path

        best_path = compress_path(best_path) if best_path else ""

        results[sid] = best_path

    return results


def multi_restart_beam(initial_state, bucket: str, num_restarts: int = 3) -> str | None:
    """Run beam search multiple times with different parameters."""
    from helpers.core import apply_path, is_solved

    configs = [
        (3000, 200),
        (2000, 300),
        (4000, 150),
    ]

    best_path = None
    best_len = 999999

    for beam_width, max_steps in configs[:num_restarts]:
        try:
            path = cayleypy_beam_solver(
                initial_state,
                beam_width=beam_width,
                max_steps=max_steps,
            )
            if path:
                try:
                    final = apply_path(initial_state, path)
                    if is_solved(final):
                        path_len = len(path.split("."))
                        if path_len < best_len:
                            best_len = path_len
                            best_path = path
                except Exception:
                    pass
        except Exception:
            pass

    return best_path


def compress_path(path: str) -> str:
    """Remove adjacent X.-X cancellations from a path."""
    if not path:
        return ""

    moves = [m for m in path.split(".") if m]
    if not moves:
        return ""

    cancelled = True
    while cancelled and len(moves) > 1:
        cancelled = False
        new_moves = []
        i = 0
        while i < len(moves):
            if i + 1 < len(moves):
                m1, m2 = moves[i], moves[i + 1]
                if m1.startswith("-") and m1[1:] == m2:
                    i += 2
                    cancelled = True
                    continue
                elif m2.startswith("-") and m2[1:] == m1:
                    i += 2
                    cancelled = True
                    continue
            new_moves.append(moves[i])
            i += 1
        moves = new_moves

    return ".".join(moves)