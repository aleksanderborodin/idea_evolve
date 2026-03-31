# Explore Agent 1 — Generation 1 Observations

## Summary of Approaches Tried

### sol01 — AVX-512 basic, NC=512, int16 accum, explicit NOT(B) (fitness: 654.75)
First AVX-512 attempt. Replaced LUT popcount with `_mm512_popcnt_epi8`, 64-col micro-kernel,
int16 accumulation. NC=512. Medium size 2x SLOWER than baseline — NC=512 caused unknown
regression. Small improved, large neutral.

### sol02 — Fixed ternarylogic (0xD8/0xE4), NC=256, int16 accum (fitness: 400.68)
Key fixes: correct ternarylogic truth tables for u_pos (0xD8) and u_neg (0xE4). NC=256.
Huge improvement — beats the 477 µs target. The ternarylogic computes (va_p|B)&(va_n|~B)
in 1 instruction instead of 3 (OR + NOT + AND).

### sol03 — 8-row micro-kernel (fitness: 493.42)
Tried 8×64 instead of 4×64. Worse due to higher register pressure (16 zmm accumulators
+ temporaries) causing spilling. 4-row is the sweet spot.

### sol04 — Direct store (no C load), NC=256 (fitness: 381.32)
Each C cell written exactly once (no KC tiling), so replaced load-add-store with pure store.
Eliminates read-for-ownership on cache lines. Solid improvement.

### sol05 — Aligned buffer + streaming stores (fitness: 964.47)
Bad idea: allocated aligned temp C, used _mm512_stream_si512, then memcpy to output.
The 32 MB memcpy killed performance for large. Much worse than baseline.

### sol06 — NC=512 with direct store (fitness: 465.65)
NC=512 is consistently worse than NC=256 even with direct stores. NC=256 better for all sizes.

### sol07 — Vectorized pack_B using zmm load/store (fitness: 306.6)
MAJOR WIN: replaced scalar pack_B inner loop (64 iterations) with single zmm load+store.
~64x reduction in pack_B instruction count. Demonstrates pack_B was a significant bottleneck.

### sol08 — No memset + vectorized pack_B (fitness: 178.28)
MAJOR WIN: benchmark harness never re-zeros C between iterations, and our hot path always
uses direct stores (overwrite, not accumulate). Removing memset saves zeroing 32 MB (large),
4 MB (medium). Nearly halved time for all sizes.

### sol09 — thread_local buffers + k-loop unroll pragma (fitness: 171.04)
thread_local TLS overhead hurt small. But k-loop unroll pragma and other effects helped
medium. Stack buffers better than _mm_malloc.

### sol10 — alignas(64) stack buffers + k-loop unroll (fitness: 148.18) ← BEST
Fixed: use `alignas(64)` local stack arrays instead of TLS or malloc.
Stack alloc is zero-cost (just stack pointer adjustment). Best result: 148.18 µs.
**19.2% of baseline (770 µs) — 5.2x speedup overall.**

## Key Discoveries

1. **ternarylogic truth tables**: u_pos uses 0xD8 (not 0xC8), u_neg uses 0xE4. Verified manually.
2. **NC=256 > NC=512**: NC=512 consistently hurts. Unknown root cause (possibly C tile cache behavior).
3. **Vectorized pack_B is critical**: scalar pack_B was the biggest bottleneck outside the kernel.
4. **memset is redundant**: harness pre-zeros C; our direct store hot path overwrites fully.
   The 32 MB memset was costing ~3.5 ms (nearly half of large time).
5. **Stack buffers faster than malloc**: _mm_malloc has ~1 µs overhead visible on small.
6. **int16 accumulation is better than int8**: int8 overflows at k_bytes=32 (correctness check).
   int16 is safe and cheaper than int32 in the inner loop.
7. **Direct store (no load) works**: since each C cell is written exactly once per call,
   reading C before writing is always reading zeroed or stale data — wasteful.

## What Failed / Dead Ends
- 8-row micro-kernel: register pressure too high, spilling
- NC=512: consistently worse for all sizes  
- Streaming stores with memcpy: memcpy of 32 MB kills performance
- thread_local buffers: TLS overhead measurable on small (4.79 µs → 5.78 µs)
- int8 accumulation: overflows at k_bytes=32 (correctness check fails)

## Unexplored Directions
- **VNNI-based reformulation** (off-limits per brief, that's explore_2's direction)
- **Prefetching B for next jc tile** — tried in sol07 but didn't show up in final
- **Wider micro-kernel (6 rows × 64 cols)** — sweet spot between 4 and 8 might exist
- **Template specialization per k_bytes** — dispatch on k_bytes=2,4,7 for unrolled versions
- **Non-temporal stores for large m** — if C were aligned; checked that it's not guaranteed
- **pack_A vectorization** — A panel is tiny, low priority vs pack_B
