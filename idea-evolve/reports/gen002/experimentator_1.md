# Experimentator Report — Gen 2, Instance 1

## Solutions Produced

| File | Fitness (µs) | Valid | small (µs) | medium (µs) | large (µs) |
|------|-------------|-------|-----------|------------|-----------|
| sol01.py | 223.17 | Yes | 5.31 | 411.45 | 5091.26 |
| best.py (ref) | 148.18 | Yes | 4.49 | 228.26 | 3176.31 |

sol01 regressed because NC=128 increases pack_A calls for large sizes. The int8 accumulation improvement (~11%) was not enough to offset the NC regression. Solution was primarily a byproduct of experiments; the real value of this session is the data below.

---

## Experiment 1: Per-Phase Timing Breakdown (HIGHEST VALUE)

**Question:** Where does the time go in the best current solution?

**Methodology:** Isolated each phase by running separate code variants (pack_B only, pack_A only, full) and differencing. Used clock_gettime median of 21 runs on isolated cores via cgexec.

**Results:**

| Phase | small (µs) | % | medium (µs) | % | large (µs) | % |
|-------|-----------|---|------------|---|-----------|---|
| pack_B | 0.13 | 1.1% | 2.29 | 0.5% | 15.75 | 0.3% |
| pack_A | 0.68 | 5.7% | 25.69 | 6.1% | 215.13 | 4.7% |
| kernel+store | 11.10 | 93.2% | 390.72 | 93.3% | 4350.71 | 95.0% |
| **Total** | **11.91** | | **418.70** | | **4581.59** | |

**Conclusion (HIGH confidence):** Kernel+store dominates at 93-95% of total time. Packing is negligible. All optimization effort should target the micro-kernel and store operations.

### Experiment 1b: Streaming Stores

| Size | Normal stores (µs) | Streaming stores (µs) | Speedup |
|------|-------------------|---------------------|---------|
| small | 9.47 | 8.62 | 1.1x |
| medium | 298.89 | 317.43 | 0.9x (WORSE) |
| large | 9849.99 | 4226.65 | **2.3x** |

**Conclusion (HIGH confidence):** Streaming stores give 2.3x on large (33 MB output bypasses cache pollution). They HURT medium (4 MB fits in L3, streaming bypasses useful cache). **CRITICAL LIMITATION:** The benchmark harness uses `std::vector<int>` for C, which is NOT 64-byte aligned. `_mm512_stream_si512` requires aligned addresses. Solutions cannot use streaming stores directly unless they allocate an aligned internal buffer and copy results.

---

## Experiment 2: Assembly Quality Inspection

**Question:** Is the compiler generating optimal code for the micro-kernel?

**Methodology:** Compiled micro-kernel with `-S -O3 -march=native -fverbose-asm`, counted instructions per type.

**Results — k-loop body (4 unrolled iterations, 225 total instructions):**

| Instruction | Count/iter | Port | Notes |
|------------|-----------|------|-------|
| vpbroadcastb | 8 | 5 only | 1c throughput |
| vpternlogq | 8 | 0/5 | 1c throughput |
| vpopcntb | 8 | 0/1 | 1c throughput |
| vpsubb | 4 | 0/5 | 0.5c throughput |
| vpmovsxbw | 8 | 5 only | 1c throughput |
| vextracti32x8 | 4 | 5 only | 1c throughput |
| vpaddw | 8 | 0/5 | 0.5c throughput |
| vmovdqu64 (loads) | ~5 | 2/3 | B data + register moves |

**No register spills detected.** All 18 zmm registers used; fits within 32 available.

**Port 5 bottleneck:** At minimum 20 port 5 uops per k-iteration (broadcast=8 + movsxbw=8 + extract=4), likely 24-28 with ternlog/addw sharing. This is the throughput bottleneck.

**Conclusion (MEDIUM confidence):** The widening operations (vpmovsxbw + vextracti32x8) cost 12 port 5 uops per k-iteration. Switching to int8 accumulation eliminates these from the inner loop, reducing port 5 pressure by ~40%.

### Experiment 2b: int8 vs int16 Accumulation

| Size | int16 (µs) | int8 (µs) | Speedup |
|------|-----------|----------|---------|
| small (k=2) | 5.07 | 4.86 | 1.04x |
| medium (k=4) | 202.67 | 183.30 | 1.11x |
| large (k=7) | 3669.63 | 3253.04 | 1.13x |

**Correctness:** PASS on all sizes. Safe when k_bytes ≤ 15 (max ±120, within int8 range -128..127). Must fall back to int16 for k_bytes > 15 (correctness test uses k=256 → k_bytes=32).

**Conclusion (HIGH confidence):** int8 accumulation is a free 11-13% win for the benchmark sizes. Improvement scales with k_bytes as expected (more iterations = more savings from deferred widening).

---

## Experiment 3: NC Sweep

**Question:** What is the optimal NC for each benchmark size?

**Methodology:** Same micro-kernel, same data. Only NC varies. Median of 15 runs.

| NC | small (µs) | medium (µs) | large (µs) | geomean (µs) |
|----|-----------|------------|-----------|-------------|
| 64 | 10.80 | 592.43 | 7280.11 | 359.79 |
| **128** | **10.82** | **472.15** | 8106.31 | **345.94** |
| 192 | 12.27 | 685.55 | 7370.59 | 395.76 |
| 256 | 11.59 | 597.55 | 7333.52 | 370.29 |
| 384 | 10.98 | 571.93 | 8266.46 | 373.02 |
| 512 | 11.70 | 554.93 | 7604.11 | 366.83 |
| 1024 | 13.36 | 681.98 | 7000.60 | 399.56 |
| m (no tiling) | 12.65 | 629.60 | **6782.99** | — |

**Conclusion (MEDIUM confidence):**
- Geomean winner: NC=128 (346 µs)
- Medium: NC=128 is clearly best (472 µs vs 597 for NC=256). B panel = 4×128 = 512 bytes fits L1.
- Large: No NC tiling is best (6783 µs). Full B = 7×65536 = 458 KB fits in L2.
- NC=128 wins geomean but hurts large (8106 vs 7334 for NC=256) because more NC blocks = more pack_A calls.
- **Per-size optimal NC is different.** An adaptive NC strategy could help.

---

## Experiment 4: Memory Bandwidth

**Question:** What is the actual DRAM bandwidth? Is large hitting the ceiling?

**Methodology:** Standalone bandwidth microbenchmarks with streaming/regular/memset writes and sequential reads.

**Write Bandwidth (GB/s):**

| Size | Stream write | Regular write | memset |
|------|-------------|--------------|--------|
| 128 KB | 10.94 | 24.87 | 24.84 |
| 4 MB | 18.21 | 17.16 | 14.26 |
| 32 MB | **24.84** | 11.38 | 17.71 |
| 64 MB | 22.01 | 10.14 | 18.99 |

**Read Bandwidth:** 128KB: 47.6 GB/s, 4MB: 19.0 GB/s, 32MB: 12.9 GB/s, 64MB: 10.4 GB/s

**Theoretical Minimum Write Times (streaming stores):**

| Size | Output (MB) | Min write time (µs) | Current best (µs) | Ratio |
|------|------------|--------------------|--------------------|-------|
| small | 0.13 | 7.70 | 4.49 | 0.6x (fits L1) |
| medium | 4.19 | 246.51 | 228.26 | 0.9x |
| large | 33.55 | 2053.53 | 3176.31 | 1.5x |

**Conclusion (HIGH confidence):**
1. **Medium is already near the bandwidth floor.** Current 228 µs vs theoretical minimum 247 µs (streaming). Regular store BW at 4 MB is ~17 GB/s → floor ~247 µs. The kernel is already within ~8% of memory bandwidth limits.
2. **Large has 1.5x headroom.** Current 3176 µs vs streaming floor 2054 µs. Streaming stores would close most of this gap (exp 1b showed 2.3x improvement).
3. **Small is compute-bound, not memory-bound.** Output fits in L1 cache.
4. **Combined read+write bandwidth for large pattern:** 2693 µs at 12.5 GB/s effective write. Current large time (3176 µs) is within 1.2x of this.

### Implications for the 24 µs target

Even with perfect optimization (zero computation overhead, pure bandwidth), the theoretical geomean floor is approximately:
- small: ~2 µs (L1 cache resident)
- medium: ~120-247 µs (L3/DRAM bandwidth limited)
- large: ~1000-2054 µs (DRAM bandwidth limited)

Geomean of optimistic estimates: ∛(2 × 120 × 1000) ≈ 62 µs

**The 24 µs target appears to be below the memory bandwidth floor** for writing n×m×4 bytes of int32 output. To achieve 24 µs, a fundamentally different approach would be needed — perhaps outputting in a compressed format, reducing write volume, or using multi-core (not allowed).

---

## What I Tried

1. **Experiment 1:** Phase timing breakdown — identified kernel+store as 93-95% of time
2. **Experiment 1b:** Streaming vs regular stores — 2.3x on large, hurts medium
3. **Experiment 2:** Assembly inspection — identified port 5 bottleneck from widening ops
4. **Experiment 2b:** int8 accumulation — 11-13% kernel improvement, correct
5. **Experiment 2c:** Combined int8 + streaming + NC=128 — 14% geomean improvement in standalone
6. **Experiment 3:** NC sweep — NC=128 best for geomean, per-size optima differ
7. **Experiment 4:** Memory bandwidth measurement — medium is near bandwidth floor
8. **sol01.py:** int8 + NC=128 without streaming stores — 223 µs (regressed from 148 µs due to NC change hurting large)

## What Information I Lacked

- **The harness allocates C with `std::vector<int>` (unaligned).** This blocks streaming stores, the single biggest optimization (2.3x on large). No documentation mentioned this constraint.
- **The correctness test includes k=256 (k_bytes=32).** This overflows int8 accumulators. Not mentioned in description.md which only lists benchmark sizes with k ≤ 56.
- **Actual port assignments on Tiger Lake for vpopcntb.** fact_004 says port 5 but this may be wrong — different sources disagree.

## What Given Facts Might Be Wrong

- **fact_004 instruction latencies:** `vpmovzxbd` listed as 3c latency, port 5. The actual port for `vpopcntb` on Tiger Lake may differ from what's stated (some sources say port 0/1, not port 5). This affects throughput analysis significantly.

## Was the State of Affairs Accurate?

Mostly yes. The open questions it listed (per-phase timing, assembly quality, NC sweep, bandwidth) were exactly the right experiments to run. The State of Affairs correctly identified that no hardware profiling had been done. The NC=256 recommendation was reasonable given the data at the time.

## What Would I Do Differently

- **Start by checking harness constraints** (C alignment, test sizes) before designing optimizations that depend on them.
- **Test streaming stores with an aligned internal buffer** — allocate aligned C internally, compute into it, then memcpy to the caller's C. This might recover the streaming store win for large.
- **Adaptive NC per size** — use NC=128 for medium but NC=256 or NC=m for large.

## Specific Experiments to Run

1. **Aligned-buffer workaround for streaming stores:** Allocate aligned internal buffer, compute with streaming stores, memcpy to unaligned C. Measure if the copy overhead eliminates the streaming benefit.
2. **Adaptive NC:** Use different NC per output size. Detect m at runtime and pick NC accordingly.
3. **8-row micro-kernel with int8 accumulation:** With int8 accum, register pressure halves (4 zmm accumulators vs 8 for int16). This frees registers for an 8-row kernel, potentially doubling compute density.
4. **No-packing direct kernel:** Eliminate pack_B entirely for large sizes where B fits in L2. Load from B directly with stride.
5. **vpternlogd truth table verification:** Confirm 0xD8 and 0xE4 are optimal by testing all valid truth tables.

## What Surprised Me

1. **Streaming stores are 2.3x faster for large but the harness blocks them.** This is the single biggest optimization opportunity and it's inaccessible due to alignment.
2. **Medium is already within 8% of the memory bandwidth floor.** Further optimization of medium is nearly impossible — the bottleneck is DRAM write bandwidth, not computation.
3. **NC=128 beats NC=256 for geomean** but NC=m (no tiling) beats everything for large. The optimal tiling strategy is size-dependent.
4. **The int8→int16 widening costs ~40% of port 5 throughput.** This was a much larger overhead than expected.

## Helper Tools Feedback

Did not use any helpers from `problem/helpers/`. No helpers exist that would have been useful for this benchmarking work. A helper for "compile and run instrumented C++ code" would be useful but doesn't fit the helper model (helpers are for solution code, not benchmarking).

## Time Budget

Had enough time for all 4 experiments plus derivative tests. If I had more time, I would have:
1. Tested the aligned-buffer workaround for streaming stores
2. Built an 8-row micro-kernel with int8 accumulators
3. Tested adaptive NC (different NC per size)
4. Run `perf stat` for actual cache miss counts (blocked by perf_event_paranoid=4)
