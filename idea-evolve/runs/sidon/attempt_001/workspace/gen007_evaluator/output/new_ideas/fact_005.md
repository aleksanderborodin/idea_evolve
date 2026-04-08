---
id: fact_005
type: fact
name: "Naive Ruzsa-Lindström is NOT valid Sidon in integer arithmetic"
confidence: 1.0
first_seen: generation_7
verified: true
source: "gen007_explore_1 — computational verification for p=61,67,71,73"
tags: [ruzsa, construction, correctness, integer-arithmetic]
---

The formula S = {x*p + gˣ mod p : x ∈ {0,...,p-1}} (where g is a primitive root mod p)
does NOT produce a valid Sidon set in the integers. For p=71, it produces a set with
264 violations (repeated pairwise sums).

**Root cause:** Integer arithmetic causes carry-induced sum collisions. When x₁*p + gˣ¹ mod p
+ x₂*p + gˣ² mod p involves modular residues that sum past p, the carry propagates into
the high-order term, creating unintended sum equalities.

**Correct formula:** S = {x*2p + gˣ mod p : x ∈ {0,...,p-1}}. The 2p spacing ensures
high-part increments (2p) exceed max low-part variation (p-1), preventing carries. This IS
a valid Sidon set, verified computationally for p=61, 67, 71, 73.

**Implication:** Any agent implementing Ruzsa-Lindström MUST use the 2p-scaled version.
The original idea_025 formula was incorrect for integer arithmetic.
