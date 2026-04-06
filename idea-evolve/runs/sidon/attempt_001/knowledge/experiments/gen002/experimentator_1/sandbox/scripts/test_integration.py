"""Integration test: import helpers from output/helpers/ as they would be in problem/helpers/."""
import sys
import time
import importlib

# We need to test that singer.py and search.py work alongside core.py.
# In the real deployment, they'll all be under problem/helpers/.
# For testing, temporarily copy them next to core.py.
import shutil
import os

HELPERS_DIR = "/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon/helpers"
OUTPUT_DIR = "/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/workspace/gen002_experimentator_1/output/helpers"

# Copy our helpers next to core.py temporarily
shutil.copy2(os.path.join(OUTPUT_DIR, "singer.py"), os.path.join(HELPERS_DIR, "singer.py"))
shutil.copy2(os.path.join(OUTPUT_DIR, "search.py"), os.path.join(HELPERS_DIR, "search.py"))

try:
    sys.path.insert(0, "/home/sasha/Desktop/project_alpha/idea-evolve/problems/sidon")

    from helpers.singer import find_singer_set
    from helpers.search import greedy_sidon, build_diff_counts
    from helpers.core import is_sidon, count_violations

    print("=" * 60)
    print("INTEGRATION TEST: All three helpers")
    print("=" * 60)

    # Test 1: find_singer_set(q=7)
    t0 = time.time()
    S7 = find_singer_set(7)
    t1 = time.time()
    assert len(S7) == 8 and is_sidon(S7), f"q=7 FAIL: len={len(S7)}, sidon={is_sidon(S7)}"
    print(f"[PASS] find_singer_set(7) = {S7}  ({t1-t0:.4f}s)")

    # Test 2: find_singer_set(q=97)
    t0 = time.time()
    S97 = find_singer_set(97)
    t1 = time.time()
    assert len(S97) == 98 and is_sidon(S97) and all(0 <= x <= 9506 for x in S97)
    print(f"[PASS] find_singer_set(97): 98 elements, is_sidon=True, range OK  ({t1-t0:.4f}s)")

    # Test 3: find_singer_set(q=101)
    t0 = time.time()
    S101 = find_singer_set(101)
    t1 = time.time()
    assert len(S101) == 102 and is_sidon(S101) and all(0 <= x <= 10302 for x in S101)
    print(f"[PASS] find_singer_set(101): 102 elements, is_sidon=True, range OK  ({t1-t0:.4f}s)")

    # Test 4: greedy_sidon baseline
    t0 = time.time()
    g66 = greedy_sidon(range(10001))
    t1 = time.time()
    assert len(g66) == 66 and is_sidon(g66)
    print(f"[PASS] greedy_sidon(range(10001)): 66 elements  ({t1-t0:.4f}s)")

    # Test 5: greedy_sidon preserves Singer set
    g97 = greedy_sidon(S97)
    assert len(g97) == 98 and is_sidon(g97)
    print(f"[PASS] greedy_sidon(singer_97): 98 elements (Singer preserved)")

    # Test 6: build_diff_counts on Singer q=97
    t0 = time.time()
    d97 = build_diff_counts(S97)
    t1 = time.time()
    expected = 98 * 97 // 2  # C(98,2) = 4753
    assert len(d97) == expected and all(v == 1 for v in d97.values())
    print(f"[PASS] build_diff_counts(singer_97): {len(d97)} diffs, all count=1  ({t1-t0:.4f}s)")

    # Test 7: Edge cases
    assert greedy_sidon([]) == []
    assert greedy_sidon([5]) == [5]
    assert build_diff_counts([]) == {}
    print(f"[PASS] Edge cases (empty, single element)")

    # Test 8: find_singer_set edge cases
    S2 = find_singer_set(2)
    S3 = find_singer_set(3)
    S5 = find_singer_set(5)
    assert len(S2) == 3 and is_sidon(S2)
    assert len(S3) == 4 and is_sidon(S3)
    assert len(S5) == 6 and is_sidon(S5)
    print(f"[PASS] find_singer_set small primes: q=2({len(S2)}), q=3({len(S3)}), q=5({len(S5)})")

    # Test 9: Cross-check: greedy on Singer q=101 elements in {0..10000}
    g101 = greedy_sidon(S101)
    print(f"[INFO] greedy_sidon(singer_101, N=10000): {len(g101)} elements")
    assert is_sidon(g101), "greedy on Singer q=101 not Sidon!"
    print(f"[PASS] greedy_sidon(singer_101) valid Sidon")

    # Test 10: Cyclic shift search for Singer q=101 (bonus experiment!)
    q = 101
    v = q * q + q + 1  # 10303
    best_count = 0
    best_shift = 0
    for shift in range(v):
        count = sum(1 for s in S101 if (s + shift) % v <= 10000)
        if count > best_count:
            best_count = count
            best_shift = shift
    print(f"[INFO] Singer q=101 best cyclic shift: shift={best_shift}, count={best_count}")

    if best_count >= 100:
        best_set = sorted([(s + best_shift) % v for s in S101 if (s + best_shift) % v <= 10000])
        assert is_sidon(best_set), "Best shifted set not Sidon!"
        print(f"[PASS] Shifted set with {best_count} elements is valid Sidon!")
        print(f"[INFO] Set: {best_set[:10]}... (first 10 of {len(best_set)})")

    print()
    print("=" * 60)
    print("ALL INTEGRATION TESTS PASSED")
    print("=" * 60)

finally:
    # Clean up: remove temp copies
    for f in ["singer.py", "search.py"]:
        p = os.path.join(HELPERS_DIR, f)
        if os.path.exists(p):
            os.remove(p)
