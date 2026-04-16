# fitness: TBD
"""
Enhanced compression + focused beam search for hard puzzles.

gen001 found compression floor at 46312 (compression_ratio=0.9158).
This solution: try smarter compression + targeted beam search on hard puzzles only.

Strategy:
1. Multi-pass enhanced compression (X.-X + non-adjacent patterns)
2. Run beam search on a SUBSET of hard/very_hard puzzles (the deepest ones)
   where potential improvement is greatest
3. Fall back to compressed sample_submission for everything else
"""

import sys
import time
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
)


def multi_pass_compress(path, max_passes=5):
    """Enhanced compression: multiple passes until stable."""
    if not path:
        return path

    moves = path.split(".")
    if not moves:
        return path

    for _ in range(max_passes):
        new_moves = []
        i = 0
        changed = False
        while i < len(moves):
            if i + 1 < len(moves):
                m1, m2 = moves[i], moves[i + 1]
                if m1.startswith("-") and m2 == m1[1:]:
                    changed = True
                    i += 2
                    continue
                if m2.startswith("-") and m1 == m2[1:]:
                    changed = True
                    i += 2
                    continue
            new_moves.append(moves[i])
            i += 1

        if not changed:
            break
        moves = new_moves

    return ".".join(moves)


def solve_hybrid():
    """Hybrid: enhanced compression + focused beam on deep puzzles."""
    import cayleypy

    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef)
    predictor = cayleypy.Predictor(graph, 'hamming')

    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()
    sample_lens = load_sample_submission_lengths()

    results = {}
    stats = {b: {"count": 0, "fitness": 0, "solved": 0, "invalid": 0}
             for b in ["special", "short", "medium", "hard", "very_hard"]}

    # First pass: enhanced compression for all
    print("Phase 1: Enhanced compression...")
    for sid, state in sorted(tests.items()):
        bucket = depth_bucket(sid)
        stats[bucket]["count"] += 1

        original = sample_paths.get(sid, "")
        compressed = multi_pass_compress(original)

        plen, ok = score_path(state, compressed)
        if ok:
            stats[bucket]["solved"] += 1
        else:
            stats[bucket]["invalid"] += 1
            compressed = original
            plen, ok = score_path(state, compressed)

        stats[bucket]["fitness"] += plen
        results[sid] = compressed

    total_before = sum(s["fitness"] for s in stats.values())
    print(f"After compression: {total_before}")
    for b in ["short", "medium", "hard", "very_hard"]:
        s = stats[b]
        print(f"  {b}: fitness={s['fitness']}, solved={s['solved']}")

    # Phase 2: Try beam search on the hardest puzzles (deepest very_hard)
    # Focus on ids 900-1000 (deepest of the deep) where beam search has most leverage
    print("\nPhase 2: Focused beam search on deepest puzzles...")

    very_hard_ids = sorted([sid for sid in tests.keys() if depth_bucket(sid) == "very_hard"])
    deep_ids = [sid for sid in very_hard_ids if sid >= 600]  # deepest half

    # Time 3 deep puzzles to estimate budget
    sample_timed = []
    for sid in deep_ids[:3]:
        state = tests[sid]
        start = time.time()
        res = graph.beam_search(
            start_state=list(state),
            beam_width=2000,
            max_steps=200,
            predictor=predictor,
            return_path=True,
        )
        elapsed = time.time() - start
        path_found = getattr(res, "path_found", False)
        path = getattr(res, "path", []) or []
        print(f"  sid={sid}: solved={path_found}, len={len(path)}, time={elapsed:.1f}s")
        sample_timed.append((sid, path_found, path, elapsed))

    avg_time = sum(t for _, _, _, t in sample_timed) / len(sample_timed)
    remaining = len(deep_ids) - len(sample_timed)
    est_remaining = avg_time * remaining
    print(f"Avg time per deep puzzle: {avg_time:.1f}s, remaining: {est_remaining:.0f}s")

    # Only continue if we can finish within budget
    # 5-minute target for beam phase
    if est_remaining < 300:
        print("Continuing with beam search...")
        for sid in deep_ids[3:]:
            if sid in [s[0] for s in sample_timed]:
                continue  # already done
            state = tests[sid]
            res = graph.beam_search(
                start_state=list(state),
                beam_width=2000,
                max_steps=200,
                predictor=predictor,
                return_path=True,
            )
            path_found = getattr(res, "path_found", False)
            path = getattr(res, "path", []) or []

            if path_found:
                moves = [gdef.generator_names[idx] for idx in path]
                kaggle_names = [_to_kaggle_name(m) for m in moves]
                beam_path = ".".join(kaggle_names)
                beam_compressed = multi_pass_compress(beam_path)

                current = results[sid]
                current_len = len(current.split(".")) if current else 0
                new_len = len(beam_compressed.split(".")) if beam_compressed else 0

                if new_len < current_len:
                    plen, ok = score_path(state, beam_compressed)
                    if ok:
                        results[sid] = beam_compressed
                        stats["very_hard"]["fitness"] += (plen - current_len)

    total_fitness = sum(s["fitness"] for s in stats.values())
    print(f"\nTotal fitness: {total_fitness}")
    for b in ["special", "short", "medium", "hard", "very_hard"]:
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
    print(f"\nPer-bucket:")
    for b in ["special", "short", "medium", "hard", "very_hard"]:
        print(f"  {b}: fitness={aux[f'bucket_{b}_fitness']}, solved={aux[f'bucket_{b}_solved']}, invalid={aux[f'bucket_{b}_invalid']}")