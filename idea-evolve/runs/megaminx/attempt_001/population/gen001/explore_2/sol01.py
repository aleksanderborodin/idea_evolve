# fitness: TBD
"""Path compression approach: shorten sample_submission paths via cancellation + local search.

Key insight: sample_submission paths are the inverse of random walks used to generate
the scrambles. Random walks have many X.-X cancellations that can be removed for free.

Strategy:
1. Start with sample_submission (guaranteed valid)
2. Apply basic inverse cancellation: X.-X -> empty
3. Try random restart local search on hard puzzles to find shorter paths
4. Fall back to sample_submission if search fails

This is a Track B radical exploration - testing whether local path editing/compression
can generate non-trivial wins below the 50572 floor.
"""

from __future__ import annotations


def entrypoint() -> dict:
    from helpers.core import (
        load_test,
        load_sample_submission_paths,
        apply_path,
        is_solved,
        GENERATOR_SET,
        solved_state,
        score_path,
        SENTINEL_ROW_SCORE,
    )
    import random

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()
    solved = solved_state()

    def cancel_path(path: str) -> str:
        """Remove X.-X inverse cancellations greedily left-to-right."""
        if not path:
            return path
        moves = path.split(".")
        result = []
        for m in moves:
            if not m:
                continue
            if result and result[-1] == inverse_move(m):
                result.pop()
            else:
                result.append(m)
        return ".".join(result)

    def inverse_move(m: str) -> str:
        """Return the inverse of a move."""
        if m.startswith("-"):
            return m[1:]
        return f"-{m}"

    def local_search(initial, target_depth, max_iters=200, restarts=3):
        """Try to find a shorter path via random local search."""
        best_path = ""
        best_len = SENTINEL_ROW_SCORE

        for _ in range(restarts):
            path = sample.get(initial[0] if isinstance(initial, tuple) else initial, "")
            if not path:
                continue
            # Try cancellation first
            path = cancel_path(path)

            # Random local search: at each step, try a small perturbation
            for _ in range(max_iters):
                moves = path.split(".") if path else []
                if len(moves) < 2:
                    break

                # Pick a random window and try to shorten it
                i = random.randint(0, len(moves) - 2)
                # Try removing 1-3 moves and see if we can find a shorter valid path
                for remove_len in [1, 2, 3]:
                    if i + remove_len > len(moves):
                        continue
                    new_moves = moves[:i] + moves[i + remove_len:]
                    new_path = ".".join(new_moves)
                    if not new_path:
                        continue
                    try:
                        final = apply_path(initial, new_path)
                    except:
                        continue
                    if is_solved(final):
                        path = new_path
                        break

            plen = len(path.split(".")) if path else 0
            if plen < best_len:
                best_len = plen
                best_path = path

        return best_path if best_len < SENTINEL_ROW_SCORE else None

    results = {}
    for sid, init_state in tests.items():
        sample_path = sample.get(sid, "")
        if not sample_path:
            results[sid] = ""
            continue

        # Apply cancellation first
        compressed = cancel_path(sample_path)

        # For deeper puzzles (depth > 50), try local search
        # to find a shorter path
        if sid > 50:
            search_path = local_search(init_state, sid, max_iters=100, restarts=2)
            if search_path:
                # Verify the searched path is valid and shorter
                try:
                    final = apply_path(init_state, search_path)
                    if is_solved(final):
                        search_len = len(search_path.split("."))
                        compressed_len = len(compressed.split(".")) if compressed else 0
                        if search_len < compressed_len:
                            compressed = search_path
                except:
                    pass

        # Fall back to sample_submission if our compressed path is worse
        sample_len = len(sample_path.split(".")) if sample_path else 0
        compressed_len = len(compressed.split(".")) if compressed else 0

        if compressed_len > 0 and compressed_len <= sample_len:
            # Verify compressed path is still valid
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