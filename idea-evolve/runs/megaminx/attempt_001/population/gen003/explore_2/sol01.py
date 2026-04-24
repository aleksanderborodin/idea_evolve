# fitness: 44094

"""
Two-phase approach: compression + trained-predictor beam search.

Phase 1: Empirical identity compression (336 rules from gen002) to get ~44114 baseline.
Phase 2: Train MLP predictor on random walks, then apply sliding-window beam search
on the last N moves of each compressed path to find shorter suffixes.

The trained predictor helps beam search find shorter paths for segments of ≤12 moves,
providing incremental improvement over compression alone.
"""

import time
from collections import Counter

import torch
import torch.nn as nn

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


def _inverse(move):
    if move.startswith("-"):
        return move[1:]
    return f"-{move}"


class _PredictorMLP(nn.Module):
    def __init__(self, input_dim, hidden_dims):
        super().__init__()
        layers = []
        prev = input_dim
        for h in hidden_dims:
            layers += [nn.Linear(prev, h), nn.ReLU()]
            prev = h
        layers.append(nn.Linear(prev, 1))
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        if x.dtype != torch.float32:
            x = x.float()
        return self.net(x).squeeze(-1)


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
        if i + plen <= len(moves):
            window = tuple(moves[i : i + plen])
            if window == pattern:
                result.extend(replacement)
                i += plen
                continue
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

    # X.-X cancellation
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

    # Conjugation: X.Y.X^{-1} -> Y
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2:
                continue
            inv1 = _inverse(gen1)
            pat = f"{gen1}.{gen2}.{inv1}"
            if pat in subseq_counts:
                try:
                    eff = apply_path(SOLVED, pat)
                    y_eff = apply_path(SOLVED, gen2)
                    if eff == y_eff:
                        stats[pat] = {
                            "pattern": (gen1, gen2, inv1),
                            "replacement": (gen2,),
                            "savings": 2,
                            "count": subseq_counts[pat],
                            "verified": True,
                        }
                except Exception:
                    pass

    # Commutator: X.Y.-X.-Y -> identity
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2:
                continue
            inv1 = _inverse(gen1)
            inv2 = _inverse(gen2)
            pat = f"{gen1}.{gen2}.{inv1}.{inv2}"
            if pat in subseq_counts:
                try:
                    eff = apply_path(SOLVED, pat)
                    if eff == SOLVED:
                        stats[pat] = {
                            "pattern": (gen1, gen2, inv1, inv2),
                            "replacement": (),
                            "savings": 4,
                            "count": subseq_counts[pat],
                            "verified": True,
                        }
                except Exception:
                    pass

    # X.-X.Y -> Y (span-2 overlap)
    for gen1 in GENERATOR_NAMES:
        for gen2 in GENERATOR_NAMES:
            if gen1 == gen2 or gen1 == _inverse(gen2):
                continue
            inv1 = _inverse(gen1)
            pat = f"{gen1}.{gen2}.{inv1}"
            if pat in subseq_counts:
                try:
                    eff = apply_path(SOLVED, pat)
                    y_eff = apply_path(SOLVED, gen2)
                    if eff == y_eff:
                        stats[pat] = {
                            "pattern": (gen1, gen2, inv1),
                            "replacement": (gen2,),
                            "savings": 2,
                            "count": subseq_counts[pat],
                            "verified": True,
                        }
                except Exception:
                    pass

    return stats


def _select_best_rules(rule_stats):
    verified = []
    for name, info in rule_stats.items():
        if not info.get("verified", False):
            continue
        if info["savings"] <= 0:
            continue
        if info["count"] < 10:
            continue
        verified.append((name, info))
    verified.sort(key=lambda x: x[1]["count"] * x[1]["savings"], reverse=True)
    return verified


def _compress_path(path, rules):
    if not path:
        return path
    max_iters = 20
    for _ in range(max_iters):
        prev = path
        moves = path.split(".")
        moves = _cancel_moves(moves)
        for rule_name, info in rules:
            moves = _apply_rule(moves, info["pattern"], info["replacement"])
        path = ".".join(moves)
        if path == prev:
            break
    return path


def _to_kaggle_name(cname):
    s = cname[2:] if cname.startswith("M_") else cname
    if s.endswith("_inv"):
        return f"-{s[:-4]}"
    return s


def entrypoint():
    t_start = time.time()

    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()

    # Phase 1: Compression
    rule_stats = _discover_rewrite_rules(sample_paths)
    verified_rules = _select_best_rules(rule_stats)
    print(f"[Phase 1] Discovered {len(rule_stats)} candidate rules, selected {len(verified_rules)}")

    compressed = {}
    for sid, state in tests.items():
        original = sample_paths.get(sid, "")
        comp = _compress_path(original, verified_rules)
        if is_solved(apply_path(state, comp)):
            compressed[sid] = comp
        else:
            compressed[sid] = original

    comp_fitness = sum(len(compressed[sid].split(".")) if compressed[sid] else 0 for sid in tests)
    print(f"[Phase 1] Compressed fitness: {comp_fitness}")

    # Phase 2: Train MLP predictor + sliding-window beam search
    import cayleypy

    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef)
    device = graph.device

    t0 = time.time()
    X, y = graph.random_walks(width=50000, length=20, mode="bfs")
    print(f"[Phase 2] Walks: X={X.shape}, y_max={y.max().item()}, in {time.time()-t0:.1f}s")

    model = _PredictorMLP(120, (256, 128)).to(device)
    Xf = X.float().to(device)
    yf = y.float().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    loss_fn = nn.MSELoss()
    for epoch in range(10):
        pred = model(Xf).squeeze(-1)
        loss = loss_fn(pred, yf)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    model.eval()
    predictor = cayleypy.Predictor(graph, model)
    print(f"[Phase 2] Predictor trained in {time.time()-t0:.1f}s")

    # Phase 2b: Apply sliding-window beam search from the tail of each compressed path
    # Strategy: work backward from the end of the path; for suffixes ≤ 12 moves,
    # try beam search to find shorter alternatives
    MAX_SUFFIX = 12
    BEAM_WIDTH = 4096
    total_savings = 0
    improved_count = 0

    for sid, state in tests.items():
        path_str = compressed[sid]
        if not path_str:
            continue
        moves = path_str.split(".")

        # Compute intermediate states along the path
        states = [state]
        s = state
        for m in moves:
            s = apply_move(s, m)
            states.append(s)

        # Try to shorten from the tail: find longest suffix where beam can help
        best_path = list(moves)
        changed = True
        while changed:
            changed = False
            cur_moves = best_path
            cur_states = [state]
            s = state
            for m in cur_moves:
                s = apply_move(s, m)
                cur_states.append(s)

            # Try suffixes of increasing length from the end
            for suffix_len in range(1, min(MAX_SUFFIX + 1, len(cur_moves) + 1)):
                start_idx = len(cur_moves) - suffix_len
                start_state = cur_states[start_idx]

                result = graph.beam_search(
                    start_state=list(start_state),
                    beam_width=BEAM_WIDTH,
                    max_steps=suffix_len,
                    return_path=True,
                    predictor=predictor,
                    beam_mode="simple",
                )

                if result.path_found and result.path:
                    beam_len = len(result.path)
                    if beam_len < suffix_len:
                        beam_moves = [
                            _to_kaggle_name(gdef.generator_names[idx])
                            for idx in result.path
                        ]
                        # Verify
                        test_s = start_state
                        for m in beam_moves:
                            test_s = apply_move(test_s, m)
                        if is_solved(test_s):
                            new_moves = cur_moves[:start_idx] + beam_moves
                            savings = suffix_len - beam_len
                            total_savings += savings
                            improved_count += 1
                            best_path = new_moves
                            changed = True
                            break

        final_str = ".".join(best_path)
        if is_solved(apply_path(state, final_str)):
            compressed[sid] = final_str

    final_fitness = sum(
        len(compressed[sid].split(".")) if compressed[sid] else 0 for sid in tests
    )
    print(f"[Phase 2] Beam savings: {total_savings} across {improved_count} puzzles")
    print(f"[Total] {comp_fitness} -> {final_fitness} (saved {comp_fitness - final_fitness})")
    print(f"[Total] Time: {time.time() - t_start:.1f}s")

    return compressed
