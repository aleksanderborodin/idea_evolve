# Experiment Suggestions — Generation 2

## Experiment 1: Symmetry enforcement with bimodal initialization

**Hypothesis**: The combination of (a) even symmetry enforcement + (b) two-bump initialization
has not been tested. Symmetric unimodal → C=2 (pattern_001) is confirmed, but the theoretical
analysis predicts symmetric bimodal should be near-optimal. The confusion between these two
cases may be causing agents to incorrectly reject symmetry enforcement entirely.

**Setup**:
- Optimize g_half (N/2 parameters) on [0, 1/4] only, then mirror: g_full = concat(g_half[::-1], g_half)
- f = softplus(g_full) (or relu)
- Initialize with two Gaussians at x ≈ +0.10 and +0.20 (mapped to half-domain x ∈ [0, 1/4])
- Use standard multi-scale Adam: N=600→N=2000, 40k→50k steps
- Run 5 random seeds for each initialization type

**What to learn**: Does enforcing even symmetry with a bimodal starting point improve over
asymmetric optimization? If yes: halving parameter count helps. If no: asymmetric solutions
are genuinely better (non-even optimal function).

**Expected information gain**: HIGH — this resolves whether symmetry enforcement is useful
(with right init) or harmful. Directly tests the main theoretical prediction from research_1.

---

## Experiment 2: softplus reparameterization in multi-scale Adam pipeline

**Hypothesis**: The gen-1 multi-scale Adam pipeline uses relu(g) after optimization. Research_1
identifies this as a key deficiency: values that go negative get zero gradient and are
effectively pruned. softplus(g) maintains full gradient signal and may find deeper local minima.

**Setup**:
- Take the standard multi-scale Adam pipeline (N=600→N=2000, adam, lr=0.005→0.002)
- Change only: f = jax.nn.softplus(g) instead of jax.nn.relu(g)
- Run 3 diverse initializations: flat block, two-bump, cosine-window
- Compare directly to explore_1/sol04 (multi-scale Adam + relu) as control

**What to learn**: Does softplus outperform relu in the multi-scale pipeline? By how much?
If improvement exists, it should be general — applies to all future multi-scale solutions.

**Expected information gain**: HIGH — if softplus gives even 0.001 improvement, it should
become the default parameterization for all future agents.

---

## Experiment 3: Sidon-inspired 4-bump initialization

**Hypothesis**: The Sidon set {0, 1, 3, 6} scaled to [-1/4, 1/4] gives bumps at approximate
positions {-0.25, -0.167, 0, 0.25}. The Sidon property ensures all pairwise differences are
distinct, which spreads the autoconvolution energy evenly. This is a strong theoretical prior
that no gen-1 agent tested.

**Setup**:
- Place 4 Gaussians at x ≈ {-0.25, -0.167, 0, 0.25} with σ ≈ 0.03–0.05
- Use multi-scale Adam on top: N=600→N=2000
- Also try 3-bump versions: {-0.25, 0, 0.25} (symmetric Sidon-{0,1,2} analog)
- Compare best results to gen-1 best (~1.5167)

**What to learn**: Can a theoretically-motivated initialization escape the 1.517x local
attractor that gen-1 Adam converges to? If Sidon-inspired init reaches <1.515, this confirms
the initialization, not the optimizer, is the bottleneck.

**Expected information gain**: HIGH if it escapes the local attractor; MEDIUM otherwise
(confirms the optimizer/landscape is the constraint, not initialization quality).

---

## Experiment 4: Adam→L-BFGS-B with softplus (clean isolation test)

**Hypothesis**: Research_1 argues that L-BFGS should excel as a *refinement* step (not
cold-start) when paired with softplus reparameterization (continuous gradients everywhere).
Gen-1 tested Adam→L-BFGS with relu (explore_1/sol10, unevaluated) and L-BFGS cold start
(explore_1/sol01–sol02, C=1.69–1.81). The combination of warm Adam start + softplus has
not been cleanly tested.

**Setup**:
- Phase 1: Adam for 40k steps at N=600 with f = softplus(g), lr=0.005
- Upsample g to N=2000
- Phase 2: L-BFGS-B via scipy.optimize.minimize at N=2000, box constraints g ≥ g_min,
  starting from Adam-found g
- Run 3 seeds, compare to multi-scale Adam baseline

**What to learn**: Whether L-BFGS-B refinement (with correct parameterization) can push
beyond the 1.517x plateau that Adam appears stuck at. L-BFGS can exploit curvature
information that Adam ignores.

**Expected information gain**: MEDIUM-HIGH — if L-BFGS adds ≥0.0005 improvement over Adam
alone, it becomes a standard post-processing step.

---

## Experiment 5: Higher resolution final phase (N=4000+)

**Hypothesis**: The gen-1 best confirmed score (1.5167, from eval_cache) was achieved by
solutions using N=2000 final resolution. explore_1/sol06 tried N=4000 third phase but was
unevaluated. A systematic test of N=2000 → N=4000 → N=8000 resolution staircase may reveal
whether there's still improvement available from finer discretization.

**Setup**:
- Take the best-scoring gen-1 solution as starting point (run evaluate.py to confirm which)
- Implement: N=600 (40k) → N=2000 (50k) → N=4000 (30k) → N=8000 (10k)
- Note wall-clock time per phase — N=8000 may be too slow for 900s budget
- Compare to the 2-phase baseline (N=600→N=2000)

**What to learn**: Whether the current resolution is a limiting factor, or whether the problem
is the landscape (local minimum) rather than the discretization. If N=4000 gives <0.0001
improvement over N=2000, resolution is not the bottleneck.

**Expected information gain**: MEDIUM — resolves whether to invest in higher-N solutions.
If N=8000 is prohibitively slow, this also sets the practical resolution ceiling.

---

## Experiment 6: Log-sum-exp smooth max objective

**Hypothesis**: The hard max in the objective is non-differentiable when the argmax changes
during optimization. JAX computes a subgradient but this creates gradient discontinuities.
The log-sum-exp smooth approximation (explore_1/sol05 used this idea via "soft-max annealing")
may improve convergence. explore_1/sol05 was unevaluated (fitness header set but no .score).

**Setup**:
- Implement smooth objective: C_smooth = log(sum(exp(beta * conv))) / beta for beta ∈ {20, 50, 100, 200}
- Anneal beta during training: start with beta=20, end with beta=200, final hard max evaluation
- Compare to vanilla Adam with hard max
- Run at N=2000, 80k steps, 3 seeds

**What to learn**: Whether smooth max annealing provides a gradient landscape that reaches
lower final C. This directly tests whether the hard-max gradient issue is limiting gen-1 scores.

**Expected information gain**: MEDIUM — if smooth max improves scores significantly, it
should be adopted as default. If not, the gradient smoothness issue is not the bottleneck.
