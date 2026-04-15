# fitness: 616
"""
Randomized perturbation search for orbit clique improvement in M(8,5).

Strategy: The standard greedy finds 11-orbit cliques consistently.
Try to escape local optima by:
1. Start with a known K-orbit clique
2. Remove 1-3 random orbits
3. Re-run greedy extension from remaining orbits
4. If better clique found, keep it
5. Repeat 500+ times with different perturbations
"""

import numpy as np
import sys
import time
import random

sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')

from helpers.agl18 import agl18_orbits, agl18_compat_graph


def greedy_clique_from_vertices(vertices, compat):
    """Build greedy clique starting from a set of vertices."""
    clique = list(vertices)
    cands = set(np.where(compat[vertices[0]])[0])
    for v in vertices[1:]:
        cands &= set(np.where(compat[v])[0])

    cands = list(cands)
    while cands:
        scored = [(c, sum(compat[c, c2] for c2 in cands)) for c in cands]
        scored.sort(key=lambda x: -x[1])
        v = scored[0][0]
        clique.append(v)
        cands = [c for c in cands if compat[v, c]]
    return clique


def entrypoint() -> np.ndarray:
    t0 = time.time()
    d = 5
    n_iterations = 500
    TIME_LIMIT = 25 * 60  # 25 minutes

    print("Building orbits and compatibility graph...", flush=True)
    orbits = agl18_orbits()
    compat = agl18_compat_graph(d=d)
    n_orbits = len(orbits)
    print(f"Graph built in {time.time()-t0:.1f}s. Running {n_iterations} perturbation rounds.", flush=True)

    # First, find the standard greedy best clique
    print("Finding baseline greedy clique...", flush=True)
    best_clique = []
    for sv in range(n_orbits):
        clique = [sv]
        cands = list(np.where(compat[sv])[0])
        while cands:
            scored = [(c, sum(compat[c, c2] for c2 in cands)) for c in cands]
            scored.sort(key=lambda x: -x[1])
            v = scored[0][0]
            clique.append(v)
            cands = [c for c in cands if compat[v, c]]
        if len(clique) > len(best_clique):
            best_clique = clique

    baseline_size = len(best_clique)
    print(f"Baseline greedy clique: {baseline_size} orbits → {baseline_size*56} codewords", flush=True)

    # Now try perturbations
    best_ever = list(best_clique)
    improvements = 0

    for iteration in range(n_iterations):
        if time.time() - t0 > TIME_LIMIT:
            print(f"Time limit reached at iteration {iteration}. Stopping.", flush=True)
            break

        if iteration % 50 == 0:
            elapsed = time.time() - t0
            print(f"Iteration {iteration}/{n_iterations}, best ever = {len(best_ever)} orbits, elapsed {elapsed:.1f}s", flush=True)

        # Start from current best clique
        start = list(best_clique)

        # Remove 1-3 random orbits
        n_remove = random.randint(1, 3)
        remove_idx = random.sample(range(len(start)), min(n_remove, len(start)))
        remaining = [start[i] for i in range(len(start)) if i not in remove_idx]

        if len(remaining) < 2:
            continue

        # Greedy extension from remaining
        candidate = greedy_clique_from_vertices(remaining, compat)

        if len(candidate) > len(best_ever):
            best_ever = candidate
            best_clique = candidate
            improvements += 1
            print(f"Iteration {iteration}: New best = {len(best_ever)} orbits → {len(best_ever)*56} codewords", flush=True)

    print(f"\nFinal best clique: {len(best_ever)} orbits → {len(best_ever)*56} codewords", flush=True)
    print(f"Improvements found: {improvements}", flush=True)
    print(f"Total time: {time.time()-t0:.1f}s", flush=True)

    # Build final code
    code_parts = [orbits[c] for c in best_ever]
    code = np.vstack(code_parts).astype(np.int32)

    print(f"Final code size: {code.shape[0]}", flush=True)
    return code