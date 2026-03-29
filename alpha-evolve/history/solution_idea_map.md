# Solution-Idea Map

## Generation 1

### gen001_full_1_sol03 (score: 1.5108) — Gen 1 Best
- Central: idea_007 (smooth-max log-sum-exp annealing), idea_008 (multi-seed 8 restarts)
- Peripheral: idea_001 (Adam optimizer), idea_009 (softplus reparameterization), idea_003 (diverse Gaussian bump inits)
- Novel elements: Temperature schedule [0.05, 0.01, 0.003, 0.001, 0.0003] with 15k steps per phase

### gen001_full_1_sol04 (score: 1.5151)
- Central: idea_007 (smooth-max), idea_008 (multi-seed 12 restarts), idea_002 (N=800)
- Peripheral: idea_001 (Adam), idea_009 (softplus), idea_003 (diverse inits)
- Novel elements: Extended temp schedule to T=0.0001, 7 phases

### gen001_explore_1_sol05 (score: 1.5155)
- Central: idea_008 (multi-seed 8 seeds), idea_010 (L-BFGS fine-tuning)
- Peripheral: idea_001 (Adam), idea_012 (shifted-support asymmetric inits)
- Novel elements: Support blocks shifted +/-N/16 per seed

### gen001_explore_1_sol07 (score: 1.5157)
- Central: idea_008 (multi-seed 32 seeds, 16 modes), idea_010 (L-BFGS fine-tuning)
- Peripheral: idea_001 (Adam), idea_003 (diverse init shapes: blocks, ramps, Gaussians, Hann)
- Novel elements: 16 distinct initialization modes with 2 seeds each

### gen001_explore_2_sol09 (score: 1.5182)
- Central: idea_011 (Lion optimizer warmup), idea_008 (4-seed restart)
- Peripheral: idea_001 (Adam fine-tuning), idea_012 (symmetric box init, symmetry broken by noise)
- Novel elements: Lion 50k + Adam 70k two-phase optimizer

### gen001_explore_1_sol04 (score: 1.5182)
- Central: idea_001 (Adam 80k steps, longer training)
- Peripheral: none beyond baseline
- Novel elements: 2x baseline step count

### gen001_explore_1_sol06 (score: 1.5183)
- Central: idea_008 (16-seed restart), idea_002 (upsample to N=1500)
- Peripheral: idea_001 (Adam), idea_010 (L-BFGS)
- Novel elements: Top-3 selection from 16 seeds, upsample + refine

### gen001_full_1_sol01 (score: 1.5185)
- Central: idea_001 (Adam), idea_003 (Gaussian bump init), idea_002 (N=1000)
- Peripheral: idea_009 (softplus), idea_008 (3 restarts)
- Novel elements: None beyond combining known ideas

### gen001_explore_1_sol03 (score: 1.5189)
- Central: idea_001 (Adam 30k), idea_010 (L-BFGS fine-tuning)
- Peripheral: none beyond baseline init
- Novel elements: Adam warmup -> L-BFGS transition

### gen001_explore_1_sol01 (score: 1.5207)
- Central: idea_003 (Gaussian init sigma=0.08), idea_002 (N=800)
- Peripheral: idea_001 (Adam 100k)
- Novel elements: None

### gen001_explore_2_sol08 (score: 1.5207)
- Central: idea_011 (Lion + Adam), idea_002 (N=1000)
- Peripheral: idea_012 (symmetric box init)
- Novel elements: Lion 60k + Adam 50k

### gen001_explore_2_sol03 (score: 1.5249)
- Central: idea_008 (5 asymmetric seeds), idea_012 (asymmetric init)
- Peripheral: idea_001 (Adam with relu)
- Novel elements: Explicit asymmetric ramp initialization

### gen001_explore_1_sol02 (score: 1.5270)
- Central: idea_004 (multi-scale N=200->600->1200), idea_003 (Hann window init)
- Peripheral: idea_001 (Adam)
- Novel elements: Three-stage upsampling

### gen001_explore_2_sol06 (score: 1.5278)
- Central: idea_008 (3 asymmetric seeds), idea_009 (softplus)
- Peripheral: idea_001 (Adam)
- Novel elements: None

### gen001_explore_2_sol04 (score: 1.5294)
- Central: idea_006 (Fourier-basis parameterization)
- Peripheral: idea_001 (Adam 60k)
- Novel elements: Cosine+sine modes for function representation

### gen001_explore_2_sol02 (score: 1.5729)
- Central: idea_012 (asymmetric ramp init)
- Peripheral: idea_001 (Adam 50k)
- Novel elements: Simple right-ramp initialization

### gen001_explore_2_sol05 (score: 1.5730)
- Central: idea_004 (multi-scale N=100->600->1200)
- Peripheral: idea_001 (Adam)
- Novel elements: Three-stage coarse-to-fine

### gen001_explore_2_sol07 (score: 1.5801)
- Central: idea_003 (Gaussian mixture K=8)
- Peripheral: idea_001 (Adam 80k)
- Novel elements: Learnable positions/widths/heights for K=8 Gaussians

### gen001_full_1_sol02 (score: 1.6887)
- Central: idea_010 (L-BFGS-B only, no Adam warmup)
- Peripheral: idea_003 (5 diverse inits), idea_002 (N=800)
- Novel elements: Pure scipy L-BFGS-B optimization

### gen001_explore_2_sol01 (score: 3.0000)
- Central: idea_006 (analytical construction -- Hann window)
- Peripheral: none (no optimization)
- Novel elements: Pure analytical, no gradient descent

## Generation 2

### gen002_explore_1_sol03 (score: 1.5091) — Gen 2 Best
- Central: idea_004 (coarse-to-fine N=80->600, warm fine stage), idea_007 (smooth-max), idea_008 (12 restarts)
- Peripheral: idea_009 (softplus), idea_003 (3-bump diverse asymmetric init)
- Novel elements: 3-bump random init; warm fine stage (T=0.05 restart after upsample); 12 restarts at N=80

### gen002_explore_1_sol02 (score: 1.5093)
- Central: idea_004 (coarse-to-fine N=80->600, warm fine stage), idea_007 (smooth-max), idea_008 (8 restarts)
- Peripheral: idea_009 (softplus), idea_003 (2-bump asymmetric init)
- Novel elements: Key insight -- warm fine stage (T=0.05) after upsampling is essential

### gen002_exploit_1_sol01 (score: 1.5107)
- Central: idea_007 (smooth-max, 6-phase schedule to T=0.0001), idea_008 (16 restarts)
- Peripheral: idea_001 (Adam), idea_009 (softplus), idea_010 (L-BFGS, zero effect)
- Novel elements: 6th temperature phase T=0.0001 (no benefit); L-BFGS on true-max (no benefit)

### gen002_exploit_1_sol02 (score: 1.5108)
- Central: idea_007 (smooth-max, 6-phase), idea_008 (20 restarts, 18k steps/phase)
- Peripheral: idea_001, idea_009, idea_010 (L-BFGS smooth T=1e-5, no effect)
- Novel elements: L-BFGS on smooth objective at T=1e-5 (confirmed no improvement)

### gen002_explore_2_sol03 (score: 1.5108)
- Central: idea_007 (smooth-max), idea_008 (8 seeds), SA fine-grid (ineffective)
- Peripheral: idea_001, idea_009, idea_010 (L-BFGS inner for SA)
- Novel elements: SA+L-BFGS inner loop; conclusively shown ineffective at N=600

### gen002_explore_2_sol02 (score: 1.5162)
- Central: idea_007, idea_008 (4 seeds), SA fine-grid (partial convergence)
- Peripheral: idea_001, idea_009
- Novel elements: SA with Adam inner optimizer

### gen002_explore_2_sol01 (score: 1.5176)
- Central: idea_007, SA fine-grid (weak init)
- Peripheral: idea_001, idea_009
- Novel elements: SA with very weak initial convergence

### gen002_explore_1_sol01 (score: 1.5188)
- Central: idea_004 (coarse-to-fine N=40->150->600, COLD fine stage), idea_007 (smooth-max)
- Peripheral: idea_009, idea_008 (6 restarts)
- Novel elements: Cold fine stage (T=0.001 start after upsampling) -- FAILS; N=40 coarse too small

## Generation 3

### gen003_research_1_sol01 (score: 1.5032) — Gen 3 OVERALL BEST, TARGET BEATEN
- Central: idea_014 (warm-start from published AlphaEvolve solution)
- Peripheral: none (verbatim array, no optimization)
- Novel elements: 1319-element step function from AlphaEvolve. LP-guided memetic algorithm (idea_016).

### gen003_explore_2_sol01 (score: 1.5090) — Best gradient-descent result
- Central: idea_004 (coarse-to-fine N=80->600), idea_007 (smooth-max), idea_013 (arcsine init)
- Peripheral: idea_001 (Adam), idea_009 (softplus), idea_008 (6 seeds)
- Novel elements: Arcsine-weighted init on biased subinterval [-0.05, 0.22]

### gen003_exploit_1_sol02 (score: 1.5091)
- Central: idea_007 (smooth-max), idea_004 (coarse-to-fine), idea_015 (DCT perturbation)
- Peripheral: idea_001 (Adam), idea_009 (softplus)
- Novel elements: DCT perturbation of raw_params. All 10 configs converge back to 1.5091.

### gen003_explore_2_sol03 (score: 1.5091)
- Central: idea_004 (3-stage N=80->200->600), idea_007 (smooth-max), idea_013 (arcsine init), idea_008 (12 seeds)
- Peripheral: idea_001 (Adam), idea_009 (softplus)
- Novel elements: 3-stage pipeline. Did NOT improve over 2-stage.

### gen003_explore_2_sol04 (score: 1.5092)
- Central: idea_004, idea_007, idea_008 (25-seed funnel), idea_013 (arcsine)
- Peripheral: idea_001, idea_009, idea_003
- Novel elements: 25-seed funnel. All top-5 were arcsine-initialized.

### gen003_exploit_1_sol01 (score: 1.5093)
- Central: idea_004 (3-stage), idea_007 (extended to T=0.00003)
- Peripheral: idea_001, idea_009, idea_008 (4 seeds)
- Novel elements: Ultra-low-temp polish. Negligible improvement (0.000025).

### gen003_explore_2_sol02 (score: 1.5102)
- Central: idea_004, idea_007, idea_013 (arcsine 10 configs)
- Peripheral: idea_001, idea_009
- Novel elements: Arcsine subinterval sweep.

### gen003_explore_1_sol01 (score: 1.5148) — Coarse SA N=40
- Central: idea_004 (N=40 + N=600), idea_007, coarse-SA (failed)
- Peripheral: idea_001, idea_008 (4 seeds)
- Novel elements: Coarse-scale SA. 96-100% acceptance — poorly calibrated.

### gen003_explore_1_sol02 (score: 1.5155)
- Central: idea_004 (N=80 + N=600), idea_007, coarse-SA (failed)
- Peripheral: idea_001, idea_008 (3 seeds)
- Novel elements: N=80 coarse SA. sigma grew uncontrollably.

### gen003_explore_1_sol03 (score: 1.5169)
- Central: idea_004 (N=30 + N=600), idea_007, coarse-SA (failed)
- Peripheral: idea_001, idea_008 (4 seeds)
- Novel elements: N=30 coarse SA.

## Generation 4

### gen004_research_1_sol01 (score: 1.5029) — Gen 4 OVERALL BEST
- Central: idea_014 (warm-start from published TTT-Discover solution), idea_018 (TTT-Discover method)
- Peripheral: none (verbatim array, no optimization)
- Novel elements: 30,000-element array from TTT-Discover (Yuksekgonul et al., Jan 2026).

### gen004_exploit_1_sol01 (score: 1.5032) — Warm-start polish attempt
- Central: idea_014 (warm-start from 1.5032 array), idea_007 (smooth-max), idea_009 (softplus)
- Peripheral: idea_001 (Adam), idea_008 (4 seeds)
- Novel elements: Conservative warm-start: inv_softplus conversion, T=0.005->0.0001. NO improvement.

### gen004_exploit_2_sol01 (score: 1.5159) — Upsample attempt
- Central: idea_014 (warm-start from 1.5032 array), idea_002 (upsample N=1319->2000), idea_007 (smooth-max)
- Peripheral: idea_001 (Adam), idea_009 (softplus)
- Novel elements: Cubic spline upsample destroyed sparse structure.

### gen004_exploit_1_sol02 (score: 1.5242) — Aggressive warm-start
- Central: idea_014 (warm-start, aggressive), idea_007 (smooth-max), idea_009 (softplus)
- Peripheral: idea_001 (Adam)
- Novel elements: Large perturbation (sigma=0.1) destroyed solution.

### gen004_explore_1_sol01 (score: INVALID — evaluation timeout)
- Central: coarse-SA (N=23, properly calibrated), idea_004 (coarse-to-fine)
- Peripheral: idea_001 (Adam), idea_007 (smooth-max)
- Novel elements: Calibrated SA exceeded evaluation timeout.

## Generation 5

### gen005_exploit_2_sol01 (score: 1.5028628894) — NEW OVERALL BEST, FIRST AGENT IMPROVEMENT
- Central: idea_019 (float64 coordinate descent), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: idea_017 (sensitivity-guided element selection)
- Novel elements: Float64 reimplementation of compute_c matching validate.py. Adaptive deltas (1e-6 to 1e-2). Top-500 elements by gradient magnitude. 10 passes with gradient recomputation. 116 improvements, most from zeroing LP residuals (~1e-13 elements). Block perturbation found nothing after coordinate descent.

### gen005_exploit_1_sol01 (score: 1.502862898) — No improvement over baseline
- Central: idea_017 (projected gradient, all variants), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: idea_001 (Adam), idea_007 (smooth-max T=0.0001)
- Novel elements: Tested 6 approaches: smooth-max projected gradient, hard-max projected gradient, normalized gradient, coordinate descent on peak contributors, broad coordinate descent (1830 micro-improvements at float64 precision limit), random perturbation search. ALL gradient-based approaches failed.

### gen005_explore_1_sol01 (score: 1.5227) — SA at N=23, buggy structure
- Central: idea_004 (coarse-to-fine N=23->600), coarse-SA (buggy: inner opt before Metropolis)
- Peripheral: idea_001 (Adam), idea_007 (smooth-max)
- Novel elements: SA at N=23 with inner optimizer running BEFORE Metropolis criterion (bug).

### gen005_explore_1_sol02 (score: 1.5227) — SA at N=23, corrected
- Central: idea_004 (coarse-to-fine N=23->600), coarse-SA (corrected, 20% acceptance)
- Peripheral: idea_001 (Adam), idea_007 (smooth-max)
- Novel elements: Corrected SA structure. Identical score to buggy sol01.

### gen005_explore_1_sol03 (score: 1.5162) — SA at N=80, corrected
- Central: idea_004 (coarse-to-fine N=80->600), coarse-SA (corrected)
- Peripheral: idea_001 (Adam), idea_007 (smooth-max)
- Novel elements: Same corrected SA at N=80.

### gen005_explore_1_sol04 (score: 1.5418) — Gaussian mixture parameterization
- Central: Gaussian mixture (15 learnable peaks), idea_001 (Adam)
- Peripheral: idea_008 (4 seeds)
- Novel elements: 15 Gaussian peaks with learnable positions/widths/amplitudes.

### gen005_research_1_sol01 (score: 1.5053) — AlphaEvolve Cell 46 (N=600)
- Central: idea_014 (published solution retrieval)
- Peripheral: none (verbatim array)
- Novel elements: N=600 array from AlphaEvolve notebook Cell 46.

### gen005_research_1_sol02 (score: 1.5040) — AlphaEvolve Cell 49 (N=600)
- Central: idea_014 (published solution retrieval)
- Peripheral: none (verbatim array)
- Novel elements: N=600 array from Cell 49.

### gen005_research_1_sol03 (score: 1.5036) — AlphaEvolve Cell 52 (N=984)
- Central: idea_014 (published solution retrieval)
- Peripheral: none (verbatim array)
- Novel elements: N=984 oscillating structure from Cell 52.

### gen005_research_1_sol04 (score: 1.5035) — AlphaEvolve Cell 54 (N=1444)
- Central: idea_014 (published solution retrieval)
- Peripheral: none (verbatim array)
- Novel elements: N=1444 smooth structure from Cell 54.

### gen005_research_1_sol05 (score: 1.5032) — AlphaEvolve Cell 58 (N=5000)
- Central: idea_014 (published solution retrieval)
- Peripheral: none (verbatim array)
- Novel elements: N=5000 fine-grained array from Cell 58.

## Generation 6

### gen006_exploit_1_sol01 (score: 1.502862872) — NEW OVERALL BEST
- Central: idea_019 (float64 coordinate descent, full-array), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: Extended full-array coordinate descent on ALL 25141 nonzero elements. O(N) incremental autoconvolution update for 28x speedup. Total delta: -2.58e-8 from TTT-Discover baseline.

### gen006_exploit_2_sol01 (score: 1.503953) — Pattern_007 float64 confirmation
- Central: idea_014 (warm-start from AlphaEvolve Cell 49 N=600), idea_007 (smooth-max Adam)
- Peripheral: idea_001 (Adam lr=1e-3), idea_009 (softplus/inv_softplus)
- Novel elements: Float64 accept/reject for smooth-max Adam on N=600 published array. ALL 6 temperature phases rejected. Confirms pattern_007 with float64 rigor.

### gen006_full_1_sol01 (score: 1.502862898) — LP refinement attempt (engineering failure)
- Central: idea_020 (LP-based refinement), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: LP constraint matrix construction consumed ~7GB RAM. LP never ran.

### gen006_explore_1 (no solution) — Session interrupted
- Central: N/A
- Novel elements: Session ended before any code was written.

## Generation 7

### gen007_explore_1_sol01 (score: 1.5028628689) — NEW OVERALL BEST
- Central: idea_021 (triplet perturbation, gradient-guided), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: idea_019 (coordinate descent — used as starting point)
- Novel elements: 60k triplet trials with 4 selection strategies, 9 step sizes. O(N) incremental autoconv update. 160 improvements, delta = -3.578e-9. Second pass (20k trials): 0 improvements. First multi-element improvement over coordinate-descent-optimized solution.

### gen007_exploit_2_sol01 (score: 1.5028628703) — Extended coord descent
- Central: idea_019 (float64 coordinate descent), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: Continued coord descent from gen006 best. 156 improvements in 3 rounds, converged to 0 in round 4. Delta = -2.13e-9.

### gen007_exploit_1_sol01 (score: 1.5028628715) — Coord descent with safe-set
- Central: idea_019 (float64 coordinate descent, safe-set optimization), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: Safe-set max computation. 3x speedup. 6 rounds, 6551 improvements, delta = -9.96e-10.

### gen007_full_1_sol04 (score: 1.5028628713) — Coord descent after LP failure
- Central: idea_019 (float64 coordinate descent), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: 257 improvements, delta = -1.217e-9. Converged in 2 rounds.

### gen007_full_1_sol01 (score: 1.5028628725) — LP at N=2000 (no improvement)
- Central: idea_020 (LP-based refinement, N=2000 downsampled), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: LP improved C at N=2000 from 1.721 to 1.710. Upsampled direction worsened C at N=30k.

### gen007_full_1_sol02 (score: 1.5028628725) — LP at N=30k, 1 constraint (no improvement)
- Central: idea_020 (LP at N=30k, minimal constraint), idea_014
- Peripheral: none
- Novel elements: LP solved in 0.16s. Found t<0 but all step sizes worsened C.

### gen007_full_1_sol03 (score: 1.5028628725) — LP at N=30k, 138 constraints (no improvement)
- Central: idea_020 (LP at N=30k, 138 tight constraints), idea_014
- Peripheral: none
- Novel elements: LP solved in 8.2s. ~6360 uncontrolled plateau points become new max.

## Generation 8

### gen008_explore_1_sol01 (score: 1.5028628685) — NEW OVERALL BEST
- Central: idea_022 (quadruplet perturbation, gradient-guided), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: idea_021 (triplet follow-up), idea_019 (coord descent — prior generations' starting point)
- Novel elements: 8015 quadruplet improvements with 4 strategies. Triplet follow-up found 2523 additional improvements. Total delta = -4.13e-10.

### gen008_exploit_1_sol01 (score: 1.5028628686) — Coord descent on gen7 triplet-modified array
- Central: idea_019 (float64 coordinate descent), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: 2008 coord descent improvements on gen7's triplet-modified array. Confirms interleaving hypothesis.

### gen008_exploit_2_sol01 (score: 1.5028628689) — Momentum triplets (no improvement)
- Central: idea_021 (momentum-enhanced triplet search, Strategy 1 only), idea_014
- Peripheral: none
- Novel elements: 36k Strategy 1 trials with momentum. 0 improvements found.

### gen008_explore_2 (no solution) — Diagnostic experiments
- Central: idea_020 (LP plateau analysis at intermediate N)
- Peripheral: idea_014 (source array)
- Novel elements: Downsampling N=30k → N=5000 gives C=7+ (pattern_015). FFT padding validation.

## Generation 9

### gen009_exploit_1_sol01 (score: 1.5028628682) — NEW OVERALL BEST
- Central: idea_019 (float64 coordinate descent, ultra-fine deltas 1e-8 to 5e-11), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: Multi-scale coord descent with extended delta grid. Total delta = -2.56e-10 from gen 8 best. Key discovery: delta resolution gap.

### gen009_explore_1_sol01 (score: 1.5028628683) — Quintuplet test + triplet follow-up
- Central: idea_021 (triplet perturbation, 150 improvements), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: idea_022 (quadruplet follow-up, 0 improvements)
- Novel elements: Quintuplets definitively at float64 precision limit (pattern_018). Triplets still effective from standard CD.

### gen009_exploit_2_sol01 (score: TIMEOUT — no score)
- Central: idea_022 (quadruplet perturbation with momentum + S4 strategy), idea_014
- Peripheral: none
- Novel elements: Evaluation timed out (>20 min). Root cause: np.argmax(autoconv) computed every trial instead of cached.

### gen009_explore_2_sol01 (score: 1.5168) — N=5000 GD + CD + LP study
- Central: idea_001 (Adam + smooth-max, N=5000 from scratch), idea_019 (coord descent at N=5000)
- Peripheral: idea_020 (LP tractability study)
- Novel elements: LP tractability at N=5000 near-optimal: definitively closes LP path at all resolutions.

### gen009_explore_2_sol02 (score: 1.5170) — N=5000 iterative LP
- Central: idea_001 (Adam + smooth-max, N=5000), idea_020 (iterative LP test)
- Peripheral: idea_019 (coord descent at N=5000)
- Novel elements: Confirms LP failure at N=5000.

## Generation 10

### gen010_explore_2_sol01 (score: 1.5028628681165177) — NEW OVERALL BEST
- Central: idea_019 (ultra-fine CD with fast_check pre-filter, 8003 improvements), idea_014 (warm-start from TTT-Discover 30k via gen9 exploit_1)
- Peripheral: none
- Novel elements: Custom fast_check using precomputed high-autoconv positions (W≈6760) for O(W×k) pre-filtering. Coarse CD confirmed converged (0 improvements). 200k triplet trials → 0 improvements. 50k quadruplet trials → 0 improvements. Ultra-fine CD (deltas 1e-11 to 1e-1, 50 values) found 8003 improvements, delta_C = -1.06e-10. Confirmed pattern_020 and debunked multi-element approaches at this precision.

### gen010_explore_1_sol01 (score: 1.5028628681659377) — Minimax LP null + CD
- Central: idea_019 (ultra-fine CD, 1281 improvements), idea_014 (warm-start from TTT-Discover 30k via gen9 exploit_1), idea_023 (minimax LP — TESTED, NULL RESULT)
- Peripheral: none
- Novel elements: First implementation of idea_023 (minimax LP). K=28 plateau positions. 47,233 minimax triplet LP trials → 0 improvements (all t*≥0). 21,217 minimax quadruplet LP trials → 0 improvements. Idea_023 DEBUNKED. Then ultra-fine CD with window-based evaluation found 1281 improvements (859 + 422 across 2 rounds), delta_C = -5.70e-11. Key insight: CD works via non-integral-preserving mechanism (pattern_024).

### gen010_exploit_1_sol01 (score: 1.5028628681839242) — Top-K screened CD, drift discovery
- Central: idea_019 (geometric CD with top-K screening + FFT resync), idea_014 (warm-start from TTT-Discover 30k via gen9 exploit_1)
- Peripheral: none
- Novel elements: Top-K screening (K=30): 50x speedup. Drift discovery: ~1.4e-12/round. 71 rounds, ~371k improvements (99.6% at 1e-13 scale). 1e-14 improvements INCREASING (pattern_023). Baked array.

### gen010_exploit_2_sol01 (score: 1.5028628682225948) — A/B test: CD only vs multi-element+CD
- Central: idea_019 (ultra-fine CD, A/B test winner), idea_014 (warm-start from TTT-Discover 30k via gen9 exploit_1)
- Peripheral: none
- Novel elements: A/B test. Path A (CD only): 19 improvements. Path B (triplets+quads+CD): 0+0+17. Path A wins by 5.57e-14.

## Generation 11

### gen011_explore_1_sol01 (score: 1.5028628677925082) — NEW OVERALL BEST
- Central: idea_024 (non-integral-preserving 2-element pair search), idea_019 (ultra-fine CD), idea_014 (warm-start from TTT-Discover 30k via gen009 exploit_1)
- Peripheral: none
- Novel elements: Two-phase protocol. Phase 2: non-IP pair search (2300 improvements, 547 neighboring + 1753 random high-sensitivity). Phase 3: ultra-fine CD (10995 improvements, 1 round). Phase 2 amplifies Phase 3 by ~15x (pattern_025). Started from gen009/exploit_1 inline array (C=1.5028628682228971), not gen010 best. Total delta from start: -4.3e-9. Delta from gen010 best: -3.24e-9.

### gen011_exploit_2_sol01 (score: 1.502862868176393)
- Central: idea_019 (focused delta CD + multi-trajectory), idea_014 (warm-start from TTT-Discover 30k via gen010 exploit_1)
- Peripheral: none
- Novel elements: Focused (1e-14..1e-11) vs broad (1e-14..1e-1) delta comparison: focused wins 1.83x (pattern_026). Multi-trajectory competition (3 seeds): all ended WORSE than Phase 2 due to intra-round drift (pattern_027). Non-reproducible gen010 entrypoint: got C=1.5028628681772360, not 1.5028628681165177 (pattern_028).

### gen011_exploit_1 (no scored solution) — Per-round FFT resync CD
- Central: idea_019 (per-round FFT resync CD), idea_014 (warm-start from TTT-Discover 30k)
- Peripheral: none
- Novel elements: Confirmed gen010 entrypoint non-reproducibility (5.9e-11 gap). Single-pass vs multi-pass: 50-100 improvements/round vs gen010's 5000/round. 410 rounds achieved only ~1.8e-12 total improvement from (worse) starting point. No scored solution produced.

### gen011_experimentator_1 (no solution — helper only)
- Central: Built topk_screened_cd shared helper
- Novel elements: Combines top-K screening (pattern_022), FFT resync (pattern_021), geometric delta grid. 14/14 tests pass. Updated helpers README.
