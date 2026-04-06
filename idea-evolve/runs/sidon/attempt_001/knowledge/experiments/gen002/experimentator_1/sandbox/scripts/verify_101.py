"""Verify the Singer q=101 cyclic shift result in detail."""
import sys
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon")
sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/workspace/gen002_experimentator_1/output/sandbox/scripts")
from helpers.core import is_sidon, count_violations
from dev_singer import find_singer_set

q = 101
v = q * q + q + 1  # 10303
S101 = find_singer_set(q)
print(f"Singer q=101: {len(S101)} elements in Z_{v}")
print(f"Max element: {max(S101)}")
print(f"is_sidon: {is_sidon(S101)}")

# The cyclic group is Z_{10303}. {0..10000} covers 10001/10303 = 97.07%
# So on average 102 * 0.9707 = 99.01 elements fit.
# But we found shift=3538 puts ALL 102 in {0..10000}!

best_shift = 3538
shifted = sorted([(s + best_shift) % v for s in S101])
print(f"\nShift = {best_shift}:")
print(f"Elements: {len(shifted)}")
print(f"Max element: {max(shifted)}")
print(f"Min element: {min(shifted)}")
print(f"All <= 10000: {all(x <= 10000 for x in shifted)}")
print(f"is_sidon: {is_sidon(shifted)}")
print(f"violations: {count_violations(shifted)}")
print(f"\nFull set ({len(shifted)} elements):")
print(shifted)

# Also check: how many shifts give 100+ elements?
count_100plus = 0
count_101plus = 0
count_102 = 0
for shift in range(v):
    count = sum(1 for s in S101 if (s + shift) % v <= 10000)
    if count >= 100:
        count_100plus += 1
    if count >= 101:
        count_101plus += 1
    if count >= 102:
        count_102 += 1
print(f"\nShifts giving >=100 elements: {count_100plus}/{v}")
print(f"Shifts giving >=101 elements: {count_101plus}/{v}")
print(f"Shifts giving all 102 elements: {count_102}/{v}")
