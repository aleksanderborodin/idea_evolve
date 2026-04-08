# fitness: TBD
"""
Multi-seed beam search: start from many different initial elements.

Previous attempts all start from [0] — the greedy ceiling may be specific
to sets anchored at 0. Starting from different initial positions explores
a broader space of Sidon sets.

Also: try picking candidates from DIFFERENT quartiles of the valid range
per beam, instead of purely "smallest valid". This creates genuine
path diversity within each seed.

k_beams_per_seed=5, n_seeds=15, n_samples=5 (alternating front/back)
Total beams = 75, total time estimated ~8s.
"""

import sys
import numpy as np

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')


def beam_search_from_seed(seed, N=10000, k_beams=5, n_samples=5):
    """Run beam search starting from given seed element."""
    valid0 = np.ones(N + 1, dtype=bool)
    valid0[seed] = False
    diffs0 = np.array([], dtype=np.int64)
    beams = [([seed], diffs0, valid0)]
    best = [seed]

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

            # Sample from front, back, and mid of valid range
            if len(valid_indices) <= n_samples:
                sampled = valid_indices.tolist()
            else:
                # Alternating: some from front, some from back
                n_front = (n_samples + 1) // 2
                n_back = n_samples - n_front
                front = valid_indices[:n_front].tolist()
                back = valid_indices[-n_back:].tolist()
                sampled = front + back

            for c in sampled:
                new_diffs = np.array([c - x for x in elems], dtype=np.int64)
                all_diffs = np.concatenate([diffs_arr, new_diffs])

                blocked = c + all_diffs
                blocked = blocked[(blocked <= N)]

                new_valid = valid_mask.copy()
                new_valid[c] = False
                if len(blocked) > 0:
                    new_valid[blocked] = False

                # Score: remaining valid above c, normalized by range
                rem = int(new_valid[c + 1:].sum())
                rng = N - c
                score = -(rem / max(rng, 1))
                pool.append((score, c, elems + [c], all_diffs, new_valid))

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
    N = 10000
    # Try seeds spread across [0, N]
    seeds = [0, 1, 5, 10, 50, 100, 500, 1000, 2000, 3000, 4000, 5000, 7500, 9000, 9999]
    best = []

    for seed in seeds:
        result = beam_search_from_seed(seed, N=N, k_beams=5, n_samples=5)
        if len(result) > len(best):
            best = result

    return best
