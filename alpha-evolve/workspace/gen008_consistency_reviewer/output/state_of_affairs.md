---
generation: 8
best_score: 1.5028628684790137
trajectory: incremental_improvement
last_updated_gen: 8
---

# State of Affairs — Generation 8

## Current Standing

Best score: **C = 1.5028628684790137** (gen008_explore_1_sol01), achieved by quadruplet perturbation + triplet follow-up on the coordinate-descent-optimized TTT-Discover 30,000-element array. Eight generations completed, ~70 valid solutions. Trajectory: **incremental improvement** — each perturbation order finds O(1e-10) beyond the previous. Total agent-driven improvement over TTT-Discover baseline: ~-3.0e-8 across gens 5-8.

Current SOTA source: TTT-Discover (Yuksekgonul et al., Jan 2026), C ≈ 1.50286 with 30k-element array. All scores below C=1.503 derive from this array.

## What Works

1. **Multi-order interleaved perturbation** (pattern_014, confidence 0.75): Coord descent → triplets → quadruplets, cycling. Each order unlocks improvement directions for the orders below it. Confirmed by two independent agents in gen 8. This is the ONLY active optimization protocol.

2. **Quadruplet perturbation** (idea_022, active, confidence 0.6): 8015 improvements in gen 8 across 4 strategies (S0/S1/S3 roughly equal, S2 weakest at 14%). Total delta ~4e-10.

3. **Float64 coordinate descent** (idea_019, established, confidence 0.9): Foundation technique. Converges alone in 3-6 rounds but regains improvements after higher-order perturbations. Gen 8 exploit_1 found 2008 new improvements after gen 7's triplet modifications.

4. **Triplet perturbation** (idea_021, established, confidence 0.8): Exhausts after ~60-80k trials alone, but quadruplet moves unlock 2523 new triplet improvements. Part of the interleaving cycle.

5. **Warm-start from published solutions** (idea_014, established, confidence 0.9): All scores below C=1.505 start from TTT-Discover or AlphaEvolve arrays.

## Current Frontier

**Full interleaved multi-order cycle** is the top priority. The complete protocol (coord → triplet → quadruplet → repeat until all converge simultaneously) has never been run end-to-end — exploit_1 gen 8 only completed one coord descent round before timeout. Performance bottleneck: Python-loop trial evaluation at 100-220 trials/s.

**WARNING — exhaustion signals:** When any method finds 0 improvements in a second full pass on the same array, it is exhausted at that perturbation order. Do NOT retry without interleaving from a higher order first. Momentum-enhanced triplets (Strategy 1) on the unmodified gen 7 best: 0/36k trials (gen 8 exploit_2).

**Highest-priority untested experiments:**
1. Full interleaved cycle to convergence (all three orders)
2. Quintuplet perturbation (d1+...+d5=0, 4D gradient projection)
3. Vectorized batch trial evaluator (10-50x throughput, enables #1)
4. Near-optimal N=5000 from scratch (to answer LP tractability question)

## Coverage Map (from coverage matrix)

**Active frontier (C < 1.50287):**
- Quadruplet + triplet on TTT-Discover 30k: 1 trial, best **1.502862868**, still improving
- Triplet perturbation on TTT-Discover 30k: 2 trials, best 1.502862869
- Coord descent on TTT-Discover 30k: 6 trials, best 1.502862869, converges alone but unlocked by higher-order moves

**Untested at frontier:**
- Full interleaved multi-order cycle (never completed end-to-end)
- Quintuplet perturbation
- Vectorized batch evaluation (engineering, not math)

**Blocked approaches:**
- LP refinement at N=30k: flat plateau with ~6500 near-max points (tight@1e-7) defeats few-constraint LP. Full-constraint LP requires 1.5GB matrix. (pattern_013)
- Downsampling N=30k to intermediate N: C=3-7, structure destroyed (pattern_015). LP at intermediate N requires fresh optimization from scratch.
- All gradient-based methods on published solutions: definitively closed (pattern_007, confirmed 0.95)

## Dead Ends

- **Single-element coord descent alone** (pattern_012): Converges. Useful only as part of interleaving cycle.
- **Smooth-max Adam on published solutions** (pattern_007, confirmed 0.95): All temperatures worsen C.
- **LP at N=30k** (pattern_013, idea_020 disputed 0.2): Flat plateau defeats LP. Engineering solved; math blocks it.
- **Downsampling TTT-Discover** (pattern_015): Interpolation destroys structure at all intermediate N.
- **Momentum triplets on unmodified arrays** (gen 8): 0/36k trials. Triplets exhaust without interleaving.
- **Gradient descent from random init**: Caps at C~1.509 (pattern_005). 20+ trials across gens 1-5.
- **SA at coarse scale** (pattern_009): Resolution-independent dead end.

## Open Questions

1. **How many interleaving cycles until full convergence?** The complete coord→triplet→quadruplet cycle has never run. Expected 2-4 cycles with O(1e-10) per cycle.
2. **Do quintuplet perturbations work where quadruplets exhaust?** Mathematical extension is sound, untested. Pattern_014 predicts they should.
3. **Is LP tractable at near-optimal N=5000?** Requires fresh optimization from scratch (30-60 min). Tight constraint density at N=5000 is ~300x lower than N=30k — potentially tractable if properly initialized. Cannot be answered by downsampling.
4. **Can the allocation overhead in incremental_update be eliminated?** Current 100-220 trials/s Python-loop bottleneck blocks the full interleaved cycle. Vectorized batch evaluation is the highest-impact engineering improvement.
5. **Is the coordinate_descent.py helper correct at N=30k?** Small-array tests pass; large-array validation incomplete. Must validate before production use in gen 9.
