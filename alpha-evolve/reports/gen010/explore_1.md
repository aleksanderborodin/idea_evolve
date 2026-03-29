# Debrief Report — explore_1, Generation 10

## Solutions

| File | Fitness (C) | Valid | Method |
|------|-------------|-------|--------|
| sol01.py | **1.5028628681659377** | Yes | Minimax LP (0 improvements) + ultra-fine CD (1281 improvements) |

**Baseline:** gen009_exploit_1_sol01.py = C = 1.5028628682228971
**Improvement:** -5.70e-11
**Eval time:** ~496s (includes optimization)

---

## 1. What did you try?

### Minimax triplet perturbation (MAIN TARGET — NULL RESULT, 0 improvements)
Implemented the full LP-based minimax approach from idea_023:
- K=28 plateau positions (within 1e-10 of max_ac)
- For each triplet (i,j,k), solved LP: minimize t s.t. h[p]·d ≤ t for all K plateau positions
- Free variables: d1, d2 (d3 = -(d1+d2) for integral preservation)
- 47,233 trials in 220s (~215 trials/s, ~4.5ms per LP solve)
- **Result: 0 improvements. Every trial returned t* ≥ 0.**

### Minimax quadruplet perturbation (NULL RESULT, 0 improvements)
- Extended to k=4 (3 free variables, 28 constraints)
- 21,217 trials in 120s
- **Result: 0 improvements. Same behavior as triplets.**

### Ultra-fine coordinate descent (SUCCESS, 1281 improvements)
- Window-based evaluation (±400 positions around tight indices)
- Delta grid: geomspace(1e-11, 1e-3, 30)
- 2 rounds: 859 improvements (round 1) + 422 improvements (round 2)
- C improved from 1.5028628682228971 → 1.5028628681659377 (delta = -5.70e-11)

---

## 2. What information did I lack?

- **Why minimax LP returns t*=0:** I didn't have a theoretical analysis showing whether the current solution is minimax-optimal. The null result itself is informative.
- **What "improvement mechanism" is left:** CD improves through changing integral, not through reducing max_ac via integral-preserving moves. This wasn't documented anywhere.
- **CD throughput at N=30000:** Only ~14 positions/second with window-based approach. A full round over 30000 positions would take ~36 minutes. I only covered ~5.7% of positions per round.

---

## 3. What given facts might be wrong or outdated?

- **idea_023 (confidence 0.4):** Should now be DEBUNKED or updated to "integral-preserving minimax finds 0 improvements." The idea was sound but the current solution is minimax-optimal w.r.t. integral-preserving moves.
- **Pattern_020 ("ultra-fine CD subsumes multi-element moves"):** More precisely: ultra-fine CD works through a DIFFERENT mechanism than integral-preserving perturbations. Both are "exhausted" but for different reasons.

---

## 4. Was the State of Affairs accurate?

**Accurate on:**
- K≈13-28 plateau positions (confirmed K=15 within 1e-12, K=28 within 1e-10)
- Minimax as highest-priority untested idea (tested, confirmed null)
- CD still finding improvements at fine scales (confirmed)

**Missing:**
- The distinction between integral-preserving moves (exhausted) and non-integral-preserving CD (still active)
- The CD throughput bottleneck at N=30000

---

## 5. What would I do differently?

1. **Faster CD implementation:** Avoid refreshing the tight-window after every improvement. Pre-select candidate positions by gradient magnitude (batch vectorized), then verify promising ones. This could achieve 100+ positions/second instead of 14.
2. **Run more CD rounds:** Only 2 rounds completed with partial coverage. 6+ full rounds with full N coverage would find many more improvements.
3. **Very fine deltas for CD:** Extend to 1e-14 (testing if floor is below 1e-11).
4. **Non-integral-preserving perturbations:** Instead of fixing d_last = -(d_sum), allow the sum to be non-zero. These are not perturbations in the strictest sense but may unlock new improvements as complementary moves to CD.

---

## 6. Specific experiments to run

### Experiment A: Full-coverage ultra-fine CD
Run CD with geomspace(1e-14, 1e-2, 60) deltas over ALL 30000 positions, multiple rounds. Use vectorized first-order pre-filter to reduce incremental_update calls. Expected: 2000-5000 improvements.

### Experiment B: Fast CD with gradient pre-filter
For each position idx, compute grad_C ∝ f_padded[(argmax-idx)%M] - C*integral in O(1). Sort by |grad_C|. Only evaluate top 20% of positions. Maintain persistent window without full recomputation.

### Experiment C: Non-integral-preserving triplets
Allow d1+d2+d3 ≠ 0 (a free parameter). Optimize C = max_ac_new / integral_new² directly. This is a different LP with 3 free variables + 1 for the max. May find improvements that purely integral-preserving moves miss.

### Experiment D: Wider plateau epsilon for minimax
Retry minimax with eps=1e-8 for plateau detection. With fewer plateau positions (maybe K=5-10), the LP might find feasible descent directions. But if the flat plateau is due to genuine optimality, this won't help.

---

## 7. What surprised you?

1. **Minimax LP returns t*=0 for ALL 68k trials.** This is a strong null result suggesting the solution is locally minimax-optimal. The theoretical reason (origin in convex hull of gradient vectors) makes sense but wasn't anticipated.

2. **CD still works via a different mechanism.** The 1281 improvements confirm that coordinate descent (non-integral-preserving) finds improvements through adjusting the integral:mass ratio, not through purely reducing the autoconvolution peak.

3. **28 plateau positions within 1e-10.** The plateau is incredibly flat. With K=28 gradient vectors in 2D (for triplets) or 3D (for quadruplets), covering the origin is almost geometrically inevitable.

4. **CD throughput only 14 positions/s** even with window-based approach. The window rebuild (tight_idx recomputation after each improvement) is expensive. Most of the time is in window management, not in the window evaluation itself.

---

## 8. Helper tools feedback

### helpers/incremental_autoconv_update.py
- Correct and essential for exact acceptance decisions.
- The window-based approximation (using ±400 around tight indices) matches well.

### helpers/cross_convolution_f64.py / autoconvolve()
- Used for initialization. Works correctly.

### helpers/compute_c_f64.py
- Used for final verification. Correct.

### Missing helper: Fast vectorized CD
A `fast_coordinate_descent(f, autoconv, f_padded, dx, M_fft, deltas, max_time)` helper that:
- Pre-filters positions by gradient magnitude
- Uses a persistent window (not rebuilt per improvement)
- Processes positions in gradient-sorted order
- Would have found 5-10x more improvements in the same time budget

### Missing helper: minimax LP feasibility check
A function `minimax_feasibility(autoconv, f_padded, dx, M_fft, plateau_eps)` that checks:
- Whether any k-plet can reduce all plateau positions simultaneously
- Returns the minimum LP objective over random samples
- Would have quickly confirmed the null result without running 47k full LP solves

---

## 9. Time budget

Time was fully used (496s). Key bottleneck:
- LP overhead: ~4.5ms per triplet trial (HiGHS setup + solve for 28-constraint, 3-variable LP)
- CD throughput: ~14 positions/s due to expensive window refresh

**With more time, would do:**
1. 5+ more rounds of CD with full N=30000 coverage (would require faster implementation)
2. Try non-integral-preserving perturbations (Experiment C above)
3. Extend CD deltas to 1e-14 to test float64 floor

**Verdict on idea_023:** TESTED AND FOUND NULL. Should be moved to debunked or reformulated as "Non-integral-preserving CD is the remaining improvement pathway."
