## Current Population Status
Best solution: `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/permcodes/attempt_001/population/gen000/baseline/sol01.py` → fitness 262 (greedy baseline)
No top/ directory yet — this is generation 1.

## Read First
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/description.md`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/agl18.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/compat.py`
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/permcodes/helpers/core.py`

## Directive

**This is a Track B exploration focused on Iterative Local Search (ILS) and Simulated Annealing.** Your goal is to beat 616 codewords by using optimization methods on top of the algebraic starting point. Do NOT just copy the AGL(1,8) construction — your specific contribution is the search strategy to exceed the algebraic bound.

**Context:** AGL(1,8) gives exactly 616 codewords. The theoretical upper bound is 926. The gap [616, 926] is wide. We need iterative search to explore it. Greedy extension from 616 is unlikely to add codewords directly because the 11-orbit AGL clique is tight — but if we "break up" the code and rebuild differently, we might find a non-AGL configuration with more codewords.

**Approach: Destroy-and-Repair ILS**

Core idea: the AGL(1,8) code is a 616-point clique in the permutation compatibility graph G(8,5). This clique may not be maximum (upper bound is 926). To search for larger cliques:

1. Start with the AGL(1,8) 616-codeword code (use `agl18_max_clique_code()`)
2. Repeat many times:
   a. **Destroy:** Remove a random subset of k codewords (try k=30, 50, 100)
   b. **Repair:** From the remaining codewords, greedily add any compatible permutation until no more can be added. Use `fast_compatible_mask` from helpers/compat.py for speed.
   c. If new code size > current best, keep it; otherwise discard
3. Track the best code found across all iterations

**Important implementation details:**
- Build all 40320 permutations once with `build_all_perms()`
- Build bucket_ids once with `build_bucket_ids(all_perms)` — this is the 0.4s precomputation
- For each repair step: given current code indices in all_perms, call `fast_compatible_mask(code_indices, bucket_ids)` to get all compatible permutations; add them in random order to try to fill more
- Use `np.random.seed` for reproducibility, but vary seeds across iterations

**Write these solutions:**

`output/sol01.py` — ILS with small destruction (k=30), 20 iterations:
```
- Start from AGL(1,8) 616-code
- 20 × [remove 30 random codewords, greedy-repair with fast_compatible_mask]
- Keep best code found
- Must call entrypoint() and return np.ndarray
```
Evaluate immediately: `python3 .../evaluate.py output/sol01.py`

`output/sol02.py` — ILS with larger destruction (k=100), 10 iterations:
```
- Same structure but remove 100 codewords per iteration
- Larger destruction → more diverse repair paths → potentially different local optima
```
Evaluate immediately.

`output/sol03.py` — Simulated Annealing on the code:
```
- Start from AGL(1,8) 616-code
- At each step: try swapping a random codeword for a random compatible codeword
  (one that is compatible with the remaining code minus the one being swapped)
- Accept if new code is larger, or with small probability if equal size (to escape plateaus)
- Run for 10000 steps
- At every 1000 steps, attempt greedy repair to add any remaining compatible codewords
```
Evaluate immediately.

**Mandatory workflow:** Write one solution → evaluate immediately → verify .score created → write next.

After all solutions evaluated, write `output/report.md` with:
- Scores achieved by each solution
- Whether ILS broke through 616
- How many compatible codewords were found during repair steps (is the 616-code tight or loose?)
- Best ILS configuration found
- Recommendations for next generation (which parameters to tune, what iteration counts to try)
