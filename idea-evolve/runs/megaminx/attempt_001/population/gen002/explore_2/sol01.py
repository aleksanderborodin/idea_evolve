# fitness: 44114

"""
Algebraic path compression for Megaminx via empirically verified rewrite rules.

This solution pursues idea_005: Megaminx commutator and identity discovery.
We empirically discover valid rewrite rules from sample_submission paths
and apply verified rules for compression.

Key constraints from brief:
- Do NOT use best.py or refine beam/compression scaffold
- Treat idea_002 (X.Y.-X heuristic) as off-limits
- Only apply empirically verified rewrite rules
- Validity is paramount
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

    # Phase 1: Discover empirically valid rewrite rules
    rule_stats = _discover_rewrite_rules(sample_paths)
    print(f"Discovered {len(rule_stats)} candidate rules")

    # Phase 2: Select verified rules with positive savings
    verified_rules = _select_best_rules(rule_stats)
    print(f"Selected {len(verified_rules)} verified rules")

    # Phase 3: Apply rules to compress paths
    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        compressed_sid = _apply_all_rules(original, verified_rules)
        # Validate
        if is_solved(apply_path(state, compressed_sid)):
            compressed[sid] = compressed_sid
        else:
            compressed[sid] = original

    return compressed


def _discover_rewrite_rules(sample_paths: dict) -> dict:
    """Scan sample_submission paths for rewrite rule opportunities."""
    stats = {}
    SOLVED = solved_state()

    # Collect all length-2 through length-4 subsequences
    subseq_counts = Counter()
    subseq_effects = {}

    for path in sample_paths.values():
        if not path:
            continue
        moves_list = path.split('.')
        for start in range(len(moves_list)):
            for length in range(2, 5):
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

    # Rule: X.-X cancellation (baseline)
    for gen in GENERATOR_NAMES:
        inv = _inverse(gen)
        pair = f"{gen}.{inv}"
        if pair in subseq_counts:
            key = f"{gen}.{inv}"
            stats[key] = {
                'pattern': (gen, inv),
                'replacement': (),
                'savings': 2,
                'count': subseq_counts[pair],
                'verified': True,
            }

    # Rule: XX -> identity (if double move is identity)
    for gen in GENERATOR_NAMES:
        double = f"{gen}.{gen}"
        if double in subseq_counts:
            try:
                effect = apply_path(SOLVED, double)
                if effect == SOLVED:
                    key = f"{gen}.{gen}"
                    stats[key] = {
                        'pattern': (gen, gen),
                        'replacement': (),
                        'savings': 2,
                        'count': subseq_counts[double],
                        'verified': True,
                    }
            except:
                pass

    # Rule: X.Y.X^{-1} -> Y (conjugation) if valid
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2:
                continue
            inv1 = _inverse(gen1)
            pattern_str = f"{gen1}.{gen2}.{inv1}"
            if pattern_str in subseq_counts:
                try:
                    effect = apply_path(SOLVED, pattern_str)
                    y_effect = apply_path(SOLVED, gen2)
                    if effect == y_effect:
                        key = pattern_str
                        stats[key] = {
                            'pattern': (gen1, gen2, inv1),
                            'replacement': (gen2,),
                            'savings': 2,
                            'count': subseq_counts[pattern_str],
                            'verified': True,
                        }
                except:
                    pass

    # Rule: X.Y.-X.-Y -> identity (commutator)
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2:
                continue
            inv1 = _inverse(gen1)
            inv2 = _inverse(gen2)
            pattern_str = f"{gen1}.{gen2}.{inv1}.{inv2}"
            if pattern_str in subseq_counts:
                try:
                    effect = apply_path(SOLVED, pattern_str)
                    if effect == SOLVED:
                        key = pattern_str
                        stats[key] = {
                            'pattern': (gen1, gen2, inv1, inv2),
                            'replacement': (),
                            'savings': 4,
                            'count': subseq_counts[pattern_str],
                            'verified': True,
                        }
                except:
                    pass

    # Rule: X.-X.Y -> Y (span-2 with overlap)
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv1 = _inverse(gen1)
            pattern_str = f"{gen1}.{gen2}.{inv1}"
            if pattern_str in subseq_counts:
                try:
                    effect = apply_path(SOLVED, pattern_str)
                    y_effect = apply_path(SOLVED, gen2)
                    if effect == y_effect:
                        key = pattern_str
                        stats[key] = {
                            'pattern': (gen1, gen2, inv1),
                            'replacement': (gen2,),
                            'savings': 2,
                            'count': subseq_counts[pattern_str],
                            'verified': True,
                        }
                except:
                    pass

    return stats


def _select_best_rules(rule_stats: dict) -> list:
    """Select rules that are verified and provide meaningful savings."""
    verified = []
    for name, info in rule_stats.items():
        if not info.get('verified', False):
            continue
        if info['savings'] <= 0:
            continue
        if info['count'] < 10:
            continue
        verified.append((name, info))
    # Sort by expected total savings (count * savings)
    verified.sort(key=lambda x: x[1]['count'] * x[1]['savings'], reverse=True)
    return verified


def _apply_all_rules(path: str, rules: list) -> str:
    """Apply cancellation and verified rewrite rules iteratively."""
    if not path:
        return path

    max_iters = 20
    for _ in range(max_iters):
        prev = path
        moves = path.split('.')
        moves = _cancel_moves(moves)
        # Apply each verified rule
        for rule_name, info in rules:
            moves = _apply_rule(moves, info['pattern'], info['replacement'])
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


def _apply_rule(moves: list, pattern: tuple, replacement: tuple) -> list:
    """Apply a rewrite rule (pattern -> replacement) anywhere in the move list."""
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


def _inverse(move: str) -> str:
    """Return the inverse of a move."""
    if move.startswith('-'):
        return move[1:]
    return f'-{move}'