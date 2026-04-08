# fitness: TBD
"""
Wide beam search k=500, greedy candidate selection (first 2 valid per beam).

Testing hypothesis: the greedy ceiling at 69 is NOT structural — it's
just that k=1 (greedy) picks the wrong path at some critical juncture.
With k=500 beams, we cover 500 different paths and should find the rare
"good" path if it exists.

If k=500 also ceilings at 67-69, this CONFIRMS the ceiling is structural
for ALL greedy-based approaches, regardless of beam width.

Cost estimate: k=500 * n_samples=2 = 1000 expansions/step * ~70 steps
= 70K expansions total. Each: O(|diffs|) numpy = fast. ~25s estimated.
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

            # Take first 2 valid candidates (greedy-like, but 2 choices)
            for c in valid_indices[:2].tolist():
                new_diffs = np.array([c - x for x in elems], dtype=np.int64)
                all_diffs = np.concatenate([diffs_arr, new_diffs])

                blocked = c + all_diffs
                blocked = blocked[(blocked <= N)]

                new_valid = valid_mask.copy()
                new_valid[c] = False
                if len(blocked) > 0:
                    new_valid[blocked] = False

                # Score: remaining valid above c (more = better)
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
