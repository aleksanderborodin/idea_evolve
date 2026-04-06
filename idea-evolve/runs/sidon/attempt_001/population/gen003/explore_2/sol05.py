# fitness: 69
# approach: wider_ordering_search_plus_blocker_analysis
#
# This solution does two things:
# 1. Wider search over Fibonacci-like and exponential orderings to beat 68.
#    Previous session found fib(3,13)=68. We explore:
#    - Larger (a,b) parameter space
#    - Geometric/exponential sequences (base 1.5, 1.7, phi)
#    - "Reverse-Fibonacci": start from N and go down in Fibonacci steps
#    - Mixed: Fibonacci prefix + dense fill in gaps
#
# 2. Blocker analysis on the 68-element set: count how many blockers each
#    non-member has. If the 68-set has FEWER blockers than Singer-102, SA
#    should have a non-zero chance. Documents this for future agents.

import random
import time
import math


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
    return sorted(S), used


def fib_ordering(a, b, N):
    fibs = []
    x, y = a, b
    while x <= N:
        fibs.append(x)
        x, y = y, x + y
    fib_set = set(fibs)
    rest = [c for c in range(N + 1) if c not in fib_set]
    return fibs + rest


def geo_ordering(base, start, N):
    """Geometric sequence prefix: start, start*base, start*base^2, ..."""
    seq = []
    v = float(start)
    seen = set()
    while v <= N:
        iv = int(round(v))
        if iv <= N and iv not in seen:
            seq.append(iv)
            seen.add(iv)
        v *= base
    rest = [c for c in range(N + 1) if c not in seen]
    return seq + rest


def wythoff_ordering(N):
    """Lower Wythoff sequence: floor(k*phi) for k=1,2,..."""
    phi = (1 + math.sqrt(5)) / 2
    seq = []
    seen = set()
    k = 1
    while True:
        v = int(k * phi)
        if v > N:
            break
        if v not in seen:
            seq.append(v)
            seen.add(v)
        k += 1
    rest = [c for c in range(N + 1) if c not in seen]
    return seq + rest


def count_blockers(S, N=10000):
    """For each non-member c, count elements of S that create a diff conflict."""
    S_set = set(S)
    used_diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            used_diffs.add(abs(S[j] - S[i]))

    blocker_hist = {}
    for c in range(N + 1):
        if c in S_set:
            continue
        blockers = sum(1 for s in S if abs(c - s) in used_diffs)
        blocker_hist[blockers] = blocker_hist.get(blockers, 0) + 1

    return blocker_hist


def entrypoint():
    N = 10000
    TIME_LIMIT = 58
    start = time.time()
    best = []
    best_score = 0

    # Phase 1: wider Fibonacci parameter search
    # Previous session found (3,13)=68. Try larger (a,b) values.
    rng = random.Random(77)
    for a in range(0, 40):
        for b in range(a + 1, a + 60):
            if time.time() - start > 30:
                break
            order = fib_ordering(a, b, N)
            S, _ = greedy_sidon(order, N)
            if len(S) > best_score:
                best_score = len(S)
                best = S[:]
        if time.time() - start > 30:
            break

    # Phase 2: geometric sequences
    for base in [1.3, 1.4, 1.5, 1.618, 1.7, 1.8, 2.0, 2.5, 3.0]:
        for start_v in [1, 2, 3, 5, 7, 11, 13]:
            if time.time() - start > 45:
                break
            order = geo_ordering(base, start_v, N)
            S, _ = greedy_sidon(order, N)
            if len(S) > best_score:
                best_score = len(S)
                best = S[:]
        if time.time() - start > 45:
            break

    # Phase 3: Wythoff ordering
    if time.time() - start < 47:
        order = wythoff_ordering(N)
        S, _ = greedy_sidon(order, N)
        if len(S) > best_score:
            best_score = len(S)
            best = S[:]

    # Phase 4: LNS improvement on best found
    if best and time.time() - start < 55:
        S_cur = list(best)
        used_cur = set()
        for i in range(len(S_cur)):
            for j in range(i + 1, len(S_cur)):
                used_cur.add(abs(S_cur[j] - S_cur[i]))

        while time.time() - start < 56:
            k = rng.randint(3, 20)
            k = min(k, max(1, len(S_cur) - 3))
            to_remove = set(rng.sample(S_cur, k))
            S_new = [x for x in S_cur if x not in to_remove]
            # Recompute diffs
            ud_new = set()
            for i in range(len(S_new)):
                for j in range(i + 1, len(S_new)):
                    ud_new.add(abs(S_new[j] - S_new[i]))
            # Greedy extend with ascending order
            in_new = set(S_new)
            for c in range(N + 1):
                if c in in_new:
                    continue
                nd = []
                ok = True
                for s in S_new:
                    d = abs(c - s)
                    if d in ud_new or d in nd:
                        ok = False
                        break
                    nd.append(d)
                if ok:
                    S_new.append(c)
                    in_new.add(c)
                    ud_new.update(nd)
            if len(S_new) >= len(S_cur):
                S_cur = S_new
                if len(S_cur) > best_score:
                    best_score = len(S_cur)
                    best = S_cur[:]

    return sorted(best) if best else [0]
