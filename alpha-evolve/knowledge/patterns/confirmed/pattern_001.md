---
type: pattern
id: pattern_001
name: "Symmetric unimodal functions yield C ~ 2.0"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [gen001_explore_2_sol01, gen001_explore_2_sol02, gen001_full_1_sol01]
related_ideas: [idea_009, idea_011]
tags: [symmetry, unimodal, failure-mode]
---

Any even-symmetric, unimodal (single-bump) function f gives C ~ 2.0 because the
autoconvolution f*f peaks at t=0, and for even unimodal f, f*f(0) = integral(f^2) >= 2*(integral f)^2
by Cauchy-Schwarz on the half-domain support.

Confirmed by three independent solutions:
- explore_2/sol01: symmetric truncated Gaussian, C = 2.000046
- explore_2/sol02: symmetry-enforced free-form (converges to unimodal), C = 2.000000
- full_1/sol01: symmetry + relu projection, C = 2.000000

This is a DEAD END. Future agents must avoid symmetric unimodal initialization.
To benefit from symmetry enforcement, one must use multi-bump (bimodal+) initialization
so that the autoconvolution peak shifts away from t=0.
