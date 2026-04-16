# fitness: INVALID

"""
Aggressive multi-pass algebraic compression.

Key insight: overlapping patterns matter. A sequence like:
  A B A^{-1} B^{-1} C D C^{-1} D^{-1}
Contains TWO overlapping commutators. A single-pass longest-match
will miss the second one. We use multiple passes and substring
replacement to catch all occurrences.
"""

from collections import Counter
from helpers.core import (
    load_test,
    load_sample_submission_paths,
    apply_path,
    is_solved,
    solved_state,
    GENERATOR_NAMES,
)


def entrypoint() -> dict:
    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()

    # Build rule dictionary
    rules = _build_all_rules(sample_paths)
    print(f"Built {len(rules)} compression rules")

    # Apply with multi-pass substring replacement
    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        compressed_sid = _multi_pass_compress(original, rules)
        if is_solved(apply_path(state, compressed_sid)):
            compressed[sid] = compressed_sid
        else:
            compressed[sid] = original

    return compressed


def _build_all_rules(sample_paths: dict) -> dict:
    """Build compression rules from both systematic enumeration and empirical mining."""
    rules = {}
    SOLVED = solved_state()

    # Systematic: commutators and conjugations that equal identity
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv2 = _inverse(gen2)

            # Commutator: ABA^{-1}B^{-1} -> identity
            pattern = (gen1, gen2, inv1, inv2)
            try:
                if apply_path(SOLVED, '.'.join(pattern)) == SOLVED:
                    rules[pattern] = ()
            except:
                pass

            # Conjugation: ABA^{-1} -> B (if true)
            short_pattern = (gen1, gen2, inv1)
            try:
                effect = apply_path(SOLVED, '.'.join(short_pattern))
                b_effect = apply_path(SOLVED, gen2)
                if effect == b_effect:
                    rules[short_pattern] = (gen2,)
            except:
                pass

            # XYX^{-1} with various targets
            for target in [(), (gen2,), (_inverse(gen2),)]:
                if target == short_pattern:
                    continue
                try:
                    if apply_path(SOLVED, '.'.join(short_pattern)) == (
                        solved_state() if not target else apply_path(SOLVED, '.'.join(target))
                    ):
                        rules[short_pattern] = target
                except:
                    pass

    # Double cancellation
    for gen in GENERATOR_NAMES:
        try:
            if apply_path(SOLVED, f"{gen}.{gen}") == SOLVED:
                rules[(gen, gen)] = ()
        except:
            pass

    # Empirical: patterns from sample_submission that compress
    # Look for patterns of span 2-6 that appear frequently
    subseq_counts = Counter()
    subseq_effects = {}

    for path in sample_paths.values():
        if not path:
            continue
        moves = path.split('.')
        for start in range(len(moves)):
            for length in range(2, 7):
                if start + length > len(moves):
                    break
                subseq = tuple(moves[start:start+length])
                subseq_str = '.'.join(subseq)
                subseq_counts[subseq_str] += 1
                if subseq_str not in subseq_effects:
                    try:
                        subseq_effects[subseq_str] = apply_path(SOLVED, subseq_str)
                    except:
                        pass

    # Filter empirical patterns
    for pattern_str, count in subseq_counts.items():
        if count < 20:  # Require high frequency
            continue
        effect = subseq_effects.get(pattern_str)
        if effect is None:
            continue
        if effect != SOLVED:
            continue
        pattern = tuple(pattern_str.split('.'))
        # Check if this is a NEW pattern (not already covered)
        if pattern not in rules:
            rules[pattern] = ()

    return rules


def _multi_pass_compress(path: str, rules: dict) -> str:
    """Multi-pass compression using substring replacement."""
    if not path:
        return path

    # Sort rules by length (longest first) for greedy matching
    sorted_rules = sorted(rules.keys(), key=len, reverse=True)

    max_passes = 100
    for pass_num in range(max_passes):
        prev = path
        moves = path.split('.')

        # Pass 1: X.-X cancellation
        moves = _cancel_moves(moves)

        # Pass 2: Apply all identity rules via substring replacement
        moves_str = '.'.join(moves)
        for pattern in sorted_rules:
            replacement = rules[pattern]
            pattern_str = '.'.join(pattern)
            if replacement:
                repl_str = '.'.join(replacement)
            else:
                repl_str = ''

            # Replace all occurrences
            if pattern_str in moves_str:
                moves_str = moves_str.replace(pattern_str, repl_str)

        moves = moves_str.split('.')
        moves = [m for m in moves if m]  # Remove empty strings
        moves = _cancel_moves(moves)
        path = '.'.join(moves)

        if path == prev:
            break

    return path


def _cancel_moves(moves: list) -> list:
    """Standard X.-X cancellation."""
    stack = []
    for m in moves:
        if not m:
            continue
        if stack and stack[-1] == _inverse(m):
            stack.pop()
        else:
            stack.append(m)
    return stack


def _inverse(move: str) -> str:
    if move.startswith('-'):
        return move[1:]
    return f'-{move}'


