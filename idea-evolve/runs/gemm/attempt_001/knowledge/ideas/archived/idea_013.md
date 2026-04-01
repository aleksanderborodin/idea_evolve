---
type: idea
id: idea_013
name: "No-Packing Direct Kernel"
lifecycle: archived
confidence: 0.3
first_seen: generation_1
last_updated: generation_3
last_confirmed_gen: 2
supported_by: [gen002/explore_2/sol04]
contradicted_by: [gen002/explore_2/sol01, gen002/explore_2/sol02, gen002/explore_2/sol03]
related_ideas: [idea_007, idea_005, idea_014]
cluster: cluster_002
tags: [packing, direct-access, no-pack, cache, archived]
---

Skip B packing entirely and read B directly from its original layout.

**Archived in gen003.** This idea has been superseded by the row-streaming
architecture (idea_014), which achieves the same no-packing benefit but with
a cleaner loop structure and better results. idea_014 was promoted to established
in gen003 with 141.0 µs best score.

The no-packing direct kernel as a standalone BLIS variant (idea_013) peaked at
182.31 µs (gen002) and has not been tested or improved since. With the shift to
row-streaming, further investment in BLIS no-pack variants is unlikely to yield
new insights.

Historical value preserved: the gen002 observation that B fits in L2 for all
sizes (max 448 KB < 1.25 MB L2) is incorporated into idea_014's understanding.
