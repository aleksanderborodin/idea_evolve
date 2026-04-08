# fitness: TBD
"""
Beam search with numpy boolean mask — fixed to only sample candidates > last element.

Bug in previous version: valid_mask sampling included positions <= max(elems),
causing negative differences and invalid Sidon sets with 444 violations.

Fix: `valid_indices = np.where(valid_mask[last+1:])[0] + last + 1`
This enforces ascending construction order: all candidates > current max.

When c > all elems, new_diffs = {c-x} are all positive.
Blocked positions = {c+d : d ∈ all_diffs} are all > c (future candidates).

Score = remaining valid candidates > c (more = better future flexibility).
"""

import sys
import numpy as np

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')


def beam_search_sidon(N=10000, k_beams=20, n_samples=8):
    valid0 = np.ones(N + 1, dtype=bool)
    valid0[0] = False  # 0 is already used
    beams = [([0], set(), valid0)]
    best = [0]

    while beams:
        pool = []

        for elems, diffs, valid_mask in beams:
            last = elems[-1]
            # Only consider candidates ABOVE current last element (ascending order)
            if last + 1 > N:
                if len(elems) > len(best):
                    best = elems[:]
                continue

            valid_indices = np.where(valid_mask[last + 1:])[0] + last + 1

            if len(valid_indices) == 0:
                if len(elems) > len(best):
                    best = elems[:]
                continue

            # Sample spread across the full valid range
            if len(valid_indices) <= n_samples:
                sampled = valid_indices.tolist()
            else:
                step = len(valid_indices) // n_samples
                idx = [i * step for i in range(n_samples)]
                idx[-1] = len(valid_indices) - 1
                sampled = valid_indices[idx].tolist()

            for c in sampled:
                # c > last > all elems, so c-x > 0 for all x in elems
                new_diffs = set(c - x for x in elems)
                all_diffs = diffs | new_diffs

                # Blocked future positions: {c+d for d in all_diffs}
                all_diffs_arr = np.fromiter(all_diffs, dtype=np.int64)
                blocked = c + all_diffs_arr
                blocked = blocked[(blocked <= N)]

                new_valid = valid_mask.copy()
                new_valid[c] = False
                if len(blocked) > 0:
                    new_valid[blocked] = False

                # Count remaining valid positions > c
                remaining = int(new_valid[c + 1:].sum())
                score = -remaining
                pool.append((score, -(len(elems) + 1), elems + [c], all_diffs, new_valid))

        if not pool:
            break

        pool.sort(key=lambda x: (x[0], x[1]))

        seen = set()
        beams = []
        for score, neg_len, elems, diffs, valid_mask in pool:
            key = tuple(elems[-3:])
            if key not in seen and len(beams) < k_beams:
                seen.add(key)
                beams.append((elems, diffs, valid_mask))

        for elems, _, _ in beams:
            if len(elems) > len(best):
                best = elems[:]

    return best


def entrypoint():
    return beam_search_sidon(N=10000, k_beams=20, n_samples=8)
