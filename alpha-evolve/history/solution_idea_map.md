# Solution-Idea Map

## Generation 1

### gen001_full_1_sol03 (score: 1.5108) — Previous Best
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
- Novel elements: Support blocks shifted ±N/16 per seed

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
- Novel elements: Adam warmup → L-BFGS transition

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
- Central: idea_006 (analytical construction — Hann window)
- Peripheral: none (no optimization)
- Novel elements: Pure analytical, no gradient descent

## Generation 2

### gen002_explore_1_sol03 (score: 1.5091) — NEW BEST
- Central: idea_004 (coarse-to-fine N=80→600, warm fine stage), idea_007 (smooth-max), idea_008 (12 restarts)
- Peripheral: idea_009 (softplus), idea_003 (3-bump diverse asymmetric init)
- Novel elements: 3-bump random init; warm fine stage (T=0.05 restart after upsample); 12 restarts at N=80

### gen002_explore_1_sol02 (score: 1.5093)
- Central: idea_004 (coarse-to-fine N=80→600, warm fine stage), idea_007 (smooth-max), idea_008 (8 restarts)
- Peripheral: idea_009 (softplus), idea_003 (2-bump asymmetric init)
- Novel elements: Key insight — warm fine stage (T=0.05) after upsampling is essential

### gen002_exploit_1_sol01 (score: 1.5107)
- Central: idea_007 (smooth-max, 6-phase schedule to T=0.0001), idea_008 (16 restarts)
- Peripheral: idea_001 (Adam), idea_009 (softplus), idea_010 (L-BFGS, zero effect)
- Novel elements: 6th temperature phase T=0.0001 (no benefit); L-BFGS on true-max (no benefit)

### gen002_exploit_1_sol02 (score: 1.5108)
- Central: idea_007 (smooth-max, 6-phase), idea_008 (20 restarts, 18k steps/phase)
- Peripheral: idea_001, idea_009, idea_010 (L-BFGS smooth T=1e-5, no effect)
- Novel elements: L-BFGS on smooth objective at T=1e-5 (confirmed no improvement)

### gen002_explore_2_sol03 (score: 1.5108)
- Central: idea_007 (smooth-max), idea_008 (8 seeds), idea_013-prototype (SA fine-grid, ineffective)
- Peripheral: idea_001, idea_009, idea_010 (L-BFGS inner for SA)
- Novel elements: SA+L-BFGS inner loop; conclusively shown ineffective at N=600

### gen002_explore_2_sol02 (score: 1.5162)
- Central: idea_007, idea_008 (4 seeds), idea_013-prototype (SA fine-grid, partial convergence)
- Peripheral: idea_001, idea_009
- Novel elements: SA with Adam inner optimizer

### gen002_explore_2_sol01 (score: 1.5176)
- Central: idea_007, idea_013-prototype (SA fine-grid, weak init)
- Peripheral: idea_001, idea_009
- Novel elements: SA with very weak initial convergence — shows importance of strong init for SA

### gen002_explore_1_sol01 (score: 1.5188)
- Central: idea_004 (coarse-to-fine N=40→150→600, COLD fine stage), idea_007 (smooth-max)
- Peripheral: idea_009, idea_008 (6 restarts)
- Novel elements: Cold fine stage (T=0.001 start after upsampling) — FAILS; N=40 coarse too small
