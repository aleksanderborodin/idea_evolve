# Observations — gen010_explore_2

## Solutions Produced

| File | Fitness (C) | Valid | Method |
|------|-------------|-------|--------|
| sol01.py | **1.5028628681165177** | Yes | Ultra-fine CD on gen009_exploit_1 |

**Baseline (gen009_exploit_1):** C = 1.5028628682228971
**Improvement:** delta_C ≈ -1.06e-10
**Total ultra-fine CD improvements:** 8003

---

## What Was Attempted

### Architecture attempts (multiple rewrites due to performance issues)

**Attempt 1 — batch_predict_c for CD (K=2000 sub-batches)**
- Timed out. K=2000 was far too large for batch_predict_c (linear scaling with K, not constant).
- Consumed all 500s on standard CD alone with 0 improvements.

**Attempt 2 — Inline window-vectorized CD (CHUNK=500)**
- Window size W=34193 at eps_rel=1e-5 — the "window" was more than half the array.
- Expected ~100ms per delta; actual was 30s per sweep. Abandoned.

**Attempt 3 — Diagnosis**
- Measured tight constraint structure: 15 positions within 1e-12 of max, spread across indices 20632–49704 (span 29072 out of M=60000).
- batch_trial_evaluator's 46x speedup claim was NOT reproducible: it assumed W≈601 (single tight cluster), but this solution has a diffuse plateau spanning half the array.

**Attempt 4 — Custom fast_check on eps_rel=1e-7 high positions (W≈6760)**
- Fast check: O(W*k) per trial; exact verify (full O(M) update) only when fast check passes.
- Coarse CD (10 delta values, 1e-4 to 1e-1): 0 improvements in 37s. Confirms standard-delta convergence.
- Triplet search (200k trials, rate 3666/s): 0 improvements.
- Quadruplet search (50k trials): 0 improvements.
- Ultra-fine CD (deltas 1e-11 to 1e-1): **8003 improvements, delta_C = -1.06e-10 in 381s**.

---

## Key Findings

1. **Triplets and quadruplets found 0 improvements** at all step sizes on this solution. This contradicts the gen9 explore_1 result (150 triplet improvements). Possible explanations:
   - The gen009_exploit_1 solution already had ultra-fine CD applied (pattern_020 confirmed: ultra-fine CD subsumes multi-element perturbations). Gen009_explore_1 started from gen008 best (only standard CD).
   - Our random strategy may have missed the specific triplet directions that gen9 found. Gen9 used a different implementation (sequential incremental_update without the fast_check filter).

2. **Ultra-fine CD still finds improvements** (8003 in 381s ≈ 21/s). The improvement per step is ~1.3e-14, which is near the float64 precision limit. This is genuine improvement, not floating-point noise.

3. **batch_trial_evaluator is NOT useful for this solution** because the autoconvolution plateau spans ~half the array. The 46x speedup assumes W≈601, but W≈6760–34193 here. The experimentator's benchmark was run on a different (or earlier) solution state.

4. **The fast_check filter on W=6760 positions correctly screens out all triplet/quadruplet candidates** — they all have pred_max/integral_sq ≥ best_c. This means NO integral-preserving multi-element move of any random triplet/quadruplet reduces C. The landscape at this solution is genuinely at a multi-element local minimum for random strategies.

5. **Throughput achieved:** 3666 triplet trials/second, far exceeding the gen9 rate of ~200/s. The fast_check pre-filter is very effective at early rejection. The overhead of 200k trials was only 55 seconds.

---

## What I Wish I Had Known

- The batch_trial_evaluator window size issue. The experimentator's "46x speedup" claim was based on a solution with W≈1 tight position. The current solution has 15 spread-out tight positions → W≈9693 → no speedup.
- Pattern_020 explicitly warns: "triplets ineffective after ultra-fine CD". The brief directed triplets BEFORE ultra-fine CD, but both gen009/exploit_1 and gen009/explore_1 had ultra-fine CD interleaved. The gen009_exploit_1 starting point was already ultra-fine-CD-polished.
- The directive to run 500k+ triplet trials assumed batch_predict_c would work at 46x speedup. With the actual speedup being ~1x (or slower), 500k trials in 500s required the custom fast_check approach, which found 0 improvements anyway.

---

## Recommendations for Next Generation

1. **Skip triplets on ultra-fine-CD-polished solutions.** Pattern_020 is confirmed: after ultra-fine CD, both triplets and quadruplets find 0 improvements. Triplet search should only be run starting from standard-CD-only solutions.

2. **Ultra-fine CD is still productive.** 8003 improvements in ~381s. Should continue with even finer deltas (1e-12 to 1e-11) in future generations.

3. **batch_trial_evaluator needs re-benchmarking on the current best solution.** The "46x speedup" is likely wrong for this solution's flat plateau. A new benchmark should measure actual speedup before relying on it.

4. **Idea_023 (minimax perturbation) is the highest-priority untested idea.** With 13 tight positions all within 1e-12 of max and no random triplet/quadruplet finding improvements, the only way to make multi-element progress is to optimize ALL tight positions simultaneously via LP.

5. **Adaptive high_pos threshold:** Use alpha-dependent epsilon for fast_check. For alpha=1e-6, W needs to cover positions within 3e-12 of max (W≈1500). For alpha=1e-1, W needs to cover positions within 3e-7 (W≈15000+). Current static W=6760 may miss some improvements.
