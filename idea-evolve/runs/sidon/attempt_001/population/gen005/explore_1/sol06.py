# fitness: TBD
"""
k=500 beam search, 3 candidates per beam: first, 25th-percentile, 75th-percentile of valid range.

sol05 (k=500, first-2) got 70 — better than greedy ceiling!
This variant adds more diversity by exploring candidates spread through the valid range.
The 25th/75th percentile choices may find paths that avoid the greedy saturation trap.

Cost: ~24s (1.5x sol05).
"""

import sys
import numpy as np

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')


def beam_search_sidon(N=10000, k_beams=500):
    valid0 = np.ones(N + 1, dtype=bool)
    valid0[0] = False
    diffs0 = np.array([], dtype=np.int64)
    beams = [([0], diffs0, valid0)]
    best = [0]

    while beams:
        pool = []

        for elems, diffs_arr, valid_mask in beams:
            last = elems[-1]
            if last + 1 > N:
                if len(elems) > len(best):
                    best = elems[:]
                continue

            valid_indices = np.where(valid_mask[last + 1:])[0] + last + 1

            if len(valid_indices) == 0:
                if len(elems) > len(best):
                    best = elems[:]
                continue

            # Sample: first, 25th pct, 75th pct of valid range
            n = len(valid_indices)
            if n == 1:
                sampled = [valid_indices[0]]
            elif n == 2:
                sampled = [valid_indices[0], valid_indices[1]]
            else:
                i25 = max(1, n // 4)
                i75 = min(n - 2, 3 * n // 4)
                sampled_idx = sorted(set([0, i25, i75]))
                sampled = valid_indices[sampled_idx].tolist()

            for c in sampled:
                new_diffs = np.array([c - x for x in elems], dtype=np.int64)
                all_diffs = np.concatenate([diffs_arr, new_diffs])

                blocked = c + all_diffs
                blocked = blocked[(blocked <= N)]

                new_valid = valid_mask.copy()
                new_valid[c] = False
                if len(blocked) > 0:
                    new_valid[blocked] = False

                rem = int(new_valid[c + 1:].sum())
                pool.append((-rem, c, elems + [c], all_diffs, new_valid))

        if not pool:
            break

        pool.sort(key=lambda x: (x[0], x[1]))

        seen = set()
        beams = []
        for score, c, elems, diffs_arr, valid_mask in pool:
            key = tuple(elems)
            if key not in seen and len(beams) < k_beams:
                seen.add(key)
                beams.append((elems, diffs_arr, valid_mask))

        for elems, _, _ in beams:
            if len(elems) > len(best):
                best = elems[:]

    return best


def entrypoint():
    return beam_search_sidon(N=10000, k_beams=500)
