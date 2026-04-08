"""Try to extend the 105-mark Rokicki-Dogon ruler by adding elements."""

RULER_105 = [0, 12, 200, 213, 235, 296, 402, 468, 473, 513, 725, 854, 855, 964, 1018, 1059, 1209, 1375, 1392, 1578, 1657, 1664, 1907, 1974, 2048, 2087, 2208, 2285, 2295, 2695, 2793, 2818, 2842, 2868, 2969, 2975, 3074, 3112, 3130, 3190, 3194, 3322, 3640, 3654, 3683, 4066, 4081, 4128, 4277, 4342, 4358, 4411, 4431, 4523, 4662, 4698, 4717, 4820, 5239, 5291, 5323, 5381, 5408, 5683, 5839, 5992, 6026, 6034, 6219, 6365, 6441, 6509, 6589, 6768, 6952, 7009, 7161, 7358, 7446, 7565, 7624, 7823, 7860, 7893, 7923, 8228, 8231, 8259, 8390, 8399, 8653, 8697, 8823, 8871, 8917, 8968, 9330, 9402, 9520, 9644, 9655, 9746, 9748, 9769, 9884]

def can_add(S_sorted, used_diffs, candidate):
    """Check if candidate can be added to S without creating a repeat difference."""
    for x in S_sorted:
        d = abs(candidate - x)
        if d in used_diffs:
            return False
    return True

def get_diffs(S):
    diffs = set()
    for i in range(len(S)):
        for j in range(i+1, len(S)):
            diffs.add(S[j] - S[i])
    return diffs

S = sorted(RULER_105)
diffs = get_diffs(S)
print(f"Starting set size: {len(S)}, span: {S[-1]}")
print(f"Number of differences used: {len(diffs)}")
print(f"Max possible differences in [0,10000]: 10000")
print(f"Remaining capacity: {10000 - len(diffs)} differences")

# Try every candidate in [0, 10000]
candidates = []
for c in range(10001):
    if c in set(S):
        continue
    if can_add(S, diffs, c):
        candidates.append(c)

print(f"\nCandidates that can be added: {len(candidates)}")
if candidates:
    print(f"Candidates: {candidates[:20]}{'...' if len(candidates) > 20 else ''}")

    # Greedy extension
    extended = list(S)
    ext_diffs = set(diffs)
    added = []
    for c in candidates:
        if can_add(extended, ext_diffs, c):
            for x in extended:
                ext_diffs.add(abs(c - x))
            extended.append(c)
            extended.sort()
            added.append(c)

    print(f"\nGreedy extension added {len(added)} elements: {added}")
    print(f"Extended set size: {len(extended)}")
else:
    print("No elements can be added — the ruler is maximal for [0, 10000].")
