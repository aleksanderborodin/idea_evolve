---
id: fact_002
type: fact
name: "Theoretical Upper Bound"
confidence: 0.95
first_seen: generation_0
last_confirmed_gen: 6
verified: true
source: Carter-Hunter-O'Bryant, confirmed by research agents gen 2-6
tags: [upper-bound, theory]
---

For a Sidon set (B2 sequence) in {0, ..., N}, the maximum size is at most
sqrt(N) + O(N^{1/4}). For N=10000, this gives an upper bound of approximately
**109 elements** (not ~100-102 as originally stated).

**Correction history:** Original fact said "~100-102" which was incorrect. The
sqrt(10000) = 100 term is only the leading order; the O(N^{1/4}) ~ 10 term
pushes the bound to ~109. Corrected in gen 2 consistency review.

**NOTE**: This file replaces the STALE version in facts/fact_002.md which still
says "~100-102". The facts/ version must be overwritten with this corrected content.
