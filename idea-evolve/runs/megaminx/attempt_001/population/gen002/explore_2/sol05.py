# fitness: 44118

"""
Aggressive algebraic compression using move-list substitution.

This is the approach that worked in sol01 (44114) but made more aggressive:
1. Build comprehensive identity rules (commutators, conjugations, double moves)
2. Apply via longest-match-first on move lists (not string substitution)
3. Multiple passes until convergence
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

    rules = _build_comprehensive_rules(sample_paths)
    print(f"Built {len(rules)} compression rules")

    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        compressed_sid = _compress_path(original, rules)
        if is_solved(apply_path(state, compressed_sid)):
            compressed[sid] = compressed_sid
        else:
            compressed[sid] = original

    return compressed


def _build_comprehensive_rules(sample_paths: dict) -> dict:
    """Build rules from systematic enumeration and empirical mining."""
    SOLVED = solved_state()
    rules = {}

    # Type 1: Commutators [A,B] = ABA^{-1}B^{-1} -> identity
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv2 = _inverse(gen2)
            pattern = (gen1, gen2, inv1, inv2)
            try:
                if apply_path(SOLVED, '.'.join(pattern)) == SOLVED:
                    rules[pattern] = ()
            except:
                pass

    # Type 2: Conjugations ABA^{-1} -> B (if true in Megaminx)
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            pattern = (gen1, gen2, inv1)
            try:
                effect = apply_path(SOLVED, '.'.join(pattern))
                b_effect = apply_path(SOLVED, gen2)
                if effect == b_effect:
                    rules[pattern] = (gen2,)
            except:
                pass

    # Type 3: Double cancellation XX -> identity
    for gen in GENERATOR_NAMES:
        pattern = (gen, gen)
        try:
            if apply_path(SOLVED, '.'.join(pattern)) == SOLVED:
                rules[pattern] = ()
        except:
            pass

    # Type 4: Span-2 patterns XZX^{-1} -> simplified form
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            pattern = (gen1, gen2, inv1)
            try:
                effect = apply_path(SOLVED, '.'.join(pattern))
                for target in [(), (gen2,), (_inverse(gen2),)]:
                    if not target:
                        target_effect = SOLVED
                    else:
                        target_effect = apply_path(SOLVED, '.'.join(target))
                    if effect == target_effect and len(pattern) > len(target):
                        rules[pattern] = target
            except:
                pass

    # Type 5: Span-3 patterns XYZ^{-1}X^{-1}Y^{-1} -> identity
    # This is [X,Y,Z] triple commutator - very expensive to enumerate
    # Skip for now

    # Type 6: Empirical patterns from sample_submission
    # Look for patterns of length 2-5 that equal identity
    subseq_counts = Counter()
    subseq_effects = {}

    for path in sample_paths.values():
        if not path:
            continue
        moves = path.split('.')
        for start in range(len(moves)):
            for length in range(2, 6):
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

    for pattern_str, count in subseq_counts.items():
        if count < 10:
            continue
        effect = subseq_effects.get(pattern_str)
        if effect is None:
            continue
        if effect != SOLVED:
            continue
        pattern = tuple(pattern_str.split('.'))
        # Only add if longer than 2 (XX patterns handled above)
        if len(pattern) <= 2:
            continue
        if pattern not in rules:
            rules[pattern] = ()

    return rules


def _compress_path(path: str, rules: dict) -> str:
    """Apply compression rules via longest-match-first on move lists."""
    if not path:
        return path

    # Sort rules by length (longest first) for greedy matching
    sorted_rules = sorted(rules.keys(), key=len, reverse=True)

    max_passes = 50
    for _ in range(max_passes):
        prev = path
        moves = path.split('.')
        moves = [m for m in moves if m]  # Remove empty strings

        # Apply X.-X cancellation first
        moves = _cancel_moves(moves)

        # Apply identity rules (longest match first)
        moves = _apply_rules_ml(moves, sorted_rules, rules)

        path = '.'.join(moves)
        if path == prev:
            break

    return path


def _apply_rules_ml(moves: list, sorted_rules: list, rules: dict) -> list:
    """Apply rules to move list using longest-match-first."""
    if not moves:
        return moves

    result = []
    i = 0
    while i < len(moves):
        matched = False
        # Try longest patterns first
        for plen in range(min(5, len(moves) - i), 1, -1):
            window = tuple(moves[i:i + plen])
            if window in rules:
                replacement = rules[window]
                result.extend(replacement)
                i += plen
                matched = True
                # Cancel after each replacement
                result = _cancel_moves(result)
                break
        if not matched:
            result.append(moves[i])
            i += 1

    return result


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