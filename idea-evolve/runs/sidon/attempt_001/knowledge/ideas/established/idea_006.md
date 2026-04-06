---
type: idea
id: idea_006
name: "Singer Difference Set Construction"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_4
last_confirmed_gen: 4
supported_by: [gen001_explore_1_sol01, gen001_explore_1_sol02, gen001_explore_1_sol03, gen001_explore_1_sol04, gen004_research_1_sol01]
contradicted_by: []
related_ideas: [idea_003, idea_004, idea_007, idea_008, idea_009]
cluster: cluster_001
tags: [algebraic, singer, construction, high-impact]
---

The Singer difference set is the dominant algebraic construction for Sidon sets. For a prime
power q, the Singer (q^2+q+1, q+1, 1)-difference set gives exactly q+1 elements in
{0, ..., q^2+q} with ALL pairwise differences distinct — a perfect Sidon set.

**For q=97**: The construction yields 98 elements in {0, ..., 9506}, all within {0, ..., 10000}.
This is a jump of +32 over the greedy baseline of 66. Implementation uses GF(97^3) arithmetic:
find an irreducible cubic over GF(97), compute a primitive element, then collect indices k
where the k-th power has zero third component (or equivalently, zero trace). Alternatively,
use the m-sequence recurrence method: find a primitive polynomial x^3 - a_1*x^2 - a_2*x - a_3 over
GF(97), run the linear recurrence, and collect zero indices.

**Evidence**: explore_1/sol01 implemented this and scored 98 (is_valid=1, violations=0) in
0.02 seconds. The construction is deterministic and fast. All four explore_1 solutions used
Singer as their foundation. Gen 4 research_1 confirmed Singer q=103 also works but keeps
only 102 elements in range (min span 10290 > 10000).

**Critical implementation note**: Must use the PRIMITIVE element of GF(q^3)*, not a subgroup
element. Using a subgroup element (e.g., g^96 instead of g) produced 84 elements with 1540
violations. This is a subtle but important distinction not clearly stated in standard references.

**Saturation property**: The Singer set for q=97 uses ALL 9506 positive differences exactly once.
This means the set is maximally "full" — no element can be added without creating a collision.
Extension beyond 98 requires removing elements to free differences first.
