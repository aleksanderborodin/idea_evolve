# fitness: 616
"""
Exhaustive AGL(1,8) orbit clique search for M(8,5).

Strategy: Try ALL 720 starting vertices (vs standard greedy's 50) to find
the maximum orbit clique. The orbit graph has degree 138 per vertex,
suggesting there may be larger cliques than the standard 11-orbit → 616.
"""

import numpy as np
import sys
import time

# Add problem helpers to path for evaluate.py
sys.path.insert(0, '/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes')

from helpers.agl18 import agl18_orbits, agl18_compat_graph


def entrypoint() -> np.ndarray:
    t0 = time.time()
    n_orbits = 720
    d = 5

    print("Building orbits and compatibility graph...", flush=True)
    orbits = agl18_orbits()
    compat = agl18_compat_graph(d=d)
    print(f"Graph built in {time.time()-t0:.1f}s. Starting exhaustive search of {n_orbits} starting vertices.", flush=True)

    best_clique = []
    best_size = 0

    # Try ALL 720 starting vertices (time-boxed to 30 min)
    TIME_LIMIT = 30 * 60  # 30 minutes

    for sv_idx, sv in enumerate(range(n_orbits)):
        if time.time() - t0 > TIME_LIMIT:
            print(f"Time limit reached at starting vertex {sv_idx}. Stopping.", flush=True)
            break

        if sv_idx % 50 == 0:
            elapsed = time.time() - t0
            print(f"Progress: {sv_idx}/{n_orbits} starting vertices tried, best clique = {len(best_clique)} orbits ({len(best_clique)*56} codewords), elapsed {elapsed:.1f}s", flush=True)

        # Greedy clique construction from this starting vertex
        clique = [sv]
        cands = list(np.where(compat[sv])[0])

        while cands:
            # Degree-ordered greedy: pick vertex with most neighbors in current candidates
            scored = [(c, sum(compat[c, c2] for c2 in cands)) for c in cands]
            scored.sort(key=lambda x: -x[1])
            v = scored[0][0]
            clique.append(v)
            cands = [c for c in cands if compat[v, c]]

        if len(clique) > best_size:
            best_size = len(clique)
            best_clique = clique
            print(f"New best clique: {len(best_clique)} orbits → {len(best_clique)*56} codewords", flush=True)

    print(f"\nFinal best clique: {len(best_clique)} orbits → {len(best_clique)*56} codewords", flush=True)
    print(f"Total time: {time.time()-t0:.1f}s", flush=True)

    # Build the code from selected orbits
    code_parts = [orbits[c] for c in best_clique]
    code = np.vstack(code_parts).astype(np.int32)

    print(f"Final code size: {code.shape[0]}", flush=True)
    return code