# fitness: 44118

"""
Combined algebraic compression: empirical pattern mining + formal identity verification.

Combines:
1. Empirical span-2 to span-5 pattern discovery from sample_submission
2. Formal identity verification (commutators, conjugations)
3. Iterative cancellation with longest-match-first replacement
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

    # Phase 1: Build identity dictionary from systematic enumeration
    identity_dict = _build_identity_dictionary()
    print(f"Systematic identities: {len(identity_dict)}")

    # Phase 2: Mine frequent patterns from sample_submission
    empirical_rules = _mine_empirical_rules(sample_paths)
    print(f"Empirical patterns: {len(empirical_rules)}")

    # Combine both rule sets
    all_rules = _combine_rules(identity_dict, empirical_rules)
    print(f"Combined rules: {len(all_rules)}")

    # Phase 3: Apply compression
    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        compressed_sid = _compress_with_rules(original, all_rules)
        if is_solved(apply_path(state, compressed_sid)):
            compressed[sid] = compressed_sid
        else:
            compressed[sid] = original

    return compressed


def _build_identity_dictionary() -> dict:
    """Systematically enumerate commutators, conjugations, double moves."""
    identities = {}
    SOLVED = solved_state()

    def try_identity(pattern: tuple, replacement: tuple) -> bool:
        try:
            pattern_str = '.'.join(pattern)
            if replacement:
                replacement_str = '.'.join(replacement)
                pe = apply_path(SOLVED, pattern_str)
                re = apply_path(SOLVED, replacement_str)
                return pe == re
            else:
                return apply_path(SOLVED, pattern_str) == SOLVED
        except:
            return False

    # Double cancellation: AA -> identity
    for gen in GENERATOR_NAMES:
        pattern = (gen, gen)
        if try_identity(pattern, ()):
            identities[pattern] = ()

    # Commutators: ABABA^{-1}B^{-1} type
    for i, gen1 in enumerate(GENERATOR_NAMES):
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv2 = _inverse(gen2)

            # ABA^{-1}B^{-1}
            pattern = (gen1, gen2, inv1, inv2)
            if try_identity(pattern, ()):
                identities[pattern] = ()

    # Conjugations: ABA^{-1} -> B
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            pattern = (gen1, gen2, inv1)
            if try_identity(pattern, (gen2,)):
                identities[pattern] = (gen2,)

    # Span-2: XYX^{-1} -> Y or -Y or identity
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            pattern = (gen1, gen2, inv1)
            for simplified in [(), (gen2,), (_inverse(gen2),)]:
                if simplified == pattern:
                    continue
                if try_identity(pattern, simplified):
                    identities[pattern] = simplified

    return identities


def _mine_empirical_rules(sample_paths: dict, min_count: int = 10) -> dict:
    """Mine frequent patterns from sample_submission that equal identity."""
    SOLVED = solved_state()
    subseq_counts = Counter()
    subseq_effects = {}

    for path in sample_paths.values():
        if not path:
            continue
        moves_list = path.split('.')
        for start in range(len(moves_list)):
            for length in range(2, 6):
                if start + length > len(moves_list):
                    break
                subseq = tuple(moves_list[start:start+length])
                subseq_str = '.'.join(subseq)
                subseq_counts[subseq_str] += 1
                if subseq_str not in subseq_effects:
                    try:
                        effect = apply_path(SOLVED, subseq_str)
                        subseq_effects[subseq_str] = effect
                    except:
                        pass

    # Find patterns that appear frequently and equal identity
    rules = {}
    for pattern_str, count in subseq_counts.items():
        if count < min_count:
            continue
        effect = subseq_effects.get(pattern_str)
        if effect is None:
            continue
        if effect != SOLVED:
            continue
        # Verify this actually compresses
        moves = pattern_str.split('.')
        # Check if the pattern has redundancy
        if len(moves) < 3:
            continue
        pattern = tuple(moves)
        # Only keep patterns that have at least 2 moves of savings
        savings = len(moves) - _shortest_equivalent(pattern)
        if savings >= 1:
            rules[pattern] = ()

    return rules


def _shortest_equivalent(pattern: tuple) -> int:
    """Find the shortest path equivalent to this pattern (brute force for small patterns)."""
    if len(pattern) <= 1:
        return len(pattern)
    SOLVED = solved_state()
    try:
        effect = apply_path(SOLVED, '.'.join(pattern))
        if effect == SOLVED:
            return 0  # Identity = shortest possible
    except:
        pass
    return len(pattern)


def _combine_rules(identity_dict: dict, empirical_rules: dict) -> dict:
    """Combine systematic and empirical rules, prioritizing by specificity."""
    combined = {}

    # Add all systematic identities
    for k, v in identity_dict.items():
        combined[k] = v

    # Add empirical rules that aren't already covered
    for k, v in empirical_rules.items():
        if k not in combined:
            combined[k] = v

    return combined


def _compress_with_rules(path: str, rules: dict) -> str:
    """Apply longest-match identity rules iteratively."""
    if not path:
        return path

    max_iters = 50
    for _ in range(max_iters):
        prev = path
        moves = path.split('.')
        moves = _cancel_moves(moves)
        moves = _apply_longest_match(moves, rules)
        path = '.'.join(moves)
        if path == prev:
            break

    return path


def _apply_longest_match(moves: list, rules: dict) -> list:
    """Apply the longest matching identity rule."""
    if not moves:
        return moves

    result = []
    i = 0
    while i < len(moves):
        matched = False
        for plen in range(min(6, len(moves) - i), 1, -1):
            window = tuple(moves[i:i + plen])
            if window in rules:
                replacement = rules[window]
                result.extend(replacement)
                i += plen
                matched = True
                # Cancel after replacement
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