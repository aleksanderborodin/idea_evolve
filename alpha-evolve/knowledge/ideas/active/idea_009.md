---
type: idea
id: idea_009
name: "Symmetry enforcement"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: [gen001_explore_2_sol01, gen001_explore_2_sol02]
related_ideas: [idea_006]
cluster: cluster_002
tags: [symmetry, parameterization, constraint]
---

Enforce even symmetry f(x) = f(-x) by optimizing only on [0, 1/4] and mirroring. This halves
the parameter count and eliminates asymmetric local minima. Research_1 provides strong
theoretical motivation: the extremal function is almost certainly even-symmetric.

Gen 1 evidence is NEGATIVE but confounded:
- explore_2/sol01 (symmetric Gaussian, C=2.0000) and sol02 (symmetry-enforced free-form, C=2.0000)
  both scored C ~ 2.0. HOWEVER, these used symmetric initialization with a SINGLE centered bump,
  which is provably bad (for even unimodal functions, f*f peaks at t=0 and C >= 2).

The issue is NOT symmetry enforcement itself — it's that symmetry + unimodal init = bad basin.
Symmetry + TWO-BUMP init (which shifts the autoconvolution peak away from t=0) is the correct
combination and has NOT been tested. This is a high-priority experiment for gen 2.

full_1/sol01 also used symmetry + relu projection and scored C=2.0, confirming the same issue.
