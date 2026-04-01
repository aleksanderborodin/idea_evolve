# fitness: TBD
"""Simulated annealing for Sidon set optimization.

Uses efficient incremental diff tracking to support fast add/remove operations.
Combines SA with iterated local search: perturb by removing multiple elements,
then greedily regrow.
"""

import random
import math
import time
import bisect


def entrypoint():
    N = 10000
    TIME_LIMIT = 27  # seconds, leaving margin

    # --- Efficient Sidon set data structure ---
    # S_sorted: sorted list of elements
    # S_set: set for O(1) membership
    # diff_count: dict mapping diff -> number of pairs producing that diff (always 0 or 1 for valid Sidon)

    def build_from_list(elements):
        """Build data structure from a list of elements (assumed valid Sidon)."""
        s = sorted(set(elements))
        dc = {}
        for i in range(len(s)):
            for j in range(i + 1, len(s)):
                d = s[j] - s[i]
                dc[d] = dc.get(d, 0) + 1
        return s, set(s), dc

    def can_add(S_sorted, diff_count, x):
        """Check if x can be added. Returns True if no conflict."""
        for s in S_sorted:
            d = abs(x - s)
            if d in diff_count:
                return False
        return True

    def add_elem(S_sorted, S_set, diff_count, x):
        """Add element x (must be valid to add)."""
        for s in S_sorted:
            d = abs(x - s)
            diff_count[d] = diff_count.get(d, 0) + 1
        bisect.insort(S_sorted, x)
        S_set.add(x)

    def remove_elem(S_sorted, S_set, diff_count, x):
        """Remove element x from the set."""
        idx = bisect.bisect_left(S_sorted, x)
        S_sorted.pop(idx)
        S_set.discard(x)
        for s in S_sorted:
            d = abs(x - s)
            diff_count[d] -= 1
            if diff_count[d] == 0:
                del diff_count[d]

    def snapshot(S_sorted):
        return list(S_sorted)

    def restore(S_sorted_ref, S_set_ref, diff_count_ref, saved_list):
        """Restore state from snapshot."""
        s, ss, dc = build_from_list(saved_list)
        S_sorted_ref.clear()
        S_sorted_ref.extend(s)
        S_set_ref.clear()
        S_set_ref.update(ss)
        diff_count_ref.clear()
        diff_count_ref.update(dc)

    # --- Build initial greedy solution ---
    S_sorted = [0]
    S_set = {0}
    diff_count = {}
    for candidate in range(1, N + 1):
        if can_add(S_sorted, diff_count, candidate):
            add_elem(S_sorted, S_set, diff_count, candidate)

    best = snapshot(S_sorted)
    best_score = len(best)

    # --- Greedy local search: try to add any element ---
    def greedy_fill(S_sorted, S_set, diff_count, candidates=None):
        """Try adding elements from candidates list or full range."""
        if candidates is None:
            candidates = range(0, N + 1)
        added = 0
        for c in candidates:
            if c not in S_set and can_add(S_sorted, diff_count, c):
                add_elem(S_sorted, S_set, diff_count, c)
                added += 1
        return added

    start_time = time.time()

    # SA parameters
    T = 1.5
    T_min = 0.01
    # We'll cool based on time remaining

    iteration = 0
    no_improve = 0

    while time.time() - start_time < TIME_LIMIT:
        elapsed = time.time() - start_time
        # Linear cooling
        T = 1.5 * (1.0 - elapsed / TIME_LIMIT) + T_min

        iteration += 1
        move_type = random.random()

        if move_type < 0.4:
            # Move 1: Try adding a random element (pure greedy)
            candidate = random.randint(0, N)
            if candidate not in S_set and can_add(S_sorted, diff_count, candidate):
                add_elem(S_sorted, S_set, diff_count, candidate)
                if len(S_sorted) > best_score:
                    best = snapshot(S_sorted)
                    best_score = len(best)
                    no_improve = 0

        elif move_type < 0.7:
            # Move 2: Swap one random element for another
            if not S_sorted:
                continue
            # Pick element to remove
            removed = random.choice(S_sorted)
            remove_elem(S_sorted, S_set, diff_count, removed)

            # Try to find a replacement
            found = False
            for _ in range(20):
                c = random.randint(0, N)
                if c not in S_set and can_add(S_sorted, diff_count, c):
                    add_elem(S_sorted, S_set, diff_count, c)
                    found = True
                    break

            if found:
                # Swap: same or different size (if we also greedy fill after)
                # Try to greedy fill after swap
                extra = 0
                for _ in range(5):
                    c = random.randint(0, N)
                    if c not in S_set and can_add(S_sorted, diff_count, c):
                        add_elem(S_sorted, S_set, diff_count, c)
                        extra += 1

                if len(S_sorted) > best_score:
                    best = snapshot(S_sorted)
                    best_score = len(best)
                    no_improve = 0
                elif len(S_sorted) < best_score:
                    # Undo: restore best
                    restore(S_sorted, S_set, diff_count, best)
            else:
                # Couldn't replace: accept smaller set with SA probability
                delta = 1
                if random.random() < math.exp(-delta / T):
                    pass  # accept smaller
                else:
                    # Restore by adding back removed element
                    add_elem(S_sorted, S_set, diff_count, removed)

        else:
            # Move 3: Remove k random elements, then greedily fill
            k = random.randint(2, max(2, len(S_sorted) // 10))
            saved = snapshot(S_sorted)

            to_remove = random.sample(S_sorted, min(k, len(S_sorted)))
            for x in to_remove:
                remove_elem(S_sorted, S_set, diff_count, x)

            # Greedy fill with random order
            candidates = list(range(0, N + 1))
            random.shuffle(candidates)
            greedy_fill(S_sorted, S_set, diff_count, candidates)

            if len(S_sorted) > best_score:
                best = snapshot(S_sorted)
                best_score = len(best)
                no_improve = 0
            elif len(S_sorted) < len(saved):
                delta = len(saved) - len(S_sorted)
                if random.random() < math.exp(-delta / T):
                    pass  # accept worse
                else:
                    restore(S_sorted, S_set, diff_count, saved)
            # else: same or better — accept

        no_improve += 1

        # Periodic restart from best if stuck
        if no_improve > 5000:
            restore(S_sorted, S_set, diff_count, best)
            no_improve = 0

    return best
