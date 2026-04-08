# fitness: TBD
"""
Beam search greedy for Sidon sets — k_beams=30, max_cand=3.

Key data structure: each beam maintains its own sorted list of still-valid
candidates. When extending by c, newly blocked positions are removed via:
  newly_blocked = {c + d for d in all_diffs}
This is O(|diffs|) incremental update, avoiding O(N*|S|) re-scan.

Score = remaining valid candidates (more = better future flexibility).
"""

import sys
import bisect

sys.path.insert(0, '/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon')


def beam_search_sidon(N=10000, k_beams=30, max_cand_per_beam=3):
    """
    Beam search for maximum Sidon set in [0, N].

    Each beam state: (elems_list, diffs_frozenset, valid_candidates_sorted_list)
    Score: number of remaining valid candidates (more = more future options = better).
    """
    initial_valid = list(range(1, N + 1))
    # State: (elems, diffs_set, valid_cands)
    beams = [([0], set(), initial_valid)]
    best = [0]

    while beams:
        pool = []  # (neg_valid_count, neg_len, elems, diffs, valid_cands)

        for elems, diffs, valid_cands in beams:
            if not valid_cands:
                if len(elems) > len(best):
                    best = elems[:]
                continue

            # Try first max_cand_per_beam candidates (already valid — no re-check needed)
            for c in valid_cands[:max_cand_per_beam]:
                new_diffs = set(c - x for x in elems)
                all_diffs = diffs | new_diffs

                # Positions blocked by adding c: {c + d for d in all_diffs}
                newly_blocked = set()
                for d in all_diffs:
                    pos = c + d
                    if pos <= N:
                        newly_blocked.add(pos)

                # Filter valid_cands: keep f > c and f not in newly_blocked
                start = bisect.bisect_right(valid_cands, c)
                new_valid = [f for f in valid_cands[start:] if f not in newly_blocked]

                score = -len(new_valid)  # ascending sort → larger remaining = lower score = better
                pool.append((score, -(len(elems) + 1), elems + [c], all_diffs, new_valid))

        if not pool:
            break

        # Sort: primary = most remaining valid, secondary = longest beam
        pool.sort(key=lambda x: (x[0], x[1]))

        # Deduplicate and keep top k_beams
        seen = set()
        beams = []
        for score, neg_len, elems, diffs, valid_cands in pool:
            key = tuple(elems)
            if key not in seen and len(beams) < k_beams:
                seen.add(key)
                beams.append((elems, diffs, valid_cands))

        for elems, _, _ in beams:
            if len(elems) > len(best):
                best = elems[:]

    return best


def entrypoint():
    return beam_search_sidon(N=10000, k_beams=30, max_cand_per_beam=3)
