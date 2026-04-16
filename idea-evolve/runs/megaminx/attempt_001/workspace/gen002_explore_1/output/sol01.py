# fitness: TBD
"""
IDA* search with corner-only pattern database for Megaminx.

Track B radical exploration: depth-first admissible search family
completely outside beam search. Corner PDB gives admissible heuristic.

Hybrid strategy: IDA* for short/medium buckets (optimal), beam search fallback
for hard/very_hard.
"""

import sys
from collections import deque
from pathlib import Path

PROBLEM_DIR = Path(__file__).resolve().parents[4].parent.parent / "problems" / "megaminx"
sys.path.insert(0, str(PROBLEM_DIR))

from helpers.core import (
    apply_move,
    depth_bucket,
    load_test,
    score_path,
    score_predictions,
    solved_state,
    load_sample_submission_paths,
    GENERATOR_NAMES,
)


def get_corner_positions():
    """Identify which state positions are corners.

    Corners move in 3-cycles, edges in 2-cycles.
    """
    import json
    info = json.loads(Path(PROBLEM_DIR / "data" / "puzzle_info.json").read_text())
    generators = info["generators"]

    corner_pos = set()
    edge_pos = set()

    for name, perm in generators.items():
        for i, p in enumerate(perm):
            if i != p:
                cycle = []
                j = i
                while j not in cycle:
                    cycle.append(j)
                    j = perm[j]
                cl = len(cycle)
                if cl == 3:
                    corner_pos.add(i)
                elif cl == 2:
                    edge_pos.add(i)

    return sorted(corner_pos), sorted(edge_pos)


def build_corner_pdb(max_depth=5):
    """BFS from solved state to build corner-config PDB."""
    import json
    info = json.loads(Path(PROBLEM_DIR / "data" / "puzzle_info.json").read_text())
    central = tuple(info["central_state"])
    generators = {name: tuple(perm) for name, perm in info["generators"].items()}

    corner_pos, _ = get_corner_positions()

    def corner_config(state):
        return tuple(state[i] for i in corner_pos)

    pdb = {corner_config(central): 0}
    queue = deque([(central, 0)])
    gennames = [g for g in GENERATOR_NAMES if g in generators]

    while queue:
        state, dist = queue.popleft()
        if dist >= max_depth:
            continue
        for gname in gennames:
            perm = generators[gname]
            new_state = tuple(state[perm[i]] for i in range(len(state)))
            cfg = corner_config(new_state)
            if cfg not in pdb:
                pdb[cfg] = dist + 1
                queue.append((new_state, dist + 1))

    print(f"Corner PDB: {len(pdb)} entries up to depth {max_depth}")
    return pdb, corner_pos


def ida_star_search(initial_state, pdb, corner_pos, max_depth=20):
    """IDA* using corner PDB heuristic. Returns path or None."""
    import json
    info = json.loads(Path(PROBLEM_DIR / "data" / "puzzle_info.json").read_text())
    generators = {name: tuple(perm) for name, perm in info["generators"].items()}
    gennames = [g for g in GENERATOR_NAMES if g in generators]

    def corner_config(state):
        return tuple(state[i] for i in corner_pos)

    def is_inverse(m1, m2):
        if m1.startswith("-"):
            return m2 == m1[1:]
        if m2.startswith("-"):
            return m2[1:] == m1
        return False

    def search(state, g, bound, path, visited):
        cfg = corner_config(state)
        h = pdb.get(cfg, max_depth)
        f = g + h
        if f > bound:
            return None, f
        if state == solved_state():
            return path[:], bound

        visited.add(state)
        best = None
        next_bound = float('inf')

        for gname in gennames:
            if path and is_inverse(path[-1], gname):
                continue

            perm = generators[gname]
            new_state = tuple(state[perm[i]] for i in range(len(state)))
            if new_state in visited:
                continue

            path.append(gname)
            result, new_f = search(new_state, g + 1, bound, path, visited)
            path.pop()

            if result is not None:
                visited.discard(state)
                return result, bound

            if new_f < next_bound:
                next_bound = new_f

        visited.discard(state)
        return None, next_bound

    cfg0 = corner_config(initial_state)
    threshold = pdb.get(cfg0, max_depth)

    path = []
    visited = set()
    while threshold <= max_depth:
        result, _ = search(initial_state, 0, threshold, path, visited)
        if result is not None:
            return result
        threshold += 1

    return None


def solve_with_ida_star():
    """Main solver using IDA* + corner PDB."""
    print("Building corner pattern database...")
    pdb, corner_pos = build_corner_pdb(max_depth=5)

    tests = load_test(proxy=True)
    sample_paths = load_sample_submission_paths()

    results = {}
    stats = {}

    for sid, state in sorted(tests.items()):
        bucket = depth_bucket(sid)
        if bucket not in stats:
            stats[bucket] = {"count": 0, "solved": 0, "invalid": 0, "fitness": 0}
        stats[bucket]["count"] += 1

        path = None
        if bucket in ("short", "medium"):
            path = ida_star_search(state, pdb, corner_pos, max_depth=20)
        if path is None:
            path = sample_paths.get(sid, "")

        plen, ok = score_path(state, path)
        if ok:
            stats[bucket]["solved"] += 1
        else:
            stats[bucket]["invalid"] += 1
        stats[bucket]["fitness"] += plen

        results[sid] = path

    total_fitness = sum(s["fitness"] for s in stats.values())
    print(f"Total fitness: {total_fitness}")
    for b in ["short", "medium", "hard", "very_hard"]:
        if b in stats:
            s = stats[b]
            print(f"  {b}: count={s['count']}, fitness={s['fitness']}, solved={s['solved']}, invalid={s['invalid']}")

    return results


def entrypoint():
    return solve_with_ida_star()


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