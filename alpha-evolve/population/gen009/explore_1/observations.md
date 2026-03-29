# Observations — gen009_explore_1

## Summary

Implemented quintuplet perturbation (d1+d2+d3+d4+d5=0) on the gen008_explore_1 best
solution (C = 1.5028628684790137).

**Final C = 1.5028628683413456** (delta = -1.38e-10)

---

## What was tried

### 1. Quintuplet perturbation (50k trials)

Gradient-guided 5-element integral-preserving moves:
- Gradient: g[m] = 2*dx*f_padded[(n* - idx_m) % M] for each selected index
- Project onto sum-zero hyperplane: g_proj = g - mean(g) (4 free variables)
- Step sizes: 9 log-spaced from 1e-1 to 1e-6 (largest valid chosen)
- 3 strategies (S0: 5 random nonzero, S1: 2 large+2 small+1 rand, S3: 3 nonzero+2 rand)

**Result: 2 improvements, delta_C = -4.4e-16 (1 ULP of float64)**

This is essentially zero in float64 precision. Quintuplets are at the numerical noise floor.

### 2. Quadruplet follow-up (20k trials)

After quintuplets, ran quadruplets to test the unlocking hypothesis.

**Result: 0 improvements**

The tiny quintuplet changes did not unlock new quadruplet directions.

### 3. Triplet follow-up (20k trials)

**Result: 150 improvements, delta_C = -1.38e-10**

Triplets found significant improvements AFTER both quintuplets and quadruplets found
none. This is not the "unlocking" effect — it's more likely that the triplet landscape
has residual structure that is slowly explored by random trial-and-error.

---

## Key Findings

### Finding 1: Quintuplets are at the float64 noise floor

The 2 improvements found by quintuplets each moved C by ~2.2e-16 (1 ULP). This is
not genuine optimization — it's floating point rounding. Quintuplets do NOT provide
meaningful improvement beyond quadruplets on this solution.

**Pattern: Perturbation hierarchy diminishing returns**
- Pairs: 1 improvement (gen 6)
- Triplets: 160 improvements (gen 7), 2523 follow-up (gen 8), 150 follow-up (gen 9)
- Quadruplets: 8015 improvements (gen 8), 0 follow-up (gen 9)
- Quintuples: 2 improvements at noise floor (gen 9)

The pattern is clear: each k-plet exhausts its improvement potential, and higher
k-plets reach the noise floor faster. We are very close to a true local minimum
under k-plet perturbations.

### Finding 2: Triplets still have residual improvement potential

Despite having run 20k triplet trials in gen008 (finding 2523 improvements), another
20k triplet trials in gen009 found 150 more improvements. Triplets are not yet fully
exhausted. A much longer triplet run (200k+ trials) might squeeze more signal.

### Finding 3: Strategy analysis

For quintuplets:
- S0 (random nonzero): 0 improvements
- S1 (mass-redistribution): 1 improvement
- S3 (mixed): 1 improvement

For triplets (150 improvements total):
- S0: 67 improvements (45%)
- S1: 36 improvements (24%)
- S3: 47 improvements (31%)

S0 (random nonzero) dominates for triplets. Matches the finding from gen8 that pure
random selection performs well.

### Finding 4: Rate at noise floor is actually fast

At this precision level, the algorithm is very fast:
- Quintuplets: 165 t/s
- Quadruplets: 289 t/s
- Triplets: 424 t/s

Triplets run at nearly 3x the speed of quintuplets. Running 500k triplet trials would
take ~20 min and might find more improvements.

---

## What failed / dead ends

**Quintuplets as a meaningful optimization strategy**: The hypothesis that quintuples
would find improvements by accessing higher-dimensional structure is NOT confirmed.
The 2 improvements are at the float64 noise floor. The hierarchy stops being useful
at k=4 (quadruplets). Further increasing k is not recommended.

---

## Hypotheses for further investigation

1. **Extended triplet search**: Run 500k+ triplet trials. At 424 t/s = 20 min. Given
   that 20k trials found 150 improvements and the rate didn't plateau, there may be
   hundreds more.

2. **Vectorized batch k-plet**: Generate 100+ candidate sets simultaneously using
   numpy broadcasting. Could increase throughput to 1000+ t/s.

3. **Different perturbation structure**: Instead of random index selection, try
   gradient-guided index selection — find the k indices where the gradient is most
   heterogeneous (largest variance in g), maximizing the projected gradient norm.

4. **Coordinate descent follow-up**: After k-plet optimization, run LP or coordinate
   descent to clean up residual structure.
