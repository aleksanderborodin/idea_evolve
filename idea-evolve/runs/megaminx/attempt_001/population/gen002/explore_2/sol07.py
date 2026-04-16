# fitness: 44114

"""
Extended empirical compression: span-2 to span-6 pattern mining.

Extends sol01's winning approach with:
1. Span-6 patterns (sol01 only went to span-5)
2. Pattern type: XYX^{-1}Y^{-1} (commutator form 2)
3. Higher savings focus: patterns that save 2+ moves
4. Combined with all commutators/conjugations from systematic enumeration
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

    rules = _build_rules(sample_paths)
    print(f"Built {len(rules)} rules")

    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        compressed_sid = _compress_path(original, rules)
        if is_solved(apply_path(state, compressed_sid)):
            compressed[sid] = compressed_sid
        else:
            compressed[sid] = original

    return compressed


def _build_rules(sample_paths: dict) -> list:
    """Build compression rules: systematic identities + empirical patterns."""
    SOLVED = solved_state()
    stats = {}

    # ===== SYSTEMATIC IDENTITIES =====

    # X.-X cancellation (baseline)
    for gen in GENERATOR_NAMES:
        inv = _inverse(gen)
        pair = f"{gen}.{inv}"
        stats[pair] = {
            'pattern': (gen, inv), 'replacement': (), 'savings': 2,
            'count': 999999, 'verified': True,
        }

    # XX -> identity (if true)
    for gen in GENERATOR_NAMES:
        try:
            if apply_path(SOLVED, f"{gen}.{gen}") == SOLVED:
                key = f"{gen}.{gen}"
                stats[key] = {
                    'pattern': (gen, gen), 'replacement': (), 'savings': 2,
                    'count': 1, 'verified': True,
                }
        except:
            pass

    # Commutators ABA^{-1}B^{-1} -> identity
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv2 = _inverse(gen2)
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

    # Conjugations ABA^{-1} -> B
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            pattern = f"{gen1}.{gen2}.{inv1}"
            try:
                effect = apply_path(SOLVED, pattern)
                b_effect = apply_path(SOLVED, gen2)
                if effect == b_effect:
                    stats[pattern] = {
                        'pattern': (gen1, gen2, inv1),
                        'replacement': (gen2,), 'savings': 2,
                        'count': 1, 'verified': True,
                    }
            except:
                pass

    # ===== EMPIRICAL PATTERNS =====

    # Collect subsequences from sample_submission
    subseq_counts = Counter()
    subseq_effects = {}

    for path in sample_paths.values():
        if not path:
            continue
        moves = path.split('.')
        for start in range(len(moves)):
            for length in range(2, 7):  # Extended to span-6
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

    # Filter: frequent patterns that equal identity
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

    # ===== CONJUGATION PATTERNS (X.Y.X^{-1} -> Y or simpler) =====
    for gen1 in GENERATOR_NAMES:
        inv1 = _inverse(gen1)
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            pattern_str = f"{gen1}.{gen2}.{inv1}"
            if pattern_str not in subseq_counts:
                continue
            try:
                effect = apply_path(SOLVED, pattern_str)
                for target in [(), (gen2,), (_inverse(gen2),)]:
                    if not target:
                        te = SOLVED
                    else:
                        te = apply_path(SOLVED, '.'.join(target))
                    if effect == te and len(pattern_str.split('.')) > len(target):
                        key = pattern_str + '->' + ('.'.join(target) if target else 'ID')
                        if key not in stats:
                            stats[key] = {
                                'pattern': (gen1, gen2, inv1),
                                'replacement': target,
                                'savings': len(pattern_str.split('.')) - len(target),
                                'count': subseq_counts[pattern_str],
                                'verified': True,
                            }
            except:
                pass

    # ===== SORT BY EXPECTED SAVINGS =====
    verified = [v for v in stats.values() if v.get('verified', False) and v['savings'] > 0]
    verified.sort(key=lambda x: x['count'] * x['savings'], reverse=True)
    return verified


def _compress_path(path: str, rules: list) -> str:
    """Apply compression rules iteratively."""
    if not path:
        return path

    max_passes = 30
    for _ in range(max_passes):
        prev = path
        moves = path.split('.')
        moves = [m for m in moves if m]
        moves = _cancel_moves(moves)

        # Apply all rules in order
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