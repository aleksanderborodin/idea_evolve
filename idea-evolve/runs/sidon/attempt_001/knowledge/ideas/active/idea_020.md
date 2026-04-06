---
type: idea
id: idea_020
name: "Rokicki-Dogon Near-Optimal Golomb Rulers"
lifecycle: active
confidence: 0.5
first_seen: generation_4
last_updated: generation_4
last_confirmed_gen: 4
supported_by: []
contradicted_by: []
related_ideas: [idea_006, idea_008]
cluster: cluster_001
tags: [literature, golomb-rulers, construction, high-priority, untested]
---

The Rokicki-Dogon "Possibly Optimal Golomb Rulers" database (cube20.org/golomb) contains
near-optimal Golomb ruler constructions (equivalent to Sidon sets) for various mark counts
and spans. Research_1 (gen 4) discovered that:

- 104-mark rulers with span ≤ 10000 exist in the database (type=pp, q=103)
- 105-mark rulers with span ≤ 10000 may also exist

A Golomb ruler is exactly a Sidon set (all pairwise differences distinct). If a 105-mark
ruler with span ≤ 10000 exists in the database, it directly gives fitness=105.

**Current gap**: Research_1 found the database entries (mark counts, spans, types) but NOT
the actual integer sequences. The mark lists are in a downloadable zip file
(cube20.org/golomb-all-00.zip) that was not fetched.

**CRITICAL ACTION**: Download and parse the Rokicki-Dogon zip file to extract the actual
104-mark and 105-mark ruler sequences for spans ≤ 10000. This is likely the single
highest-value action available — it could immediately yield fitness=104 or 105 without
any search or computation.

**Caveat**: Research_1 noted that Singer q=103 raw construction has minimum span 10290 > 10000.
The Rokicki-Dogon database may use Singer as a SEED and apply further search to minimize span.
The raw database entry for "type=pp, q=103" might not directly give a 104-element set fitting
in {0,...,10000}. The actual mark lists must be verified.

**Confidence note (gen 4 consistency review)**: Downgraded from 0.7 to 0.5. The database
was found but mark lists were never downloaded or verified. Zero supporting solutions.
The claim that 104-105 mark sets exist for span<=10000 is plausible but unconfirmed.

**Priority**: HIGHEST. If the constructive lower bound is 105 (not 102), the pipeline is
3 elements behind the state of the art.
