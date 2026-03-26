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

### gen004_research_1_sol01 (score: 1.5029) — NEW OVERALL BEST
- Central: idea_014 (warm-start from published TTT-Discover solution), idea_018 (TTT-Discover method)
- Peripheral: none (verbatim array, no optimization)
- Novel elements: 30,000-element array from TTT-Discover (Yuksekgonul et al., Jan 2026). LP with heuristic focusing on near-tight constraints. Qualitatively different structure from all prior solutions.

### gen004_exploit_1_sol01 (score: 1.5032) — Warm-start polish attempt
- Central: idea_014 (warm-start from 1.5032 array), idea_007 (smooth-max), idea_009 (softplus)
- Peripheral: idea_001 (Adam), idea_008 (4 seeds)
- Novel elements: Conservative warm-start: inv_softplus conversion, T=0.005→0.0001, sigma=0.01 perturbation. Result: NO improvement (3.8e-9 change = floating-point noise).

### gen004_exploit_2_sol01 (score: 1.5159) — Upsample attempt
- Central: idea_014 (warm-start from 1.5032 array), idea_002 (upsample N=1319→2000), idea_007 (smooth-max)
- Peripheral: idea_001 (Adam), idea_009 (softplus)
- Novel elements: Cubic spline upsample to N=2000. Destroyed sparse structure, score much worse. Confirms cubic interpolation inappropriate for sparse solutions.

### gen004_exploit_1_sol02 (score: 1.5242) — Aggressive warm-start
- Central: idea_014 (warm-start, aggressive), idea_007 (smooth-max), idea_009 (softplus)
- Peripheral: idea_001 (Adam)
- Novel elements: Large perturbation (sigma=0.1), high starting T=0.05. Destroyed solution, landed in inferior basin (~1.524).

### gen004_explore_1_sol01 (score: INVALID — evaluation timeout)
- Central: coarse-SA (N=23, properly calibrated), idea_004 (coarse-to-fine)
- Peripheral: idea_001 (Adam), idea_007 (smooth-max)
- Novel elements: Calibrated SA at N=23 per Boyer et al. protocol: sigma=0.05*std, metro_t calibrated to 20-40% acceptance, cold inner optimizer (T=0.001 only, 300 steps). Implementation was correct but computation budget (4 seeds × 500 SA iters × 300 inner steps = 600k gradient evals) exceeded evaluation timeout.
- **Key finding:** The SA approach is computationally viable but needs reduced budget (2 seeds, 100 SA iters).
