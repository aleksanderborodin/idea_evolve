---
type: idea
id: idea_001
name: "Gradient descent with JAX"
lifecycle: established
confidence: 0.8
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [gen001_explore_1_sol03, gen001_explore_1_sol04, gen001_explore_1_sol05, gen001_explore_1_sol06, gen001_explore_1_sol09, gen001_explore_1_sol11, gen001_explore_1_sol12]
contradicted_by: []
related_ideas: [idea_004, idea_007]
cluster: cluster_001
tags: [optimizer, adam, gradient]
---

JAX + optax Adam is the workhorse optimizer for this problem. Adam with cosine warmup schedule
consistently reaches C ~ 1.517-1.526 depending on initialization and resolution. It significantly
outperforms L-BFGS from cold start (which gets stuck at C ~ 1.69-1.81).

Gen 1 evidence: Every solution that scored below 1.53 used Adam as its primary optimizer.
Adam's adaptive learning rates handle the non-smooth max objective better than second-order
methods starting from scratch. The best learning rate appears to be 0.005 for coarse phases
and 0.002 for fine phases, with 2000-step warmups.

AdamW with weight decay was tried (explore_1/sol06) but showed no clear advantage over plain Adam.
The Lion optimizer (explore_1/sol07, C=1.5217) performed slightly worse than Adam variants.
