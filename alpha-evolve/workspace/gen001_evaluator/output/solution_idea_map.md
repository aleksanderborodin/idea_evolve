# Solution-Idea Map

## Generation 1

### explore_1/sol01 (score: 1.6904)
- Central: idea_001 (gradient descent — L-BFGS variant), idea_010 (softplus reparameterization)
- Peripheral: idea_003 (Gaussian init)
- Novel elements: None

### explore_1/sol02 (score: 1.8111)
- Central: idea_001 (gradient descent — L-BFGS variant), idea_010 (softplus reparameterization)
- Peripheral: idea_003 (flat block init)
- Novel elements: None

### explore_1/sol03 (score: 1.5257)
- Central: idea_001 (Adam optimizer)
- Peripheral: idea_003 (cosine window init)
- Novel elements: None

### explore_1/sol04 (score: 1.5178)
- Central: idea_001 (Adam), idea_004 (multi-scale N=600->2000)
- Peripheral: None
- Novel elements: None

### explore_1/sol05 (score: 1.5177)
- Central: idea_001 (Adam), idea_004 (multi-scale), idea_012 (multiple seeds)
- Peripheral: None
- Novel elements: None

### explore_1/sol06 (score: 1.5176)
- Central: idea_001 (Adam/AdamW), idea_004 (multi-scale N=600->2000->4000)
- Peripheral: idea_002 (higher resolution N=4000)
- Novel elements: Three-phase upsampling

### explore_1/sol07 (score: 1.5217)
- Central: idea_001 (Lion optimizer variant)
- Peripheral: idea_002 (N=2000)
- Novel elements: Lion optimizer (underperforms Adam)

### explore_1/sol08 (score: 1.5177)
- Central: idea_001 (Adam), idea_004 (multi-scale), idea_012 (multi-start 3 seeds)
- Peripheral: None
- Novel elements: None

### explore_1/sol09 (score: 1.5174)
- Central: idea_001 (Adam), idea_004 (multi-scale), idea_012 (multi-start 5 diverse inits)
- Peripheral: idea_003 (varied shape priors: flat, narrow, wide, two-bump)
- Novel elements: Diverse initialization pool including two-bump

### explore_1/sol10 (score: 1.5178)
- Central: idea_001 (Adam), idea_004 (multi-scale), idea_008 (Adam->L-BFGS-B hybrid)
- Peripheral: None
- Novel elements: None

### explore_1/sol11 (score: 1.5168)
- Central: idea_001 (Adam), idea_004 (multi-scale), idea_007 (basin hopping 5 rounds)
- Peripheral: None
- Novel elements: None

### explore_1/sol12 (score: 1.5168) **BEST**
- Central: idea_001 (Adam), idea_004 (multi-scale), idea_007 (basin hopping 10 rounds)
- Peripheral: idea_012 (diverse seed starts before hopping)
- Novel elements: Aggressive noise schedule (varying levels 0.05-0.10)

### explore_1/sol13 (score: 1.5203)
- Central: idea_001 (Adam), idea_004 (multi-scale), idea_005 (L1 normalization)
- Peripheral: None
- Novel elements: L1-projected optimization (underperforms)

### explore_2/sol01 (score: 2.0000)
- Central: idea_001 (Adam), idea_009 (symmetry enforcement)
- Peripheral: idea_003 (truncated Gaussian init)
- Novel elements: None — confirmed dead end (pattern_001)

### explore_2/sol02 (score: 2.0000)
- Central: idea_001 (Adam), idea_009 (symmetry enforcement)
- Peripheral: None
- Novel elements: Symmetry-enforced free-form — same dead end

### explore_2/sol03 (score: 1.5295)
- Central: idea_001 (Adam)
- Peripheral: None
- Novel elements: Asymmetric initialization (right-biased)

### explore_2/sol04 (score: 1.5785)
- Central: idea_001 (Adam)
- Peripheral: idea_003 (B-spline basis parameterization)
- Novel elements: B-spline basis reduction (underperforms)

### explore_2/sol05 (score: 1.5184)
- Central: idea_001 (Adam), idea_012 (multi-start 3 inits)
- Peripheral: None
- Novel elements: None

### explore_2/sol06 (score: 1.5191)
- Central: idea_001 (Adam), idea_008 (Adam->L-BFGS-B hybrid)
- Peripheral: None
- Novel elements: None

### explore_2/sol07 (score: 1.5182)
- Central: idea_001 (Adam 80k steps), idea_008 (L-BFGS refinement)
- Peripheral: None
- Novel elements: Extended Adam budget (80k steps)

### explore_2/sol08 (score: 1.5179)
- Central: idea_001 (Adam), idea_008 (L-BFGS refinement), idea_002 (N=1000)
- Peripheral: None
- Novel elements: None

### explore_2/sol09 (score: 1.5207)
- Central: idea_001 (Adam), idea_008 (L-BFGS), idea_002 (N=1200), idea_012 (multi-seed)
- Peripheral: None
- Novel elements: None

### explore_2/sol10 (score: 1.5354)
- Central: idea_001 (Adam), idea_005 (TV regularization annealing)
- Peripheral: idea_008 (L-BFGS phase)
- Novel elements: TV annealing schedule (underperforms)

### explore_2/sol11 (score: 1.5182)
- Central: idea_001 (Adam), idea_012 (multi-seed), idea_002 (N=1000)
- Peripheral: idea_008 (L-BFGS)
- Novel elements: None

### explore_2/sol12 (score: 1.5179)
- Central: idea_001 (Adam cyclic LR), idea_008 (L-BFGS refinement), idea_002 (N=1000)
- Peripheral: None
- Novel elements: Cyclic cosine LR schedule (3 cycles)

### full_1/sol01 (score: 2.0000)
- Central: idea_001 (Adam), idea_009 (symmetry enforcement)
- Peripheral: None
- Novel elements: Inline relu projection each step — dead end (pattern_001)

### full_1/sol02 (score: 1.5202)
- Central: idea_001 (Adam), idea_002 (N=1200)
- Peripheral: None
- Novel elements: End-only relu (allows negative during training)

### full_1/sol03 (score: 1.5178)
- Central: idea_001 (Adam), idea_008 (Adam->L-BFGS-B), idea_012 (3 restarts)
- Peripheral: None
- Novel elements: None

### full_1/sol04 (score: 1.5183)
- Central: idea_001 (Adam 40k), idea_008 (L-BFGS-B 50k), idea_002 (N=1000)
- Peripheral: idea_012 (3 restarts)
- Novel elements: Extended L-BFGS-B budget (50k iters)

### full_1/sol05 (score: 1.5187)
- Central: idea_001 (Adam), idea_008 (L-BFGS-B)
- Peripheral: None
- Novel elements: Soft-max annealing (log-sum-exp beta 20->500) — did not improve over hard max
