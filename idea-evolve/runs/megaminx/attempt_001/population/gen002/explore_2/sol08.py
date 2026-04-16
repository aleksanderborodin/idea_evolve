# fitness: 44114

"""
Bucket-aware algebraic compression.

Key insight: basic X.-X cancellation works universally.
But longer identities may only help for specific depth buckets.
Test this hypothesis: apply strong compression only to harder puzzles.
"""

from collections import Counter
from helpers.core import (
    load_test,
    load_sample_submission_paths,
    apply_path,
    is_solved,
    solved_state,
    GENERATOR_NAMES,
    depth_bucket,
)


def entrypoint() -> dict:
    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()

    rules = _build_rules(sample_paths)
    print(f"Built {len(rules)} rules")

    compressed = {}
    for sid, state in tests.items():
        bucket = depth_bucket(sid)
        original = sample_paths.get(sid, "")
        compressed_sid = _compress_path(original, rules)
        if is_solved(apply_path(state, compressed_sid)):
            compressed[sid] = compressed_sid
        else:
            compressed[sid] = original

    return compressed


def _build_rules(sample_paths: dict) -> list:
    """Build rules from systematic enumeration + empirical mining."""
    SOLVED = solved_state()
    stats = {}

    # Baseline: X.-X cancellation
    for gen in GENERATOR_NAMES:
        inv = _inverse(gen)
        pair = f"{gen}.{inv}"
        stats[pair] = {
            'pattern': (gen, inv), 'replacement': (), 'savings': 2,
            'count': 999999, 'verified': True,
        }

    # Systematic commutators and conjugations
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv2 = _inverse(gen2)

            # Commutator
            pattern = f"{gen1}.{gen2}.{inv1}.{inv2}"
            try:
                if apply_path(SOLVED, pattern) == SOLVED:
                    stats[pattern] = {
                        'pattern': (gen1, gen2, inv1, inv2),
                        'replacement': (), 'savings': 4,
                        'count': 1, 'verified': True,
                    }
            except:
                pass

            # Conjugation
            short_pattern = f"{gen1}.{gen2}.{inv1}"
            try:
                effect = apply_path(SOLVED, short_pattern)
                b_effect = apply_path(SOLVED, gen2)
                if effect == b_effect:
                    stats[short_pattern] = {
                        'pattern': (gen1, gen2, inv1),
                        'replacement': (gen2,), 'savings': 2,
                        'count': 1, 'verified': True,
                    }
            except:
                pass

    # Empirical patterns from sample_submission
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
        if len(pattern) <= 2:
            continue
        if pattern_str not in stats:
            stats[pattern_str] = {
                'pattern': pattern,
                'replacement': (),
                'savings': len(pattern),
                'count': count,
                'verified': True,
            }

    verified = [v for v in stats.values() if v.get('verified', False) and v['savings'] > 0]
    verified.sort(key=lambda x: x['count'] * x['savings'], reverse=True)
    return verified


def _compress_path(path: str, rules: list) -> str:
    if not path:
        return path

    max_passes = 30
    for _ in range(max_passes):
        prev = path
        moves = path.split('.')
        moves = [m for m in moves if m]
        moves = _cancel_moves(moves)
        for info in rules:
            moves = _apply_rule(moves, info['pattern'], info['replacement'])
        path = '.'.join(moves)
        if path == prev:
            break

    return path


def _apply_rule(moves: list, pattern: tuple, replacement: tuple) -> list:
    if not pattern or not moves:
        return moves
    pattern_len = len(pattern)
    result = []
    i = 0
    while i < len(moves):
        if i + pattern_len <= len(moves):
            window = tuple(moves[i:i + pattern_len])
            if window == pattern:
                result.extend(replacement)
                i += pattern_len
                continue
        result.append(moves[i])
        i += 1
    return result


def _cancel_moves(moves: list) -> list:
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