---
type: idea
id: idea_011
name: "Sidon-set and multi-bump initializations"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: []
related_ideas: [idea_006, idea_003, idea_009]
cluster: cluster_002
tags: [initialization, sidon, multi-bump, bimodal]
---

Initialize optimization with multi-bump functions inspired by Sidon set constructions from
additive combinatorics. Research_1 identified that:

1. Bimodal (two-bump) functions can achieve lower C than unimodal functions because they shift
   the autoconvolution peak away from t=0.
2. Sidon sets {0, 1, 3, 6} provide positions for Gaussian bumps that naturally produce flat
   autoconvolution.
3. Suggested initializations:
   - Two symmetric Gaussians at +/-0.15 (sigma ~0.04)
   - Sidon-inspired 4 bumps at x ~ {-0.25, -0.167, 0, 0.25}
   - Wide center + narrow wings

UNTESTED in gen 1. All successful solutions used flat-block or single-bump initialization and
converged to what appears to be a unimodal solution. Multi-bump initializations access
fundamentally different basins and could break below the current 1.5168 floor.

This is the HIGHEST PRIORITY untested idea for gen 2.
