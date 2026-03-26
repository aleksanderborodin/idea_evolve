# Pre-Concatenated Knowledge Dump


## All Ideas


### [active] idea_003

---
type: idea
id: idea_003
name: "Function shape priors"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_explore_1_sol05, gen001_full_1_sol03]
contradicted_by: [gen001_explore_1_sol01, gen001_explore_2_sol01, gen001_explore_2_sol07]
related_ideas: [idea_006, idea_008, idea_013]
cluster: cluster_002
tags: [initialization, shape, prior, gaussian, hann]
---

Initialize with known function families that have good autoconvolution properties:
Gaussians, bump functions, cosine windows, B-splines. Use these as starting
points for optimization rather than flat/random initialization.

**Gen 1 evidence is mixed:**
- Gaussian initialization (explore_1/sol01): 1.5207 — WORSE than flat+noise baseline.
  Symmetric Gaussians converge to symmetric local minima with C >= 2 before breaking symmetry.
- Hann window (explore_2/sol01): 3.0 — terrible. Symmetric and concentrated.
- Gaussian mixture K=8 (explore_2/sol07): 1.5801 — over-parameterized, hard to optimize.
- However, DIVERSE random bumps as seeds (explore_1/sol05, full_1/sol03) worked well
  when combined with multi-restart — the shape prior is useful as part of a diverse
  seed pool, not as a single initialization.

Key insight: No single shape prior is reliably better than flat+noise. The value
is in diversity of initializations across multiple restarts.

**Gen 3 update:** Arcsine initialization (idea_013) emerged as the best single
shape prior at coarse scale, but the advantage over Gaussian is marginal (1.5090
vs 1.5091). All init families converge to the same ~1.509 attractor basin.


### [active] idea_005

---
type: idea
id: idea_005
name: "Regularization approaches"
lifecycle: active
confidence: 0.4
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 0
supported_by: []
contradicted_by: []
related_ideas: [idea_001, idea_007]
cluster: cluster_001
tags: [regularization, smoothness, constraints]
---

Add regularization terms to the objective: smoothness penalties, sparsity,
symmetry enforcement. These may help the optimizer avoid local minima
with high C values.

Not directly tested in gen 1. However, the softplus reparameterization used
in full_1/sol03 (best solution, C=1.5108) is a form of implicit regularization —
it ensures strict positivity and smooth gradients. The graduated smoothing
(log-sum-exp temperature annealing) in sol03 is also a regularization approach
applied to the max operator itself, not to the function. Both were highly effective.

The explicit smoothness/sparsity penalties remain untested. Scale invariance
(C(alpha*f) = C(f)) means the optimizer should normalize periodically — this
is an implicit constraint that was not widely adopted in gen 1.


### [active] idea_006

---
type: idea
id: idea_006
name: "Analytical constructions"
lifecycle: active
confidence: 0.4
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen001_explore_2_sol01]
related_ideas: [idea_003, idea_008, idea_014, idea_016]
cluster: cluster_002
tags: [analytical, theory, construction]
---

Study the mathematical structure of the problem. The optimal function may
have analytical properties (symmetry, specific support pattern) that can
be constructed directly rather than optimized numerically.

**Gen 1 evidence:**
- explore_2/sol01 (pure Hann window, no optimization): C=3.0 — analytical
  constructions without optimization are far from competitive.
- Research agent (research_1) found that the AlphaEvolve team achieved C=1.5032
  with a 600-interval step function, and ThetaEvolve matched at 1.503133.
- The optimal function has "non-symmetric, multi-peaked, complex structure"
  according to literature — simple analytical forms don't suffice.
- The arcsine distribution shape was suggested as a promising initialization
  but remains untested.

**Gen 3 update:** The AlphaEvolve solution (C=1.5032, N=1319) reveals that the
best-known functions have qualitatively different structure from gradient-descent
solutions: dense region at start, sparse gap, complex multi-peaked structure.
This structure was produced by an LP-guided memetic algorithm (idea_016), not
gradient descent. Understanding this structure may guide initialization design.

The idea remains active because understanding the mathematical structure
(e.g., C >= 2 for symmetric functions) provides critical guidance even if
no closed-form optimum exists.


### [active] idea_009

---
type: idea
id: idea_009
name: "Softplus reparameterization for non-negativity"
lifecycle: active
confidence: 0.6
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04]
contradicted_by: []
related_ideas: [idea_005, idea_001]
cluster: cluster_001
tags: [reparameterization, softplus, non-negativity, constraint]
---

Instead of using relu(f) or bounds to enforce non-negativity, parameterize
f = softplus(raw_params) where raw_params are unconstrained. This ensures
f > 0 strictly (no dead gradients from relu's flat region at 0) and provides
smooth gradients everywhere.

**Evidence:**
- full_1/sol03 and sol04 (both top-2 solutions) use softplus reparameterization.
- explore_1/sol05 and sol07 use relu — also good but 0.005 worse than softplus solutions.
- explore_2/sol09 uses relu — 1.5182.

The evidence is suggestive but not conclusive: sol03's advantage over sol05 could
be due to smooth-max rather than softplus. A controlled experiment isolating softplus
vs relu with the same optimizer would clarify.

**Gen 2-3 update:** Softplus is now standard in all top solutions across gens 2-3.
Never isolated as an independent variable. The DCT perturbation experiment (gen 3)
confirmed that perturbing in f-space (post-softplus) causes NaN due to near-zero
regions, while perturbing in raw_params space (pre-softplus) is clean — validating
the softplus parameterization's numerical benefits.


### [active] idea_011

---
type: idea
id: idea_011
name: "Lion optimizer for escaping plateaus"
lifecycle: active
confidence: 0.35
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_2_sol09]
contradicted_by: []
related_ideas: [idea_001, idea_008]
cluster: cluster_001
tags: [lion, optimizer, sign-gradient]
---

Use the Lion optimizer (sign-based gradient updates) as a warmup phase before
Adam. Lion's sign-gradient property may escape plateaus that Adam gets stuck in.

**Evidence:**
- explore_2/sol08 (Lion 60k + Adam 50k): C = 1.5207
- explore_2/sol09 (Lion 50k + Adam 70k, 4 seeds): C = 1.5182
- explore_2 report claims "Lion > Adam for this objective in the same step budget."

However, explore_2/sol09 at 1.5182 is essentially identical to the baseline (1.5185)
and explore_1/sol04 (pure Adam 80k: 1.5182). The Lion advantage is marginal at best
and may be entirely explained by the multi-seed search in sol09. A controlled
experiment (Lion vs Adam, same total steps, same seeds) is needed.


### [active] idea_013

---
type: idea
id: idea_013
name: "Arcsine initialization for coarse-to-fine"
lifecycle: active
confidence: 0.55
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003_explore_2_sol01, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_012]
cluster: cluster_002
tags: [initialization, arcsine, coarse-to-fine, asymmetric]
---

Initialize with an arcsine-weighted profile (U-shaped, concentrated at interval
endpoints) on a biased subinterval, then optimize via coarse-to-fine + warm
smooth-max. The arcsine shape f(x) ~ 1/sqrt(x*(0.5-x)) naturally produces
mass concentration at domain boundaries, which is intrinsically asymmetric
when placed on a biased subinterval.

**Gen 3 evidence:**
- explore_2/sol01 (arcsine on [-0.05, 0.22], positive tilt, 6 seeds): C = **1.5090** — marginal improvement over 1.5091 baseline.
- explore_2/sol03 (arcsine, 3-stage N=80->200->600, 12 seeds): C = 1.5091.
- explore_2/sol04 (25-seed funnel: 12 arcsine + 8 Gaussian + 5 comb): C = 1.5092. All top-5 coarse seeds were arcsine-initialized.
- explore_2/sol02 (arcsine subinterval sweep, 10 configs): C = 1.5102.

**Key findings:**
- Arcsine dominates Gaussian, comb, and step inits in head-to-head competition at coarse scale (all top-5 of 25 diverse seeds were arcsine).
- Subinterval placement matters: biased toward one half of domain works best ([-0.05, 0.22] or [-0.22, 0.05]).
- Step function init is a dead end (1.519-1.522 range).
- Comb init is mediocre (worse than arcsine and Gaussian).

**However:** The improvement over Gaussian init is marginal (1.5090 vs 1.5091),
suggesting all init families converge to the same ~1.509 attractor basin. The
arcsine advantage may be in more reliably finding this basin, not finding a
better one.


### [active] idea_014

---
type: idea
id: idea_014
name: "Warm-start from published best-known solutions"
lifecycle: active
confidence: 0.8
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003_research_1_sol01]
contradicted_by: []
related_ideas: [idea_006, idea_007, idea_004]
cluster: cluster_003
tags: [warm-start, published-solutions, alphaevolve, literature]
---

Retrieve published best-known solutions from the literature and use them as
starting points for further optimization. The AlphaEvolve team (Georgiev et al.,
Dec 2025) published a 1319-element array achieving C = 1.5032 in the
`alphaevolve_repository_of_problems` GitHub repository.

**Gen 3 evidence:**
- research_1/sol01: Retrieved the AlphaEvolve array verbatim. C = **1.5032** —
  NEW BEST, beats the target of 1.5053 by 0.0021.

**Available published solutions (not all retrieved yet):**
- Cell 46 (C=1.5053, N=600): Original AlphaEvolve result
- Cell 49 (C=1.5040, N~1136): Intermediate improvement
- Cell 52-56 (C=1.5036-1.5035): Further intermediates
- Cell 58 (C=1.5033, N~3530): Near-best
- Cell 60 (C=1.5032, N=1319): Best retrieved ← our sol01
- Yuksekgonul et al. (Jan 2026): C <= 1.5029 — NOT YET PUBLIC in a repo
- ThetaEvolve (C=1.503133): Possibly in Cell 91 (~50000 elements), unverified

**Critical next step:** Warm-start gradient descent (smooth-max annealing) from
the 1.5032 array. The function has qualitatively different structure from our
gradient-descent solutions: dense region at start (~25 elements), sparse gap,
then complex multi-peaked structure with near-zero valleys. Our optimizer may
find further improvements from this starting point that it cannot reach from
random initialization.

**Important correction:** The "Boyer et al. coarse-SA-at-N=23" previously
attributed to AlphaEvolve is actually from a different paper. AlphaEvolve used
LP-guided gradient + SA memetic algorithm, not coarse-grid SA.


### [active] idea_015

---
type: idea
id: idea_015
name: "DCT-domain perturbation for basin escape"
lifecycle: active
confidence: 0.2
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: [gen003_exploit_1_sol02]
related_ideas: [idea_007, idea_008]
cluster: cluster_001
tags: [perturbation, DCT, basin-escape, frequency-domain]
---

Perturb the raw parameters in DCT (Discrete Cosine Transform) space to explore
neighboring basins while preserving the overall solution structure. Work in
raw-param space (pre-softplus) to avoid non-negativity issues.

**Gen 3 evidence: NEGATIVE.**
- exploit_1/sol02: 10 perturbation configs with n_modes in {10,15,20,25} and
  scale in {0.05-0.18}. ALL 10 seeds converged back to C = 1.5091 (variation
  only 0.000028). A perturbation raising C from 1.509 to 1.83 still converges
  back to the same basin floor.

**Technical notes:**
- Perturbing in f-space (not raw-param space) causes NaN: clipped near-zero
  regions create near-zero integrals leading to division by zero in smooth_c.
- The raw-param space perturbation is numerically clean but ineffective.

**Conclusion:** The ~1.509 basin is remarkably deep. DCT perturbation at any
tested scale cannot escape it. The basin's attractor radius extends to at least
18% perturbation magnitude. This strongly suggests qualitatively different
methods (not just perturbation-based) are needed to find better basins.


### [active] idea_016

---
type: idea
id: idea_016
name: "LP-guided memetic algorithm (AlphaEvolve approach)"
lifecycle: active
confidence: 0.7
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen003_research_1_sol01]
contradicted_by: []
related_ideas: [idea_014, idea_001, idea_006]
cluster: cluster_003
tags: [LP, memetic, alphaevolve, hybrid, simulated-annealing]
---

AlphaEvolve's actual algorithm is a hybrid memetic approach combining:
1. LP-guided gradient direction (solve_convolution_lp for descent directions)
2. Cubic backtracking line search with momentum
3. Simulated annealing perturbations with sine-map pseudo-random generator
4. Temperature cooling tied to remaining runtime

This is NOT coarse-grid SA (that was Boyer et al., a different paper). The
AlphaEvolve method works at the full resolution and uses LP to find descent
directions that the standard gradient may miss.

**Evidence:** The 1319-element solution (C=1.5032) has qualitatively different
structure from our gradient-descent solutions: dense non-zero region in first
~25 elements, large sparse gap (near-zero for ~100 elements), then complex
multi-peaked structure with many near-zero valleys. This suggests the LP-guided
approach navigates a fundamentally different part of the solution space than
Adam + smooth-max.

**Implication:** Our pure gradient descent pipeline may be structurally limited
to the ~1.509 basin neighborhood. Reaching 1.503-level scores may require
either (a) warm-starting from published solutions (idea_014) or (b)
implementing elements of the LP-guided approach.

**Not yet implemented.** The LP component requires formulating and solving a
linear program at each step, which is a significant implementation effort.


### [debunked] idea_010

---
type: idea
id: idea_010
name: "L-BFGS-B fine-tuning after first-order optimization"
lifecycle: debunked
confidence: 0.1
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol05]
contradicted_by: [gen001_explore_1_sol03, gen001_full_1_sol02, gen002_exploit_1_sol01, gen002_exploit_1_sol02, gen003_exploit_1_sol01]
related_ideas: [idea_001, idea_009, idea_007]
cluster: cluster_001
tags: [L-BFGS, second-order, fine-tuning, scipy, debunked]
---

After Adam converges, switch to scipy L-BFGS-B for second-order fine-tuning.

**DEBUNKED after 3 generations of negative evidence:**
- Gen 1: Only positive evidence was explore_1/sol05 (multi-seed context, L-BFGS contribution unclear).
- Gen 1: pure L-BFGS alone: C=1.6887.
- Gen 2: L-BFGS after smooth-max: zero effect (2 trials).
- Gen 3: exploit_1/sol01 extended polish including L-BFGS: no improvement.

L-BFGS has zero effect after smooth-max convergence and is actively harmful
as the sole optimizer. The smooth-max gradient provides sufficient information
for Adam to fully converge within its basin. L-BFGS cannot help escape the
basin, and within the basin Adam has already found the floor.

Confidence lowered to 0.1. Should not be used in future solutions.


### [disputed] idea_002

---
type: idea
id: idea_002
name: "Higher resolution discretization"
lifecycle: disputed
confidence: 0.3
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 0
supported_by: []
contradicted_by: [gen001_full_1_sol04, gen001_explore_1_sol06, gen001_explore_1_sol01]
related_ideas: [idea_004]
cluster: cluster_002
tags: [resolution, discretization, N]
---

Increase the number of grid points N beyond the baseline 600. More points
give a finer representation of the function shape, potentially finding
better optima. Trade-off: slower computation per iteration.

**Gen 1 evidence is negative:**
- full_1/sol04 (N=800, same approach as best sol03): 1.5151 vs sol03's 1.5108 at N=600.
- explore_1/sol01 (N=800): 1.5207 vs baseline 1.5185.
- explore_1/sol06 upsampled to N=1500: 1.5183, not better.
- explore_2/sol08 (N=1000, Lion+Adam): 1.5207, same as N=800 result.

Higher N means slower steps and fewer iterations in fixed time, leading to
worse convergence. N=600 appears sufficient for the current score range.
Higher N may help when scores approach 1.503 and fine structure matters,
but it is counterproductive at the current optimization quality level.


### [established] idea_001

---
type: idea
id: idea_001
name: "Gradient descent with JAX"
lifecycle: established
confidence: 0.8
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol03, gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_full_1_sol03, gen001_explore_2_sol09]
contradicted_by: []
related_ideas: [idea_005, idea_007]
cluster: cluster_001
tags: [optimization, gradient, adam, lion]
---

Use JAX + optax for differentiable optimization of the C constant directly.
The baseline uses Adam with cosine schedule. Generation 1 confirmed that Adam
is the workhorse optimizer: all top-5 solutions use Adam (some with Lion warmup).

Key findings from gen 1:
- Adam alone with 40k steps converges to C ~ 1.5185 (baseline basin).
- Longer runs (80k steps) give marginal improvement (1.5182).
- Lion optimizer as warmup before Adam (explore_2/sol09) matches baseline at 1.5182.
- The real gains come from combining Adam with other ideas (smooth-max, multi-seed).
- L-BFGS-B alone performs poorly (full_1/sol02: 1.6887) due to non-smooth landscape,
  but works well as a fine-tuning step after Adam (explore_1/sol05: 1.5155).


### [established] idea_004

---
type: idea
id: idea_004
name: "Multi-scale optimization (coarse-to-fine)"
lifecycle: established
confidence: 0.75
first_seen: generation_0
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen002_explore_1_sol03, gen002_explore_1_sol02, gen003_explore_2_sol01, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: [gen001_explore_1_sol02, gen001_explore_2_sol05, gen002_explore_1_sol01, gen003_explore_1_sol01, gen003_explore_1_sol02, gen003_explore_1_sol03]
related_ideas: [idea_002, idea_007, idea_013]
cluster: cluster_002
tags: [multi-scale, coarse-to-fine, upsampling]
---

Start with low resolution (small N), optimize, then upsample and refine at
higher resolution. Coarse optimization finds the right general shape; fine
optimization tunes it. The WARM fine stage (re-annealing from T=0.05 after
upsample) is essential — cold fine stage is a confirmed dead end.

**Promoted to established** based on gen 2-3 evidence across multiple agents.

**Gen 3 findings:**
- 2-stage (N=80->600) continues to work: explore_2/sol01 (arcsine init): C=1.5090.
- 3-stage (N=80->200->600) does NOT improve over 2-stage (explore_2/sol03: 1.5091).
- **SA at coarse scale FAILED** (explore_1): N=40 SA (1.5148), N=80 SA (1.5155), N=30 SA (1.5169). All worse than simple multi-seed coarse-to-fine without SA.

**SA failure analysis:**
- Metropolis temperature was poorly calibrated (acceptance 60-100%, not selective enough).
- sigma grew uncontrollably with raw_params magnitude.
- Warm inner optimizer (T=0.05) defeats SA purpose — converges back to same basin.
- A cold inner optimizer might work better for SA basin-hopping, but this has not been tested.
- N=40 is confirmed too coarse for quality upsampling to N=600.

**Optimal recipe:** N=80 coarse, warm smooth-max, upsample to N=600, warm fine
stage (T=0.05). 8-12 seeds. Best: C=1.5090-1.5091.

**Temperature schedule:** 5-phase [0.05, 0.01, 0.003, 0.001, 0.0003] at both
coarse and fine stages. Extended phases (T=0.0001, 

[TRUNCATED — read full file for details]


### [established] idea_007

---
type: idea
id: idea_007
name: "Graduated smooth-max (log-sum-exp temperature annealing)"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_full_1_sol03, gen001_full_1_sol04, gen002_explore_1_sol03, gen002_explore_1_sol02, gen002_exploit_1_sol01, gen003_explore_2_sol01, gen003_exploit_1_sol01, gen003_exploit_1_sol02]
contradicted_by: []
related_ideas: [idea_001, idea_005, idea_004]
cluster: cluster_001
tags: [smooth-max, log-sum-exp, temperature, annealing, gradient]
---

Replace jnp.max in the objective with a log-sum-exp soft maximum, annealing
the temperature from warm (T=0.05) to cold (T=0.0003) over training.

**Status:** Most impactful technique across all 3 generations. Confidence 0.95.
No solution has broken below 1.5155 without smooth-max. With it, 1.5090.

**Gen 3 confirmation:**
- exploit_1/sol01 (extended to T=0.00003): C improved from 1.5094 to 1.5093 — only 0.000025.
- exploit_1/sol02 (DCT perturbation + re-optimization): All 10 seeds converge to 1.5091.
- explore_2/sol01 (arcsine init + smooth-max): C=1.5090 — the technique remains essential.

**Temperature schedule finalized:** 5-phase [0.05, 0.01, 0.003, 0.001, 0.0003]
with 15k steps per phase is the proven optimum. Extended phases (T=0.0001,
T=0.00003) provide negligible benefit (gen 2 + gen 3 confirmation). Ultra-low
temperature polish is now a confirmed dead end.

**Important limitation:** Smooth-max + Adam can reach C~1.509 but appears to
have a hard floor there. The AlphaEvolve solution (C=1.5032) uses a fundamentally
different algorithm (LP-guided memetic), suggesting smooth-max gradient descent
cannot break below ~1.509 from random initialization.


### [established] idea_008

---
type: idea
id: idea_008
name: "Multi-seed restart with diverse initializations"
lifecycle: established
confidence: 0.8
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_explore_1_sol05, gen001_explore_1_sol07, gen001_full_1_sol03, gen001_full_1_sol04, gen001_explore_2_sol09, gen002_explore_1_sol03, gen002_explore_1_sol02, gen003_explore_2_sol03, gen003_explore_2_sol04]
contradicted_by: []
related_ideas: [idea_003, idea_001, idea_013]
cluster: cluster_001
tags: [multi-seed, restart, diversity, initialization]
---

Run multiple optimization trajectories from different random seeds and/or
different initialization shapes, then keep the best result. The problem
landscape has many local minima with meaningfully different C values.

**Evidence (gens 1-3):**
- Gen 1: 8 seeds is the sweet spot. 32 seeds didn't beat 8 seeds. Diversity
  of initialization shape matters more than count.
- Gen 2: 12 restarts at coarse scale (N=80) + warm fine → 1.5091 (best at time).
- Gen 3: 25-seed funnel showed arcsine inits dominate all top-5 coarse slots.
  exploit_1 found only 25% of seeds (1 of 4) reach the ~1.509 basin — more
  seeds increase reliability of finding this basin, not finding better ones.

**Key findings:**
- 4-8 seeds is the sweet spot for cost/benefit.
- Diversity of initialization shape matters more than number of seeds.
- Multi-seed combines multiplicatively with smooth-max.
- The ~1.509 basin is hard to find (25% hit rate) but once found, inescapable.


### [established] idea_012

---
type: idea
id: idea_012
name: "Asymmetry exploitation"
lifecycle: established
confidence: 0.9
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 3
supported_by: [gen001_explore_2_sol09, gen001_explore_1_sol05, gen001_full_1_sol03, gen003_explore_2_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_006, idea_013]
cluster: cluster_002
tags: [asymmetry, symmetry-breaking, mathematical]
---

The optimal function for this problem is strongly asymmetric. Symmetric functions
satisfy C >= 2 (proven via Cauchy-Schwarz), so any competitive solution must
break symmetry.

**Evidence:**
- explore_2 discovered and proved that C >= 2 for all symmetric functions on
  [-1/4, 1/4]. This is a hard mathematical barrier.
- The baseline's flat+noise initialization breaks symmetry via noise — this is
  why it converges to C ~ 1.518 rather than C >= 2.
- Gaussian initialization (centered, symmetric) gave C = 1.5207 (worse), confirming
  that symmetric starts are suboptimal.
- Hann window (symmetric): C = 3.0.

**Gen 3 update:** Arcsine init on biased subinterval (idea_013) is intrinsically
asymmetric and dominates other init families. The AlphaEvolve solution (C=1.5032)
is strongly asymmetric with mass concentrated at one end of the domain.

**Implication:** Initializations should be deliberately asymmetric or at minimum
include sufficient noise to break symmetry quickly.


## All Clusters


### cluster_001

---
type: cluster
id: cluster_001
name: "Optimization algorithms and techniques"
member_ideas: [idea_001, idea_005, idea_007, idea_008, idea_009, idea_010, idea_011, idea_015]
best_score: 1.5090
best_solution: gen003_explore_2_sol01
status: active
last_updated: generation_3
---

This cluster groups all ideas related to HOW the optimization is performed:
which optimizer (Adam, Lion, L-BFGS), what objective modification (smooth-max),
what reparameterization (softplus), and what search strategy (multi-seed restart,
DCT perturbation).

**Gen 3 update:**
- idea_010 (L-BFGS) DEBUNKED: zero effect in all gen 3 tests. Confidence 0.1.
- idea_015 (DCT perturbation) added: 10 perturbation configs all return to same 1.509 basin. Shows basin depth but not useful for escaping.
- Best score marginally improved: 1.5091 -> 1.5090 via arcsine init (explore_2/sol01).
- Ultra-low temperature polish confirmed useless (0.000025 improvement).

**The cluster is approaching exhaustion for our gradient pipeline.** All tested
optimization variations converge to the ~1.509 basin. The only path to C < 1.505
within this cluster would be a fundamentally different optimizer (LP-guided, etc.).

**Unexplored within this cluster:**
- Warm-start smooth-max from published 1.5032 solution (idea_014, cluster_003)
- Lion warmup + coarse-to-fine (still untested)
- Coordinate descent on best solution


### cluster_002

---
type: cluster
id: cluster_002
name: "Problem representation and initialization"
member_ideas: [idea_002, idea_003, idea_004, idea_006, idea_012, idea_013]
best_score: 1.5090
best_solution: gen003_explore_2_sol01
status: active
last_updated: generation_3
---

This cluster groups ideas related to WHAT is optimized: discretization resolution,
starting function shape, multi-scale strategy, analytical/mathematical insights,
asymmetry, and initialization family.

**Gen 3 update:**
- idea_004 (coarse-to-fine) promoted to ESTABLISHED. Continues to power all best results.
- idea_013 (arcsine init) added: dominates other init families at coarse scale, marginal improvement (1.5090 vs 1.5091).
- Coarse-scale SA FAILED: explore_1 tried N=30, N=40, N=80 SA, all worse than simple coarse-to-fine (1.5148-1.5169 vs 1.5090-1.5091).
- 3-stage pipeline (N=80->200->600) does NOT improve over 2-stage (N=80->600).
- Step function init is a dead end (1.519-1.522).

**Cluster is near-exhausted for finding new basins.** All init families converge
to the same ~1.509 attractor. The AlphaEvolve solution (1.5032, cluster_003)
has fundamentally different structure (sparse, multi-peaked) that suggests our
representation approach may be limited.

**Remaining opportunities:**
- Properly calibrated coarse-SA (20-40% acceptance, cold inner optimizer) — previous
  attempts had 96-100% acceptance due to metro_T miscalibration.
- Arcsine + Gaussian composite init (untested).


### cluster_003

---
type: cluster
id: cluster_003
name: "Published solutions and warm-start approaches"
member_ideas: [idea_014, idea_016]
best_score: 1.5032
best_solution: gen003_research_1_sol01
status: active
last_updated: generation_3
---

NEW CLUSTER for generation 3. Groups ideas related to leveraging published
solutions and alternative algorithms from the literature.

**Members:**
- idea_014 (warm-start from published solutions): AlphaEvolve array at C=1.5032 retrieved. Multiple intermediate arrays available (C=1.5053 to 1.5032).
- idea_016 (LP-guided memetic algorithm): AlphaEvolve's actual method. Not yet implemented but understood.

**This cluster represents the new frontier.** The gradient-descent pipeline
(clusters 1+2) has plateaued at C~1.509. The only path to C < 1.505 is either:
1. Warm-starting from 1.5032 and polishing with smooth-max → may reach C < 1.503
2. Implementing the LP-guided approach → significant engineering effort
3. Finding the Yuksekgonul et al. (2026) array at C <= 1.5029

**Priority experiments:**
1. Warm-start smooth-max from sol01.py (C=1.5032): tighter schedule, 30k steps/phase
2. Verify Cell 91 array (~50000 elements) — may be ThetaEvolve's 1.503133
3. Search for Yuksekgonul 2026 paper and array


## All Patterns


### [active] pattern_003

---
type: pattern
id: pattern_003
name: "Diminishing returns from more optimizer steps"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol04, gen001_explore_2_sol09]
related_ideas: [idea_001, idea_007]
tags: [convergence, diminishing-returns, steps]
---

Doubling or tripling the number of Adam steps yields only marginal improvements
when using the standard (true max) objective:
- 40k steps: C = 1.5185 (baseline)
- 80k steps: C = 1.5182 (explore_1/sol04)
- 120k steps (Lion+Adam): C = 1.5182 (explore_2/sol09)

The optimizer converges to a local minimum by ~40k steps and additional
steps only provide negligible refinement. This contrasts with the smooth-max
approach (idea_007), which changes the landscape itself to enable continued
progress.

This pattern suggests that algorithmic changes (smooth-max, better initialization
strategy) are more valuable than more compute on the same algorithm.


### [active] pattern_004

---
type: pattern
id: pattern_004
name: "N=600 outperforms higher N at current optimization quality"
lifecycle: active
confidence: 0.65
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_full_1_sol03, gen001_full_1_sol04, gen001_explore_1_sol01]
related_ideas: [idea_002]
tags: [resolution, N, performance]
---

At the current optimization level, N=600 produces better scores than N=800
or N=1000, because fewer parameters means faster iterations and more
exploration in fixed wall-clock time.

- N=600, smooth-max, 8 seeds: C = 1.5108 (best)
- N=800, smooth-max, 12 seeds: C = 1.5151
- N=800, standard, 3 seeds: C = 1.5207
- N=1000, standard, 4 seeds: C = 1.5182

This pattern may reverse when optimization quality improves sufficiently
that fine-scale structure matters (approaching C ~ 1.503).


### [active] pattern_005

---
type: pattern
id: pattern_005
name: "The 1.509x basin is extremely deep — perturbation cannot escape it"
lifecycle: active
confidence: 0.85
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_exploit_1_sol02, gen003_exploit_1_sol01, gen003_explore_1_sol01, gen003_explore_1_sol02]
related_ideas: [idea_007, idea_008, idea_015]
tags: [basin, attractor, perturbation, convergence, depth]
---

The ~1.509 basin reached by smooth-max + Adam is extremely deep. Evidence from
gen 3:

1. **DCT perturbation:** 10 configs with scales 5%-18% all converge back to
   C = 1.5091 +/- 0.000028. Even perturbations raising C to 1.83 (36% worse)
   converge back to the same basin floor.

2. **Extended low-temp polish:** T=0.00003 with 45k steps yields only 0.000025
   improvement (1.50936 -> 1.50933). The basin floor is effectively flat.

3. **Coarse-scale SA:** All 3 SA solutions (N=30-80) converge to worse scores
   (1.5148-1.5169), suggesting SA perturbations at coarse scale don't fi

[TRUNCATED — read full file for details]


### [active] pattern_006

---
type: pattern
id: pattern_006
name: "Arcsine initialization dominates other families at coarse scale"
lifecycle: active
confidence: 0.6
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_explore_2_sol01, gen003_explore_2_sol04]
related_ideas: [idea_013, idea_003, idea_012]
tags: [initialization, arcsine, comparison, coarse]
---

In head-to-head comparison across initialization families at coarse scale (N=80):
- Arcsine (U-shaped, endpoint-concentrated): Best, occupies all top-5 slots in 25-seed funnel
- Gaussian bumps: Second best, familiar ~1.5091 territory
- Comb (narrow peaks): Mediocre
- Step function: Dead end (1.519-1.522)

The arcsine profile (peaks at interval endpoints) on a biased subinterval
consistently outperforms bell-shaped initializations. However, the final fine
scores differ by only ~0.0001 (arcsine: 1.5090, Gaussian: 1.5091), suggesting
all families converge to the same attractor basin. Arcsine may find this basin
more reliably rather than find

[TRUNCATED — read full file for details]


### [confirmed] pattern_001

---
type: pattern
id: pattern_001
name: "The 1.5185 attractor basin"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol04, gen001_full_1_sol01, gen001_explore_2_sol09, gen001_explore_1_sol06, gen001_explore_1_sol03]
related_ideas: [idea_001, idea_007]
tags: [convergence, local-minimum, basin]
---

Standard Adam optimization (any initialization, any step count 40k-120k) converges
to C ~ 1.5182-1.5189. This is a very wide attractor basin that captures most
optimization trajectories.

Evidence: 5+ solutions across 3 agents all converge to this narrow range:
- baseline: 1.5185
- explore_1/sol04 (80k Adam): 1.5182
- full_1/sol01 (N=1000, 3 restarts): 1.5185
- explore_2/sol09 (Lion+Adam, 4 seeds): 1.5182
- explore_1/sol06 (16 seeds refined): 1.5183

Only the smooth-max technique (idea_007) reliably breaks below this basin.
Multi-seed without smooth-max can reach 1.5155 but not much lower.


### [confirmed] pattern_002

---
type: pattern
id: pattern_002
name: "Symmetric initializations converge to worse minima"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_1_sol01, gen001_explore_2_sol01, gen001_explore_2_sol07]
related_ideas: [idea_003, idea_012]
tags: [symmetry, initialization, convergence]
---

Solutions initialized with symmetric functions (centered Gaussian, Hann window,
centered raised cosine) consistently score worse than flat+noise or asymmetric
initializations.

- Hann window: C = 3.0 (catastrophic)
- Centered Gaussian (N=800): C = 1.5207 (worse than baseline 1.5185)
- Gaussian mixture K=8: C = 1.5801

This is explained by the mathematical fact that C >= 2 for symmetric functions.
Symmetric initializations must first break symmetry through gradient noise before
making progress, wasting optimization budget.
