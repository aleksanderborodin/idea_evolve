# fitness: TBD
"""Optimized cancellation: multiple passes with optimization for different depths.

Key insight: basic cancellation achieves ~8.4% compression. To do better,
we need to find structural patterns, not just X.-X pairs.

Approach:
1. Multi-pass iterative cancellation (already proven to work)
2. For short puzzles (depth < 50): try beam search with very small beam
3. For deeper puzzles: stick with aggressive cancellation
4. Always validate before accepting a compressed path
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
        cayleypy_beam_solver,
    )
    import random

    tests = load_test(proxy=True)
    sample = load_sample_submission_paths()
    solved = solved_state()

    def inverse_move(m: str) -> str:
        if m.startswith("-"):
            return m[1:]
        return f"-{m}"

    def cancel_iterative(path: str, max_iters=100) -> str:
        """Iterate bidirectional cancellation until fixed point."""
        if not path:
            return path
        moves = path.split(".")
        if not moves:
            return path

        for _ in range(max_iters):
            changed = False
            result = []
            i = 0
            while i < len(moves):
                if i + 1 < len(moves) and moves[i + 1] == inverse_move(moves[i]):
                    changed = True
                    i += 2
                else:
                    result.append(moves[i])
                    i += 1
            moves = result
            if not changed:
                break
        return ".".join(moves)

    def local_shorten(init_state, path: str, budget=100) -> str:
        """Try to shorten a valid path via random local search."""
        if not path:
            return path
        moves = path.split(".")
        if len(moves) < 4:
            return path

        best = moves[:]
        best_len = len(moves)

        generators = list(GENERATOR_SET)

        for _ in range(budget):
            if len(best) < 4:
                break

            # Pick two random cut points
            i = random.randint(0, len(best) - 2)
            j = random.randint(i + 2, min(i + 8, len(best)))

            # Try removing the window [i, j)
            new_moves = best[:i] + best[j:]
            if len(new_moves) >= best_len or len(new_moves) < 2:
                continue

            new_path = ".".join(new_moves)
            try:
                final = apply_path(init_state, new_path)
                if is_solved(final):
                    best = new_moves
                    best_len = len(new_moves)
            except:
                pass

        return ".".join(best)

    results = {}
    for sid, init_state in tests.items():
        sample_path = sample.get(sid, "")
        if not sample_path:
            results[sid] = ""
            continue

        # Step 1: aggressive cancellation
        compressed = cancel_iterative(sample_path)

        # Step 2: for shallow puzzles, try beam search
        if sid <= 50:
            # Try beam search for shallow puzzles
            beam_path = cayleypy_beam_solver(init_state, beam_width=256, max_steps=sid + 20)
            if beam_path:
                beam_compressed = cancel_iterative(beam_path)
                try:
                    final = apply_path(init_state, beam_compressed)
                    if is_solved(final):
                        if len(beam_compressed.split(".")) < len(compressed.split(".")):
                            compressed = beam_compressed
                except:
                    pass

        # Step 3: for all puzzles, try local shortening
        if len(compressed.split(".")) > 10:
            shortened = local_shorten(init_state, compressed, budget=50)
            try:
                final = apply_path(init_state, shortened)
                if is_solved(final):
                    if len(shortened.split(".")) < len(compressed.split(".")):
                        compressed = shortened
            except:
                pass

        # Final verification
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