# State of Affairs — Generation 11

**Best score:** C = 1.5028628677925082 (gen011_explore_1_sol01)
**Generations completed:** 11
**Target:** C ≤ 1.5053 — beaten since gen 3.
**Trajectory:** Accelerating after plateau. Gen 11 improvement: 3.24e-9 (largest since gen 6). Prior 3 gens averaged ~3e-10. The non-IP pair technique reversed the decelerating trend.

## What Works

- **Warm-start from TTT-Discover 30k array** (idea_014, confidence 0.95). Foundation of ALL frontier scores since gen 4. Every competitive solution derives from this array.

- **Ultra-fine float64 coordinate descent** (idea_019, confidence 0.95). Primary optimization technique. Engineering requirements: focused delta grid np.geomspace(1e-14, 1e-11, 40) for 1.83x speedup over broad grid (pattern_026). Top-K screening K=30 for 50x speedup (pattern_022). FFT resync every 500 modifications — NOT per-round (pattern_027 supersedes pattern_021).

- **Non-integral-preserving 2-element moves before CD** (idea_024, confidence 0.85). NEW gen 11. Two-phase protocol: non-IP pair search → ultra-fine CD. Pair moves amplify subsequent CD gains by ~15x (pattern_025). Produced the new overall best. Mechanism: pair moves change the integral, unlocking new CD descent paths that integral-preserving moves cannot access (pattern_024). Single observation — needs gen 12 confirmation.

## Current Frontier

**Protocol:** Non-IP pairs → ultra-fine CD (two-phase). This replaces the CD-only protocol from gens 5-10.

**Gen 11 results:** explore_1 ran 15k pair trials (2300 improvements, rate still increasing) then 1 round focused CD (10995 improvements). exploit_2 confirmed focused deltas 1.83x better than broad. exploit_1 confirmed entrypoint non-reproducibility but produced no scored solution (single-pass CD too slow).

**Critical for gen 12:** The gen011 best array MUST be baked as a numpy literal (pattern_028). Deadline-based entrypoints have ~6e-11 variance, exceeding a full generation's improvement.

## Coverage Map

**Well-explored:** CD on TTT-Discover 30k at all delta scales (gens 5-11, 15+ sessions). Integral-preserving multi-element moves after ultra-fine CD: 0 improvements in ~400k trials (pattern_020, confirmed). LP at all resolutions near optimality (5 gens, resolution-independent plateau of 25-32%, debunked). GD from random init (caps at ~1.509).

**Under-explored:** Extended non-IP pair search (only 15k trials in gen 11, improvement rate still increasing). Non-IP triplets (0 gens). Multi-cycle pair→CD alternation (0 gens). Focused delta CD + sub-round resync combined (0 gens).

**Confirmed dead:** All integral-preserving multi-element perturbations after ultra-fine CD. LP refinement at all resolutions. Smooth-max Adam on published solutions. SA at all scales. Gradient methods on well-optimized solutions. Downsampling TTT-Discover. Quintuplet perturbation (noise floor).

## Dead Ends

- **Integral-preserving multi-element moves** (pattern_020, confirmed 0.95): ~400k trials, 0 improvements. Solution is locally minimax-optimal for these moves.
- **LP refinement** (idea_020, debunked 0.05): 25-32% of autoconvolution points near-maximal at ANY resolution near optimality. Mathematically blocked.
- **Smooth-max Adam on published solutions** (pattern_007, confirmed 0.95): Worsens ALL published solutions, confirmed float64.
- **Multi-trajectory competition without sub-round resync** (pattern_027): Drift dominates; results meaningless.

## Open Questions

1. **Does the non-IP amplification effect compound?** Gen 11 showed 15x amplification in one pair→CD cycle. Would pair→CD→pair→CD→... compound over multiple cycles? This determines whether the technique sustains multi-generation improvements or is a one-shot gain. Highest priority for gen 12.

2. **Non-IP triplets.** If 2-element non-IP moves find improvements invisible to CD, 3-element non-IP moves may find improvements invisible to both. Untested.

3. **topk_screened_cd helper untested at N=30000.** The experimentator-built helper passed 14/14 tests at N=1000 only. Agents should verify at production scale before relying on it.

4. **Prior-gen drift contamination.** Gen 10 critic noted drift was 3.5x real improvement. Final validated scores are accurate (validate.py uses full FFT), but intermediate improvement counts in agent reports from gens 7-10 may be overstated. Does not affect trajectory.

5. **Diminishing practical value.** Target beaten since gen 3. Gen 11 improvement is 3.24e-9. User decision on whether to continue, pivot, or conclude.
