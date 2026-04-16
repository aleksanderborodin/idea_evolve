"""Improved MITM solver with better pruning for Megaminx.

Strategy:
1. Move cancellation on sample_submission paths (free improvement)
2. Bidirectional BFS for short puzzles (depth <= 25) with depth limit 5
3. Deeper BFS for medium puzzles (depth 26-100) with depth limit 8, beam pruning
4. Fall back to compressed sample_submission if search fails

Key optimizations:
- Prune backward frontier to only keep best (shortest) path per state
- Limit total states per depth level to prevent memory explosion
- Use move cancellation iteratively
"""

from __future__ import annotations

from collections import deque
from functools import lru_cache


def entrypoint() -> dict:
    from helpers.core import (
        GENERATOR_NAMES,
        apply_path,
        depth_bucket,
        is_solved,
        load_sample_submission_paths,
        load_test,
        solved_state,
    )

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()

    results = {}

    for sid, initial_state in tests.items():
        bucket = depth_bucket(sid)

        path = sample[sid]

        if bucket == "special":
            solved_path = mitm_solve(initial_state, max_depth=5, beam_size=5000)
            if solved_path:
                path = solved_path
        elif bucket == "short":
            solved_path = mitm_solve(initial_state, max_depth=6, beam_size=3000)
            if solved_path:
                path = solved_path
        elif bucket == "medium":
            solved_path = mitm_solve(initial_state, max_depth=8, beam_size=1000)
            if solved_path:
                path = solved_path

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


def mitm_solve(initial_state: tuple, max_depth: int = 5, beam_size: int = 5000) -> str | None:
    """Meet-in-the-middle BFS solver with beam pruning.

    Searches forward from initial_state and backward from solved_state.
    Returns a dot-joined path string, or None if no solution found.
    """
    from helpers.core import GENERATOR_NAMES, apply_move, solved_state

    solved = solved_state()

    if initial_state == solved:
        return ""

    inverse_moves = {name: name[1:] if name.startswith("-") else f"-{name}"
                     for name in GENERATOR_NAMES}

    forward_visited: dict[tuple, tuple] = {initial_state: ()}
    backward_visited: dict[tuple, tuple] = {solved: ()}

    forward_queue = deque([(initial_state, ())])
    backward_queue = deque([(solved, ())])

    forward_depth = 0
    backward_depth = 0

    while forward_queue or backward_queue:
        if forward_depth < max_depth and forward_queue:
            forward_depth += 1
            next_level = []
            for _ in range(len(forward_queue)):
                state, path = forward_queue.popleft()
                for move in GENERATOR_NAMES:
                    new_state = apply_move(state, move)
                    if new_state in forward_visited:
                        continue
                    new_path = path + (move,)
                    forward_visited[new_state] = new_path
                    next_level.append((new_state, new_path))
            forward_queue.extend(next_level[:beam_size])

        if backward_depth < max_depth and backward_queue:
            backward_depth += 1
            next_level = []
            for _ in range(len(backward_queue)):
                state, path = backward_queue.popleft()
                for move in GENERATOR_NAMES:
                    new_state = apply_move(state, move)
                    if new_state in backward_visited:
                        continue
                    new_path = path + (move,)
                    backward_visited[new_state] = new_path
                    next_level.append((new_state, new_path))
            backward_queue.extend(next_level[:beam_size])

        intersection = set(forward_visited.keys()) & set(backward_visited.keys())
        if intersection:
            meeting_state = next(iter(intersection))
            forward_path = forward_visited[meeting_state]
            backward_path = backward_visited[meeting_state]

            inv_backward = tuple(inverse_moves[m] for m in reversed(backward_path))

            full_path = forward_path + inv_backward
            return ".".join(full_path)

        if forward_depth + backward_depth >= max_depth:
            break

    return None