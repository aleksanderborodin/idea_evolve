"""Try remove-k and re-extend on the 105-mark ruler to find 106+."""
import random
import time

RULER_105 = [0, 12, 200, 213, 235, 296, 402, 468, 473, 513, 725, 854, 855, 964, 1018, 1059, 1209, 1375, 1392, 1578, 1657, 1664, 1907, 1974, 2048, 2087, 2208, 2285, 2295, 2695, 2793, 2818, 2842, 2868, 2969, 2975, 3074, 3112, 3130, 3190, 3194, 3322, 3640, 3654, 3683, 4066, 4081, 4128, 4277, 4342, 4358, 4411, 4431, 4523, 4662, 4698, 4717, 4820, 5239, 5291, 5323, 5381, 5408, 5683, 5839, 5992, 6026, 6034, 6219, 6365, 6441, 6509, 6589, 6768, 6952, 7009, 7161, 7358, 7446, 7565, 7624, 7823, 7860, 7893, 7923, 8228, 8231, 8259, 8390, 8399, 8653, 8697, 8823, 8871, 8917, 8968, 9330, 9402, 9520, 9644, 9655, 9746, 9748, 9769, 9884]

def greedy_extend(S, N=10000):
    S = sorted(S)
    s_set = set(S)
    diffs = set()
    for i in range(len(S)):
        for j in range(i + 1, len(S)):
            diffs.add(S[j] - S[i])
    for c in range(N + 1):
        if c in s_set:
            continue
        ok = True
        new_diffs = []
        for x in S:
            d = abs(c - x)
            if d in diffs:
                ok = False
                break
            new_diffs.append(d)
        if ok:
            S.append(c)
            S.sort()
            s_set.add(c)
            for d in new_diffs:
                diffs.add(d)
    return S

random.seed(42)
best_size = 105
best_set = list(RULER_105)

start = time.time()

for k in [1, 2, 3, 4, 5]:
    trials = min(2000, max(100, 5000 // k))
    improved = 0
    for t in range(trials):
        to_remove = set(random.sample(RULER_105, k))
        remaining = [x for x in RULER_105 if x not in to_remove]
        extended = greedy_extend(remaining)
        if len(extended) > best_size:
            best_size = len(extended)
            best_set = extended
            improved += 1
            print(f"  k={k}, trial {t}: NEW BEST = {best_size} (removed {sorted(to_remove)})")
    elapsed = time.time() - start
    print(f"k={k}: {trials} trials done, best={best_size}, elapsed={elapsed:.1f}s")
    if elapsed > 120:
        print("Time limit approaching, stopping.")
        break

print(f"\nFinal best size: {best_size}")
if best_size > 105:
    print(f"Best set: {best_set}")
