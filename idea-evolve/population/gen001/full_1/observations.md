# Observations — gen001 full_1

## Summary of Results

| Solution | Fitness (µs) | time_small | time_medium | time_large | vs Baseline |
|----------|-------------|------------|-------------|------------|-------------|
| Baseline (V14opt) | ~770 | 15.78 | 911.64 | 12422.36 | 1.00x |
| Target | 477 | — | — | — | — |
| sol01 | 602.29 | 11.94 | 1145.33 | 15981.55 | 1.28x |
| sol02 | 339.09 | 11.61 | 507.40 | 6620.63 | 2.27x |
| sol03 | 442.43 | 20.04 | 696.88 | 6199.68 | 1.74x |
| **sol04** | **167.23** | **5.99** | **220.63** | **3540.60** | **4.61x** |

**Best: sol04 at 167.23 µs — 4.61x faster than baseline, 2.85x faster than target.**

---

## What Was Tried

### sol01: AVX-512 4×64 micro-kernel with hardware popcnt (baseline conversion)
- Replaced AVX2 LUT popcount with `_mm512_popcnt_epi8` (single instruction)
- Widened micro-kernel from 4×32 to 4×64 (doubles columns per iteration)
- Used 16 zmm int32 accumulators (4 rows × 4 chunks of 16)
- Int32 accumulation with `_mm512_cvtepi8_epi32` in the hot loop
- **Result**: Small improved (11.94 vs 15.78) but medium/large got WORSE vs baseline

### sol02: Int8 accumulation + streaming stores
- **Key insight**: k_bytes ≤ 7, so accumulated diff per byte ≤ 7×8 = 56 — fits in int8 (max 127)
- Moved `_mm512_cvtepi8_epi32` and `_mm512_extracti32x4_epi32` OUT of the hot loop
- Hot loop only does: load B, XOR (NOT), 4× (broadcast×2, OR×4, AND×2, popcnt×2, sub, add_epi8)
- Widen int8→int32 ONCE after the k-loop (not per-k-byte)
- Added streaming NT stores (`_mm512_stream_si512`) for large m (≥16384) when C is 64-byte aligned
- Direct store to C (not read-modify-write) since C is pre-zeroed and each element computed once
- **Result**: 339.09 µs — BEAT target (477 µs), 2.27x speedup. Massive improvement.

### sol03: Template k-loop unrolling + switch dispatch (WORSE)
- Templated `micro_kernel_4x64<KBYTES, USE_STREAM>` with compile-time KBYTES
- switch(k_bytes) dispatch for k_bytes=2, 4, 7 + generic fallback
- **Result**: 442.43 µs — WORSE than sol02. Code bloat from 6 template instantiations caused
  I-cache pressure. Small (20.04 µs) and medium (696.88 µs) regressed significantly.

### sol04: Skip memset (direct store to C) — BEST
- **Key insight**: Each C element is computed exactly once (no KC tiling, all k in one pass)
  AND we use direct stores (not +=). So memset is completely wasted bandwidth:
  - Small: saves ~128KB of zero-writes
  - Medium: saves ~4MB of zero-writes
  - Large: saves ~32MB of zero-writes (at 30 GB/s memory bandwidth = ~1 GB saved)
- Condition: only skip memset when k_bytes ≤ 7 (int8 safe), m%64==0, n%4==0 (no partial tiles)
- Kept sol02's simpler single-kernel design (no template bloat)
- **Result**: 167.23 µs — 4.61x faster than baseline, 2.85x faster than target.

---

## Key Findings

1. **Int8 accumulation is transformative**: Moving cvtepi8_epi32 out of the hot loop gave 1.77x speedup (602→339 µs). This is the single biggest optimization.

2. **Skipping memset is massive**: Going from 339→167 µs (2x speedup) by eliminating the extra pass over C. For the large benchmark (C=32MB in memory), the memset was itself taking ~1 GB of memory writes. With streaming stores we write C only once instead of twice.

3. **Template unrolling hurts via code bloat**: Creating 6 copies of the kernel (3 k_bytes × 2 stream modes) caused I-cache pressure and hurt all sizes, especially small. Keep ONE kernel path.

4. **Streaming stores are crucial for large m**: For m=65536, C=32MB doesn't fit in L3. NT stores bypass cache, letting B data stay resident. Combined with direct stores (no prior read), we write C only once.

5. **NC=512 works well**: B panel = 512×7 = 3584 bytes → fits in L1 (48KB). Good for all sizes.

---

## What I'd Try Next (with more time)

1. **No-packing direct kernel**: Since k_bytes is tiny (2-7), try reading B directly from memory without packing — might avoid packing overhead for the small/medium cases.

2. **Larger row tiling (MC=128)**: n=128 could use 128-row tiles to amortize B-panel loading across more row work.

3. **Prefetching next B panel**: Issue prefetch hints during current computation.

4. **k-loop unrolling without code bloat**: Use `#pragma GCC unroll 7` on the k-loop with runtime kc — might get unrolling benefit without multiple kernel copies.

5. **Even wider micro-kernel (4×128)**: Use 2 zmm for B per k-step, 8 acc registers per row — if register pressure allows.
