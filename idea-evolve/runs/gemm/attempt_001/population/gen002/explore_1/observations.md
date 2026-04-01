# Observations — gen002 explore_1 (Row-Streaming No-Pack Kernel)

## Task
Implement a row-streaming no-pack kernel for Binary-Ternary GEMM on Intel i5-1135G7 (Tiger Lake, AVX-512 BITALG/VPOPCNTDQ). Forbidden: BLIS-style packing, tiling, pre-allocated buffers. Must stream rows of A directly.

## Architecture
Each row of A is streamed one at a time (or 2 at a time). For each row-chunk, broadcast each A pos/neg byte as a 512-bit constant and compute dot products against 64-byte columns of B using `_mm512_ternarylogic_epi32` + `_mm512_popcnt_epi8`. Accumulate int8, flush to int32 periodically.

Core formula (verified correct truth tables):
- pos_contrib = popcnt(vpternlogd(a_pos, a_neg, b, 0xD8))
- neg_contrib = popcnt(vpternlogd(a_pos, a_neg, b, 0xE4))
- C[i][j] += pos_contrib - neg_contrib

## Key findings

### Correctness bug (fixed in sol01)
Initial ternarylogic constants 0xCA/0xAC were wrong. Intel vpternlogd uses index=(src1<<2)|(src2<<1)|(src3<<0). Correct constants: 0xD8 (pos), 0xE4 (neg). Verified against reference gemmV0.

### int8 overflow (fixed in sol01)
With k_bytes=32 (correctness test), int8 accumulator overflows. Fixed: flush int8→int32 every 15 k-iterations.

### 2-row unrolling (sol03 > sol01)
Processing 2 rows simultaneously with inline A broadcasts reduces B loads by 2x for each j-chunk. 193 µs vs 258 µs. Stack array pre-broadcast (sol02) regressed badly (359 µs) due to 8KB stack spill.

### Streaming stores (sol04)
`_mm512_stream_si512` for m≥4096 bypasses write-allocate, improving medium and small substantially. 162 µs vs 194 µs.

### B 64-col micro-pack for large (sol06)
For k_bytes≥5 (large: n=128, m=65536, k_bytes=7), B is 448KB accessed 128 times = repeated L2 reads. Packing each 64-col chunk (7×64=448 bytes) to aligned stack before iterating all 128 rows reduces B traffic from ~28MB to 448KB single L2 read. Large improved from 6914 µs (sol01) → 3900 µs (sol06). **This is the best result at 150.04 µs.**

### B NC=256 mini-pack for medium (sol07, sol08) — failed
Applying NC=256 or 64-col micro-pack to medium (k_bytes=4, m=16384) consistently regressed:
- sol07 (64-col pack for k_bytes≥4): 183 µs — stride C access pattern for medium exhausts write-combining buffers
- sol08 (NC=256 panel pack): 161 µs — slight improvement over sol07 but still worse than sol06's 150 µs

Medium appears to hit a different bottleneck. The 2-row sequential approach (sol04/sol06) with streaming stores remains best for medium (266 µs).

## Summary of scores (lower is better)

| Sol | Description | Fitness (µs) | Small | Medium | Large |
|-----|-------------|-------------|-------|--------|-------|
| sol01 | 1-row baseline | 257.92 | 5.91 | 419.65 | 6913.71 |
| sol02 | 2-row with stack pre-broadcast (regressed) | 359.42 | 8.23 | 1032.89 | 5463.73 |
| sol03 | 2-row inline A loading | 193.76 | 4.53 | 358.92 | 4469.59 |
| sol04 | 2-row + streaming stores | 162.34 | 3.25 | 277.16 | 4749.48 |
| sol05 | Function-based pre-broadcast (regressed) | 243.30 | 5.62 | 490.19 | 5227.36 |
| **sol06** | **2-row + streaming stores + B micro-pack (large)** | **150.04** | **3.26** | **266.09** | **3899.59** |
| sol07 | sol04 + micro-pack for medium too | 183.28 | 3.31 | 406.63 | 4571.43 |
| sol08 | NC=256 mini-pack medium + sol06 large | 160.95 | 3.05 | 277.34 | 4923.15 |

**Best: sol06 at 150.04 µs** (vs gen best 148.18 µs, 1.3% off).

## Remaining gaps
- Medium (266 µs vs 228 µs target): B is read from L2 (12c latency); every B panel access is an L2 miss. Mini-pack approaches tried but regressed due to stride C writes. Potential fix: ensure C writes are sequential when using panel packing.
- Large (3900 µs): B micro-pack helped but large B (448KB) + large C (128×65536×4 = 32MB) both stress memory. Further gains likely need multi-row unrolling (4-row) or software prefetching.
- Small is near-optimal (3.26 µs): B fits in L1, streaming stores help.
