## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → 148.18 µs (geomean)
Per-size breakdown: small=4.49 µs, medium=228.26 µs, large=3176.31 µs
**TARGET: 24 µs** (~6x improvement over current best needed)

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_004.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_005.md`
- `../fast-conv/gemm/baseline.cpp`

## Directive

**This is a Track B radical exploration. You must NOT start from the current best solution or any file in `/home/sasha/Desktop/project_alpha/idea-evolve/population/`. You must NOT use BLIS-style tiling. Start from scratch.**

The current best (148 µs) uses a classical BLIS micro-kernel approach: pack A, pack B into contiguous panels, then run a 4×64 micro-kernel with AVX-512 popcount. This approach has been optimized through 10 iterations and is near its ceiling. The 24 µs target requires a **fundamentally different architecture.**

**Your approach: Row-streaming with no packing, no tiling, no buffers.**

Key insight: k is absurdly small (2-7 bytes). For each output row i:
- A[i] is only 14 bytes (7 pos + 7 neg). Broadcast each k-byte to a zmm register — 14 broadcasts total, all fit in registers permanently.
- Scan B column-by-column: load 64 bytes at B[k*m + j], compute popcount of boolean combo with pre-broadcast A bytes, accumulate, store 64 int32 results.
- No packing needed. No tiling needed. Just: for each row, sweep across all m columns.

This eliminates ALL overhead: no pack_A, no pack_B, no buffer allocation, no buffer copies. Pure compute + streaming reads/writes.

**Specific implementation approach:**
1. For each row i of A (outer loop):
   - Load all k_bytes pos bytes and neg bytes into zmm via `_mm512_set1_epi8(byte)` — at most 14 registers used.
   - For j = 0 to m in steps of 64:
     - For each k in 0..k_bytes-1: load `B[k*m + j]` (64 bytes), compute vpternlogd with broadcast A bytes, popcount, accumulate in int8.
     - After k-loop: widen int8 accumulators to int32 (4 separate `_mm512_cvtepi8_epi32` calls per 64-byte chunk), store to C[i*m + j..j+15], C[i*m + j+16..j+31], etc.
2. Process 2 or 4 rows simultaneously to increase instruction-level parallelism. With 14 zmm for A broadcasts + 4 zmm for B loads + 4×4 zmm accumulators = ~34 registers — fits in 32 zmm if using 2 rows.

**Why this could reach 24 µs:**
- Small (n=32, m=1024): 32 rows × 16 column blocks × ~7 cycles per block ≈ 3584 cycles ≈ 1.5 µs
- Medium (n=64, m=16384): 64 rows × 256 blocks × ~7 cycles ≈ 114K cycles ≈ 47 µs → needs dual-row to halve
- Large: limited by memory write bandwidth (~1000 µs floor for 32MB), but no-pack saves the pack_B overhead

**What NOT to do:**
- Do NOT read population/best.py or any existing solution
- Do NOT implement BLIS-style tiling or packing
- Do NOT use NC/MC tile parameters
- Do NOT use malloc, aligned_alloc, or stack buffers for packed data
- Do NOT try VNNI (debunked)

**IMPORTANT:** Write your first solution within 10 turns. Start simple — even a 1-row-at-a-time no-pack kernel. Get a baseline score, then optimize from there. Read the detail_file for per-size breakdown.
