---
type: idea
id: idea_010
name: "L-BFGS-B fine-tuning after first-order optimization"
lifecycle: active
confidence: 0.25
first_seen: generation_1
last_updated: generation_2
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol05]
contradicted_by: [gen001_explore_1_sol03, gen001_full_1_sol02, gen002_exploit_1_sol01, gen002_exploit_1_sol02]
related_ideas: [idea_001, idea_009, idea_007]
cluster: cluster_001
tags: [L-BFGS, second-order, fine-tuning, scipy]
---

After Adam converges, switch to scipy L-BFGS-B with bounds=[0, None] for
second-order fine-tuning. L-BFGS-B uses curvature information to converge
faster near a local minimum.

**Evidence is now mostly negative:**
- Gen 1 explore_1/sol05 (Adam + L-BFGS, no smooth-max): C = 1.5155 — only
  positive evidence, but L-BFGS contribution vs multi-seed unclear.
- Gen 1 explore_1/sol03 (Adam 30k + L-BFGS): C = 1.5189 — no benefit.
- Gen 1 full_1/sol02 (pure L-BFGS): C = 1.6887 — much worse alone.
- **Gen 2 exploit_1/sol01 (L-BFGS on true max after smooth-max): zero effect.**
- **Gen 2 exploit_1/sol02 (L-BFGS on smooth obj T=1e-5): zero effect.**
- Gen 2 explore_2/sol03 (L-BFGS as SA inner optimizer): no improvement.

**Conclusion:** L-BFGS has zero effect after smooth-max convergence. The
smooth-max already provides sufficient gradient information for Adam to fully
converge within its basin. L-BFGS may still have marginal value WITHOUT
smooth-max, but that's a less interesting regime.

Confidence lowered to 0.25 based on strong gen 2 negative evidence.
