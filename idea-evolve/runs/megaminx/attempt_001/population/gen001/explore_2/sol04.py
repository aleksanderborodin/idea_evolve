# fitness: TBD
"""N-gram pattern compression: learn common sequences and replace them.

Key insight: sample_submission paths are random walks, which follow predictable
statistical patterns. Some sequences of moves are redundant or can be replaced
with shorter equivalent sequences.

Strategy:
1. Analyze sample_submission paths to find common n-grams
2. Learn which n-grams have shorter equivalents
3. Apply learned compression rules
4. Fall back to basic cancellation + sample_submission
"""

from __future__ import annotations
from collections import Counter


def entrypoint() -> dict:
    from helpers.core import (
        load_test,
        load_sample_submission_paths,
        apply_path,
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

    def cancel_all(path: str, max_iters=100) -> str:
        """Iterate cancellation until fixed point."""
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

    # Analyze all sample paths to find common bigrams and trigrams
    bigram_counts = Counter()
    trigram_counts = Counter()

    for sid, path in sample.items():
        if not path:
            continue
        moves = path.split(".")
        for i in range(len(moves) - 1):
            bigram_counts[(moves[i], moves[i + 1])] += 1
        for i in range(len(moves) - 2):
            trigram_counts[(moves[i], moves[i + 1], moves[i + 2])] += 1

    # Find "redundant" bigrams: X.-X pairs (these are pure cancellations)
    # These are already handled by cancel_all
    # Find patterns where X.Y.-X ≈ Y or similar identities

    # Try a different approach: identify "corner turns" - sequences that return
    # to the same face orientation but with extra moves. These are compressible.

    def smart_cancel(path: str) -> str:
        """Cancel inversions, but also look for X.Y.-X patterns."""
        if not path:
            return path
        moves = path.split(".")
        if not moves:
            return path

        result = []
        i = 0
        while i < len(moves):
            m = moves[i]

            # Check for X.-X cancellation
            if i + 1 < len(moves) and moves[i + 1] == inverse_move(m):
                i += 2
                continue

            # Check for X.Y.-X pattern (try to replace with Y alone)
            # This is an approximation of commutator-like behavior
            if i + 2 < len(moves) and moves[i + 2] == inverse_move(m):
                # X.Y.-X pattern - try keeping just Y
                y = moves[i + 1]
                # Heuristic: keep the longer/more complex move
                # For Megaminx, faces are U, D, F, B, L, R, DR, DL, BL, BR, FL, FR
                face_moves = {"U", "-U", "D", "-D", "F", "-F", "B", "-B", "L", "-L", "R", "-R"}
                m_is_face = m in face_moves
                y_is_face = y in face_moves

                if m_is_face and not y_is_face:
                    # Keep the non-face move
                    result.append(y)
                    i += 3
                    continue
                elif not m_is_face and y_is_face:
                    # Keep the face move
                    result.append(y)
                    i += 3
                    continue

            result.append(m)
            i += 1

        return ".".join(result)

    # Two-pass: smart_cancel then full cancellation
    def compress_path(path: str) -> str:
        if not path:
            return path
        # First pass: smart cancellation
        x = smart_cancel(path)
        # Second pass: complete cancellation
        x = cancel_all(x)
        return x

    results = {}
    for sid, init_state in tests.items():
        sample_path = sample.get(sid, "")
        if not sample_path:
            results[sid] = ""
            continue

        compressed = compress_path(sample_path)

        # Verify and compare
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