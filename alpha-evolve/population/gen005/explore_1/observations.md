# Observations — explore_1, Generation 5

## Summary

Four solutions evaluated. None beat the 1.5090 gradient-descent floor. The main finding:
**properly calibrated SA at coarse scale definitively does not escape the 1.509 basin**, even
when all gen3/gen4 failure modes are corrected.

---

## Solution Table

| File | Approach | C | Notes |
|------|----------|---|-------|
| sol01.py | SA at N=23 (bug: inner opt before Metropolis) | 1.5227 | Metropolis saw post-opt proposals → ~100% acceptance |
| sol02.py | SA at N=23 (corrected: Metropolis on raw perturbed state) | 1.5227 | Calibrated to 20% acceptance, SA found no improvements |
| sol03.py | SA at N=80 (same corrected protocol) | 1.5162 | Fits historical 1.5148-1.5169 range exactly |
| sol04.py | Gaussian mixture (15 peaks, N=600) | 1.5418 | Different parameterization, not competitive |

---

## What Was Attempted

### sol01 — SA at N=23, inner optimizer before Metropolis check (BUG)

The brief said "cold inner optimizer after each SA perturbation acceptance". I misread this as
running the inner optimizer before the Metropolis acceptance check. Result: ~80-100% acceptance
rate during calibration because inner optimization IMPROVES almost every proposal. The SA loop
accepted everything early and then stopped (early stop: no improvement in 30 iters). C=1.5227.

### sol02 — SA at N=23, corrected (Metropolis on RAW perturbation)

Fixed the SA structure:
1. Perturb current_raw → proposed_raw (raw perturbation, no inner opt)
2. Compute C(softplus(proposed_raw)) — NO inner optimizer
3. Apply Metropolis on raw perturbed C
4. If accepted: THEN run inner optimizer

Calibration converged properly to 20% acceptance at metro_t=0.012595.
SA ran all 100 iterations for seed 1 but found no improvement over the coarse baseline (1.541).
Coarse-to-fine result after fine-tuning: C=1.5227 (same as sol01).

**Key finding**: With proper calibration AND correct SA structure, SA at N=23 still cannot
improve the coarse baseline. The landscape at N=23 is flat/shallow — SA moves don't escape.

### sol03 — SA at N=80 (same corrected protocol)

Switched from N=23 to N=80 (the resolution gen3 used for coarse-to-fine).
Same calibration and SA structure as sol02.
Coarse optimization at N=80 got 1.525718 (better than N=23's 1.541, as expected).
SA ran all 100 iterations, found no improvements over coarse baseline.
After upsample to N=600 + fine-tune: C=1.5162.

**Key finding**: Fits the historical range (1.5148-1.5169) exactly. Proper calibration doesn't
change the qualitative outcome. SA at N=80 is just as ineffective as poorly-calibrated SA.

### sol04 — Gaussian mixture parameterization

Represent f as sum of N_PEAKS=15 learnable Gaussian peaks.
Parameters per peak: position (via tanh), width (via softplus), amplitude (via softplus).
Optimize 45 parameters instead of 600 grid values.
Step time: 0.853ms (fast for N=600 evaluation).
4 seeds × 60k steps each, smooth-max temperatures [0.05, 0.01, 0.003, 0.001, 0.0003].
Best result: C=1.5418. All seeds converged to 1.541-1.590.

**Key finding**: Gaussian mixture parameterization is worse than grid parameterization.
The minimum amplitude constraint (from softplus) prevents near-zero elements.
The best published solutions (AlphaEvolve, ThetaEvolve) are SPARSE arrays — Gaussian peaks
with minimum amplitude can't represent sparse structure.

---

## Key Learnings

### 1. SA at coarse scale is definitively exhausted

Prior result: 1.5148-1.5169 with poorly calibrated SA.
Our result: 1.5162 with properly calibrated SA (20% acceptance, cold inner optimizer).
The range difference (0.5%) is noise-level. Proper calibration doesn't help escape the 1.509 basin.

The hypothesis in the brief was: "SA at coarse resolution smooths the landscape, potentially
revealing escape routes from the 1.509 basin." The experiment shows this hypothesis is FALSE.
The coarse landscape at N=80 still has the same attractor structure as N=600.

### 2. N=23 is too coarse for useful structure

N=23 gradient descent only reaches 1.541. After upsample to N=600 + fine-tune, best is 1.522.
The N=23 landscape is too distorted — it can't represent the function shapes needed for C<1.51.

### 3. SA structure matters for calibration but not for final result

sol01 (wrong structure) → 1.5227
sol02 (correct structure) → 1.5227
The calibration bug in sol01 caused incorrect acceptance rates but the final fine-tuned result
is identical. This suggests the fine-tuning at N=600 is the binding constraint, not the SA.

### 4. Gaussian mixture is not the right parameterization for sparse solutions

The best solutions are SPARSE (many near-zero elements, few dominant peaks). Gaussian mixture
parameterization with positivity constraints prevents sparsity. A better alternative might be:
- Sparse basis: use a discrete set of Dirac-like narrow peaks, some with zero amplitude
- Or: use L1-regularized grid optimization to force sparsity

### 5. The 1.509 basin is deep for ALL optimization methods tried at this resolution

Summary of all N=600 optimization results:
- Random init gradient descent: 1.5107-1.5108
- Coarse-to-fine (N=80→N=600): 1.5090-1.5093
- Coarse-to-fine with SA (N=80→N=600, this gen): 1.5162 (WORSE, not better)
The 1.509 basin is the global attractor for smooth-max Adam regardless of initialization.

---

## What to Try Next

### High priority:
1. **Projected gradient descent on published arrays** (Experiment 1 from gen4 suggestions).
   This is still untested. The TTT-Discover 30k array at C=1.50286 might respond differently
   to projected gradient descent (f-space, not softplus-space).

2. **Coordinate descent on TTT-Discover** (Experiment 2). Low cost, might find micro-improvements.

3. **ABANDON SA at all coarse scales**. This is now a confirmed dead end with proper evidence.

### Archive as dead end:
- SA at any coarse resolution (N=23, N=30-80): confirmed 1.5148-1.5169 range regardless of calibration
- Gaussian mixture parameterization: 1.54+ range

---

## Timing Summary

| Solution | Eval time |
|---------|-----------|
| sol01 | 88.8s |
| sol02 | 32.7s |
| sol03 | 91.4s |
| sol04 | 146.9s |
| Total | ~360s |
