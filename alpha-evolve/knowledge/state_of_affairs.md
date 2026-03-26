---
generation: 3
best_score: 1.5032
trajectory: strategic_shift
last_updated_gen: 3
---

# State of Affairs — Generation 3

## Current Standing

Best score: **C = 1.5032** (gen003_research_1_sol01), retrieved verbatim from the AlphaEvolve published repository (Georgiev et al., Dec 2025). This beats the original target of C <= 1.5053 by 0.0021. Best gradient-descent result: **C = 1.5090** (gen003_explore_2_sol01). Three generations completed, 38 valid solutions total. Trajectory: **strategic shift** — the pipeline must pivot from random-init gradient descent to warm-start optimization of published solutions.

Current SOTA: Yuksekgonul et al. (Jan 2026) report C <= 1.5029 but no public array yet.

## What Works

1. **Smooth-max temperature annealing** (idea_007, confidence 0.95, established): Most impactful technique across all 3 generations. Log-sum-exp T=0.05->0.0003 over 5 phases of 15k steps. No solution breaks below 1.5155 without it. Temperature schedule finalized — extensions below T=0.0003 give negligible benefit (0.000025).

2. **Coarse-to-fine with warm fine stage** (idea_004, confidence 0.75, established): N=80 coarse, upsample to N=600, re-anneal from T=0.05. 3-stage (N=80->200->600) does NOT improve over 2-stage. Best gradient result: 1.5090.

3. **Multi-seed restart** (idea_008, confidence 0.8, established): 8 diverse seeds is the sweet spot. Diversity of init shape matters more than count. 25-seed funnels show arcsine inits dominate top slots.

4. **Asymmetry** (idea_012, confidence 0.9, established): C >= 2 for symmetric functions (proven). All competitive solutions are asymmetric.

5. **Warm-start from published solutions** (idea_014, confidence 0.8, active): AlphaEvolve 1319-element array verified at C=1.5032. Multiple intermediate arrays available (C=1.5053 to C=1.5032).

## Current Frontier

The gradient-descent pipeline has plateaued at C~1.509. The 1.509 basin is extremely deep — DCT perturbations up to 18% magnitude, coarse-scale SA at N=30-80, and ultra-low temperature polish all fail to escape it (pattern_005, confirmed). The only path forward is warm-starting from published solutions.

**Priority 1:** Warm-start smooth-max Adam from the 1.5032 array. Convert to raw_params via inv_softplus, run T=0.005->0.0001 schedule. The function has qualitatively different structure (sparse, multi-peaked) from gradient-descent solutions — our optimizer may find improvements the LP-guided algorithm missed.

**Priority 2:** Retrieve additional published arrays — Cell 46 (C=1.5053, N=600, same resolution as our pipeline), Cell 91 (~50000 elements, possibly ThetaEvolve 1.503133), Yuksekgonul 2026 (C<=1.5029).

## Coverage Map

**Exhausted (gradient descent from random init):**
- Adam + smooth-max + multi-seed at N=600: 1.5107-1.5108 (5+ trials). Basin floor.
- Coarse-to-fine (N=80) + warm smooth-max: 1.5090-1.5093 (5+ trials across init families). All converge to same ~1.509 attractor.
- Coarse-scale SA (N=30-80): 1.5148-1.5169 (3 trials). All worse than simple coarse-to-fine. Calibration was poor (96-100% acceptance) but technique is questionable.
- DCT perturbation: 10 configs, all return to 1.509 basin.
- Extended temp (T<=0.00003): negligible (0.000025).

**Untested high-priority:**
1. Warm-start from 1.5032 array + smooth-max polish.
2. Warm-start from intermediate arrays (C=1.5053 at N=600).
3. Properly calibrated coarse-SA (20-40% acceptance, cold inner optimizer).

## Dead Ends

- **L-BFGS after smooth-max** (idea_010, debunked): zero effect in 3 gens of tests.
- **SA at N=600 fine grid:** returns to same basin every time.
- **Cold fine stage in coarse-to-fine:** 1.5188, negates coarse benefit.
- **Step function init:** 1.519-1.522 range.
- **DCT perturbation for basin escape:** all scales return to 1.509 basin.
- **Extended temp below T=0.0003:** 0.000025 improvement.
- **More restarts beyond 8:** diminishing returns (<0.0001).
- **Symmetric initializations:** C >= 2 mathematical barrier.

## Open Questions

1. **Can warm-start polish push 1.5032 below 1.503?** Highest priority experiment. The AlphaEvolve solution's sparse multi-peaked structure may respond differently to smooth-max Adam than our Gaussian-bump solutions.
2. **Is the Cell 91 array ThetaEvolve's 1.503133?** Unverified ~50000-element sparse array.
3. **Is Yuksekgonul 2026 (C<=1.5029) publicly available?** No array found yet.
4. **Can coarse-SA work with proper calibration?** All 3 gen-3 SA attempts had 96-100% acceptance (metro_T too high). A properly calibrated run (20-40% acceptance, cold inner optimizer) has never been tested.
5. **Is arcsine init's 1.5090 vs Gaussian's 1.5091 real or noise?** 50-seed reproducibility test needed.
6. **Correction applied:** "Boyer et al. coarse-SA-at-N=23" was incorrectly attributed to AlphaEvolve for 2 generations. AlphaEvolve used LP-guided memetic algorithm at full resolution.
