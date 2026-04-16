"""Hybrid solver: beam search + compression + best-of approach.

For each puzzle:
1. Try cayleypy beam solver with good parameters
2. Compress the beam result
3. Also compress the sample_submission path
4. Return whichever is shorter (or sample if beam fails)

This ensures we always get the best available path.
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
        solved_state,
    )

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()
    solved = solved_state()

    results = {}

    for sid, initial_state in tests.items():
        bucket = depth_bucket(sid)

        beam_path = None
        if bucket in ("special", "short", "medium"):
            beam_path = solve_with_beam(initial_state, beam_width=2000, max_steps=150)

        sample_compressed = compress_path(sample[sid]) if sample[sid] else ""

        if beam_path:
            beam_compressed = compress_path(beam_path)
            beam_len = len(beam_compressed.split(".")) if beam_compressed else 999999
            sample_len = len(sample_compressed.split(".")) if sample_compressed else 999999
            if beam_len <= sample_len:
                results[sid] = beam_compressed
            else:
                results[sid] = sample_compressed
        else:
            results[sid] = sample_compressed

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


def solve_with_beam(initial_state, beam_width: int = 2000, max_steps: int = 150) -> str | None:
    """Solve using cayleypy beam search. Returns dot-joined path or None."""
    try:
        path = cayleypy_beam_solver(
            initial_state,
            beam_width=beam_width,
            max_steps=max_steps,
        )
        if path and is_valid_path(initial_state, path):
            return path
        return None
    except Exception:
        return None


def is_valid_path(initial_state, path: str) -> bool:
    """Check if a path actually solves the puzzle."""
    from helpers.core import apply_path, is_solved, solved_state
    try:
        final = apply_path(initial_state, path)
        return is_solved(final)
    except Exception:
        return False