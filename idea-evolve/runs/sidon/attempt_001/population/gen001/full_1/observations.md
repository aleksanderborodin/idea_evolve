# Observations — gen001_full_1

## Solutions Produced

| File | Fitness | Valid | Violations | Raw Size | Notes |
|------|---------|-------|------------|----------|-------|
| sol01.py | 66 | yes | 0 | 66 | Iterated local search + greedy |

## What I Tried

### Attempt 1: Parabola/quadratic-residue algebraic construction
- Tried embedding `{i*p + (i^2 mod p) : i=0,...,p-1}` for primes p=97 and p=101
- **Result: NOT a valid Sidon set for large p.** p=7 works (verified), but p=101 had 312 violations.
- Root cause: the "parabola embedding" into integers is only Sidon for very small primes where the residue differences can't accidentally produce collisions across the p-boundary.
- Lesson: This construction is WRONG for large p. Do not reuse.

### Attempt 2: Random greedy with numpy speedup
- Tried shuffling candidates randomly before greedy scan
- Random ordering gives **58–62 elements** (worse than deterministic 66!)
- The forward scan (0,1,2,...) is actually a strong greedy heuristic — it picks the densest packing of small numbers.
- 10 random restarts in ~1.5s → never beat 66.

### Attempt 3: Local search (remove-1, add-2+)
- Start from greedy-66, try: remove one element, rebuild diff set, greedily add candidates
- Vectorized `_find_available` using numpy to find non-blocked candidates
- **Critical finding:** after removing any single element from the greedy-66 set, only **1 candidate** becomes available (the removed element itself). The greedy-66 set is an extremely dense local maximum — removing any element doesn't free enough differences to add 2 new elements.
- Result: no improvement, stayed at 66.

### Attempt 4: Iterated local search (perturbation + fill + local search)
- Perturb by removing 2-5 random elements, then greedily fill
- After perturbation: greedy fill gets back to ~63-65, then local search can't improve
- Still 66.

## Key Insights

1. **The greedy-66 set is a very strong local optimum.** Simple 1-opt moves (remove 1, add 2) don't find improvements because the greedy packing is extremely tight.

2. **Random greedy is inferior to deterministic greedy** for this problem. The smallest-first ordering naturally finds a dense Sidon set.

3. **The parabola construction `i*p + i^2 mod p` is NOT Sidon for large p.** Verified violations for p=101. The correct Singer/Paige difference set construction requires GF(p^3) arithmetic.

4. **Local search needs larger moves.** To escape the 66-element local optimum, we probably need to remove 10-20 elements simultaneously and then re-optimize — effectively a restart with a modified candidate pool.

5. **Validate.py was modified** during the run: violations now give fitness=0 (sentinel) instead of extracting a valid subset. The "violation exploitation" strategy from the brief is no longer viable.

## What Would Help

- A correct Singer difference set implementation: For prime p=97, a Singer set gives 98 elements in {0,...,9506}. This requires GF(p^2) arithmetic (find element of order p^2+p+1).
- Simulated annealing with large neighborhood moves
- More time — the current local search needs more iterations to escape the dense local optima

## Time Budget
Used all 27 seconds (26.6s eval time). Not enough time left to try additional approaches after the slow local search.
