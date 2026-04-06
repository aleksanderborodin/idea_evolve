## Question

Can three shared helper functions (find_singer_set, greedy_sidon, build_diff_counts) be built,
tested, and deployed reliably? Additionally: does Singer q=101 with cyclic shift achieve ≥100
elements in {0..10000}?

## Methodology

### Helper Development
- **Control**: Existing `helpers/core.py` functions (`is_sidon`, `count_violations`, etc.)
- **Treatment**: Three new helpers developed iteratively in `output/sandbox/scripts/`
- **Verification**: Each helper tested against known ground-truth values
- **Integration**: Tested with helpers deployed alongside `core.py` via temporary copy

### Singer q=101 Cyclic Shift Search (Bonus Experiment)
- **Control**: Singer q=97 + perturbation = 99 elements (current best)
- **Treatment**: Singer q=101 (102 elements in Z_{10303}), exhaustive search over all 10303 cyclic shifts
- **Measurement**: Count of elements falling within {0..10000} for each shift

## Results

### Helper Verification

| Helper | Test | Expected | Actual | Pass? |
|--------|------|----------|--------|-------|
| `find_singer_set(7)` | Size | 8 | 8 | ✓ |
| `find_singer_set(7)` | is_sidon | True | True | ✓ |
| `find_singer_set(97)` | Size | 98 | 98 | ✓ |
| `find_singer_set(97)` | is_sidon | True | True | ✓ |
| `find_singer_set(97)` | Range | {0..9506} | {0..9506} | ✓ |
| `find_singer_set(101)` | Size | 102 | 102 | ✓ |
| `find_singer_set(101)` | is_sidon | True | True | ✓ |
| `find_singer_set(101)` | Range | {0..10302} | {0..10302} | ✓ |
| `find_singer_set(2)` | Size | 3 | 3 | ✓ |
| `find_singer_set(3)` | Size | 4 | 4 | ✓ |
| `find_singer_set(5)` | Size | 6 | 6 | ✓ |
| `greedy_sidon(range(10001))` | Size | 66 | 66 | ✓ |
| `greedy_sidon(singer_97)` | Size | 98 | 98 | ✓ |
| `greedy_sidon(singer_101)` | Size | ≥100 | 100 | ✓ |
| `build_diff_counts(singer_97)` | Diff count | 4753 | 4753 | ✓ |
| `build_diff_counts(singer_97)` | All=1 | True | True | ✓ |

### Performance

| Helper | Input | Time |
|--------|-------|------|
| `find_singer_set(7)` | q=7 | 0.001s |
| `find_singer_set(97)` | q=97 | 0.057s |
| `find_singer_set(101)` | q=101 | 0.035s |
| `greedy_sidon(range(10001))` | 10001 candidates | 0.046s |
| `build_diff_counts(singer_97)` | 98 elements | 0.001s |

### Singer q=101 Cyclic Shift Search

**KEY FINDING**: Shift 3538 places ALL 102 elements of Singer q=101 within {0..10000}.

| Metric | Value |
|--------|-------|
| Best shift | 3538 |
| Elements in {0..10000} | **102** (all of them) |
| Max element | 9957 |
| Min element | 0 |
| is_sidon | True |
| violations | 0 |
| Shifts giving ≥100 | 4478/10303 (43.5%) |
| Shifts giving ≥101 | 1807/10303 (17.5%) |
| Shifts giving all 102 | 569/10303 (5.5%) |

The resulting 102-element Sidon set:
```
[0, 15, 26, 48, 235, 366, 447, 616, 652, 918, 1005, 1054, 1106, 1151, 1201, 1308,
 1449, 1488, 1506, 1673, 1685, 1813, 1833, 1931, 1937, 1966, 2004, 2109, 2328, 2372,
 2431, 2441, 2531, 2645, 2682, 2747, 3018, 3279, 3309, 3538, 3539, 3541, 3546, 3609,
 3623, 3683, 3951, 3994, 4086, 4152, 4263, 4272, 4380, 4427, 4670, 4796, 4838, 5347,
 5499, 5626, 5755, 5787, 5808, 5833, 5849, 6134, 6299, 6379, 6875, 6898, 7081, 7190,
 7276, 7401, 7523, 7635, 7696, 7750, 8176, 8207, 8306, 8346, 8370, 8397, 8425, 8546,
 8559, 8563, 8635, 8669, 8785, 8843, 8939, 9027, 9120, 9252, 9335, 9534, 9590, 9609,
 9765, 9957]
```

## Conclusions

1. **All three helpers are correct and ready for deployment.** Every verification test passes.
   Performance is fast enough for interactive use (all < 0.1s).

2. **Singer q=101 with shift=3538 yields a 102-element Sidon set in {0..10000}.**
   This exceeds the target of 100 by 2 elements. The previous best was 99 (Singer q=97 +
   perturbation). This is a +3 improvement and a new record for this problem instance.

3. **The State of Affairs was wrong about the 99→100 barrier.** It assumed this was a hard
   boundary requiring sophisticated search. In reality, the right algebraic construction
   (q=101 instead of q=97) trivially exceeds it. The barrier was an artifact of using
   the wrong prime, not a fundamental limitation.

4. **569 out of 10303 shifts (5.5%) give all 102 elements.** The Singer q=101 set is well-suited
   to the {0..10000} constraint because 10303 is close to 10001, so only ~3% of elements
   can fall outside the window at any shift.

## Confidence Level

**High** — all results verified by `is_sidon()` from the existing trusted helper, and
independently by `evaluate.py` which scored the solution at fitness=102.

## Limitations

- `find_singer_set` only works for prime q (not prime powers). The full Singer construction
  over GF(q^k) for prime powers would require polynomial arithmetic, which is more complex.
- The primitive element search is brute-force and could be slow for very large primes (q > 200).
  For the primes relevant to this problem (q ≤ 109), it completes in < 0.1s.
- The specific shift (3538) depends on the primitive polynomial and primitive element found.
  Different runs with different GF(101) representations may need a different shift value.
  Solution agents should search for the optimal shift rather than hardcoding it.
