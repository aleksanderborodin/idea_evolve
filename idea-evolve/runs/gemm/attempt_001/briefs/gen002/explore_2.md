## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/population/best.py` → 148.18 µs (geomean)
Per-size breakdown: small=4.49 µs, medium=228.26 µs, large=3176.31 µs
**TARGET: 24 µs** (~6x improvement over current best needed)

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/knowledge/facts/fact_005.md`
- `../fast-conv/gemm/baseline.cpp`

## Directive

**This is a Track B radical exploration. You must NOT start from the current best solution or any file in `/home/sasha/Desktop/project_alpha/idea-evolve/population/`. You must NOT use BLIS-style tiling. Start from scratch.**

The current approach tiles in m-dimension (NC panels) and processes 4 rows × 64 columns per micro-kernel call. Every solution in gen 1 follows this pattern. You must try something structurally different.

**Your approach: Transposed/column-major computation with output-stationary accumulation.**

Key insight: the problem has tiny k (2-7 bytes) but huge m. Instead of the standard row-major approach, think about the computation differently:

**Approach 1 — Bit-parallel column processing:**
- For each k-byte position t (only 2-7 iterations):
  - Load the full column of A pos bits: `A[row*k_bytes*2 + t*2]` for all n rows → n bytes (32-128 bytes, fits in 1-2 zmm)
  - Load the full column of A neg bits: similarly
  - For each column j of B: `B[t*m + j]` is a single byte containing 8 binary values
  - Broadcast this B byte across a zmm, then compute the boolean operation against all n rows of A simultaneously
  - This processes ALL rows for one (k, j) pair in one instruction sequence

This inverts the loop order: instead of (row, column, k), use (k, column, row). With n ≤ 128, the A column fits in 2 zmm registers. You process all rows at once.

**Approach 2 — Lookup table for byte combinations:**
- For ternary × binary byte multiplication, there are only 3^8 = 6561 possible ternary bytes and 256 possible binary bytes. But 6561 × 256 is too large.
- Better: decompose. A ternary byte = (pos_byte, neg_byte) where each is 0-255. The result for one byte pair is: `popcount((pos|b) & (neg|~b)) - popcount((pos|~b) & (neg|b))`. This is a function of (pos, neg, b) → int8.
- Precompute a 256×256×256 table? Too large (16MB). But: precompute per-row tables for just the k_bytes values of pos/neg that each row actually uses.
- For each row, there are at most 7 (pos, neg) pairs. For each pair, there are 256 possible b values → result is int8. Table: 7 × 256 = 1792 bytes per row. Total for all rows: 128 × 1792 = 224KB. Fits in L2.
- Then for each column j: for each k byte, look up result from table and accumulate. This replaces SIMD popcount with table lookups, which can be vectorized with `vpshufb` (byte shuffle as 4-bit LUT) or `vpgatherdd`.

**Approach 3 — Multi-row batch with register-blocked A:**
- Process all n rows together for a block of 64 output columns. Since k_bytes ≤ 7 and n ≤ 128:
  - Pre-load ALL of A into registers: 128 rows × 7 bytes × 2 planes = 1792 bytes = 28 zmm registers. Just barely fits (32 zmm available).
  - Then sweep across columns: for each j block of 64, load k_bytes zmm from B, compute all n×64 outputs, store.
  - No tiling, no packing, everything in registers.

Pick whichever approach seems most promising after reading the problem description carefully. If one doesn't work, try another.

**What NOT to do:**
- Do NOT read population/best.py or any existing solution
- Do NOT implement BLIS MC/NC tiling
- Do NOT use packing buffers
- Do NOT try VNNI (debunked)

**IMPORTANT:** Write your first solution within 10 turns. Evaluate immediately. Iterate based on results.
