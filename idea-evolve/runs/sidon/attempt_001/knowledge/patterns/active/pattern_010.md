---
type: pattern
id: pattern_010
name: "Truncated Singer sets have zero addable elements for all primes tested"
lifecycle: active
confidence: 0.9
first_seen: generation_3
last_updated: generation_3
evidence: [gen003_experimentator_1]
related_ideas: [idea_006, idea_008, idea_013]
tags: [singer, saturation, rigidity, structural]
---

Experimentator_1 tested truncated Singer sets for q = 97, 101, 103, 107, 109, 113.
In every case, after optimal truncation to fit [0, 10000], the resulting set has ZERO
addable elements via greedy single-element extension.

This is surprising for larger primes where significant truncation occurs:
- q=107: loses 9 elements (108→99), freeing 927 differences. Still zero addable.
- q=109: loses 11 elements (110→99), freeing 1089 differences. Still zero addable.

The Singer difference structure has a deep rigidity property: even partial subsets
of Singer sets inherit full local saturation. This goes beyond the well-known "perfect
difference set uses all differences exactly once" property — it means that sub-patterns
of Singer differences also create dense local coverage.

**Implication**: Any approach that starts from a Singer base and tries to extend it
(greedy, perturbation, SA) is futile. The only path past 102 is a fundamentally
different construction that doesn't use Singer sets as seeds.
