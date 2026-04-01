---
type: idea
id: idea_020
name: "Multi-Threading via pthreads (2 cores)"
lifecycle: active
confidence: 0.3
first_seen: generation_3
last_updated: generation_3
last_confirmed_gen: 3
supported_by: []
contradicted_by: []
related_ideas: [idea_006, idea_015]
cluster: cluster_002
tags: [multi-threading, pthreads, bandwidth, parallelism, cores]
---

Research_1 (gen003) identified that the cgexec cgroup contains cores 0 and 1.
A gemmCandidate implementation can spawn a second thread pinned to core 1 to
parallelize the computation. Each thread processes n/2 rows, writing to disjoint
C regions.

**Potential benefit:** Dual-channel DDR4 can serve 2 write streams, potentially
1.3-1.8x bandwidth improvement for large. Since large is memory-bandwidth-bound,
this directly addresses the bottleneck.

**Expected impact on large:** 3841 µs → ~2100-2950 µs (1.3-1.8x)
**Expected geomean impact:** ~105-130 µs (from 141 µs)

**Key uncertainties:**
1. Whether the cgexec cgroup allows 2 concurrent threads (cpuset vs cpu bandwidth limit)
2. Actual 2-thread bandwidth on this machine (unmeasured)
3. Thread creation/join overhead for small benchmarks (could worsen small from 3.36 µs)
4. Static thread pool vs per-call pthread_create tradeoff

**Implementation notes:**
- Use a static thread pool (create once, reuse) to avoid per-call pthread overhead
- Split rows evenly: thread 0 = rows [0, n/2), thread 1 = rows [n/2, n)
- Each thread uses NT stores (if aligned) for its slice
- Main thread does _mm_sfence() after join

Completely untested. Needs validation of cgroup constraints first.
