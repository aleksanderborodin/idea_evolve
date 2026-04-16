# fitness: TBD
"""
Hybrid solver: compression + per-bucket beam strategy.

All gen001 solutions converged to 46312 (compression floor, compression_ratio=0.9158).
We need to beat this. Strategy:
1. Enhanced compression (non-adjacent cancellation patterns)
2. Beam search with hamming predictor for hard/very_hard buckets

Key finding from debugging: all 24 Megaminx generators have 5-cycle structure,
no 2-cycles or 3-cycles. So corner/edge classification doesn't apply as in cubes.

This is a genuinely different search family from pure beam search.
"""

import sys
from pathlib import Path

PROBLEM_DIR = Path(__file__).resolve().parents[4].parent.parent / "problems" / "megaminx"
sys.path.insert(0, str(PROBLEM_DIR))

from helpers.core import (
    depth_bucket,
    load_test,
    score_path,
    score_predictions,
    load_sample_submission_paths,
    load_sample_submission_lengths,
    GENERATOR_NAMES,
)


def enhanced_compress(path):
    """Extended cancellation: adjacent pairs, then re-scan.

    The gen001 solutions all used single-pass greedy X.-X cancellation.
    We try multiple passes until no change.
    """
    if not path:
        return path

    moves = path.split(".")
    if not moves:
        return path

    changed = True
    while changed:
        changed = False
        new_moves = []
        i = 0
        while i < len(moves):
            if i + 1 < len(moves):
                m1, m2 = moves[i], moves[i + 1]
                # X.-X cancellation
                if m1.startswith("-") and m2 == m1[1:]:
                    changed = True
                    i += 2
                    continue
                # -X.X cancellation
                if m2.startswith("-") and m1 == m2[1:]:
                    changed = True
                    i += 2
                    continue
            new_moves.append(moves[i])
            i += 1

        if changed:
            moves = new_moves
        else:
            break

    return ".".join(moves)


def solve_hybrid():
    """Hybrid: compression + predictor-guided beam for hard buckets."""
    import cayleypy

    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef)

    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()

    results = {}
    stats = {}

    # First: apply enhanced compression to all sample_submission paths
    # This is the gen001 baseline approach but with multiple passes
    print("Phase 1: Enhanced compression...")
    for sid, state in sorted(tests.items()):
        bucket = depth_bucket(sid)
        if bucket not in stats:
            stats[bucket] = {"count": 0, "solved": 0, "invalid": 0, "fitness": 0}
        stats[bucket]["count"] += 1

        original_path = sample_paths.get(sid, "")
        compressed = enhanced_compress(original_path)

        # If compression didn't help much, try hamming-guided beam for hard/very_hard
        if bucket in ("hard", "very_hard") and len(compressed.split(".")) > 20:
            predictor = cayleypy.Predictor(graph, 'hamming')
            res = graph.beam_search(
                start_state=list(state),
                beam_width=1500,
                max_steps=150,
                predictor=predictor,
                return_path=True,
            )
            path_found = getattr(res, "path_found", False)
            path = getattr(res, "path", []) or []

            if path_found and len(path) > 0:
                moves = [gdef.generator_names[idx] for idx in path]
                kaggle_names = [_to_kaggle_name(m) for m in moves]
                beam_path = ".".join(kaggle_names)
                beam_compressed = enhanced_compress(beam_path)

                # Use beam path if it's meaningfully shorter than compressed sample
                if len(beam_compressed.split(".")) < len(compressed.split(".")):
                    compressed = beam_compressed

        plen, ok = score_path(state, compressed)
        if ok:
            stats[bucket]["solved"] += 1
        else:
            stats[bucket]["invalid"] += 1
            # Fall back to original sample_submission path
            plen, ok = score_path(state, original_path)
        stats[bucket]["fitness"] += plen
        results[sid] = compressed if ok else original_path

    total_fitness = sum(s["fitness"] for s in stats.values())
    print(f"Total fitness: {total_fitness}")
    for b in ["special", "short", "medium", "hard", "very_hard"]:
        if b in stats:
            s = stats[b]
            print(f"  {b}: count={s['count']}, fitness={s['fitness']}, solved={s['solved']}, invalid={s['invalid']}")

    return results


def _to_kaggle_name(cname):
    s = cname[2:] if cname.startswith("M_") else cname
    if s.endswith("_inv"):
        return f"-{s[:-4]}"
    return s


def entrypoint():
    return solve_hybrid()


if __name__ == "__main__":
    results = entrypoint()
    fitness, is_valid, aux = score_predictions(results, proxy=True)
    print(f"\nFinal fitness: {fitness}, is_valid: {is_valid}")
    print(f"compression_ratio: {aux['compression_ratio']}")
    print(f"solved_count: {aux['solved_count']}, invalid_count: {aux['invalid_count']}")
    print(f"improved_count: {aux['improved_count']}")
    print(f"max_path_length: {aux['max_path_length']}")
    print(f"p50_path_length: {aux['p50_path_length']}")
    print(f"\nPer-bucket:")
    for b in ["special", "short", "medium", "hard", "very_hard"]:
        print(f"  {b}: fitness={aux[f'bucket_{b}_fitness']}, solved={aux[f'bucket_{b}_solved']}, invalid={aux[f'bucket_{b}_invalid']}")