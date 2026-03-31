# Research Findings — Binary/Ternary GEMM Optimization

## Summary

The baseline V14opt is an AVX2 BLIS-style kernel with LUT-based popcount (6 instructions per 32-byte chunk). The most impactful single change is replacing this with AVX-512 `_mm512_popcnt_epi8` (1 instruction per 64-byte chunk), doubling throughput and width simultaneously — a potential ~3-4x speedup in the compute-bound inner loop. Additional gains come from micro-kernel widening (8×64), int16 accumulation, k-loop specialization for the tiny k sizes (2-7 bytes), and non-temporal stores for the 32 MB output of the large benchmark.

---

## Finding 1: AVX-512 Hardware Popcount Replaces 6-Instruction LUT

**Relevance**: All ideas (idea_001 central)
**Detail**: The baseline uses a 6-instruction nibble LUT: `and`, `srli`, `and`, `shuffle`, `shuffle`, `add` — consuming two `vpshufb` and four other instructions per 32 bytes. AVX-512 BITALG provides `vpopcntb` (encoded as `_mm512_popcnt_epi8`), which counts bits per byte in a single instruction on a 512-bit register (64 bytes). According to fact_004, `vpopcntb` runs at 1-cycle throughput on port 5. The LUT pair on AVX2 ran at ~3-4 cycles per 32-byte chunk. Switching to AVX-512: (a) processes 64 bytes instead of 32, doubling width, (b) uses 1 instruction instead of 6, reducing instruction pressure. Conservative estimate: 4-5x reduction in popcount cost. Since popcount is the hottest operation (called twice per row per k-byte in the micro-kernel), this is transformative.

**Key intrinsics**:
- `_mm512_popcnt_epi8(v)` — per-byte popcount in 1 cycle
- `_mm512_loadu_si512(ptr)` — load 64 bytes of packed B in 1 instruction (was 1 `_mm256_loadu_si256` for 32 bytes)
- `_mm512_or_si512`, `_mm512_and_si512`, `_mm512_andnot_si512` — AVX-512 width, 0.5 cycle throughput

**Estimated speedup**: 2-4x in micro-kernel compute throughput
**Implementation difficulty**: Low — near drop-in replacement
**Which benchmarks**: All (small, medium, large)
**Actionable implication**: Rewrite micro-kernel to use zmm registers. Process 64 columns of B instead of 32. Replace `fast_popcount_epi8` with `_mm512_popcnt_epi8`.

---

## Finding 2: Accumulate in int16, Widen to int32 Only at End

**Relevance**: idea_004
**Detail**: In V14opt, each byte of `diff = popcount_pos - popcount_neg` is widened to int32 via `_mm256_cvtepi8_epi32` immediately — expanding 8 bytes → 8×int32 = 32 bytes. This requires 4 `cvtepi8_epi32` calls per row per k-step plus 4 `add_epi32`. With k_bytes ≤ 7, the maximum accumulated diff per output column is ±7×8 = ±56, which comfortably fits in int8 (range ±127). So we can accumulate the diff bytes directly without widening, use `_mm512_add_epi8`, and only widen to int32 at the very end (once after the k-loop).

However, if we widen to int16 (not int32): `_mm512_cvtepi8_epi16` widens 64 int8 → 32 int16, keeping 2x more elements in a register. With k_bytes=7, accumulated diff per column ≤ ±56, well within int16 range (±32767). We accumulate in int16, then widen to int32 once per micro-kernel call. This doubles the number of C-columns we compute per accumulator register.

**For the AVX-512 4×64 micro-kernel with int16 accum**:
- Per k-step: 2×`popcnt_epi8` (64-byte), 1×`sub_epi8` → 1×`cvtepi8_epi16` giving 32 int16 diffs → `add_epi16` accumulator (32 int16 = 1 zmm)
- Per row of A: 1 zmm accumulator covers 32 B-columns in int16
- After k-loop: 2×`cvtepi16_epi32` to convert 32 int16 → two 16×int32 zmm regs for C-store

**Estimated speedup**: 1.2-1.5x additional (fewer widening ops, more parallel accumulation)
**Implementation difficulty**: Medium — requires tracking overflow bounds; safe for k_bytes ≤ 15
**Which benchmarks**: All (k_bytes 2, 4, 7 all safe)
**Actionable implication**: Replace 4×`_mm256_cvtepi8_epi32` per row per k-step with 1×`_mm512_cvtepi8_epi16` after k-loop completion.

---

## Finding 3: Wider Micro-Kernel 8×64 Exploits All 32 zmm Registers

**Relevance**: idea_009
**Detail**: AVX-512 provides 32 zmm registers (vs 16 ymm in AVX2). V14opt's 4×32 micro-kernel uses 4 rows × 4 accumulators = 16 registers — exactly filling AVX2's register file. With AVX-512's 32 registers, an 8×64 micro-kernel uses 8 rows × 2 accumulators (int16) = 16 registers, leaving 16 free for B data, A broadcasts, and temporaries. The 8×64 shape processes twice as many output elements per kernel call:
- Halves the number of micro-kernel invocations → less function-call and loop overhead
- Each k-step: load 1 zmm of B (64 bytes), broadcast 8 scalar A values, compute 8 rows simultaneously
- B data is loaded once and reused across 8 rows (vs 4 rows in V14opt) — better B-cache utilization

**Register layout for 8×64 with int16 accum (1 zmm per row = 32 int16)**:
- zmm0..zmm7: 8 accumulators (one per A row, covering 32 B columns each in int16)
- zmm8: current 64-byte B chunk
- zmm9..zmm16: 8 broadcast A values (can preload next)
- zmm17..zmm31: free for temps, second B chunk, prefetch buffers

**Estimated speedup**: 1.3-1.5x additional (half the micro-kernel call overhead, better B reuse)
**Implementation difficulty**: Medium
**Which benchmarks**: Medium and large (overhead amortization matters most when many k-iterations run; for small k=2, startup cost matters less)
**Actionable implication**: Change micro_kernel to process 8 rows of A at once. Use `_mm512_set1_epi8` to broadcast each A byte.

---

## Finding 4: k-Loop Specialization Eliminates All Loop Overhead

**Relevance**: idea_002
**Detail**: k_bytes is exactly 2, 4, or 7 for our three benchmark sizes. KC=128 in V14opt far exceeds k_bytes, so the KC loop always iterates exactly once. But inside the micro-kernel, the k-loop runs 2, 4, or 7 times — and each iteration involves: loop counter increment, compare, branch, plus memory pointer arithmetic. With k=2, this 2-instruction body loop overhead is ~20-30% of compute. Full unrolling gives the compiler visibility to schedule instructions optimally and hoist invariant computations.

**Implementation approach**: `switch(k_bytes) { case 2: ... case 4: ... case 7: ... }` with fully unrolled inner loops, or a template `<int K>` specialization.

For k=2: entire inner product is 2 iterations. Total per output cell (64 B cols): 2×(2 popcnt + bitwise + sub) + 1×widen = ~20 instructions.
For k=7: 7 iterations, more compute-bound — loop overhead relatively smaller.

**Estimated speedup**: 1.1-1.3x for small benchmark, 1.05-1.1x for large
**Implementation difficulty**: Low-medium
**Which benchmarks**: Small most (k=2), medium (k=4), large (k=7) least
**Actionable implication**: Add `switch(k_bytes)` dispatch before inner loops. Alternatively, let the KC-removal optimization (idea_008) + template specialization handle this.

---

## Finding 5: Remove KC-Tiling Entirely — k Always Fits in Registers

**Relevance**: idea_008
**Detail**: With k_bytes ≤ 7, the entire A matrix (max 128 rows × 7 bytes × 2 = 1792 bytes) fits in L1. The KC loop in V14opt iterates once (KC=128 >> 7). Every call to `pack_A_candidate` and `pack_B_candidate` is doing a full copy for nothing except reformatting for micro-kernel access. The tiling machinery (3 nested loops + buffer allocation + pack calls) adds overhead that is pure waste when k is this small.

**Simplified structure**:
```
for j in range(0, m, NC):           # tile m for B-panel L2 fit
    pack B panel (jc..jc+NC columns, all k_bytes rows)
    for i in range(0, n, MC):        # tile n for A-panel L1 fit
        pack A panel (ic..ic+MC rows, all k_bytes cols)
        for jr in range(0, NC, 64):  # micro-tile: 64 B-columns
            for ir in range(0, MC, 8):  # micro-tile: 8 A-rows
                micro_kernel_8x64(k_bytes, ...)
```

The B-panel pack writes `NC × k_bytes` bytes = (e.g. 1024 × 7) = 7 KB for NC=1024. This fits comfortably in L2 (1.25 MB). A-panel: `MC × k_bytes × 2` = 64 × 7 × 2 = 896 bytes — fits in L1.

**Estimated speedup**: 1.1-1.2x (removes one loop level and unused KC loop)
**Implementation difficulty**: Low
**Which benchmarks**: All
**Actionable implication**: Remove `pc` / KC loop. Set kc = k_bytes. Reorganize outer loops to jc → ic → jr → ir.

---

## Finding 6: Non-Temporal Stores Bypass Cache for 32 MB Output

**Relevance**: idea_006
**Detail**: The large benchmark output C is 128 × 65536 × 4 bytes = 32 MB. During computation, writing accumulated int32 values to C triggers cache-line read-modify-write operations (RFO: read-for-ownership) — each 64-byte cache line must be brought in from memory before being written. Since C will never be read again within the benchmark loop, these RFOs waste memory bandwidth. Non-temporal stores (`_mm512_stream_si512`) write directly to write-combining buffers, bypassing the cache hierarchy entirely — no RFO required.

**Alignment requirement**: `_mm512_stream_si512` requires 64-byte aligned destination. Since C is `int32*` allocated externally, alignment is not guaranteed. Solutions:
1. Pad/align C internally (not possible since it's external)
2. Use masked stores for alignment edges + stream for aligned interior
3. Use `_mm256_stream_si256` (32-byte aligned) which is more forgiving, or use stores with `CLFLUSHOPT`

**Memory bandwidth math**: Large benchmark: 128 × 65536 × 4 = 32 MB output. At 38 GB/s bandwidth, streaming these takes ~0.84 ms. With cached stores + RFO: effectively reading and writing 32 MB → ~1.7 ms for this alone. Non-temporal: ~0.84 ms. Saving ~0.8 ms vs. large benchmark's total of ~12 ms = ~6% improvement from this alone.

**Also relevant for zero initialization**: `memset` on 32 MB is ~0.84 ms with streaming. Consider using `_mm512_stream_si512` for the zero-fill too, or omitting C initialization if guaranteed zero from the caller (it is not — must zero per spec).

**Estimated speedup**: 1.05-1.15x for large benchmark specifically
**Implementation difficulty**: Medium (alignment handling is tricky)
**Which benchmarks**: Large primarily
**Actionable implication**: In the C-store section of the micro-kernel, use `_mm512_stream_si512` when NC tile boundaries are 64-byte aligned. Add `_mm_sfence()` after streaming stores.

---

## Finding 7: vpternlogd Can Fuse OR+AND Logic — Reduce Instruction Count

**Relevance**: idea_003 partial
**Detail**: The core binary-ternary formula per byte is:
```
pos_result = (a_pos | b) & (a_neg | ~b)
neg_result = (a_pos | ~b) & (a_neg | b)
```
Each line is a 3-input bitwise expression. `vpternlogd` computes any bitwise function of 3 inputs in 1 instruction using an 8-bit truth table. The above expressions can each be computed with a single `vpternlogd`:

- `(a_pos | b) & (a_neg | ~b)` = vpternlogd(a_pos, a_neg, b, imm8=?)
  - Bit logic: for each bit position, look up {a_pos_bit, a_neg_bit, b_bit} → (a_pos|b)&(a_neg|~b)
  - Truth table: (0,0,0)→0, (0,0,1)→0, (0,1,0)→1, (0,1,1)→0, (1,0,0)→0, (1,0,1)→1, (1,1,0)→1, (1,1,1)→1
  - imm8 = 0b11001010 = 0xCA

- `(a_pos | ~b) & (a_neg | b)` — same inputs, different truth table
  - Truth table: (0,0,0)→0, (0,0,1)→0, (0,1,0)→1, (0,1,1)→1, (1,0,0)→0, (1,0,1)→1, (1,1,0)→0, (1,1,1)→1
  - imm8 = 0b10101100 = 0xAC

**Current code (per row, per k-step)**:
```
or(va_p, v_b), or(va_n, v_not_b), and → u_pos   [3 instructions]
or(va_p, v_not_b), or(va_n, v_b), and → u_neg   [3 instructions + 1 pre-computed ~b]
= 7 instructions (including not-b pre-computation shared)
```
**With vpternlogd**:
```
vpternlogd(va_p, va_n, v_b, 0xCA) → u_pos       [1 instruction]
vpternlogd(va_p, va_n, v_b, 0xAC) → u_neg       [1 instruction]
= 2 instructions (no ~b precomputation needed!)
```
This halves the bitwise instruction count per row from 6-7 to 2. Port 0/5 at 0.5c throughput each. Combined with popcnt_epi8 (also port 5), careful scheduling can keep both ports busy.

**Important caveat**: `vpternlogd` operates on 32-bit (dword) or 64-bit (qword) elements — it is NOT byte-granular. For our use case (bitwise operations over a byte array treated as a bit vector), this doesn't matter — we want bitwise boolean operations over all 512 bits at once, and `vpternlogd` delivers exactly that.

**Estimated speedup**: 1.2-1.5x additional on top of AVX-512 popcount upgrade (reduces instruction stream density)
**Implementation difficulty**: Low once truth table values are derived
**Which benchmarks**: All
**Actionable implication**: Replace the 3-instruction `(a|b)&(c|~b)` pattern with `_mm512_ternarylogic_epi32(a, c, b, 0xCA)` for u_pos and `_mm512_ternarylogic_epi32(a, c, b, 0xAC)` for u_neg.

---

## Finding 8: SIMD Packing Can Reduce pack_B Overhead

**Relevance**: idea_007
**Detail**: `pack_B_candidate` is a scalar double-nested loop copying bytes from `B[k * m + j + c]` to `B_packed[(j/32 * kc + k) * 32 + c]`. For the medium benchmark: NC=256, kc=4 → packing 4 × 256 = 1024 bytes in a scalar loop. For large: NC=256 (or larger with re-tuning), kc=7 → 1792 bytes scalar. The stride pattern in B is `m` (1024/16384/65536 bytes between k-rows), so each k-row's 32 bytes are read strided. We need to transpose-pack: k-major → column-major.

With AVX-512: load 64 consecutive bytes from one row of B (one zmm), store to packed buffer. Since kc ≤ 7 and each row segment is NC bytes wide, one pass copies all k-rows at once for NC=64 (1 zmm per k-row). For NC=64: 7 loads + 7 stores = 14 AVX-512 instructions vs. ~7×64 = 448 scalar byte copies.

**Estimated speedup**: 1.05-1.15x overall (packing is not the dominant bottleneck, but improves latency for small/medium)
**Implementation difficulty**: Low
**Which benchmarks**: All, medium most
**Actionable implication**: Replace scalar pack_B loop with AVX-512 loads/stores. For column-chunks that are multiples of 64 bytes, use `_mm512_storeu_si512`.

---

## Finding 9: Tune NC Tile for Better L2 B-Panel Reuse

**Relevance**: idea_005
**Detail**: Current NC=256. With an 8×64 micro-kernel and AVX-512, the B-panel needs to fit in L2 (1.25 MB). For the large benchmark with kc=k_bytes=7:
- NC=1024: B-panel = 1024 × 7 = 7 KB — fits in L1
- NC=4096: B-panel = 4096 × 7 = 28 KB — fits in L1 (< 48 KB L1d)
- NC=16384: B-panel = 16384 × 7 = 112 KB — fits in L2 (< 1.25 MB)
- NC=65536 (entire m): B-panel = 65536 × 7 = 448 KB — fits in L2!

This means for the large benchmark, we can potentially pack the entire B matrix once and iterate over all n rows, avoiding repeated B packing. The A matrix (128 × 7 × 2 = 1792 bytes) always fits in L1.

**Optimal strategy for each benchmark**:
- Small (m=1024, k=2): NC=1024 (full m), kc=2. B-panel = 2 KB — in L1. No NC tiling needed.
- Medium (m=16384, k=4): NC=4096 or 8192, kc=4. B-panel = 16-32 KB — in L1/L2.
- Large (m=65536, k=7): NC=16384 or 32768, kc=7. B-panel = 112-224 KB — in L2.

Increasing NC reduces re-packing overhead and keeps B in cache longer for all n-rows.

**Estimated speedup**: 1.1-1.2x (better cache utilization, fewer pack_B calls)
**Implementation difficulty**: Medium (requires size-specific NC selection)
**Which benchmarks**: All, large most
**Actionable implication**: Set NC dynamically: `NC = min(m, L2_BYTES / k_bytes)`. For m=65536 and k=7: NC = min(65536, 1250000/7) ≈ 65536 — process all of m in one B-panel.

---

## Finding 10: Port Contention Analysis — Port 5 Pressure

**Relevance**: fact_003, fact_004
**Detail**: Tiger Lake Willow Cove has AVX-512 execution units on port 0 and port 5. From fact_004:
- `vpopcntb` → port 5, 1c throughput
- `vpshufb` → port 5, 1c throughput
- bitwise AND/OR → port 0 or 5, 0.5c throughput
- `vpmovzxbd`/`vpmovsxbd` → port 5, 1c throughput

With AVX2 LUT popcount: the two `vpshufb` instructions dominate port 5. With AVX-512 `vpopcntb` replacing LUT: only 2 popcnt calls per k-step remain on port 5. If we also use `vpternlogd` for the boolean logic (port 0), we shift work from port 5 to port 0, creating better balance.

**Port 5 per micro-kernel step (AVX2 baseline)**:
- 2 rows × 2×`vpshufb` per popcnt × 2 popcnt per row = 8 vpshufb per k-step → port 5 bottleneck

**Port pressure with AVX-512 changes**:
- 2×`vpopcntb` (port 5) + 2×`vpternlogd` (port 0) = balanced
- Adding int16 accumulation: `_mm512_cvtepi8_epi16` (port 5) once per k-loop end = minor

**Key insight**: The AVX2 kernel is port-5-bound. Switching to AVX-512 with vpternlogd distributes work across both ports. With a well-scheduled 8-row kernel, sustained throughput approaches 2 operations/cycle.

**Estimated speedup**: Already captured in Findings 1, 2, 7 combined
**Implementation difficulty**: N/A (microarchitecture-level consideration for scheduling)
**Which benchmarks**: All
**Actionable implication**: Structure the AVX-512 kernel to interleave port-0 (ternary logic) and port-5 (popcnt) instructions. Let the compiler/OOO handle fine-grained scheduling.

---

## Finding 11: VNNI (`vpdpbusd`) Is NOT Directly Applicable

**Relevance**: idea_003
**Detail**: `vpdpbusd` computes `C += dot(A_uint8, B_int8)` — it multiplies 8-bit unsigned A by 8-bit signed B and accumulates into int32. The binary-ternary multiply problem uses bit-packed data where individual element products are computed via bitwise operations, not integer multiplication. The ternary values {-1,0,+1} are stored as two bit-planes (pos_bits, neg_bits), not as sign-magnitude integers. The binary values {-1,+1} are stored as 1 bit per element (0=+1, 1=-1).

To use VNNI, we'd need to decode the bit-packed ternary/binary values back to integer form first (expand 8 bits → 8 × int8 values), then call VNNI. This decoding step costs more than the operation saves. The popcount approach is inherently more efficient for bit-packed data.

**Conclusion**: VNNI does not apply here. The bit-packing and bitwise-popcount approach used in V14opt is the correct abstraction for this data format.

**Estimated speedup**: 0 (not applicable)
**Implementation difficulty**: N/A
**Which benchmarks**: N/A
**Actionable implication**: Do not pursue VNNI for this computation. Focus on popcnt + ternary logic approach.

---

## Finding 12: BitNet.cpp Production Evidence for LUT Kernels

**Relevance**: Corroborates idea direction
**Detail**: Microsoft's BitNet.cpp (published 2024-2025) achieves 2.37x to 6.17x speedup on x86 for ternary weight LLM inference. Their I2_S kernel for x86 uses 2-bit packed weights (matching our ternary encoding) with SIMD unpack to perform multiply-accumulate. Their TL1/TL2 kernels use lookup tables for blocks of weights. The speedups are relative to non-quantized baseline with much larger k dimensions (LLM matrix sizes >> our k=2-7). For our tiny k problem, the LUT overhead doesn't amortize — the direct bitwise-popcount approach remains superior.

The key insight from BitNet.cpp research: for ternary weights, `int16` intermediate accumulation is standard practice (to handle {-1,0,+1} × {-1,+1} = {-1,0,+1} products that sum to at most ±k). This confirms idea_004's correctness.

**Estimated speedup**: N/A (indirect confirmation)
**Implementation difficulty**: N/A
**Which benchmarks**: N/A
**Actionable implication**: The industry direction confirms our AVX-512 popcount + int16 accumulation approach. No need to implement LUT-based kernels for this problem's k sizes.

---

## Combined Expected Improvement

Applying findings together (multiplicative, rough estimates):
| Optimization | Estimated speedup |
|---|---|
| AVX-512 hardware popcnt + 2× width (Finding 1) | 2.5-4× micro-kernel |
| vpternlogd fused logic (Finding 7) | 1.2-1.5× additional |
| 8-row micro-kernel (Finding 3) | 1.3-1.5× overhead reduction |
| k-loop specialization (Finding 4) | 1.1-1.3× |
| Remove KC-tiling (Finding 5) | 1.1-1.2× |
| NC tuning (Finding 9) | 1.1-1.2× |
| Non-temporal stores (Finding 6) | 1.05-1.15× (large only) |
| int16 accumulation (Finding 2) | 1.2-1.5× |

**Combined rough estimate**: 6-20× potential improvement. Actual gains will be lower due to memory-bandwidth bottlenecks (especially large benchmark). Target of 477 µs (1.6× speedup) is very achievable; aggressive implementation may reach 3-5× on large.

---

## Open Questions

1. **Are aligned stores available for C?** The C pointer alignment is unknown. If unaligned, streaming stores require mask handling or alignment padding, complicating the micro-kernel's write path.

2. **Port 5 saturation at 8-row kernels**: With 8 rows × 2 `vpopcntb` per k-step = 16 port-5 ops per k-step. At 1c throughput each, that's 16 cycles for 8×64=512 multiply-accumulate operations. Combined with vpternlogd (port 0): total ~16-24 cycle micro-kernel inner loop per k-step. Is there ILP headroom? Measurement needed.

3. **Does int8 accumulation (no widening at all) work?** With k_bytes=7, max diff per column is ±7×8=±56, which fits in int8 (±127). If we accumulate 7 iterations in int8 (using `_mm512_add_epi8`), then widen once, we avoid all mid-kernel widening. But int8 subtraction (`sub_epi8`) is already being used for `diff = popcnt_pos - popcnt_neg`, and int8 add saturates — we'd need to be careful. Could be investigated.

4. **Pack_B efficiency with large stride**: For the large benchmark, B is laid out as `B[k_byte * m + j]`. With m=65536 (65 KB per k-row), reading 64 bytes from each of 7 k-rows involves 7 cache-line reads from 7 locations spaced 65 KB apart. This is sequential within each k-row but the 7 different rows compete for TLB and L2 prefetch. Hardware prefetcher may handle it, but measuring B-packing time separately would be valuable.

5. **What tile dimensions maximize throughput on the actual machine?** The estimates above are theoretical. The actual optimal MC, NC, micro-kernel shape (4×64 vs 8×64 vs 4×128) depend on Tiger Lake's out-of-order window depth, L1 bank conflicts, and write-buffer capacity. Empirical tuning via `evaluate.py` is essential.

6. **Does vpternlogd imm8 = 0xCA correctly compute `(a|b)&(c|~b)`?** The truth table derivation above should be verified in code before relying on it.
