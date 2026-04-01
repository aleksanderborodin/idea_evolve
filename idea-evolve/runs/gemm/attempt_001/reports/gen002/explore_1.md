# Debrief Report — gen002 explore_1

**Agent:** explore_1
**Generation:** 002
**Approach:** Row-streaming no-pack kernel (forbidden: BLIS packing, tiling, pre-allocated buffers)
**Best result:** sol06 — **150.04 µs** (geo-mean of 3 sizes, lower is better)
**Gen best at start:** 148.18 µs
**Target:** 24 µs

## Solution Scores

| File | Fitness (µs) | Small (µs) | Medium (µs) | Large (µs) | Notes |
|------|-------------|-----------|------------|-----------|-------|
| sol01.py | 257.92 | 5.91 | 419.65 | 6913.71 | 1-row baseline, streaming B reads |
| sol02.py | 359.42 | 8.23 | 1032.89 | 5463.73 | 2-row with stack pre-broadcast arrays — REGRESSED (stack spill) |
| sol03.py | 193.76 | 4.53 | 358.92 | 4469.59 | 2-row inline A loading |
| sol04.py | 162.34 | 3.25 | 277.16 | 4749.48 | 2-row + streaming stores for m≥4096 |
| sol05.py | 243.30 | 5.62 | 490.19 | 5227.36 | Function-based pre-broadcast — REGRESSED |
| **sol06.py** | **150.04** | **3.26** | **266.09** | **3899.59** | **BEST: 2-row+stream stores + B 64-col micro-pack for large** |
| sol07.py | 183.28 | 3.31 | 406.63 | 4571.43 | Micro-pack applied to medium too — REGRESSED (stride C writes) |
| sol08.py | 160.95 | 3.05 | 277.34 | 4923.15 | NC=256 panel pack for medium — still worse than sol06 |

## What Worked

1. **2-row unrolling with inline A loading** (sol03): Broadcasting each A byte as `_mm512_set1_epi8` inline rather than pre-storing to arrays avoids stack spill. 26% speedup over 1-row (258→194 µs).

2. **Streaming stores** (sol04): `_mm512_stream_si512` for m≥4096 bypasses write-allocate on output matrix C. Critical for medium (m=16384) and large (m=65536). 16% gain (194→162 µs).

3. **B 64-col micro-pack for large** (sol06): For k_bytes≥5, packing each 64-column B chunk to an aligned stack buffer before iterating all n=128 rows converts ~28MB of repeated L2 reads into one 448KB L2 read + L1 reuse. Large improved 46% (6914→3900 µs). Overall geo-mean improved to **150.04 µs**.

## What Failed

- **Stack pre-broadcast arrays** (sol02): Pre-broadcasting 28 A registers into `__m512i a[32]` on the stack caused 8KB stack frame and register spilling. 2x regression.
- **B micro-pack for medium** (sol07, sol08): Medium (m=16384) uses non-sequential C row writes when iterating by B panel. Stride-access C rows (spaced 64KB apart) overwhelms write-combining buffers. NC=256 panel pack also failed to beat sequential 2-row approach.

## Correctness Issues Found and Fixed

- **Wrong ternarylogic truth tables**: Initial constants 0xCA/0xAC were incorrect. Intel vpternlogd indexes src bits as `(src1<<2)|(src2<<1)|(src3<<0)`. Correct: 0xD8 for pos_contrib, 0xE4 for neg_contrib.
- **int8 overflow for k_bytes=32**: Correctness test uses k=256 (k_bytes=32). Max int8 diff per step is ±8; after 16 steps ±128 overflows. Fixed: flush int8→int32 accumulator every 15 k-iterations.

## Ideas for Future Agents

1. **4-row unrolling for large**: sol06 processes 1 row per B-cache-load. Unrolling to 4 rows would amortize the B micro-pack memcpy cost over 4× more compute. Est. 25% gain on large.

2. **Software prefetch on B**: Add `_mm_prefetch` for the next B chunk during current row processing. For large, B micro-pack memcpy is sequential but the CPU may not prefetch inner-loop L2→L1 aggressively enough.

3. **Medium: fix C stride in panel packing**: sol07/sol08 regressed because C rows are written non-sequentially when iterating by B panel. Solution: transpose the loop order so j (B panel) is outermost and rows i are inner — writing C[i][j0..j0+NC] before advancing i. This is essentially what sol06 does for large but needs to also work for medium.

4. **VNNI-based approach**: `_mm512_dpbusd_epi32` (VNNI) can compute 4-bit dot products. Ternary values could be re-encoded to exploit VNNI's 8-bit SAD arithmetic for higher throughput.

5. **Prefetch A rows**: For large with 128 rows and k_bytes=7, streaming A sequentially; add prefetch of next A row during current B-chunk computation.

## Conclusion

sol06 at **150.04 µs** is 1.3% slower than the generation best (148.18 µs). The row-streaming architecture is competitive at small/medium but trails on large due to memory bandwidth constraints on B. The key insight is that B micro-packing is essential for large but must be structured to maintain sequential C writes.
