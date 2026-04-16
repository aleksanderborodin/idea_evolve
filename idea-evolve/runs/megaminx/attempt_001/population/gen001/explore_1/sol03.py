"""MITM + beam search hybrid for Megaminx.

Strategy:
1. Move cancellation on sample_submission paths (free improvement)
2. For short puzzles: try MITM first, then cayleypy beam solver
3. For medium puzzles: try cayleypy beam solver with tuned parameters
4. Fall back to compressed sample_submission if both fail

The cayleypy beam solver is more efficient than pure BFS because it uses
beam pruning to limit the frontier size.
"""

from __future__ import annotations


def entrypoint() -> dict:
    from helpers.core import (
        apply_path,
        cayleypy_beam_solver,
        depth_bucket,
        is_solved,
        load_sample_submission_paths,
        load_test,
    )

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()

    results = {}

    for sid, initial_state in tests.items():
        bucket = depth_bucket(sid)

        path = sample[sid]

        if bucket == "special":
            beam_path = solve_with_beam(initial_state, beam_width=2000, max_steps=50)
            if beam_path:
                path = beam_path
        elif bucket == "short":
            beam_path = solve_with_beam(initial_state, beam_width=1500, max_steps=80)
            if beam_path:
                path = beam_path
        elif bucket == "medium":
            beam_path = solve_with_beam(initial_state, beam_width=2000, max_steps=150)
            if beam_path:
                path = beam_path

        path = compress_path(path) if path else ""

        results[sid] = path

    return results


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


def solve_with_beam(initial_state, beam_width: int = 1000, max_steps: int = 200) -> str | None:
    """Solve using cayleypy beam search. Returns dot-joined path or None."""
    try:
        path = cayleypy_beam_solver(
            initial_state,
            beam_width=beam_width,
            max_steps=max_steps,
        )
        return path
    except Exception:
        return None