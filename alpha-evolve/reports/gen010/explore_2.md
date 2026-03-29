# Debrief Report — gen010_explore_2

## Solutions

| File | Fitness (C) | Valid | Method |
|------|-------------|-------|--------|
| sol01.py | **1.5028628681165177** | Yes | Ultra-fine CD on gen009_exploit_1 best |

**Baseline (gen009_exploit_1):** C = 1.5028628682228971
**Improvement:** delta_C ≈ −1.06e-10
**Ultra-fine CD improvements:** 8003 moves, 381s

---

## 1. What did I try?

### Coarse CD (10 deltas, 1e-4 to 1e-1) — 37s
Used a custom `fast_check` function (O(W×k) per trial, W≈6760 positions near max at eps_rel=1e-7) as a pre-filter before full O(M) incremental updates. Result: **0 improvements**. Confirms the starting point is standard-delta-converged.

### Triplet search (200k trials) — 55s
Three strategies (S0: random nonzero, S1: 1 large + 1 small + 1 random, S3: 2 nonzero + 1 any). Step sizes log-spaced 1e-6 to 1e-1. Fast_check pre-filter with W≈6760. Result: **0 improvements** in 200k trials at 3666 trials/s.

### Quadruplet search (50k trials) — 18s
Same strategy as triplets but k=4. Result: **0 improvements**.

### Ultra-fine CD (deltas 1e-11 to 1e-1, 50 values) — 381s
Full sweep of all N=30000 elements with fast_check pre-filter and exact incremental_update for candidates. Result: **8003 improvements, delta_C ≈ −1.06e-10**.

---

## 2. What information did I lack?

- **batch_trial_evaluator actual performance on this solution.** The helper was benchmarked at 46x speedup assuming W≈601 (1 tight index at eps_rel=1e-5). This solution has 15 tight positions spread across indices 20632–49704 → W≈9693 → no speedup. Had I known this, I would have skipped the batch_predict_c approach entirely and gone straight to the custom fast_check.
- **Pattern_020 implication for the starting point.** The gen009_exploit_1 solution had ultra-fine CD already applied. The brief's triplet directive assumed starting from a standard-CD-only solution (like gen009_explore_1 which found 150 triplet improvements).
- **Tight position count vs. spread.** The State of Affairs says "13 positions within 1e-12" but doesn't say they're spread across 29072 array positions. This mattered critically for performance.

---

## 3. What given facts might be wrong or outdated?

- **batch_trial_evaluator "46x speedup"**: Not reproducible on the current best solution. Speedup is effectively 1x because W is large, not ~601.
- **"Triplet search with batch pre-filtering" recommended in brief**: Based on false premise that batch_predict_c would be fast. For this solution, batch_predict_c is slower than the custom fast_check on the actual tight-position set.
- **Directive's triplet improvement estimate "hundreds more improvements"**: Was wrong. 200k trials found 0, not ~300-1000. Gen9 explore_1's 150 improvements came from a solution that had only standard CD applied, not ultra-fine CD. Starting from the fully-polished gen9 exploit_1 is fundamentally different.

---

## 4. Was the State of Affairs accurate?

Partially. The State of Affairs correctly:
- Identifies ultra-fine CD as productive (confirmed: 8003 improvements)
- Warns "triplets ineffective after ultra-fine CD" (pattern_020, confirmed)
- Notes idea_023 (minimax) as highest-priority untested approach

Inaccuracy: does not clarify that the gen009_exploit_1 starting point is already ultra-fine-CD-polished. This led the brief to recommend triplet search that was predictably going to find 0 improvements.

---

## 5. What would I do differently?

1. Start with ultra-fine CD immediately (skip triplets and quads entirely for this starting point).
2. Implement idea_023 (minimax perturbation via small LP): solve a 13-constraint LP to find a k-element direction that reduces ALL 13 tight positions simultaneously.
3. Investigate whether the 8003 ultra-fine CD improvements unlocked any new multi-element directions (run a quick 5k triplet test after ultra-fine CD completes, if time allows).

---

## 6. Specific experiments

### Experiment A: Minimax perturbation (idea_023) — HIGHEST PRIORITY
- Enumerate the 13 tight autoconvolution positions (within 1e-12 of max)
- For each pair of elements (i, j), solve a 2-variable LP: min δ₁ subject to: for each tight n, 2*dx*(δ₁*f[(n-i)%M] + δ₂*f[(n-j)%M]) ≤ -ε, δ₂ = -δ₁ (integral-preserving)
- If feasible: the LP gives a direction guaranteed to improve C by reducing all 13 tight positions
- Expected: LP takes ~1ms per (i,j) pair; with 30000² pairs that's too many, but sampling nonzero-index pairs (say top 1000 by gradient norm) would take ~1s

### Experiment B: Post-ultra-fine-CD triplet search
- After sol01.py runs (which now includes ultra-fine CD), the solution has been re-polished
- Run 10k triplet trials to test if the 8003 ultra-fine improvements unlocked new triplet directions
- Expected: 0 improvements (pattern_020 holds) but worth confirming

### Experiment C: Extended ultra-fine CD
- Run more ultra-fine CD passes with deltas 1e-12 to 1e-11 (even finer than current)
- Current run stopped at 1e-11; there may be more improvements at 1e-12 to 1e-13

---

## 7. What surprised me?

1. **Zero triplet improvements despite 200k trials**: Very surprising given gen9 found 150 in 20k. The key difference: gen9 started from a standard-CD-only point; this session started from gen9 exploit_1 which had ultra-fine CD. Pattern_020 is strongly confirmed.

2. **High triplet throughput (3666/s)**: The fast_check approach works beautifully as an early-rejection filter — essentially 100% of trials are rejected at the fast_check stage (no exact verifications needed), giving high throughput.

3. **Ultra-fine CD still finds 8003 improvements on an already-ultra-fine-CD-polished solution**: The previous session (gen9 exploit_1) also did ultra-fine CD. Finding 8003 more improvements suggests the ultra-fine CD landscape is not exhausted. The sequence matters — triplets unlock CD, and here the starting point had NOT had triplets applied (explore_2 was meant to apply triplets first, but they found nothing). So this may be a "pure ultra-fine CD on a fresh starting state" scenario.

4. **The fast_check W=6760 correctly classified ALL 200k triplet trials as non-improving**: This is strong evidence that the solution is at a multi-element local minimum for random-strategy triplets, not just a "few more to find" scenario.

---

## 8. Helper tools feedback

- **batch_trial_evaluator.py**: Misleading documentation. The "46x speedup" and "only 1 tight index at eps_rel=1e-5" claims do not hold for the current best solution. The window approach assumes a tightly clustered autoconvolution maximum, but the current solution has a diffuse plateau spanning ~half the array. Recommend adding a caveat: "speedup degrades if tight positions are spread across the array" and a diagnostic function to report actual window size before use.
- **incremental_autoconv_update.py**: Correct and essential. The in-place use pattern (reassigning autoconv = incremental_update(...)) worked cleanly.
- **compute_c_f64.py**: Not needed (tracked C directly via max(autoconv)/integral_sq).
- **Wished existed**: `minimax_lp_perturbation(autoconv, f_padded, tight_positions, dx, M, k=2)` — returns the optimal k-element integral-preserving perturbation that minimizes the new maximum autoconvolution over all tight positions simultaneously. This would implement idea_023 directly.

---

## 9. Time budget

Total: ~490s (just under the 500s deadline).
- Loading + init: ~5s
- Coarse CD: 37s
- Triplets (200k): 55s
- Quads (50k): 18s
- Ultra-fine CD: 381s (ran to deadline)

Had more time: would have run idea_023 (minimax LP perturbation) and then more ultra-fine CD passes. The most impactful next step is idea_023.
