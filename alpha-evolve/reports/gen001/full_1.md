# Agent Report — gen001 full_1

## Solutions Produced

| File | Fitness (µs) | is_valid | time_small | time_medium | time_large | vs Baseline | vs Target |
|------|-------------|----------|------------|-------------|------------|-------------|-----------|
| sol01.py | 602.29 | ✓ | 11.94 | 1145.33 | 15981.55 | 1.28x faster | MISSED |
| sol02.py | 339.09 | ✓ | 11.61 | 507.40 | 6620.63 | 2.27x faster | BEAT ✓ |
| sol03.py | 442.43 | ✓ | 20.04 | 696.88 | 6199.68 | 1.74x faster | MISSED |
| **sol04.py** | **167.23** | ✓ | **5.99** | **220.63** | **3540.60** | **4.61x faster** | **BEAT 2.85x ✓** |

Baseline (V14opt): ~770 µs. Target: 477 µs. **Best: sol04 at 167.23 µs.**

---

## 1. What I Tried

**sol01** — AVX-512 4×64 micro-kernel, int32 accumulation in hot loop.
Replaced the AVX2 LUT popcount with `_mm512_popcnt_epi8`, widened kernel from 4×32 to 4×64 columns. Used 16 zmm int32 accumulators. However, `_mm512_cvtepi8_epi32` + `_mm512_extracti32x4_epi32` ran inside the k-loop, adding 16 expensive operations per k-byte. Result: small improved but medium/large degraded vs baseline (0.80x and 0.78x speedup respectively). Fitness: 602.29 µs.

**sol02** — Int8 accumulation + streaming stores.
Key insight: since k_bytes ≤ 7, the accumulated popcount diff per byte is in [-56, 56], which fits in int8. So widening to int32 can be done ONCE after the k-loop, not per k-step. This cut the hot-loop operation count dramatically. Also added: (a) streaming NT stores (`_mm512_stream_si512`) for large m when C is 64-byte aligned — bypasses cache, keeps B panel resident; (b) direct store to C instead of read-modify-write since C is pre-zeroed and each element computed exactly once. Fitness: 339.09 µs (beat target, 2.27x speedup).

**sol03** — Template k-loop unrolling with switch dispatch (regressed).
Templated the kernel on `KBYTES` so the compiler would fully unroll for k=2, 4, 7. Used switch(k_bytes) dispatch + generic fallback for other values. This created 6 kernel copies (3 k_bytes × 2 stream modes), causing I-cache pressure. Small case degraded from 11.61→20.04 µs. Overall fitness: 442.43 µs — worse than sol02.

**sol04** — Skip memset (direct stores, no pre-zero needed).
Key insight: each C element is visited exactly once (no KC tiling, all k processed in one micro-kernel call; m and n are exact multiples of 64 and 4 respectively for benchmark sizes). Direct stores overwrite C completely, so `memset(C, 0, ...)` is pure wasted bandwidth. Savings:
- Large (C=32MB, memory bandwidth ~30 GB/s): ~1066 µs saved
- Medium (C=4MB, L3 ~100 GB/s): ~40 µs saved
- Small (C=128KB, L2 ~200 GB/s): ~0.6 µs saved

Skips memset when `k_bytes ≤ 7 && m%64==0 && n%4==0`. Falls back to memset+accumulate for other cases (e.g. correctness test with k_bytes=32). Fitness: **167.23 µs — 4.61x faster than baseline**.

---

## 2. What Information I Lacked

- Actual L2/L3 bandwidth figures for this specific machine (used estimates)
- Whether C is guaranteed to be 64-byte aligned by the harness (assumed yes for stream path)
- Exact cost of `_mm512_extracti32x4_epi32` on Tiger Lake (estimated 3c latency based on facts)

---

## 3. What Given Facts Might Be Wrong

- `fact_004` says `vpmovzxbd` has 3c latency on Tiger Lake. If it's actually 1c, the int32-in-hot-loop approach (sol01) might have been less penalized. But empirically int8 accumulation is clearly faster.
- Memory bandwidth estimate: I used ~30 GB/s but actual measured bandwidth might differ.

---

## 4. State of Affairs Accuracy

Not applicable — this is generation 1 with no prior state of affairs.

---

## 5. What I'd Do Differently

- Start with the memset-skip optimization from the beginning (biggest single win)
- Avoid template-based multi-kernel dispatch (causes code bloat)
- Test streaming stores earlier — crucial for large m

---

## 6. Specific Experiments to Run

1. **NC tuning**: Is NC=512 optimal? Try NC=256, 384, 640, 1024. Affects B packing overhead vs reuse.
2. **No-packing micro-kernel**: Skip B packing entirely and read B directly. For k_bytes=2 (2KB total B), B fits in L1 without packing — no packing overhead.
3. **Wider kernel (4×128)**: Use 2 zmm per B load, 8 int8 accumulators per row. More register pressure but better memory bandwidth utilization for medium/large.
4. **Prefetch hints**: `_mm_prefetch` for next B panel before it's needed.
5. **MC=128**: For n=128, use 128-row macro-tiles. Amortize B-panel reads across more row work.

---

## 7. Surprises

- Skipping memset gave a **2x speedup** (339→167 µs). This is larger than the initial AVX-512 conversion, which was expected to be the big win. The bandwidth savings from not writing 32MB of zeros to memory were enormous.
- Template unrolling HURT performance (sol03 worse than sol02). I expected compile-time loop unrolling to help, but code bloat from 6 instantiated templates caused more I-cache pressure than the loop overhead saved.
- sol01 was slower than V14opt on medium/large despite using AVX-512. The culprit was cvtepi8_epi32 in the hot loop — a 3-cycle instruction called 16 times per k-byte made the theoretical 2x throughput gain disappear.

---

## 8. Helper Tools Feedback

Used `from helpers.core import compute_c` indirectly via the evaluation pipeline. No direct use needed. No bugs found. Would have found a "check alignment of C pointer" helper useful, and an "estimate memset cost in µs given size and memory level" utility.

---

## 9. Time Budget

Had enough time to produce 4 solutions and iterate meaningfully. With more time I would:
1. Try no-packing direct kernel for the small case
2. Tune NC systematically (it's a critical parameter)
3. Explore 4×128 kernel width
4. Add software prefetching for B panels
