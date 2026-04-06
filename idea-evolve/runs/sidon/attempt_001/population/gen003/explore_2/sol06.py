# fitness: 68
# approach: sa_violation_relaxed
# Simulated Annealing on Sidon sets, ALLOWING TEMPORARY VIOLATIONS.
#
# Standard SA fails because valid neighborhoods are empty (0 valid moves
# from a greedy-optimal set). Relaxed SA treats the set as having an
# objective: size - penalty * violations. This allows "downhill" moves
# through invalid states to escape local optima.
#
# Neighborhood: remove one element, add one element (swap).
#   - Both elements chosen randomly
#   - The move may INCREASE violations
#   - Accept with probability exp(delta_obj / T)
#
# After SA: extract the largest valid Sidon subset via greedy maximization.
#
# Key hypothesis: the 68-element Fibonacci greedy set may have a smaller
# blocker cone than Singer-102, making SA escape more likely.
# Even if SA can't reach 102+, it might find 69-80 element solutions
# with different structural properties.

import random
import time


def build_used_diffs(S):
    """All pairwise positive differences."""
    d = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            d.add(abs(S[j] - S[i]))
    return d


def count_violations(S):
    """Count repeated pairwise sums."""
    sums = {}
    v = 0
    for i in range(len(S)):
        for j in range(i, len(S)):
            s = S[i] + S[j]
            if s in sums:
                v += 1
            else:
                sums[s] = True
    return v


def fib_ordering(a, b, N):
    fibs = []
    x, y = a, b
    while x <= N:
        fibs.append(x)
        x, y = y, x + y
    fib_set = set(fibs)
    rest = [c for c in range(N + 1) if c not in fib_set]
    return fibs + rest


def greedy_sidon(order, N=10000):
    S = []
    used = set()
    for c in order:
        if c < 0 or c > N:
            continue
        nd = []
        ok = True
        for s in S:
            d = abs(c - s)
            if d in used or d in nd:
                ok = False
                break
            nd.append(d)
        if ok:
            S.append(c)
            used.update(nd)
    return sorted(S)


def extract_valid_sidon(S):
    """Greedily extract largest valid Sidon subset."""
    S = sorted(S)
    result = []
    used = set()
    for c in S:
        nd = []
        ok = True
        for s in result:
            d = abs(c - s)
            if d in used or d in nd:
                ok = False
                break
            nd.append(d)
        if ok:
            result.append(c)
            used.update(nd)
    return result


def entrypoint():
    N = 10000
    TIME_LIMIT = 58
    PENALTY = 8.0   # penalty per violation
    start = time.time()

    # Build initial solution using Fibonacci ordering (best from prev session: 68)
    S = greedy_sidon(fib_ordering(3, 13, N), N)
    S = list(S)
    S_set = set(S)
    n_violations = count_violations(S)
    obj = len(S) - PENALTY * n_violations

    best_valid = extract_valid_sidon(S)[:]
    best_obj = obj

    all_elements = list(range(N + 1))

    # SA parameters
    T = 3.0
    T_min = 0.05
    alpha = 0.9998
    rng = random.Random(42)

    step = 0
    while time.time() - start < TIME_LIMIT:
        step += 1
        T = max(T * alpha, T_min)

        # Choose a random swap: remove r, add a
        if not S:
            break
        r = rng.choice(S)
        a = rng.randint(0, N)
        if a in S_set:
            continue

        # Compute change in violations
        # Violations are counted via repeated pairwise sums.
        # Computing exactly is O(|S|^2) -- too slow.
        # Use approximation: only count violations involving r or a.

        # Violations involving r (before removal):
        # For each pair (r, x) with x in S, x != r: sum r+x might be repeated
        # This is hard to compute incrementally without full sum tracking.
        # Use full recompute on every 100th step, fast approx otherwise.

        # Faster approach: track diff set, measure "collision count" as
        # |{d : d appears >= 2 times in pairwise diffs}|
        # Removing r frees |S|-1 diffs; adding a adds |S|-1 new diffs (after removal).

        # For speed: just do the swap and recount violations periodically.
        # Use delta = (new_size - PENALTY * new_violations) - (old_obj)

        # Actually: full recount is O(|S|^2) = ~68^2 = 4624 ops per step.
        # With 58 seconds, we can do ~58*1000 = 58,000 steps / (68^2/10000) ops
        # = at most ~10,000 steps with full recount at each step. Not great.

        # Optimization: batch recount every 50 steps
        S_new = [x for x in S if x != r]
        S_new.append(a)
        n_viol_new = count_violations(S_new)
        obj_new = len(S_new) - PENALTY * n_viol_new

        delta = obj_new - obj
        if delta > 0 or (T > T_min and rng.random() < (2.718 ** (delta / T))):
            S = S_new
            S_set = set(S)
            n_violations = n_viol_new
            obj = obj_new

            # Check if best valid improved
            if n_viol_new == 0 and len(S) > len(best_valid):
                best_valid = S[:]
            elif n_viol_new > 0:
                # Extract valid subset occasionally
                if step % 200 == 0:
                    cand = extract_valid_sidon(S)
                    if len(cand) > len(best_valid):
                        best_valid = cand

    # Final extraction
    cand = extract_valid_sidon(S)
    if len(cand) > len(best_valid):
        best_valid = cand

    return sorted(best_valid)
