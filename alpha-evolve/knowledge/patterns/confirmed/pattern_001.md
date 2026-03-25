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
