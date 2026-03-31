# Binary-Ternary Matrix Multiplication Optimization

## Challenge

Optimize a specialized matrix multiplication kernel for **binary-ternary neural network inference**
on a specific CPU (Intel i5-1135G7, Tiger Lake). One matrix has ternary values {-1, 0, +1}, the
other has binary values {-1, +1}. Both are bit-packed for density.

Your goal: write C++ code that computes this multiplication **as fast as possible** on this exact CPU,
beating the current best implementation.

## How It Works

### Data Encoding

**Matrix A** (ternary, {-1, 0, +1}):
- Packed as 2 bits per element using two bitplanes: `pos_bits` and `neg_bits`
- For each group of 8 ternary values: 2 bytes (pos byte, neg byte)
- `pos_bits[i]` = 1 if `A[i] == +1`, else 0
- `neg_bits[i]` = 1 if `A[i] == -1`, else 0
- If `A[i] == 0`: both bits are 0
- Layout: `A[(row * k_bytes + t) * 2]` = pos byte, `A[(row * k_bytes + t) * 2 + 1]` = neg byte

**Matrix B** (binary, {-1, +1}):
- Packed as 1 bit per element, transposed by k-dimension
- 8 consecutive k-rows at the same column j are packed into 1 byte
- `B[t * m + j]` = byte containing 8 binary values
- Bit set = original value was -1

**Result C** is `int32[n × m]`.

### Core Formula

For each byte of packed data, the multiply-accumulate is done with bitwise ops + popcount:

```
pos_contrib = popcount((a_pos | b) & (a_neg | ~b))    // counts +1 contributions
neg_contrib = popcount((a_pos | ~b) & (a_neg | b))     // counts -1 contributions
C[i][j] += pos_contrib - neg_contrib
```

This processes 8 element-wise products per byte operation.

### Function Signature

Your solution must define exactly this function:

```cpp
void gemmCandidate(uint8_t* A, uint8_t* B, int* C, int n, int m, int k)
```

Where:
- `A`: ternary-encoded matrix, size `n * k_bytes * 2` bytes (k_bytes = k/8)
- `B`: binary-encoded matrix, size `k_bytes * m` bytes
- `C`: output `int32` matrix, size `n * m` (pre-allocated, you must zero it)
- `n`: number of rows in A / rows in C
- `m`: number of columns in B / columns in C
- `k`: inner dimension **in bits** (always a multiple of 8). k_bytes = k / 8

### Benchmark Sizes

Your code is measured on these 3 sizes (n, m, k_raw → k = 8*(k_raw/8+1)):

| Size | n | m | k (bits) | k_bytes | Notes |
|------|---|---|----------|---------|-------|
| Small  | 32  | 1,024   | 16 | 2 | k fits in registers trivially |
| Medium | 64  | 16,384  | 32 | 4 | m is large, memory-bound |
| Large  | 128 | 65,536  | 56 | 7 | m is huge, cache is critical |

**Key observation:** k is always very small (2-7 bytes). The inner dimension fits entirely in
registers. The bottleneck is iterating over m (columns of B). Optimize for large m, tiny k.

## Scoring

**Fitness = geometric median of wall-clock times (µs)** across all 3 sizes. **Lower is better.**

The baseline is V14opt (BLIS-style AVX2 tiling + LUT popcount micro-kernel).
Baseline median: ~770 µs. The old target of 477 µs has already been beaten.
**NEW TARGET: 24 µs** (~3% of baseline — roughly 32x overall speedup). This is an extremely
aggressive goal requiring fundamentally different approaches, not incremental improvements.
Solutions already exist in the 100-200 µs range — you must go far beyond those.

Per-size reference times fluctuate with system load. What matters is relative improvement:
all candidates are benchmarked under the same conditions (pinned cores, serialized).

- All 3 sizes weighted equally (geometric median of times).
- Correctness is a hard constraint — must match the naive reference (gemmV0) exactly.

## Target CPU: Intel i5-1135G7 (Tiger Lake)

**Cache hierarchy:**
- L1d: 48 KB per core, 12-way, 64B lines, 5-cycle latency
- L2: 1.25 MB per core, 10-way, ~12-cycle latency
- L3: 8 MB shared, ~40-cycle latency

**Available SIMD extensions:**
- SSE4.2, AVX2 (256-bit, 16 × ymm registers)
- **AVX-512** with full extensions:
  - `AVX512F`, `AVX512BW`, `AVX512VL` — base 512-bit ops
  - **`AVX512_VPOPCNTDQ`** — hardware popcount on 512-bit vectors
  - **`AVX512_BITALG`** — `_mm512_popcnt_epi8()` — per-byte popcount in one instruction!
  - **`AVX512_VNNI`** — `_mm512_dpbusd_epi32()` — int8 dot-product accumulate
  - 32 × zmm registers (double AVX2's register file)
- Tiger Lake runs AVX-512 at **full frequency** (no downclocking unlike Skylake-X)

**Key intrinsics for this problem:**
- `_mm512_popcnt_epi8(v)` — replaces the 6-instruction LUT-based popcount with 1 instruction
- `_mm512_set1_epi8(byte)` — broadcast a single byte to all 64 positions
- `_mm512_loadu_si512(ptr)` — load 64 bytes of B at once
- `_mm512_andnot_si512(a, b)` = `~a & b`
- `_mm512_or_si512`, `_mm512_and_si512` — bitwise ops
- `_mm512_sub_epi8` — subtract per-byte
- `_mm512_cvtepi8_epi32` — widen 8-bit to 32-bit (for accumulation)

## What Your Solution Must Do

1. `entrypoint()` returns a **C++ source code string** defining `void gemmCandidate(...)`.
2. The C++ code is compiled with: `g++ -O3 -std=c++17 -march=native -mavx512f -mavx512bw -mavx512vl -mavx512vpopcntdq -mavx512bitalg -mavx512vnni`
3. Correctness is checked against the naive reference on 4 test cases.
4. If correct, performance is benchmarked on the 3 sizes above (10 repetitions each).
5. Fitness = geometric median time in µs (lower = better).

## Available Reference Code

You can read the existing implementations for inspiration:
- `../fast-conv/gemm/baseline.cpp` — naive O(nmk) reference (gemmV0)
- `../fast-conv/gemm/V14opt.cpp` — current best: BLIS-style tiling + AVX2 micro-kernel 4×32
- `../fast-conv/gemm/final.cpp` — V19: BLIS + AVX2 micro-kernel 4×24
- `../fast-conv/gemm/micro_kernel.cpp` — several micro-kernel variants
- `../fast-conv/util/encoder.cpp` — encoding/decoding + popcount utilities
- `../fast-conv/candidate_template.cpp` — V14opt wrapped as gemmCandidate (the baseline)

## Key Optimization Ideas

1. **AVX-512 micro-kernel**: Process 64 columns of B per iteration instead of 32. Use `_mm512_popcnt_epi8` for 1-cycle popcount instead of 6-instruction LUT.

2. **Fully unroll the k-loop**: k is only 2-7 bytes — eliminate all loop overhead with template specialization or manual unrolling.

3. **Tune BLIS tile sizes** for Tiger Lake: MC, KC, NC should match the cache hierarchy.

4. **Accumulate in int16**: The popcount diff per byte is at most ±8. For k_bytes ≤ 15, accumulated diff fits in int16. Widen to int32 less frequently.

5. **Streaming stores**: For huge m (65536), output rows won't be re-read. Use `_mm512_stream_si512`.

6. **Packing with SIMD**: Current pack_A / pack_B are scalar loops. AVX-512 gather/scatter or bulk copies could help.

## Diagnostics

After evaluation, a detailed breakdown is written to a file. The path is returned in the
`detail_file` field of the evaluation result. Read it with `cat` to see per-size timings,
speedups, and compiler warnings.

## Failure Modes to Avoid

- **Incorrect results**: Any mismatch with gemmV0 → `is_valid: 0`, `fitness: 0.0`
- **Compilation failure**: Missing includes, wrong signature, syntax errors → `fitness: 0.0`
- **Not defining gemmCandidate**: The function must be named exactly `gemmCandidate`
- **Forgetting to zero C**: You must `memset(res, 0, n * m * sizeof(int))` at the start
- **Wrong k interpretation**: k is in **bits**, not bytes. k_bytes = k / 8
- **Buffer overflow**: Packed array sizes depend on k_bytes, not k
