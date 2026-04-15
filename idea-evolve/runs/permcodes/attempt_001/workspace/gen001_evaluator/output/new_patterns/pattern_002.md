---
type: pattern
id: pattern_002
name: "AGL(1,8) Orbit Size is 56, Not 168"
lifecycle: confirmed
confidence: 1.0
first_seen: gen001
last_updated: gen001
evidence: [architect_report_gen001]
related_ideas: [idea_002]
tags: [algebraic, orbits, math-error]
---

The architect's initial reasoning stated 11 orbits × 168 = 1848, but the actual AGL(1,8) orbit size is 56 (not 168). The Smith-Montemanni result of 616 = 11 × 56. This is a critical correction for calculating theoretical bounds and understanding why AGL(1,8) max clique gives exactly 616.

This matters for: (1) understanding why 616 is the AGL(1,8) maximum, (2) calculating how close we are to the 926 upper bound, (3) designing partial orbit mixing strategies.
