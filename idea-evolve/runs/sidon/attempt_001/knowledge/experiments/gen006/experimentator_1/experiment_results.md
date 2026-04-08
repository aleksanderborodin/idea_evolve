# Experiment Results: Helper Module Creation

## Question
Can we create two validated, reusable helper modules (`rokicki_data.py` and `extend.py`)
that all future agents can import, eliminating repeated reimplementation of common utilities?

## Methodology

This was a helper creation task (not a hypothesis experiment). The approach:

1. Read the best solution files (population/top/rank01..03) to extract literal set data
2. Read the existing core helper (helpers/core.py) to understand available primitives
3. Implement helper modules with proper docstrings and test coverage
4. Validate correctness: `is_sidon()` on all stored sets, functional tests on extend.py functions

**Validation tests run:**
- `is_sidon(BEST_105)` → True (len=105)
- `is_sidon(BEST_104)` → True (len=104)
- `is_sidon(BEST_102)` → True (len=102)
- `greedy_extend(BEST_105[:100])` → 105 elements, `is_sidon()` → True
- `count_addable(BEST_105)` → 0 (greedy-maximal confirmed)
- `random_perturbation(BEST_105, 3, seed=42)` → 105 elements, `is_sidon()` → True
- `blocking_power(BEST_105)` → dict of 105 entries, max blocker: element 4662 (7851 blocks)

## Results

### rokicki_data.py
- BEST_105: 105 elements, span=9884, valid Sidon set ✓
- BEST_104: 104 elements, span=9581, valid Sidon set ✓
- BEST_102: 102 elements, span=9775, valid Sidon set ✓

### extend.py
- `greedy_extend(BEST_105[:100])` recovered full 105-element set ✓
  - Removing 5 tail elements and re-extending yields the same greedy-maximal set
- `count_addable(BEST_105)` = 0 confirms greedy-maximality ✓
- `random_perturbation(BEST_105, 3)` preserves Sidon validity and length ✓
- `blocking_power()` works correctly; element 4662 is the highest blocker (7851 candidates blocked) ✓

### Interesting finding from blocking_power
The most blocking element in BEST_105 is 4662, blocking 7851 out of ~9000+ non-member
candidates. This is a key metric for perturbation strategies — removing high-blockers
can open up space for new elements. Future exploit agents should use this.

## Conclusions

Both helpers created, validated, and ready for deployment. Future agents can:
1. Import known-good Sidon sets without reimplementing or hardcoding them
2. Use `greedy_extend` for post-perturbation repair in O(N*k) time
3. Use `blocking_power` to identify candidate elements to remove for perturbation strategies
4. Use `count_addable` to verify greedy-maximality of a candidate solution

## Confidence Level

**High** — all functions tested against ground truth with `is_sidon()` verification.

## Limitations

- `rokicki_data.py` only contains sets of size 102, 104, 105. Sets of other sizes (103, 106+)
  not included — would require downloading from cube20.org.
- `blocking_power()` is O(N*k) and may be slow for large N with large sets. Consider caching
  for repeated calls on the same set.
- `greedy_extend` is deterministic (scans 0..N in order), so it always finds the same greedy
  extension. Non-deterministic variants (random scan order) might find larger sets.
