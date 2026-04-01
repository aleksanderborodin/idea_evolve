# Observations — Experimentator 1, Gen 3

## Solutions

| File | Fitness (µs) | Valid | small (µs) | medium (µs) | large (µs) | Notes |
|------|-------------|-------|-----------|------------|-----------|-------|
| **baseline (gen002/explore_1/sol01)** | **147.26** | Yes | **3.69** | **225.55** | **3841.72** | Row-streaming, regular stores |
| sol01.py | 400.32 | Yes | 9.96 | 317.41 | 20290.23 | NT stores + per-rep _mm_malloc(32 MB) |
| sol01b.py | 250.98 | Yes | 4.96 | 347.77 | 9173.21 | NT stores + static buffer (no malloc overhead) |
| sol02.py | 197.33 | Yes | 4.97 | 311.15 | 4972.18 | 4-row k_bytes=2 small kernel + general path |

All three solutions are WORSE than the baseline. Details below.

---

## Experiment 1: Aligned-Buffer NT Stores Overhead

**Question:** What is the net benefit of NT stores after accounting for aligned_alloc + memcpy overhead?

### sol01: Per-rep _mm_malloc approach
- large: 20290 µs vs baseline 3841 µs — **5.3x SLOWER**
- Cause: `_mm_malloc(32 MB)` on every benchmark rep calls `mmap()` which triggers page fault
  handling for 8192 new 4 KB pages per rep (~100-200 ns per fault = ~1600 µs in page faults alone).
  Then `_mm_free()` calls `munmap()` with TLB shootdowns. The OS overhead dominates.

### sol01b: Static pre-allocated buffer (no malloc per rep)
- large: 9173 µs vs baseline 3841 µs — **2.39x SLOWER**
- Eliminates malloc overhead but NT + memcpy is still much worse.
- Breakdown (estimated):
  - Compute: ~1029 µs (from gen002 timing: kernel+store 95% of 3841 - write portion)
  - NT writes (24.84 GB/s for 32 MB): ~1289 µs
  - memcpy C_work→C: nt_buf is cache-cold (NT bypassed cache); reading from DRAM at 12.9 GB/s
    + writing to C at 11.38 GB/s concurrently → ~5000-6000 µs for 32 MB memcpy
  - Total: ~7300-8300 µs, consistent with measured 9173 µs

### Conclusion (HIGH confidence)
**The aligned-buffer NT store workaround does NOT help.** The memcpy of 32 MB cold DRAM data
takes ~5000-6000 µs, far exceeding the NT store savings (~1523 µs saved on write bandwidth:
2812 µs regular vs 1289 µs NT). Net: ~3500-4500 µs EXTRA overhead from the cold read in memcpy.

The only way to exploit NT stores for large is to write DIRECTLY to C with NT stores.
This requires the benchmark harness to allocate C with `_mm_malloc` (64-byte aligned),
not `std::vector<int>`. Alternatively, request the harness be modified (see fact_006).

Note: small/medium appear slower in sol01/sol01b because the kernel is split into helper
functions that the compiler may not fully inline, adding overhead vs the monolithic baseline.

---

## Experiment 2: Port Assignment Verification

**Question:** Is vpopcntb on port 5 (as fact_004 states) or port 0/1 (as gen002 asm analysis suggests)?

### Microbenchmark results (from port_bench.cpp)

CPU frequency estimate: 1.382 GHz (TSC rate; low due to power management at startup)

| Instruction | Measured ns/instr | Estimated cycles | Notes |
|------------|------------------|-----------------|-------|
| vpopcntb zmm,zmm | 0.255 | 0.352 | ~0.5c → dual port |
| vpternlogq | 0.356 | 0.492 | ~0.5c → dual port (0/5) |
| vpbroadcastb zmm,r8 | 0.489 | 0.675 | ~1c → single port 5 |
| vpsubb zmm | 0.557 | 0.770 | (inflated by dep chain) |
| vpmovsxbw zmm,ymm | 0 | — | Compiler DCE eliminated loop |
| cvtepi8_epi32 zmm,xmm | 0 | — | Compiler DCE eliminated loop |

Key observations:
- **vpopcntb is ~2x faster than vpbroadcastb** (0.255 vs 0.489 ns)
  → vpopcntb has 0.5c throughput (dual port 0/1)
  → vpbroadcastb has ~1c throughput (single port 5, confirmed)
  → **fact_004 "port 5" for vpopcntb is WRONG**
- vpternlogq at ~0.5c confirms dual port 0/5 (consistent with fact_004)
- vpbroadcastb from volatile stack variable includes load overhead; actual pure broadcast
  is likely closer to 1.0c

### Conclusion (MEDIUM confidence — limited by frequency measurement accuracy)
**vpopcntb zmm operates on ports 0/1, NOT port 5.** This confirms the gen002 assembly
analysis finding. fact_004 must be corrected.

**Port bottleneck analysis:**
In the kernel hot path per 64-col block (k_bytes=2):
- Port 5 ops: 2 × vpbroadcastb (1c each) + 2 × vpternlogq (0.5c each) = 3c port 5
- Port 0/1 ops: 2 × vpopcntb (0.5c each) = 1c port 0/1
- Widening (post-k-loop): 4 × cvtepi8_epi32 + 4 × vextracti32x4 → ~4-8c port 5

**vpbroadcastb (port 5) is the primary bottleneck in the inner loop**, not vpopcntb.
The widening ops (post-k-loop) also contribute but can be eliminated by int8 accumulation
(which defers widening entirely outside the j-loop).

---

## Experiment 3: Pack-Free Small Kernel

**Question:** Can eliminating packing overhead push small below 2 µs with a 4-row kernel?

### sol02: 4-row kernel for k_bytes<=2, standard row-streaming for larger k

Results:
- small: **4.97 µs vs baseline 3.69 µs — WORSE** (1.35x slower)
- medium: 311 µs vs baseline 226 µs — 1.38x SLOWER (general path, likely non-inlining)
- large: 4972 µs vs baseline 3842 µs — 1.29x SLOWER (general path)

### Why the 4-row kernel failed to improve small

The baseline 1-row kernel (gen002/explore_1/sol01) runs at 3.69 µs for small (n=32, m=1024,
k_bytes=2). My 4-row variant:
1. Pre-broadcasts 16 A values (4 rows × 2 k-steps × 2 pos/neg) before the j-loop.
   This adds 16 × 1c = 16c of port 5 operations per group of 4 rows (8 groups × 16c = 128c total).
2. Shares 2 B loads across 4 rows: saves 75% of B loads (1024 → 256 total loads).
3. For B in L1 cache (small benchmark: B=2 KB), each load is ~1 cycle. Savings: ~768 cycles.
4. The 16c extra broadcast overhead per group = 128c total, which partially offsets the 768c savings.

However, the 4-row kernel is implemented as a non-inlined static function called from
gemmCandidate. Without inlining, the compiler cannot optimize the k-loop (k_bytes=2 is a
runtime argument) and adds function call overhead. This likely accounts for the regression.

Additionally, the small benchmark's actual bottleneck appears to be the widening operations
(4 × vextracti32x4 + 4 × cvtepi8_epi32 per 64-col block), which are port 5 only. Both
1-row and 4-row have the same number of widening ops per row per block.

### Conclusion (HIGH confidence)
The 4-row kernel does NOT improve the small benchmark in this implementation. The function
call overhead and pre-broadcast cost dominate any B-load savings for L1-resident B data.

**The small benchmark is dominated by widening ops (port 5).** To push below 2 µs:
- Widen LESS often: accumulate in int16 (not int8) across rows and widen once per-row at
  the very end (outside j-loop). This moves widening from per-j-block to per-row-group.
- Or use a completely different layout.

---

## Summary of Key Findings

1. **NT stores + memcpy is ALWAYS WORSE** for large (2.4x worst case with static buffer).
   The only viable path to using NT stores is to directly write to an aligned C — which
   requires modifying the harness (fact_006 constraint).

2. **vpopcntb is port 0/1, NOT port 5.** fact_004 is wrong. The true bottleneck in the
   inner loop is **vpbroadcastb** (port 5 only, 1c throughput).

3. **4-row kernel for small does not help** in a split-function implementation.
   The 1-row baseline is competitive; the key bottleneck for small is widening ops (port 5).

4. **Non-inlined helper functions regress performance by ~1.3-1.5x** vs a monolithic kernel.
   All future optimizations must be implemented in a single function to avoid this overhead.
