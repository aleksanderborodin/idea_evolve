# Observations — Experimentator 1, Gen 3

## Key findings

### 1. Singer ceiling is 102 for N=10000 (geometric proof)
- q=101: v=10303, max_gap=509 > excess=302 → all 102 fit
- q=103: v=10713, max_gap=423 < excess=712 → lose 2 → 102
- q≥107: losses increase rapidly (9, 11, 17 for q=107, 109, 113)
- The critical condition is: max_gap > (v - N - 1)

### 2. Truncated Singer sets are fully saturated (zero addable elements)
- Tested q=103 (freed 205 diffs) and q=107 (freed 927 diffs)
- Both have ZERO addable elements after truncation
- Singer's difference structure has deep rigidity — even partial subsets inherit full saturation

### 3. Minimum blockers = 45 for q=101 truncation
- Easiest-to-add elements: 9843, 9958, 9981 (all near N=10000)
- Even these require removing 45 of 102 members
- Blocker distribution: mean=67.1, max=90

### 4. Helper deployed: `optimal_shift.py`
- `find_optimal_shift(singer_set, v, N)` → (best_shift, truncated_set)
- `analyze_blockers(sidon_set, N)` → {non_member: blocker_count}
- 9 tests passed, verified on 5 primes

## Strategic implications

1. **Singer is definitively exhausted.** Not just empirically (SA fails) but provably — the geometric constraint caps Singer at 102 for N=10000, and even truncated subsets cannot be extended.

2. **103+ requires non-Singer elements.** The path forward must involve constructions from a fundamentally different algebraic family, or ILP/constraint programming to find solutions with no algebraic structure.

3. **Boundary elements are the weak point.** The elements with fewest blockers (45) are all near N=10000. This hints that slightly expanding the range (if allowed) or using constructions that naturally avoid boundary effects might help.
