# Debrief Report — explore_1, Generation 7

## Solutions

| File | Fitness (C) | Valid | Method |
|------|-------------|-------|--------|
| sol01.py | **1.5028628688924555** | Yes | TTT-Discover 30k + gradient-guided triplet perturbation |

**Baseline:** gen006_exploit_1 = C = 1.5028628724712894  
**Improvement:** -3.578e-9  
**Method:** 60k triplet trials with incremental autoconv updates (~220 trials/sec)

---

## 1. What did you try?

### Gradient-guided triplet perturbation (MAIN, 60k trials)
For each triplet (i, j, k), computed first-order gradient of the autoconv peak with
respect to (d1, d2) under the constraint d1+d2+d3=0 (integral-preserving). Moved
in the gradient descent direction with 9 step sizes: [1e-7, 5e-7, ..., 1e-3].

Selection strategies rotated (every 4 trials):
- Strategy 0: 3 random elements from nonzero (25140 elements)
- Strategy 1: 1 large + 1 small + 1 random (mass redistribution)  
- Strategy 2: 3 consecutive neighbors starting from a nonzero element
- Strategy 3: 3 fully random elements from [0..N)

Used O(N) incremental autoconv update (no FFT per trial):
  autoconv[n] += dx * 2 * delta * f_padded[(n-idx)%M]  for all n
  autoconv[2*idx%M] += dx * delta^2
This is exact (matches compute_c_f64 to 1e-10) and ~28x faster than FFT.

**Result: 160 improvements, C: 1.502862872471 → 1.502862868892 (delta: -3.578e-9)**

### Second pass (20k additional trials)
Different seeds, same strategies. **0 improvements.** Diminishing returns after 60k.

---

## 2. What information did you lack?

- **Which triplet families are most productive.** Of 4 strategies, I logged only totals.
  Breaking down improvements by strategy type would identify which structural approach
  (mass redistribution, neighbor, random) contributes most.
  
- **The autoconv structure near n*=32194.** Knowing which neighborhoods of the autoconv
  have near-equal values to n* would tell us where perturbations are most likely to succeed.

- **History of which elements were changed most by coordinate descent.** If I knew which
  elements changed most in gen5-6, I could bias triplet selection to those coordinates.

---

## 3. What given facts might be wrong or outdated?

- **State of Affairs open question: "Can extended coordinate descent push below 1.50286?"**
  Gen 6 showed 1800 improvements in round 3. This should still be true — triplet perturbation
  only found -3.578e-9 while continued coordinate descent likely has more to give.
  
- **The brief says "pairs found only 1 improvement in 300 trials (gen 6 exploit_1)."** But 
  the gen 6 report actually says pairs were tested only for "top-50 elements, 6 delta scales".
  Pairs on the full 25k nonzero elements with gradient-guided selection might find more.

---

## 4. Was the State of Affairs accurate?

Yes, the State of Affairs accurately described the frontier. The coverage map correctly
listed "Triplet perturbation (pairs near-useless; triplets untested)" as a high-priority
untested approach, and triplets did find improvements.

---

## 5. What would I do differently?

1. **Start with more systematic strategy analysis:** Log improvements per strategy to
   identify which triplet selection approach is most fruitful.
   
2. **Larger initial steps for dramatic triplets:** Try step sizes up to 0.01 for structure-
   changing moves (mass from large to small), not just fine-tuning at 1e-7.
   
3. **Interleave with coordinate descent:** After finding 160 triplet improvements, run
   1-2 rounds of single-element coordinate descent. Then triplets again. The improvements
   may enable more single-element improvements.

4. **Momentum approach:** When a triplet at (i, j, k, d1, d2) improves C, try the SAME
   triplet again with larger step sizes, and also try nearby triplets.

---

## 6. Specific experiments to run

### Experiment A: Extended coordinate descent + triplet interleaving
- Continue sol01.py with 3-5 more rounds of full-array coordinate descent
- Then 30k additional triplet trials
- Repeat until both converge simultaneously
- Expected: combined improvements > either method alone

### Experiment B: Momentum-enhanced triplet search
- After each accepted triplet move, immediately retry same triplet with 2x step
- Also retry with same j and k but different i (neighborhood search around accepted move)
- Could find long chains of improvements in the same direction

### Experiment C: LP refinement at N=2000 with upsampling
- Downsample sol01.py from N=30000 to N=2000 using structure-preserving interpolation
- Run LP refinement on N=2000 (avoids RAM issue from gen 6)
- Upsample back and use as starting point
- This is the highest-upside unexplored direction

### Experiment D: Strategy A/B/C/D breakdown
- Run 10k triplets per strategy separately and log improvement density
- This will identify which structural approach dominates

---

## 7. What surprised me?

1. **Triplets find improvements while pairs find almost none.** The mathematical reason:
   under single-element coord descent optimality, pairs have zero first-order gradient
   (from the stationarity condition f[(n*-i)%M] = C*integral for all active i). But
   triplets have a different constraint and can have nonzero gradients at the pair-optimal
   point. The improvement density is lower than pairs-from-nonoptimal (obvious) but
   significant enough to matter.

2. **The improvement rate drops but doesn't stop.** Rate: 100 in first 20k trials, 
   60 in second 20k, ~10-20 in final 20k. Gradual convergence, not sudden cutoff.

3. **Zero-gradient fraction grows from ~3% to ~10% over the run.** As improvements 
   are applied, the solution becomes more uniform near n*, making more triplets have
   degenerate gradients. This is consistent with theory.

4. **Second pass (different seed) found zero improvements.** After 60k trials, the
   triplet-reachable space was largely exhausted. 160 improvements over 60k trials is
   a ~0.27% success rate.

---

## 8. Helper tools feedback

### helpers/compute_c_f64.py
- Used for initial verification and final verification. Correct.
- The direct incremental approach (manual O(N) update) was faster than calling this helper.

### The incremental autoconv update trick
- The O(N) incremental update from gen6 report (formula provided there) was correctly
  applied here. This is the key enabling technology — without it, 60k triplet trials
  at 20ms each = 1200 seconds (impossible within budget).
  
### Missing helpers
- **helpers/incremental_autoconv.py** — would be extremely valuable. Should expose:
  - `apply_element_update(f_padded, autoconv, idx, delta, dx)` 
  - `revert_element_update(f_padded, autoconv, idx, delta, dx)`
  - With clear docstring explaining the O(N) math.
  Currently every agent reimplements this from scratch.
  
- **helpers/coord_descent_round.py** — a full round of single-element coordinate descent
  using the incremental update, returning (improved_f, n_improvements, new_c). Would
  avoid agents rewriting the same optimization loop.
