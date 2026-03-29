# Coverage Matrix — Generation 11

**Sparse format: only tested combinations shown. Cap: top 20 ideas by usage.**
**Lower score is better (minimize C).**

| Idea Combination | Times Tried | Best Score | Avg Score | Last Tried |
|---|---|---|---|---|
| idea_014 + idea_024 + idea_019 (non-IP pairs + ultra-fine CD) | 1 | **1.502862867793** | 1.502862867793 | **gen_11** |
| idea_014 + idea_019 (focused deltas 1e-14..1e-11, multi-trajectory) | 1 | 1.502862868176 | 1.502862868176 | **gen_11** |
| idea_014 + idea_019 (per-round FFT resync CD, single-pass) | 1 | N/A (no .score) | N/A | **gen_11** |
| idea_014 + idea_019 (ultra-fine CD with fast_check pre-filter) | 1 | 1.502862868117 | 1.502862868117 | gen_10 |
| idea_014 + idea_019 (ultra-fine CD with top-K screening, 71 rounds) | 1 | 1.502862868184 | 1.502862868184 | gen_10 |
| idea_014 + idea_019 (ultra-fine CD, window-based after minimax null) | 1 | 1.502862868166 | 1.502862868166 | gen_10 |
| idea_014 + idea_019 (ultra-fine CD, A/B test Path A) | 1 | 1.502862868223 | 1.502862868223 | gen_10 |
| idea_014 + idea_023 (minimax LP triplet/quad, DEBUNKED) | 1 | N/A (0 improvements) | N/A | gen_10 |
| idea_014 + idea_019 (ultra-fine CD on TTT-Discover 30k) | 2 | 1.502862868222 | 1.502862868222 | gen_9 |
| idea_014 + idea_021 (triplet perturbation on TTT-Discover 30k) | 3 | 1.502862868 | 1.502862876 | gen_9 |
| idea_014 + idea_022 (quadruplet perturbation on TTT-Discover 30k) | 2 | 1.502862868 | 1.502862868 | gen_9 |
| idea_014 + idea_019 (float64 coord descent, standard deltas) | 6 | 1.502862869 | 1.502862872 | gen_8 |
| idea_014 + idea_018 (TTT-Discover verbatim) | 1 | 1.5029 | 1.5029 | gen_4 |
| idea_014 + idea_017 (projected gradient on TTT-Discover 30k) | 1 | 1.5029 | 1.5029 | gen_5 |
| idea_014 + idea_020 (LP refinement on TTT-Discover 30k) | 4 | 1.5029 | 1.5029 | gen_7 |
| idea_014 + idea_020 (LP at N=5000 near-optimal) | 2 | N/A (diagnostic) | N/A | gen_9 |
| idea_001 + idea_019 (GD + CD at N=5000 from scratch) | 2 | 1.5168 | 1.5169 | gen_9 |
| idea_014 (AlphaEvolve verbatim, various resolutions) | 6 | 1.5032 | 1.5039 | gen_5 |
| idea_001 + idea_007 + idea_008 + idea_004 (warm fine) + idea_013 | 3 | 1.5090 | 1.5095 | gen_3 |
| idea_001 + idea_007 + idea_008 + idea_004 (warm fine) | 2 | 1.5091 | 1.5092 | gen_2 |
| idea_001 + idea_007 + idea_008 + idea_010 (L-BFGS polish) | 2 | 1.5107 | 1.5108 | gen_2 |
| idea_001 + idea_007 + idea_008 | 2 | 1.5108 | 1.5130 | gen_1 |

## Unexplored High-Priority Combinations for Gen 12

1. **Extended non-IP pair search + multi-round CD** — explore_1 only got 15k pair trials and 1 CD round. 50k-100k pair trials + 3+ CD rounds would compound. Improvement rate was STILL INCREASING at 15k trials.
2. **Non-IP triplets** — If 2-element non-IP moves work, 3-element non-IP moves may find deeper improvements.
3. **Non-IP pairs starting from gen011/explore_1 array** — The gen 11 best hasn't been further optimized yet. It should respond to more non-IP + CD rounds.
4. **Focused delta CD (1e-14..1e-11) with sub-round resync** — Combine pattern_026 (focused deltas) with pattern_027 (500-mod resync). Never tested together.
5. **Multi-trajectory competition with sub-round resyncs** — exploit_2's test was contaminated by drift. Re-test with proper sub-round resyncs to get meaningful trajectory comparison.

## Confirmed Dead Ends

- SA at N=600 fine-grid: returns to same basin every time
- L-BFGS after smooth-max convergence: zero effect (DEBUNKED, idea_010)
- Extended temp schedule beyond T=0.0003: negligible benefit
- DCT perturbation: all perturbation scales return to 1.509 basin (DEBUNKED, idea_015)
- Cold fine stage in coarse-to-fine: 1.5188
- SA at coarse scale (N=23-80): 1.5148-1.5227 regardless of calibration (pattern_009)
- Smooth-max Adam warm-start of published solutions: cannot improve them (pattern_007, CONFIRMED)
- Cubic spline upsample: destroys structure
- Projected gradient on 30k array: gradient too sparse/uniform
- Gaussian mixture parameterization: can't represent sparsity
- LP at all resolutions: plateau defeats LP (5 gens, 3 resolutions)
- Quintuplet perturbation: noise floor (pattern_018)
- **Integral-preserving triplet/quadruplet after ultra-fine CD: 0 improvements in ~400k+ trials (pattern_020, CONFIRMED)**
- **Minimax LP (idea_023): 68k trials, 0 improvements (DEBUNKED gen 10)**
- **Multi-trajectory competition WITHOUT sub-round resync: drift dominates, results meaningless (pattern_027, gen 11)**
