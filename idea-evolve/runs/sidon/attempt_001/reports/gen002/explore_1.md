# Debrief Report — gen002_explore_1 (Explore, Track B)

## Solution Summary

| Solution | Construction | Fitness | Valid | Violations | Eval Time |
|----------|-------------|---------|-------|------------|-----------|
| sol01.py | Erdős-Turán p=71: {2·71·k + k²%71 : k=1..70} | **70** | ✓ | 0 | 0.004s |
| sol02.py | ET p=71 + greedy extension over {0..10000} | **74** | ✓ | 0 | 0.038s |
| sol03.py | ET p=71 + greedy + 1-opt swap (each element tried) | **75** | ✓ | 0 | 1.4s |
| sol04.py | Randomized greedy + 1-opt, 25s multi-restart | **75** | ✓ | 0 | 25s |

Best result: **75** (sol03 and sol04). All solutions have zero violations.

---

## 1. What I Tried

**Ruzsa construction {a·p + a²%p}**: The brief described this as producing p Sidon elements. Testing showed it produces 0 violations only for p≤7, then fails with hundreds of violations for larger primes (p=97: 312 violations, p=101: 304 violations). The carry mechanism: (a+b-c-d)·p = r_c+r_d-r_a-r_b can equal ±p since |RHS| < 2p. Not usable.

**Bose-Chowla {i·p + g^i%p}**: Same carry issue. p=97: 248 violations. Not usable.

**Erdős-Turán {2pk + k²%p}**: Uses spacing 2p, which prevents all carries (|RHS| < 2p < 2p). Proven valid. p=71 gives 70 elements in {143..9941}. Best prime for N=10000.

**Greedy extension**: Added 4 elements (0, 71, 235, 4219) to ET(71), giving 74 elements.

**1-opt swap search**: Removed one element at a time, re-greedy-extended. Found one improvement (removing element 9010 → 75 elements). Converged after one productive pass.

**Multi-restart randomized greedy + 1-opt**: 25-second time limit, random orderings of {0..10000}. All restarts converged to 75. No improvement over ET-seeded 1-opt.

---

## 2. What Information I Lacked

- The correct formulas for Ruzsa and Bose-Chowla Sidon constructions. The brief's formulas are wrong for large primes. I would have benefited from: "the Ruzsa construction requires spacing ≥ 2p to prevent carry violations, making it equivalent to Erdős-Turán."
- Whether a 2-opt search (remove 2, add 3) could break the 75-element barrier. I estimated probability ~10^{-11} per pair, making it infeasible in Python.

---

## 3. What Given Facts Might Be Wrong

- **Brief Option A (Ruzsa)** says "This gives p elements in {0, ..., p²+p-1} forming a Sidon set." FALSE for p≥11. The formula {a·p + a²%p} has sum collisions due to carries.
- **Brief Option B (Bose-Chowla)** has the same issue. Neither formula works as stated.
- The dead-end in state_of_affairs ("Parabola/quadratic-residue constructions: Mathematically incorrect for large primes") is CORRECT and covers both constructions.

---

## 4. Was the State of Affairs Accurate?

Yes, the state of affairs was accurate. The dead-end note about quadratic constructions was correct. The coverage map correctly showed ET as untested (it wasn't listed). This was a genuinely new direction.

---

## 5. What I Would Do Differently

- Skip Ruzsa/Bose-Chowla immediately (they don't work as described)
- Implement ET as the main algebraic alternative: ET(71) → greedy → 1-opt → 75 elements
- Spend remaining time on 2-opt or SA with size-decreasing moves from the 75-element set

---

## 6. Specific Experiments to Run

1. **2-opt from ET(75)**: Remove pairs of elements and greedy extend. Time: ~30 minutes (2775 pairs × 0.7s each). Might find 76-77. Worth doing in a dedicated session.
2. **SA with size-decrease acceptance**: From the 75-element local optimum, run SA that accepts temporary size decreases (probability e^{-1/T}). T schedule: 2.0 → 0.1 over 10000 steps. Might find 77-80.
3. **ET + Singer hybrid**: Combine the ET(75) set structure with Singer q=97 via genetic crossover. The two sets live in different regions of {0..10000} and have different difference structures — might be compatible.
4. **Correct Ruzsa construction**: The actual Ruzsa construction that works uses {a·(p+1) + something} or a different parameterization. Worth researching the original 1993 paper.

---

## 7. Surprises

- The Ruzsa and Bose-Chowla formulas described in the brief don't work. The state_of_affairs "dead-end" note about quadratic constructions was already covering this, but the brief presented them as valid options.
- ET(71) + greedy + 1-opt converges to exactly 75 with high stability — every random restart gives exactly 75. This is a strong local optimum.
- ET uses only 24% of difference space (vs Singer's 50%), suggesting it's less "dense" than Singer but also less saturated. Yet the search still caps at 75.
- All 4 random-restart runs converged to the same size (75), suggesting 75 is a robust local maximum for non-algebraic search starting below it.

---

## 8. Helper Tools Feedback

- `is_sidon()` and `count_violations()` are essential. Used them indirectly via evaluate.py.
- `can_add(S_sorted, used_diffs, candidate)` would have made the greedy extension cleaner. I reimplemented it inline.
- Missing: a `find_et_set(p)` helper that validates the prime and returns the Erdős-Turán set directly. Would prevent the trial-and-error on which primes work.
- Missing: a `build_diff_set(S)` helper — I reimplemented this in every solution.

---

## 9. Time Budget

Adequate. The exploration was thorough for the Track B constraint (no Singer). The main bottleneck was discovering the Ruzsa/Bose-Chowla formulas were incorrect, which consumed the time originally planned for those constructions. With correct formulas from the start, I could have spent more time on 2-opt or SA variants.
