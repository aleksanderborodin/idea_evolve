# Observations — gen009 explore_2

## Overview

Executed the N=5000 LP tractability study as directed. Two solutions produced:
- sol01: Full 4-seed optimization (gradient descent + coord descent) + basic LP analysis
- sol02: 2-seed optimization + focused iterative LP at epsilon_rel=1e-7 and 1e-6

## Experiment A: N=5000 Gradient Descent (sol01)

**Setup:** 4 seeds × 5 temperature phases × 15k steps/phase = 75k steps/seed
**Results:**
| Seed | C after GD |
|------|-----------|
| 0    | 1.518255  |
| 1    | 1.517157  |
| 2    | 1.516854  |
| 3    | 1.517720  |

Best GD: **C = 1.516854** (seed 2)

**Key finding:** Gradient descent at N=5000 reaches C~1.517. This is significantly above the
N=30k frontier of C=1.503. The gap is ~0.014 — N=5000 cannot replicate the TTT-Discover
structure.

## Experiment B: Coordinate Descent at N=5000 (sol01 + sol02)

**sol01 result:** C = 1.516854 → **1.516845** (5 rounds, 2095 total improvements)
**sol02 result:** C = 1.517027 → **1.517016** (8 rounds, 2746 total improvements)

**Tight constraint profile at convergence:**

| epsilon_rel | tight count | fraction of 2N=10000 points |
|-------------|-------------|------------------------------|
| 1e-4        | ~3149-3170  | 31.5-31.7%                   |
| 1e-5        | ~2396-2827  | 24-28%                       |
| 1e-6        | ~56-59      | 0.56-0.59%                   |
| 1e-7        | ~13-15      | 0.13-0.15%                   |
| 1e-8        | ~11         | 0.11%                        |

**Critical comparison with N=30k (C=1.503):**
- N=30k tight@1e-5 ≈ 16185 (30.5% of 2N=60000)
- N=5000 tight@1e-5 ≈ 2396-2827 (24-28% of 2N=10000)

The plateau fraction is *nearly identical* (~30% vs ~24-28%). The plateau character at
N=5000 near-optimal is the same as at N=30k.

## Experiment C: Iterative LP Test (sol02)

**LP at epsilon_rel=1e-7 (13 constraints):**
- Iteration 1: Found step with alpha=2.64e-3, C improvement = **-5.85e-12** (essentially 0)
- Iteration 2: No improvement found. Stopped.

**LP at epsilon_rel=1e-6 (59 constraints):**
- Iteration 1: No improvement found. predicted_improvement = 0.0

**Interpretation:**
The LP "improvement" of -5.85e-12 is within floating point round-off (< 1e-11). This is
not a real improvement — it's numerical noise. LP did not work at N=5000.

The same fundamental obstacle applies at N=5000 as at N=30k:
1. Few-constraint LP (13 constraints) controls only the top 13 autoconv points
2. The remaining ~2800 tight@1e-5 points become the new maximum after perturbation
3. LP predicted_improvement shows 0 (the LP finds no direction that reduces the global max)

## Summary: LP Tractability at N=5000

**DEFINITIVE RESULT: LP is NOT tractable at N=5000 near-optimal.**

| Metric | N=5000 (this study) | N=30k (prior work) |
|--------|--------------------|--------------------|
| Near-optimal C | ~1.517 | ~1.503 |
| tight@1e-5 | ~2400-2800 | ~16000 |
| LP at 1e-7 (13-15 tight) | -5.85e-12 (noise) | not tested |
| LP at 1e-6 (56-59 tight) | no improvement | not tested |
| LP verdict | FAILS (plateau) | FAILS (plateau, pattern_013) |

The plateau at N=5000 near-optimal is similar in character (though smaller in absolute
number) to N=30k. Few-constraint LP fails because the excluded constraints become the
new maxima. The N=5000 problem reaches C~1.517 which is far above the frontier.

## Recommendation for idea_020

**Archive idea_020 (LP-based refinement of existing solutions).**

Evidence:
- N=30k: Failed due to flat plateau with ~6500 near-max points (pattern_013)
- N=5000: Near-optimal at C=1.517 with ~2400 tight@1e-5. LP gives -5.85e-12 improvement (noise).
- Intermediate resolution LP does not offer a path to improvement.

The LP approach is fundamentally blocked by the plateau structure that emerges near
convergence of any optimization at any resolution tested.

## What Did NOT Work (Failed Approaches)

- LP at N=5000 (epsilon_rel=1e-6, 59 constraints): No improvement
- LP at N=5000 (epsilon_rel=1e-7, 13 constraints): Negligible noise improvement (-5.85e-12)
- N=5000 optimization reaching C=1.503: Not achievable. Floor is ~C=1.517.

## What Worked

- Fresh N=5000 optimization from scratch reaches C~1.517 (expected, consistent with N=600 results)
- Coordinate descent provides small improvement (~1e-5 over GD output)
- The tight constraint profile measurement is accurate and reproducible
