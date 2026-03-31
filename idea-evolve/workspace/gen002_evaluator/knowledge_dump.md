# Pre-Concatenated Knowledge Dump


## All Ideas


### [active] idea_005

---
type: idea
id: idea_005
name: "Re-tune BLIS Tile Sizes for Tiger Lake"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol10]
contradicted_by: [explore_1/sol01, explore_1/sol06]
related_ideas: [idea_008]
cluster: cluster_002
tags: [tiling, NC, MC, cache, blis]
---

Current baseline: MC=64, KC=128, NC=256 (tuned for AVX2). With AVX-512 (64-byte
wide ops), NC should be re-evaluated for the larger register width and Tiger Lake
cache hierarchy (L1d=48KB, L2=1.25MB).

Gen001 evidence is mixed on NC specifically:
- NC=256 is used by the best solutions (explore_1/sol10: 148.18 µs, explore_1/sol07: 306.60 µs)
- NC=512 consistently regressed: explore_1/sol01 (654.75 µs), explore_1/sol06 (465.65 µs),
  full_1/sol04 uses NC=512 but achieves 167.23 µs (good but worse than NC=256 sol10)
- NC=256 appears optimal for the current 4×64 micro-kernel shape

The reason NC=512 hurts is not yet fully understood. Hypotheses from explore_1:
cache line conflicts, TLB pressure, B panel alignment issues. Research agent
calculated that even NC=65536 (entire m) would fit B in L2 for the large benchmark.
The bottleneck may be pack_B overhead or cache associativity conflicts, not capacity.

MC=64 is used by all successful solutions and appears appropriate. KC tiling is
irrelevant (see idea_008). NC tuning remains an open optimization opportunity.


### [active] idea_006

---
type: idea
id: idea_006
name: "Streaming Stores for Large m"
lifecycle: active
confidence: 0.5
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [full_1/sol02, full_1/sol04]
contradicted_by: []
related_ideas: [idea_010]
cluster: cluster_002
tags: [streaming-stores, non-temporal, memory-bandwidth, large-m]
---

For m=65536, each output row is 256KB — doesn't fit in L2. Use `_mm512_stream_si512`
to bypass cache on stores, freeing cache capacity for B data.

full_1/sol02 used streaming NT stores when C is 64-byte aligned and m >= 16384.
Score: 339.09 µs. However, the benefit is hard to isolate because sol02 also
introduced int8 accumulation simultaneously. full_1/sol04 (167.23 µs) includes
streaming stores as well but the dominant improvement was memset elimination.

The research agent estimated streaming stores save ~6% on the large benchmark by
eliminating read-for-ownership overhead (Finding 6). This is a modest but real gain,
primarily relevant for the large benchmark (32 MB output).

Note: streaming stores require 64-byte aligned C pointer and `_mm_sfence()` after.
C alignment is not guaranteed by the harness — full_1/sol04 checks alignment at
runtime and falls back to regular stores if unaligned. This is the correct approach.

Needs more isolated testing to quantify the standalone impact.


### [active] idea_011

---
type: idea
id: idea_011
name: "vpternlogd for Fused Boolean Logic"
lifecycle: active
confidence: 0.6
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol02, explore_1/sol10]
contradicted_by: []
related_ideas: [idea_001]
cluster: cluster_001
tags: [vpternlogd, ternary-logic, instruction-reduction, avx512]
---

`vpternlogd` computes any 3-input boolean function in one instruction using an
8-bit truth table. The core binary-ternary formula:
- `(a_pos | b) & (a_neg | ~b)` = `vpternlogd(a_pos, a_neg, b, 0xD8)` or `0xCA`
- `(a_pos | ~b) & (a_neg | b)` = `vpternlogd(a_pos, a_neg, b, 0xE4)` or `0xAC`

This replaces 6-7 bitwise instructions (including pre-computing ~b) with 2
ternary logic instructions per row per k-step. It also eliminates the need for
a dedicated `v_not_b` register, saving one register.

explore_1/sol02 used `_mm512_ternarylogic_epi64` with imm8 values 0xD8/0xE4 and
achieved 400.68 µs (1.92x vs baseline). explore_1/sol10 (148.18 µs, best solution)
also uses ternarylogic. Research Finding 7 confirmed the truth table derivation
and noted that vpternlogd runs on port 0, balancing load with popcnt (port 5).

Note: there is some uncertainty about the exact truth table values. explore_1
uses 0xD8/0xE4 while research derived 0xCA/0xAC. The exact value depends on
operand order in `_mm512_ternarylogic_epi64(a, b, c, imm8)`. Both produce
correct results as verified by evaluation. However, truth table verification
should be a priority to avoid subtle correctness bugs.

Active — well-supported but needs isolated benchmarking to quantify the standalone
improvement vs the old OR+AND approach.


### [active] idea_012

---
type: idea
id: idea_012
name: "Stack-Allocated Aligned Buffers (No malloc/TLS)"
lifecycle: active
confidence: 0.5
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol10]
contradicted_by: []
related_ideas: [idea_005]
cluster: cluster_002
tags: [allocation, stack, alignment, malloc, tls]
---

Use `alignas(64)` stack-allocated arrays for packed A and B buffers instead of
`_mm_malloc` or `thread_local` storage. For our problem's small k values, the
buffers are small enough to fit on the stack:
- A_packed: MC/4 × MAX_KB × 8 = 16 × 32 × 8 = 4096 bytes
- B_packed: NC/64 × MAX_KB × 64 = 4 × 32 × 64 = 8192 bytes

explore_1/sol10 used stack buffers and achieved 148.18 µs (best score), versus
sol09's 171.04 µs with thread_local buffers. The improvement is modest (~13%)
but consistent. Stack allocation avoids:
- `_mm_malloc`/`_mm_free` overhead per call (full_1/sol04 uses _mm_malloc)
- TLS indirection overhead (sol09's thread_local approach hurt small benchmark)
- Potential allocator contention in multi-threaded scenarios

The main limitation is stack size: 4096 + 8192 = 12 KB is fine, but larger NC
or MC values would exceed safe stack limits. This approach is specific to our
small k problem.


### [active] idea_013

---
type: idea
id: idea_013
name: "No-Packing Direct Kernel"
lifecycle: active
confidence: 0.3
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: []
related_ideas: [idea_007, idea_005]
cluster: cluster_002
tags: [packing, direct-access, no-pack, cache]
---

Skip B packing entirely and read B directly from its original layout. For small
benchmark (k_bytes=2, B = 2×1024 = 2 KB), B fits entirely in L1 without any
packing. For medium (k_bytes=4, B = 4×16384 = 64 KB), B fits in L2. Even for
large (k_bytes=7, B = 7×65536 = 448 KB), B fits in L2.

Since B is accessed as `B[k * m + j]`, reading 64 consecutive bytes at offset j
is a single cache line (or 2 cache lines). The stride between k-rows is m bytes,
which may cause TLB misses for large m. But with only 2-7 k-rows, this is at
most 7 TLB entries.

This idea was suggested by full_1 agent ("no-packing micro-kernel" experiment)
and research agent (Finding 5 notes B fits in L2). No solution attempted it in
gen001. The potential benefit is eliminating pack_B overhead entirely, which was
identified as a major bottleneck by explore_1 (bigger than micro-kernel itself
for medium/large).

Risk: strided access pattern may be less cache-friendly than packed sequential
access, especially for the large benchmark. Needs empirical testing.


### [debunked] idea_003

---
type: idea
id: idea_003
name: "VNNI for Accumulation"
lifecycle: debunked
confidence: 0.1
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 0
supported_by: []
contradicted_by: []
related_ideas: []
cluster: null
tags: [vnni, vpdpbusd, accumulation]
---

`_mm512_dpbusd_epi32` computes a dot product of int8 values and accumulates into
int32, all in one instruction (1 cycle throughput). The binary-ternary multiply
was hypothesized to be reformulatable as a VNNI operation.

Research agent (Finding 11) conclusively determined that VNNI does NOT apply to
bit-packed binary-ternary data. The ternary values {-1,0,+1} are stored as two
bit-planes (pos_bits, neg_bits), not as sign-magnitude integers. To use VNNI,
you'd need to decode bit-packed values back to integer form first (expand 8 bits
→ 8 × int8), and this decoding step costs more than the operation saves. The
popcount approach is inherently more efficient for bit-packed data.

No agent attempted a VNNI-based solution in gen001. Debunked based on theoretical
analysis — the data format mismatch is fundamental, not implementation-specific.


### [disputed] idea_002

---
type: idea
id: idea_002
name: "Fully Unrolled k-Loop"
lifecycle: disputed
confidence: 0.4
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol09]
contradicted_by: [full_1/sol03]
related_ideas: [idea_008]
cluster: cluster_001
tags: [unrolling, k-loop, template-specialization]
---

k_bytes is always 2, 4, or 7 for our benchmark sizes. Instead of a generic loop,
create specialized versions for each k value via template specialization or
`switch(k_bytes)` dispatch.

Evidence is mixed from generation 1. full_1/sol03 used template specialization
with `switch(k_bytes)` dispatch to create 6 kernel variants (3 k values × 2 store
modes). This caused I-cache pressure from code bloat and *regressed* performance
(442.43 µs vs 339.09 µs for sol02 without templates). Small case degraded from
11.61 → 20.04 µs specifically.

However, explore_1/sol09 used `#pragma GCC unroll` (a lighter approach) and
achieved 171.04 µs. explore_1/sol10 also uses `#pragma GCC unroll 7` in its
micro-kernel and achieved the best score (148.18 µs).

Conclusion: compiler-hint unrolling (`#pragma`) works; heavy template
specialization with multiple kernel copies hurts via I-cache pressure. The idea
is partially valid but the implementation approach matters critically.


### [disputed] idea_009

---
type: idea
id: idea_009
name: "Wider Micro-Kernel 8x64"
lifecycle: disputed
confidence: 0.4
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: []
contradicted_by: [explore_1/sol03]
related_ideas: [idea_001, idea_004]
cluster: cluster_001
tags: [micro-kernel, 8x64, register-pressure, avx512]
---

With 32 zmm registers (AVX-512), we can afford 8 rows × accumulators. Process 8
rows of A at once instead of 4, halving the number of micro-kernel calls.

explore_1/sol03 attempted an 8-row × 64-col micro-kernel and got 493.42 µs —
worse than the 4×64 sol02 (400.68 µs). The agent reported "register pressure
hurt it." With 8 rows of int16 accumulators (2 zmm each = 16 zmm) plus B data,
broadcast registers, and temporaries, register pressure forces spills to memory.

No solution in gen001 successfully improved performance with an 8-row kernel.
The 4-row kernel is consistently the best shape. However, the 8-row kernel has
not been tested with int8 accumulation (which uses 1 zmm per row instead of 2),
so the register budget might work with that approach.

Disputed: theoretically sound but practically failed in gen001. Needs further
experimentation with lighter accumulation strategies.


### [established] idea_001

---
type: idea
id: idea_001
name: "AVX-512 Micro-Kernel with Hardware Popcount"
lifecycle: established
confidence: 0.95
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol01, explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol01, full_1/sol02, full_1/sol03, full_1/sol04]
contradicted_by: []
related_ideas: [idea_002, idea_004, idea_007, idea_008, idea_009, idea_011]
cluster: cluster_001
tags: [avx512, micro-kernel, popcount, bitalg]
---

Replace the 6-instruction LUT-based popcount (`vpshufb` + masks) with a single
`_mm512_popcnt_epi8()` instruction (AVX512_BITALG). Process 64 bytes of B per
iteration instead of 32 (AVX2). Micro-kernel shape becomes 4x64 (4 rows of A,
64 columns of B).

This is the foundational optimization of generation 1. Every successful solution
uses it. The first solution to apply it (explore_1/sol01, 654.75 µs) already
improved over baseline on small sizes, though medium/large regressed due to
int32-in-hot-loop widening overhead. Once combined with int8/int16 accumulation
(idea_004) and other optimizations, the AVX-512 popcount kernel achieves up to
5.20x speedup (explore_1/sol10, 148.18 µs).

Evidence is overwhelming: all 14 valid solutions use this idea, and the best
(148.18 µs) is 5.20x faster than the AVX2 baseline (770 µs). Established with
high confidence.


### [established] idea_004

---
type: idea
id: idea_004
name: "int8/int16 Accumulation (Deferred Widening)"
lifecycle: established
confidence: 0.95
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol02, full_1/sol03, full_1/sol04]
contradicted_by: [full_1/sol01]
related_ideas: [idea_001, idea_009]
cluster: cluster_001
tags: [accumulation, int8, int16, widening]
---

The diff per byte (popcount_pos - popcount_neg) is at most ±8. For k_bytes ≤ 7,
the accumulated sum fits in int8 (max ±56) or int16 (max ±56, well within ±32767).
Accumulate in narrow types, widen to int32 only at the end after the k-loop.

This was one of the most impactful optimizations in gen001. full_1/sol01 accumulated
in int32 *inside* the k-loop using `_mm512_cvtepi8_epi32` + `_mm512_extracti32x4_epi32`
— 16 expensive operations per k-byte. Result: 602.29 µs (worse than baseline on
medium/large). full_1/sol02 switched to int8 accumulation across the k-loop and
widening once at the end: 339.09 µs (1.78x improvement from this single change).

The best solutions use two variants:
- **int8 accumulation** (full_1/sol02, full_1/sol04): `_mm512_add_epi8` in k-loop,
  `_mm512_cvtepi8_epi32` once after. Simpler, fewer registers.
- **int16 accumulation** (explore_1/sol10): `_mm512_cvtepi8_epi16` per k-step,
  `_mm512_add_epi16` in k-loop, then `_mm512_cvtepi16_epi32` at end. Uses 2 zmm
  accumulators per row (32 int16 each) to cover 64 columns.

Both approaches are valid. int8 is simpler; int16 gives more headroom for larger k.
Established with high confidence — the contrast between sol01 (int32-in-loop) and
sol02+ (deferred widening) is dramatic.


### [established] idea_007

---
type: idea
id: idea_007
name: "SIMD Packing (Vectorized pack_B)"
lifecycle: established
confidence: 0.85
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10]
contradicted_by: []
related_ideas: [idea_001, idea_013]
cluster: cluster_001
tags: [packing, simd, pack_b, avx512]
---

Replace scalar byte-by-byte pack_B loop with AVX-512 `_mm512_loadu_si512` /
`_mm512_storeu_si512`. For 64-column chunks of B, one zmm load + one zmm store
replaces 64 scalar byte copies per k-row.

This was one of the biggest single-step improvements in gen001. explore_1/sol07
introduced vectorized pack_B and jumped from 381.32 µs (sol04) to 306.60 µs —
a major improvement. The agent reported that pack_B was a bigger bottleneck than
the micro-kernel itself for medium/large sizes.

All subsequent top solutions (sol08-sol10) retained vectorized pack_B. The
improvement compounds with other optimizations: by reducing packing overhead,
the relative weight of micro-kernel compute increases, making micro-kernel
optimizations (int16 accum, ternarylogic) more impactful.

explore_1/sol10 also handles partial columns (< 64) via masked loads:
`_mm512_maskz_loadu_epi8(mask, ...)`. This is correct and handles edge cases.

pack_A remains scalar in all solutions. It could be vectorized too, but A is
much smaller (MC × k_bytes × 2 ≤ 64 × 7 × 2 = 896 bytes) so the payoff is
minimal.


### [established] idea_008

---
type: idea
id: idea_008
name: "Skip KC Tiling for Small k"
lifecycle: established
confidence: 0.9
first_seen: generation_0
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol01, explore_1/sol02, explore_1/sol03, explore_1/sol04, explore_1/sol05, explore_1/sol06, explore_1/sol07, explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol01, full_1/sol02, full_1/sol03, full_1/sol04]
contradicted_by: []
related_ideas: [idea_002, idea_005, idea_010]
cluster: cluster_002
tags: [tiling, kc-loop, simplification]
---

When k_bytes ≤ 7, the entire k-dimension fits in registers. The KC loop always
has exactly one iteration. Remove the KC-tiling overhead entirely — just iterate
over m-tiles and n-tiles directly, setting kc = k_bytes.

All gen001 solutions implicitly use this: none implement a KC loop. The outer
loop structure is jc → ic → jr → ir with kc = k_bytes throughout. Research
Finding 5 confirmed this is correct: entire B matrix (max 448 KB for large) fits
in L2, and A always fits in L1.

This simplification removes one loop level and eliminates unnecessary buffer
management. Combined with the tiny k values (2-7 bytes), the micro-kernel's
k-loop is the only remaining inner loop. Established — all evidence supports it.


### [established] idea_010

---
type: idea
id: idea_010
name: "Skip memset — Direct Store Without Pre-Zeroing C"
lifecycle: established
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
last_confirmed_gen: 1
supported_by: [explore_1/sol08, explore_1/sol09, explore_1/sol10, full_1/sol04]
contradicted_by: []
related_ideas: [idea_006, idea_008]
cluster: cluster_002
tags: [memset, direct-store, memory-bandwidth, zero-elimination]
---

When k_bytes ≤ 7 and m%64==0 and n%4==0 (true for all benchmark sizes), each C
element is written exactly once by the micro-kernel (no KC tiling means no
accumulation across tiles). Direct stores overwrite C completely, so `memset(C, 0, ...)`
is pure wasted bandwidth.

This was the single largest optimization discovered in gen001. The savings are
enormous for the large benchmark:
- Large (C = 128×65536×4 = 32 MB): memset costs ~1066 µs at ~30 GB/s bandwidth
- Medium (C = 64×16384×4 = 4 MB): memset costs ~40 µs
- Small (C = 32×1024×4 = 128 KB): memset costs ~0.6 µs

Evidence: explore_1/sol08 removed memset and jumped from 306.60 µs (sol07) to
178.28 µs — a **1.72x speedup** from this single change. full_1/sol04 also
skips memset conditionally and achieves 167.23 µs (4.61x vs baseline).

Both agents independently noted this as their most surprising finding. Explore_1
reported: "memset was costing ~3.5 ms on large — nearly half the total time!"

The approach requires a correctness fallback: if dimensions are not aligned to
micro-kernel tile sizes, or k_bytes > 7 (int8 overflow risk), memset must still
be used. All implementations include this safety check.


## All Clusters


### cluster_001

---
type: cluster
id: cluster_001
name: "AVX-512 Micro-Kernel Compute"
member_ideas: [idea_001, idea_002, idea_004, idea_007, idea_009, idea_011]
best_score: 148.18
best_solution: explore_1/sol10
status: active
last_updated: generation_1
---

This cluster groups ideas related to the AVX-512 micro-kernel's compute path:
hardware popcount (idea_001), k-loop unrolling (idea_002), accumulation strategy
(idea_004), SIMD packing (idea_007), kernel width (idea_009), and fused boolean
logic via vpternlogd (idea_011).

The best solution using this cluster is explore_1/sol10 at 148.18 µs (5.20x
baseline). Key established techniques: AVX-512 popcount (idea_001), deferred
widening in int16 (idea_004), vectorized pack_B (idea_007). Disputed: 8-row
kernel (idea_009) and heavy template unrolling (idea_002). Active: vpternlogd
(idea_011).

**Next frontier for this cluster:**
- Isolate vpternlogd contribution (idea_011)
- Retry 8-row kernel with int8 accumulation (idea_009 + idea_004)
- Test 6-row kernel as a middle ground
- Software prefetching for B panels


### cluster_002

---
type: cluster
id: cluster_002
name: "Memory & Tiling Optimization"
member_ideas: [idea_005, idea_006, idea_008, idea_010, idea_012, idea_013]
best_score: 148.18
best_solution: explore_1/sol10
status: active
last_updated: generation_1
---

This cluster groups ideas about memory access patterns, buffer management, and
tiling strategy: tile size tuning (idea_005), streaming stores (idea_006), KC
elimination (idea_008), memset skip (idea_010), stack allocation (idea_012),
and no-packing direct kernel (idea_013).

The memset-skip optimization (idea_010) was the single highest-impact discovery
in gen001, providing up to 2x speedup alone. KC elimination (idea_008) is
universally adopted. NC=256 appears optimal (pattern_002).

**Next frontier for this cluster:**
- No-packing direct kernel (idea_013) — untested, potentially large win
- Systematic NC tuning (128, 192, 256, 384) across all benchmark sizes
- Software prefetching for next B panel
- Investigate why NC=512 regresses (pattern_002)


## All Patterns


### [active] pattern_002

---
type: pattern
id: pattern_002
name: "NC=256 consistently outperforms NC=512 for 4x64 kernel"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [explore_1/sol01, explore_1/sol02, explore_1/sol06, explore_1/sol10, full_1/sol04]
related_ideas: [idea_005]
tags: [tiling, NC, cache, performance]
---

Solutions using NC=256 consistently outperform those using NC=512, despite NC=512
theoretically reducing the number of B-panel packing operations. Examples:
- explore_1/sol02 (NC=256): 400.68 µs vs explore_1/sol01 (NC=512): 654.75 µs
- explore_1/sol10 (NC=256): 148.18 µs vs full_1/sol04 (NC=512): 167.23 µs
- explore_1/sol06 (NC=512 with direct stores): 465.65 µs

The root cause is unclear. Hypotheses from explore_1: cache line conflicts, TLB
pressure, B panel alignment issues. The B panel at NC=512 is 512 × k_bytes bytes
(max 3584 bytes for k=7), which still fits in L1. The regression may be due to
micro-kernel call overhead patterns or cache set

[TRUNCATED — read full file for details]


### [active] pattern_003

---
type: pattern
id: pattern_003
name: "Template specialization causes I-cache pressure and regressions"
lifecycle: active
confidence: 0.7
first_seen: generation_1
last_updated: generation_1
evidence: [full_1/sol03, explore_1/sol10]
related_ideas: [idea_002]
tags: [template, i-cache, code-bloat, unrolling]
---

Heavy template specialization (multiple kernel variants instantiated via
`switch(k_bytes)` dispatch) hurts performance due to instruction cache pressure.
full_1/sol03 created 6 kernel copies (3 k_bytes × 2 store modes) and regressed
from 339.09 µs (sol02) to 442.43 µs. The small benchmark was hit hardest:
11.61 → 20.04 µs.

In contrast, lightweight compiler hints (`#pragma GCC unroll 7`) achieve loop
unrolling without code duplication. explore_1/sol10 uses this approach and
achieves 148.18 µs — the best score.

This pattern suggests: for this problem's small k values, let the compiler handle
unrolling via pragmas rather than manually instantiating multiple kernel templates.
The

[TRUNCATED — read full file for details]


### [confirmed] pattern_001

---
type: pattern
id: pattern_001
name: "Memset dominates large benchmark cost"
lifecycle: confirmed
confidence: 0.95
first_seen: generation_1
last_updated: generation_1
evidence: [explore_1/sol07, explore_1/sol08, full_1/sol02, full_1/sol04]
related_ideas: [idea_010]
tags: [memset, memory-bandwidth, large-benchmark]
---

For the large benchmark (128×65536, C = 32 MB), `memset(C, 0, ...)` consumes
~1000-3500 µs — a substantial fraction of total execution time. Removing memset
(via direct stores) consistently provides 1.5-2x speedup on the large benchmark.

Evidence: explore_1/sol07 (with memset) scored 306.60 µs. explore_1/sol08 (memset
removed, otherwise identical) scored 178.28 µs — 1.72x faster. Similarly,
full_1/sol02 (339.09 µs, with memset for some paths) vs full_1/sol04 (167.23 µs,
memset skipped) shows a 2.03x improvement.

This pattern reveals that memory bandwidth, not compute, is the primary bottleneck
for the large benchmark. Any optimization that reduces memory traffic (fe

[TRUNCATED — read full file for details]


### [confirmed] pattern_004

---
type: pattern
id: pattern_004
name: "Incremental optimization trajectory: each fix builds on previous"
lifecycle: confirmed
confidence: 0.9
first_seen: generation_1
last_updated: generation_1
evidence: [explore_1/sol01 through explore_1/sol10]
related_ideas: [idea_001, idea_004, idea_007, idea_010, idea_011, idea_012]
tags: [optimization-process, incremental, compounding]
---

The explore_1 agent demonstrated a highly effective incremental optimization
trajectory across 10 solutions:

1. AVX-512 popcount (sol01: 654 µs) — basic port from AVX2
2. + vpternlogd + NC=256 (sol02: 400 µs) — fix truth tables, tune tiling
3. 8-row kernel attempt (sol03: 493 µs) — regression, abandoned
4. + direct store (sol04: 381 µs) — eliminate read-for-ownership
5. Aligned temp buffer + streaming (sol05: 964 µs) — regression, memcpy too expensive
6. NC=512 + direct store (sol06: 465 µs) — regression, NC=512 consistently worse
7. + vectorized pack_B (sol07: 306 µs) — major win
8. + remove memset (sol08: 

[TRUNCATED — read full file for details]
