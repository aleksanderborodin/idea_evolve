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
