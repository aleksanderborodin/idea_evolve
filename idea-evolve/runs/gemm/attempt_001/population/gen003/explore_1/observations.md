# Observations — explore_1, Gen 3

## Solutions Summary

| File | Fitness (µs) | Valid | small | medium | large | Approach |
|------|-------------|-------|-------|--------|-------|----------|
| sol01.py | 220.33 | Yes | 5.47 | 365.87 | 5349.45 | 1-row row-streaming baseline |
| sol02.py | 168.35 | Yes | 5.24 | 283.62 | 3212.90 | 8-row row-streaming (BEST) |
| sol03.py | 204.52 | Yes | 5.75 | 366.71 | 4057.70 | 4-row row-streaming |
| sol04.py | 184.84 | Yes | 4.00 | 413.02 | 3823.64 | Hybrid: 8-row regular + 1-row NT large |

## Key Findings

### 1. 8-row kernel is the best compute architecture
The 8-row kernel (sol02) outperformed 1-row and 4-row variants. By loading B once and processing 8 rows simultaneously, B memory traffic is reduced 8x. The improvement is most pronounced on large (5349→3212 µs = 40%) where B data reuse matters most.

### 2. NT stores DO NOT help in this harness
Extensive testing of non-temporal stores showed they either don't help or hurt performance:

**Why NT stores fail:**
- **C alignment**: The harness uses `std::vector<int>`. Small allocations (<128KB) are NOT 64-byte aligned, causing segfaults. Large allocations (>128KB) use mmap and ARE page-aligned.
- **WC buffer saturation**: With the 8-row kernel, the flush loop writes to 8 different rows' cache lines (separated by 256KB). This overwhelms the 12 WC buffers, negating NT store benefits.
- **1-row NT stores (sol04)**: Even with WC-friendly sequential writes, the measured large time (3823 µs) was only marginally better than 8-row regular (3212 µs). The 1-row kernel loses the 8x B-load amortization benefit.
- **Aligned buffer approach**: Allocating a temp buffer + memcpy back adds ~2900 µs of overhead (32MB memcpy), completely negating any NT store benefit. Also suffers page fault penalty on first use.

**Conclusion**: NT stores are a dead end for this benchmark configuration. The C alignment constraint and WC buffer limitations make them impractical.

### 3. Single-vpternlog algebraic optimization does not help
Tried computing `diff = 2*popcnt(pos) - nonzero_count` to eliminate one vpternlog + one vpopcntb per iteration. The extra overhead of tracking nonzero counts and applying the correction (shift + subtract) outweighed the instruction savings. The 2-vpternlog approach is faster in practice.

### 4. 128-column processing hurts
Processing 128 columns per iteration (2 B loads per k-byte) caused register spilling and worse performance than 64-column processing.

### 5. Software prefetching has no effect
B fits in L2 (448KB < 1.25MB) for all benchmark sizes. Hardware prefetching is already handling B loads efficiently. Software prefetch hints added overhead without benefit.

### 6. Benchmark variance is ~30-40%
The same solution evaluated twice gives significantly different results (sol02: 168 µs first run, 275 µs second run). This makes it very difficult to reliably evaluate small optimizations. The `Repetitions(10)` + median approach in Google Benchmark helps within a single run, but cross-run variance is high — likely due to system load, thermal throttling, or CPU frequency scaling despite core pinning.

## Bottleneck Analysis

For the large benchmark (128 × 65536 × 7):
- C output = 32 MB
- At regular store bandwidth ~11 GB/s → minimum write time ~2900 µs
- Current 3212 µs → within 10% of write bandwidth limit
- **Large is write-bandwidth bound. No compute optimization can improve it without NT stores.**

For medium (64 × 16384 × 4):
- C output = 4 MB
- At regular store bandwidth ~17 GB/s → minimum write time ~235 µs
- Current 283 µs → within 20% of bandwidth limit
- **Medium is also approaching write-bandwidth limits.**

The 24 µs target requires `(small × medium × large)^(1/3) ≤ 24`, meaning `small × medium × large ≤ 13824`. Even at theoretical minimums (~5 × 235 × 1300 = 1,527,500), the geomean is ~115 µs with NT stores and ~170 µs without. **The 24 µs target appears physically impossible with regular stores and probably needs architectural changes to the harness** (aligned C allocation or direct mmap).

## Unexplored Directions

1. **Column-blocking for cache reuse**: Tile in the j-dimension (column panels) to keep C output tiles in L1/L2 for write-back before moving to the next panel. This could improve write bandwidth utilization.
2. **Interleaved row processing**: Instead of processing all columns for 8 rows, process partial columns, then switch rows to keep C in cache.
3. **VNNI-based approach**: Despite being "debunked," the ternary→binary decomposition could use `_mm512_dpbusd_epi32` if the encoding is restructured.
4. **Assembly inspection**: No solution has verified the compiler's register allocation and instruction scheduling. The inner loop might have unnecessary spills or poor scheduling.
