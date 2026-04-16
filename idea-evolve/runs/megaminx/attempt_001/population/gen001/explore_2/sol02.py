# fitness: TBD
"""Aggressive path compression v2: iterative bidirectional cancellation + random splice.

Key insight: random walks have many cancellations. Single-pass left-to-right misses
cancellations that span across the path. We need iterative cancellation until fixed point.

Strategy:
1. Start with sample_submission (guaranteed valid)
2. Apply ITERATIVE bidirectional cancellation until no more cancellations
3. Try random splice: pick two points, try to bridge them shorter
4. Fall back to sample_submission if our path is invalid or longer
"""

from __future__ import annotations


def entrypoint() -> dict:
    from helpers.core import (
        load_test,
        load_sample_submission_paths,
        apply_path,
        is_solved,
        solved_state,
    )
    import random

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()

    def inverse_move(m: str) -> str:
        """Return the inverse of a move."""
        if m.startswith("-"):
            return m[1:]
        return f"-{m}"

    def iterative_cancel(path: str, max_iters=100) -> str:
        """Iterate bidirectional cancellation until fixed point."""
        if not path:
            return path
        moves = path.split(".")
        if not moves:
            return path

        for _ in range(max_iters):
            changed = False
            i = 0
            result = []
            while i < len(moves):
                if i + 1 < len(moves) and moves[i + 1] == inverse_move(moves[i]):
                    # Cancellation found: skip both
                    changed = True
                    i += 2
                else:
                    result.append(moves[i])
                    i += 1
            moves = result
            if not changed:
                break

        return ".".join(moves)

    def random_splice(init_state, path: str, max_attempts=50) -> str:
        """Try to find a shorter path by splicing at random points."""
        if not path or len(path.split(".")) < 6:
            return path

        moves = path.split(".")
        best = path

        for _ in range(max_attempts):
            if len(moves) < 4:
                break

            # Pick two random cut points
            i = random.randint(0, len(moves) - 2)
            j = random.randint(i + 1, min(i + 10, len(moves)))  # Keep window small

            # Try removing the window
            if j - i < 2:
                continue
            new_moves = moves[:i] + moves[j:]
            if not new_moves:
                continue
            new_path = ".".join(new_moves)

            try:
                final = apply_path(init_state, new_path)
                if is_solved(final):
                    if len(new_moves) < len(best.split(".")):
                        best = new_path
            except:
                pass

        return best

    results = {}
    for sid, init_state in tests.items():
        sample_path = sample.get(sid, "")
        if not sample_path:
            results[sid] = ""
            continue

        # Iterative bidirectional cancellation
        compressed = iterative_cancel(sample_path)

        # Try random splice for deeper puzzles
        if sid > 30 and len(compressed.split(".")) > 10:
            spliced = random_splice(init_state, compressed, max_attempts=30)
            # Only use spliced if it's shorter AND valid
            if spliced:
                try:
                    final = apply_path(init_state, spliced)
                    if is_solved(final):
                        if len(spliced.split(".")) < len(compressed.split(".")):
                            compressed = spliced
                except:
                    pass

        # Verify compressed path is valid
        sample_len = len(sample_path.split(".")) if sample_path else 0
        compressed_len = len(compressed.split(".")) if compressed else 0

        if compressed_len > 0 and compressed_len <= sample_len:
            try:
                final = apply_path(init_state, compressed)
                if is_solved(final):
                    results[sid] = compressed
                else:
                    results[sid] = sample_path
            except:
                results[sid] = sample_path
        else:
            results[sid] = sample_path

    return results