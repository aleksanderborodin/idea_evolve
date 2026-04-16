# fitness: TBD
"""Midpoint repair approach: split paths and search for shorter bridges.

Key insight from initial_ideas.md: "Path stitching - split sample[sid] at the
midpoint, search from both endpoints toward center, and splice if you find a
shorter bridge."

Strategy:
1. Start with sample_submission (guaranteed valid)
2. For each path, split at midpoint
3. Try to find a shorter path from start -> midpoint and from midpoint -> end
4. Use the sample_submission as the bridge if we can't find better
5. Apply cancellation to the result
"""

from __future__ import annotations


def entrypoint() -> dict:
    from helpers.core import (
        load_test,
        load_sample_submission_paths,
        apply_path,
        apply_move,
        is_solved,
        solved_state,
        GENERATOR_SET,
    )
    import random

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()
    solved = solved_state()

    def inverse_move(m: str) -> str:
        if m.startswith("-"):
            return m[1:]
        return f"-{m}"

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

    def apply_half_path(state, moves_str: str):
        """Apply a half-path (from start to midpoint or midpoint to end)."""
        if not moves_str:
            return state
        return apply_path(state, moves_str)

    def midpoint_repair(init_state, path: str, budget=50) -> str:
        """Try to find a shorter bridge at the midpoint."""
        if not path:
            return path
        moves = path.split(".")
        if len(moves) < 6:
            return path

        # Split at midpoint
        mid = len(moves) // 2
        first_half = ".".join(moves[:mid])
        second_half = ".".join(moves[mid:])

        mid_state = apply_half_path(init_state, first_half)
        end_state = apply_half_path(mid_state, second_half)

        # If midpoint state equals end state, first_half already reaches end
        # This means the path is already optimal from start to mid
        if is_solved(end_state):
            # The path solves the puzzle - check if first half alone also solves
            if is_solved(apply_half_path(init_state, first_half)):
                # First half alone solves - the second half is unnecessary
                return first_half
            # Otherwise return original
            return path

        # Try random bridges from midpoint to near-solved state
        # This is a simplified version - full implementation would use beam search
        best = path
        best_len = len(moves)

        generators = list(GENERATOR_SET)

        for _ in range(budget):
            # Random walk from midpoint toward solved
            state = mid_state
            bridge_moves = []
            for __ in range(10):  # Max 10 moves in bridge
                m = random.choice(generators)
                try:
                    state = apply_move(state, m)
                    bridge_moves.append(m)
                    if is_solved(state):
                        # Found a path to solved
                        break
                except:
                    break

            if is_solved(state):
                # Construct new path: first_half + bridge
                new_path = first_half
                if bridge_moves:
                    new_path = first_half + "." + ".".join(bridge_moves)
                new_path = cancel_path(new_path)
                new_moves = new_path.split(".") if new_path else []
                if len(new_moves) < best_len:
                    # Verify
                    try:
                        final = apply_path(init_state, new_path)
                        if is_solved(final):
                            best = new_path
                            best_len = len(new_moves)
                    except:
                        pass

        return best

    results = {}
    for sid, init_state in tests.items():
        sample_path = sample.get(sid, "")
        if not sample_path:
            results[sid] = ""
            continue

        # First apply basic cancellation
        compressed = cancel_path(sample_path)

        # Try midpoint repair for deeper puzzles
        if sid > 100 and len(compressed.split(".")) > 20:
            repaired = midpoint_repair(init_state, compressed, budget=30)
            if repaired:
                try:
                    final = apply_path(init_state, repaired)
                    if is_solved(final):
                        if len(repaired.split(".")) < len(compressed.split(".")):
                            compressed = repaired
                except:
                    pass

        # Final cancellation
        compressed = cancel_path(compressed)

        # Verify
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