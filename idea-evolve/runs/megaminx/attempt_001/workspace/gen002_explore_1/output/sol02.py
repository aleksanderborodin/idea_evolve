# fitness: TBD
"""
Hamming-predictor-guided beam search for Megaminx.

This is EXP-1 from the gen001 experiment suggestions: zero-cost test of
whether ANY predictor-guided search beats pure compression.

Use cayleypy's built-in `Predictor(graph, 'hamming')` — no training needed.
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
)


def solve_with_hamming_predictor():
    """Use hamming-predictor guided beam search via cayleypy."""
    import cayleypy

    gdef = cayleypy.Puzzles.megaminx()
    graph = cayleypy.CayleyGraph(gdef)

    predictor = cayleypy.Predictor(graph, 'hamming')

    tests = load_test(proxy=True)
    results = {}

    import time

    sample_results = {}
    first_5 = list(tests.items())[:5]
    for sid, state in first_5:
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
        print(f"sid={sid}: solved={path_found}, path_len={len(path)}, time={elapsed:.1f}s")
        sample_results[sid] = (path_found, path, elapsed)

    avg_time = sum(t for _, _, t in sample_results.values()) / len(sample_results)
    total_est = avg_time * len(tests)
    print(f"Estimated total time: {total_est:.0f}s = {total_est/60:.1f} min")

    for sid, state in tests.items():
        bucket = depth_bucket(sid)
        if bucket == "very_hard":
            beam_width = 3000
            max_steps = 300
        elif bucket == "hard":
            beam_width = 2000
            max_steps = 250
        else:
            beam_width = 1500
            max_steps = 150

        res = graph.beam_search(
            start_state=list(state),
            beam_width=beam_width,
            max_steps=max_steps,
            predictor=predictor,
            return_path=True,
        )
        path_found = getattr(res, "path_found", False)
        path = getattr(res, "path", []) or []

        if path_found and len(path) > 0:
            moves = [gdef.generator_names[idx] for idx in path]
            kaggle_names = [_to_kaggle_name(m) for m in moves]
            results[sid] = ".".join(kaggle_names)
        else:
            results[sid] = ""

    return results


def _to_kaggle_name(cname):
    s = cname[2:] if cname.startswith("M_") else cname
    if s.endswith("_inv"):
        return f"-{s[:-4]}"
    return s


def entrypoint():
    return solve_with_hamming_predictor()


if __name__ == "__main__":
    results = entrypoint()
    fitness, is_valid, aux = score_predictions(results, proxy=True)
    print(f"\nFinal fitness: {fitness}, is_valid: {is_valid}")
    print(f"compression_ratio: {aux['compression_ratio']}")
    print(f"solved_count: {aux['solved_count']}, invalid_count: {aux['invalid_count']}")
    print(f"improved_count: {aux['improved_count']}")
    print(f"\nPer-bucket:")
    for b in ["special", "short", "medium", "hard", "very_hard"]:
        print(f"  {b}: fitness={aux[f'bucket_{b}_fitness']}, solved={aux[f'bucket_{b}_solved']}, invalid={aux[f'bucket_{b}_invalid']}")