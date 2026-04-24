# fitness: TBD

"""
Compression + trained-predictor beam search — optimized version.

Uses the helper trained_predictor_beam_search module for cleaner code.
Phase 1: Empirical identity compression (336 rules).
Phase 2: Train predictor, then scan compressed paths from tail using beam search
to find shorter suffixes. Multiple passes until no more improvements.
"""

import time
from collections import Counter

from helpers.core import (
    GENERATOR_NAMES,
    apply_move,
    apply_path,
    is_solved,
    load_sample_submission_paths,
    load_test,
    score_path,
    solved_state,
)
from helpers.trained_predictor_beam_search import (
    _PredictorMLP,
    _to_kaggle_name,
    build_graph,
    train_predictor,
)


def _inverse(move):
    if move.startswith("-"):
        return move[1:]
    return f"-{move}"


def _cancel_moves(moves):
    stack = []
    for m in moves:
        if not m:
            continue
        if stack and stack[-1] == _inverse(m):
            stack.pop()
        else:
            stack.append(m)
    return stack


def _apply_rule(moves, pattern, replacement):
    if not pattern or not moves:
        return moves
    plen = len(pattern)
    result = []
    i = 0
    while i < len(moves):
        if i + plen <= len(moves) and tuple(moves[i : i + plen]) == pattern:
            result.extend(replacement)
            i += plen
        else:
            result.append(moves[i])
            i += 1
    return result


def _discover_rewrite_rules(sample_paths):
    SOLVED = solved_state()
    subseq_counts = Counter()
    subseq_effects = {}

    for path in sample_paths.values():
        if not path:
            continue
        moves_list = path.split(".")
        for start in range(len(moves_list)):
            for length in range(2, 5):
                if start + length > len(moves_list):
                    break
                subseq = tuple(moves_list[start : start + length])
                subseq_str = ".".join(subseq)
                subseq_counts[subseq_str] += 1
                if subseq_str not in subseq_effects:
                    try:
                        subseq_effects[subseq_str] = apply_path(SOLVED, subseq_str)
                    except Exception:
                        pass

    stats = {}
    for gen in GENERATOR_NAMES:
        inv = _inverse(gen)
        pair = f"{gen}.{inv}"
        if pair in subseq_counts:
            stats[pair] = {
                "pattern": (gen, inv),
                "replacement": (),
                "savings": 2,
                "count": subseq_counts[pair],
                "verified": True,
            }

    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2:
                continue
            inv1 = _inverse(gen1)
            for pat, repl, sav in [
                (f"{gen1}.{gen2}.{inv1}", (gen2,), 2),
            ]:
                if pat in subseq_counts:
                    try:
                        if apply_path(SOLVED, pat) == apply_path(SOLVED, gen2):
                            stats[pat] = {"pattern": (gen1, gen2, inv1), "replacement": repl, "savings": sav, "count": subseq_counts[pat], "verified": True}
                    except Exception:
                        pass

            inv2 = _inverse(gen2)
            pat = f"{gen1}.{gen2}.{inv1}.{inv2}"
            if pat in subseq_counts:
                try:
                    if apply_path(SOLVED, pat) == SOLVED:
                        stats[pat] = {"pattern": (gen1, gen2, inv1, inv2), "replacement": (), "savings": 4, "count": subseq_counts[pat], "verified": True}
                except Exception:
                    pass

    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv1 = _inverse(gen1)
            pat = f"{gen1}.{gen2}.{inv1}"
            if pat in subseq_counts and pat not in stats:
                try:
                    if apply_path(SOLVED, pat) == apply_path(SOLVED, gen2):
                        stats[pat] = {"pattern": (gen1, gen2, inv1), "replacement": (gen2,), "savings": 2, "count": subseq_counts[pat], "verified": True}
                except Exception:
                    pass

    return stats


def _select_best_rules(rule_stats):
    verified = []
    for name, info in rule_stats.items():
        if info.get("verified") and info["savings"] > 0 and info["count"] >= 10:
            verified.append((name, info))
    verified.sort(key=lambda x: x[1]["count"] * x[1]["savings"], reverse=True)
    return verified


def _compress_path(path, rules):
    if not path:
        return path
    for _ in range(20):
        prev = path
        moves = _cancel_moves(path.split("."))
        for _, info in rules:
            moves = _apply_rule(moves, info["pattern"], info["replacement"])
        path = ".".join(moves)
        if path == prev:
            break
    return path


def entrypoint():
    t_start = time.time()
    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()

    # Phase 1: Compression
    rule_stats = _discover_rewrite_rules(sample_paths)
    verified_rules = _select_best_rules(rule_stats)
    print(f"[P1] {len(verified_rules)} rules")

    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        comp = _compress_path(original, verified_rules)
        compressed[sid] = comp if is_solved(apply_path(state, comp)) else original

    comp_fit = sum(len(compressed[s].split(".")) if compressed[s] else 0 for s in tests)
    print(f"[P1] fitness={comp_fit}")

    # Phase 2: Train predictor + tail beam search
    import cayleypy

    graph, gdef = build_graph()
    predictor = train_predictor(graph, n_walks=50000, walk_length=20, hidden_dims=(256, 128), epochs=10, verbose=False)
    print(f"[P2] Predictor trained")

    total_savings = 0
    for sid, state in tests.items():
        path_str = compressed[sid]
        if not path_str:
            continue
        best = path_str.split(".")
        if len(best) <= 5:
            continue

        for _pass in range(5):
            states = [state]
            s = state
            for m in best:
                s = apply_move(s, m)
                states.append(s)

            improved = False
            for suffix_len in range(2, min(16, len(best) + 1)):
                idx = len(best) - suffix_len
                result = graph.beam_search(
                    start_state=list(states[idx]),
                    beam_width=4096,
                    max_steps=suffix_len,
                    return_path=True,
                    predictor=predictor,
                    beam_mode="simple",
                )
                if result.path_found and result.path and len(result.path) < suffix_len:
                    beam_moves = [_to_kaggle_name(gdef.generator_names[i]) for i in result.path]
                    ts = states[idx]
                    for m in beam_moves:
                        ts = apply_move(ts, m)
                    if is_solved(ts):
                        total_savings += suffix_len - len(beam_moves)
                        best = best[:idx] + beam_moves
                        improved = True
                        break
            if not improved:
                break

        final = ".".join(best)
        if is_solved(apply_path(state, final)):
            compressed[sid] = final

    final_fit = sum(len(compressed[s].split(".")) if compressed[s] else 0 for s in tests)
    print(f"[P2] savings={total_savings}, final={final_fit}, time={time.time()-t_start:.0f}s")
    return compressed
