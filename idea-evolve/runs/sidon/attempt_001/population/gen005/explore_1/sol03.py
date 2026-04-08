# fitness: TBD
"""
Beam search with greedy-lookahead scoring — k_beams=50, n_samples=10.

Problem with sol01/sol02: score = "remaining valid" → always picks smallest
valid candidate → reduces to greedy → same ceiling of 66-69.

Fix: use greedy-lookahead scoring. For each candidate c:
  1. Tentatively extend the beam by c
  2. Run L=5 greedy steps (pick smallest valid each time)
  3. Score = -(current_size + greedy_added)

This scores candidate choices by their actual downstream fertility,
not just how many abstract positions remain valid.
Diverse sampling (spread through full range) + greedy lookahead should
identify which beam paths are genuinely "growable" vs stuck.
"""

import sys
import numpy as np

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')


def greedy_lookahead(valid_mask, elems, diffs_arr, N, depth=5):
    """Run depth greedy steps from current state, return count added."""
    v = valid_mask.copy()
    last = elems[-1]
    d = diffs_arr.copy()
    added = 0

    for _ in range(depth):
        # Find smallest valid candidate > last
        remaining = np.where(v[last + 1:])[0]
        if len(remaining) == 0:
            break
        c = int(remaining[0]) + last + 1

        # Add c
        new_diffs = np.array([c - x for x in range(0)], dtype=np.int64)  # placeholder
        # We don't have elems list in lookahead — use diff tracking via valid_mask
        # Actually we need to track diffs to compute new blocking when adding c
        # Use approximation: count of valid remaining after c as proxy, no blocking update
        # (This is an approximation — full tracking would be too expensive)
        v[c] = False
        last = c
        added += 1

    return added


def greedy_lookahead_full(valid_mask, elems, diffs_arr, N, depth=5):
    """Full greedy lookahead: correctly updates valid_mask at each step."""
    v = valid_mask.copy()
    elems_local = list(elems)
    d = diffs_arr  # we'll rebuild as needed
    # Use the fact that valid_mask already encodes all blocked positions
    # Just greedily pick smallest valid and update mask
    # But we need diffs to compute new blocking — use elems_local
    added = 0

    for _ in range(depth):
        last = elems_local[-1]
        remaining = np.where(v[last + 1:])[0]
        if len(remaining) == 0:
            break
        c = int(remaining[0]) + last + 1

        # Compute new diffs and update mask
        new_d = np.array([c - x for x in elems_local], dtype=np.int64)
        all_d = np.concatenate([d, new_d])
        blocked = c + all_d
        blocked = blocked[(blocked <= N)]

        v[c] = False
        if len(blocked) > 0:
            v[blocked] = False

        elems_local.append(c)
        d = all_d
        added += 1

    return added


def beam_search_sidon(N=10000, k_beams=50, n_samples=10, lookahead_depth=5):
    initial_valid = np.ones(N + 1, dtype=bool)
    initial_valid[0] = False
    initial_diffs = np.array([], dtype=np.int64)
    beams = [([0], initial_diffs, initial_valid)]
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

            # Sample spread across valid range
            if len(valid_indices) <= n_samples:
                sampled = valid_indices.tolist()
            else:
                step = len(valid_indices) // n_samples
                idx = [min(i * step, len(valid_indices) - 1) for i in range(n_samples)]
                idx[-1] = len(valid_indices) - 1
                sampled = valid_indices[sorted(set(idx))].tolist()

            for c in sampled:
                new_diffs = np.array([c - x for x in elems], dtype=np.int64)
                all_diffs = np.concatenate([diffs_arr, new_diffs])

                blocked = c + all_diffs
                blocked = blocked[(blocked <= N)]

                new_valid = valid_mask.copy()
                new_valid[c] = False
                if len(blocked) > 0:
                    new_valid[blocked] = False

                new_elems = elems + [c]

                # Score by greedy lookahead
                la = greedy_lookahead_full(new_valid, new_elems, all_diffs, N, depth=lookahead_depth)
                score = -(len(new_elems) + la)

                pool.append((score, c, new_elems, all_diffs, new_valid))

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
    return beam_search_sidon(N=10000, k_beams=50, n_samples=10, lookahead_depth=5)
