# Research Agent Report — Generation 1

## What I Researched

I surveyed the binary-ternary GEMM optimization landscape with the following coverage:

1. **Baseline code analysis**: Read and analyzed V14opt.cpp, final.cpp (V19), micro_kernel.cpp (V12-V18), baseline.cpp. The V14opt baseline is an AVX2 BLIS-style GEMM with a 4×32 micro-kernel using LUT-based popcount.

2. **AVX-512 instruction capabilities**: Investigated BITALG (`vpopcntb`), VNNI (`vpdpbusd`), and `vpternlogd` for this problem. Found that `vpopcntb` is the single highest-impact instruction available, and `vpternlogd` can fuse 3-input boolean expressions into 1 instruction.

3. **Tiger Lake microarchitecture**: Confirmed no frequency downclocking for AVX-512 (unlike Skylake-X), 32 zmm registers, port 0/5 execution units. Baseline's LUT popcount is port-5-bound (two `vpshufb` per chunk). Switching to `vpopcntb` + `vpternlogd` balances across ports 0 and 5.

4. **Production binary/ternary NN inference**: Investigated BitNet.cpp (Microsoft) which achieves 2.37-6.17x on x86 for ternary weight LLM inference. Their kernels use LUT-based or I2_S direct approaches, but for our tiny k (2-7 bytes), the direct bitwise-popcount approach is superior — LUT overhead doesn't amortize.

5. **Non-temporal stores**: Confirmed that for the 32 MB output of the large benchmark, non-temporal stores eliminate read-for-ownership overhead, saving an estimated ~6% on the large benchmark.

6. **Cache/tile sizing**: Calculated that for our problem's k_bytes ≤ 7, the entire B matrix can fit in L2 (448 KB for large) and A always fits in L1. The KC tiling dimension is entirely unnecessary and should be removed.

7. **vpternlogd truth table analysis**: Worked out that `(a_pos | b) & (a_neg | ~b)` = `vpternlogd(a_pos, a_neg, b, 0xCA)` and `(a_pos | ~b) & (a_neg | b)` = `vpternlogd(a_pos, a_neg, b, 0xAC)`. This replaces 6-7 bitwise instructions with 2 per row per k-step.

## What Information I Lacked

1. **Actual Agner Fog / uops.info measurements for Tiger Lake**: I could not access the instruction tables to get precise throughput/latency for `vpopcntb`, `vpternlogd`, and `vpmovzxbd` on Tiger Lake. I relied on the fact_004 values which appear user-provided. The `vpternlogd` throughput is listed as 0.5 cycles (ports 0+5 both capable) in general AVX-512 docs but I couldn't verify this for Willow Cove specifically.

2. **Measured B-packing overhead**: I don't know what fraction of total time is spent in pack_B vs. the micro-kernel. For the large benchmark, B-packing scans 7 × 65536 = 448 KB with strided access. If packing takes >10% of time, SIMD packing (Finding 8) becomes important.

3. **C-pointer alignment**: The problem spec says C is `int32*` pre-allocated by the harness. I don't know if it's 64-byte aligned. This affects whether `_mm512_stream_si512` can be used without masking overhead.

4. **Actual speedup from each optimization in isolation**: Without running experiments, all speedup estimates are theoretical. The interaction effects (e.g., does widening from 32→64 columns per kernel call change the cache behavior enough to hurt or help?) are uncertain.

5. **BitNet.cpp x86 kernel source details**: The paper described high-level strategies but the actual SIMD intrinsics used in their AVX2 kernels were not disclosed in the accessible version.

## What Facts Might Be Wrong

1. **vpternlogd imm8 values**: The truth table derivation for `(a_pos | b) & (a_neg | ~b)` = 0xCA and `(a_pos | ~b) & (a_neg | b)` = 0xAC should be verified by code. A mistake here produces silently wrong results — the hardest class of bug.

2. **"Tiger Lake doesn't downclock for AVX-512"**: fact_003 states this. It is true for Tiger Lake (11th gen Willow Cove) but NOT for Ice Lake (10th gen Sunny Cove) or Skylake-X. Since the machine is confirmed i5-1135G7 (Tiger Lake), this should be correct, but worth double-checking since it fundamentally changes whether AVX-512 is beneficial.

3. **Port assignments in fact_004**: `vpopcntb` on "port 5" is consistent with literature for ICL/TGL, but the 0.5c throughput for bitwise ops (two per cycle) assumes the CPU can dispatch to both port 0 and port 5 simultaneously. In practice, structural hazards and instruction decoding overhead may reduce this.

4. **int16 overflow safety claim**: I stated k_bytes ≤ 7 → max diff ≤ ±56 fits in int16. This is correct if each byte contributes at most ±8 to the diff. The formula is: `diff_byte = popcount(u_pos_byte) - popcount(u_neg_byte)`. Max diff per byte = +8 (u_pos all 1s, u_neg all 0s) or -8. Over 7 bytes: ±56. int16 range is ±32767. Safe. However, if KC or k_bytes could ever exceed ~4000 (extremely unlikely given benchmark k_bytes 2-7), int16 would overflow.

5. **Non-temporal store alignment**: I stated `_mm512_stream_si512` requires 64-byte alignment. This is the documented requirement. If alignment isn't guaranteed, using `_mm256_stream_si256` (32-byte requirement) or a fallback is needed.

## What I Would Do Differently With More Time

1. **Actually measure instruction throughput**: Run `perf stat` with hardware counters (port utilization) on the baseline V14opt to know where cycles are actually going. The theoretical analysis may be wrong about the bottleneck.

2. **Prototype and measure each optimization in isolation**: Build a standalone microbenchmark that just times the micro-kernel at various configurations (4×32 AVX2 LUT, 4×64 AVX-512 popcnt, 8×64 AVX-512 popcnt+ternlog, etc.) against synthetic data.

3. **Verify vpternlogd truth tables with a correctness test**: Write a scalar version, an AVX-512 version, check agreement on random inputs before using it in the full kernel.

4. **Check bitnet.cpp source code on GitHub**: The Microsoft BitNet repository is public. Reading the actual `kernel/ggml-cpu/ggml-quants.c` or equivalent AVX2/AVX-512 kernel would give ground truth about what approaches work in production.

5. **Profile the exact benchmark sizes**: The small benchmark (32×1024×2) is likely compute-bound in the micro-kernel. The large (128×65536×7) is likely memory-bandwidth-bound. Understanding which regime each size is in determines which optimizations matter most for the geometric mean.

## Specific Experiments to Run

In priority order:

1. **AVX-512 4×64 with `_mm512_popcnt_epi8`** (lowest risk, highest expected gain): Drop-in replacement of the micro-kernel, keeping BLIS structure. Should give ~2-3x alone. Expected score: ~250-400 µs.

2. **Add `vpternlogd` to the 4×64 kernel**: Replace `(a|b)&(c|~b)` pattern with ternary logic instructions. Verify correctness with a comparison test first.

3. **8×64 micro-kernel with int16 accum**: Process 8 rows, accumulate in int16, widen once at end. If register pressure is too high, fall back to 4×64 with int16 accum.

4. **Remove KC tiling, add size-specific k-loop unrolling**: Use `switch(k_bytes)` to dispatch to unrolled specializations.

5. **Tune NC for each benchmark**: Larger NC = fewer pack_B calls. Try NC=64, 128, 256, 512, 1024, 4096 and measure.

6. **Non-temporal stores for large benchmark**: Add NT stores for C writes when aligned. Measure impact specifically on the 128×65536×7 case.

## What Surprised Me

1. **k is tiny and the KC loop is completely unnecessary**: I expected KC to be used for larger k values. The fact that k is always 2-7 bytes means the entire inner dimension fits in registers. The BLIS 5-loop structure with KC tiling is essentially dead code for this problem. This is a significant oversight in V14opt that the exploration agents should prioritize.

2. **vpternlogd eliminates ~b precomputation entirely**: In V14opt, `v_not_b = _mm256_andnot_si256(v_b, mask_ff)` is precomputed and stored. With `vpternlogd`, this register is unnecessary — the truth table computes ~b implicitly as part of the 3-input logic. This saves one register and one instruction per k-step.

3. **Whole B matrix fits in L2**: For all three benchmarks, the entire B matrix (max 448 KB for large) fits within Tiger Lake's 1.25 MB L2 cache. This means if we pack B once and iterate over all A rows, B data stays hot. This is much more favorable than I initially expected.

4. **BitNet.cpp doesn't use AVX-512 aggressively**: For a production inference framework targeting x86, it primarily uses AVX2 and relies on compiler optimizations for the I2_S kernel. This suggests AVX-512 manual optimization for ternary inference is still an open area — our problem may benefit from being on the frontier of what's been hand-tuned.

5. **int8 accumulation may be entirely safe throughout**: With k_bytes ≤ 7 and max per-byte diff of ±8, the accumulated diff is ≤ ±56 after all k iterations. int8 range is ±127. If we accumulate in int8 (using `_mm512_adds_epi8` for saturation safety), we can fit 64 accumulated diffs in a single zmm register, requiring only 1 zmm accumulator per row instead of 2 (for int16). This merits exploration and could enable even wider micro-kernels.
