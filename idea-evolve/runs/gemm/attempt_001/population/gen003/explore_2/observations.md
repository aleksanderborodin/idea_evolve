# Observations — Explore_2, Gen 3

## Solutions

| File | Fitness (µs) | Valid | Notes |
|------|-------------|-------|-------|
| sol01.py | 533.93 | Yes | Single-row vpshufb, stack LUT loads inside j-loop |
| sol02.py | 345.25 | Yes | Single-row vpshufb, register LUTs precomputed outside j-loop |
| sol03.py | 419.67 | Yes | 4-row vpshufb, int32 flush overhead inside k-loop |
| sol04.py | 341.78 | Yes | 4-row vpshufb, int8-only accumulation (widen once at end) |
| sol05.py | 347.49 | Yes | Adaptive: register LUTs for small, stack LUTs for medium/large |

**Best from this session:** sol04.py at 341.78 µs (vs current best 147.26 µs — 2.3x worse)

## Critical Finding: vpshufb IS a port-5 instruction

**The central hypothesis in idea_018 was WRONG.**

idea_018 claimed: "vpshufb runs on port 0/1, NOT port 5."
Measured result: vpshufb is slower than vpternlogd+vpopcntb.

On Tiger Lake (Willow Cove), **vpshufb (EVEX 512-bit) is a shuffle instruction
that runs on port 5**, the same port as vpternlogd. It does NOT relieve port-5
pressure — it increases it.

Evidence:
- sol02 (single-row vpshufb, otherwise same structure as current best) = 345 µs vs 147 µs (2.3x slower)
- The extra 8 instructions per k-byte (nibble extraction: 2 AND + 1 srli) add overhead
- Port-5 bottleneck: vpshufb (2 per k-byte) + AND+AND+ADD+ADD (4 ops) = ~6 port-5 ops
  vs current best: vpternlogd (2) + sub+add (2) = ~4 port-5 ops

## What the 4-row approach revealed (sol04 vs sol02)

| Benchmark | sol02 (1-row) | sol04 (4-row) | Improvement |
|-----------|--------------|--------------|-------------|
| Small | 5.29 µs | 13.24 µs | 2.5x WORSE |
| Medium | 822.13 µs | 530.66 µs | 1.55x better |
| Large | 9469.94 µs | 5682.46 µs | 1.67x better |

**Multi-row amortization clearly helps for medium/large** (where B bandwidth matters),
but hurts small (where setup/overhead costs dominate small compute time).

The 4-row approach reduces B loads by 4x. For medium (B=64 KB in L2) and large
(B=448 KB in L3), fewer B loads → measurable improvement.

## Why vpshufb is less efficient per k-byte

Current best (ternlogd+popcnt) per k-byte:
1. vpternlogd pos_bits: port 5, 1 cycle — computes (a|b)&(a|~b) in ONE instruction
2. vpternlogd neg_bits: port 5, 1 cycle
3. vpopcntb pos: port 0/1, 1 cycle  
4. vpopcntb neg: port 0/1, 1 cycle
5. vsubb: port 0/5
6. vadd acc8: port 0/5
= ~5 cycles total, 2 cycles on port 5 (ternlogd bottleneck)

vpshufb per k-byte:
1. AND for lo nibbles: port 0/5
2. srli_epi16 for hi: port 0/1
3. AND hi mask: port 0/5
4. vpshufb lo: PORT 5 — 1 cycle
5. vpshufb hi: PORT 5 — 1 cycle
6. add_epi8 combine: port 0/5
7. add_epi8 accumulate: port 0/5
= ~7 cycles total, 3-4 cycles on port 5 (worse than ternlogd!)

vpternlogd encodes 3 boolean ops (2 ORs + 1 AND) in ONE instruction = extremely dense.
vpshufb requires nibble splitting first (2 extra ops), is itself port-5, and 2 shuffles
per k-byte = same port pressure as ternlogd but with more total instructions.

## The 256-byte global LUT approach works but adds overhead

The g_nibble_lut[256][16] = 4KB table is a good way to avoid O(k_bytes×16×4) scalar
LUT construction per row. With this lookup, per (row, k-byte) LUT setup = 2 table lookups
+ 2 memcpy(16 bytes). This is ~10x faster than computing from scratch.

However, the broadcast operation (_mm512_broadcast_i32x4) inside the j-loop (sol01/sol03)
adds 2 extra L1 loads per k-byte, slowing down the inner loop significantly.

Moving broadcasts outside the j-loop (sol02) gives 3.7x speedup for sol02 vs sol01 on large.

## NT stores not activated

The harness allocates C via std::vector<int>, which is NOT 64-byte aligned. The
runtime alignment check `((uintptr_t)C & 63) == 0` was always false, so NT stores
were never used. The large benchmark C write overhead (32 MB at ~30 GB/s = ~1000 µs
theoretical minimum) still dominates.

## Multi-row with register LUTs only works for k_bytes ≤ 2

For 4-row register LUT approach: need 4 × 2 × k_bytes = 16 × k_bytes zmm.
- k_bytes=2 (small): 16 zmm → fits in 32-zmm register file ✓
- k_bytes=4 (medium): 32 zmm → tight (need 4 acc8 + temporaries, probably spills)
- k_bytes=7 (large): 56 zmm → definitely spills to stack

Even for k_bytes=2, sol05 (4-row register LUT) was 8.22 µs vs sol02's 5.29 µs.
The 4-row structure has more j-block overhead (4 widen_store per j-block vs 1).

## Directions not explored (time ran out)

1. **8-row vpshufb with register LUTs**: For k_bytes=2 (small), 8×2×2=32 zmm, tight.
   Might be worth testing for small to see if 8-row amortization (16 j-blocks of 64-col)
   significantly beats 4-row (8 groups of 4 rows).

2. **128-column B tiles**: Load 2 zmm B registers, extract nibbles from both, apply same
   row LUTs. Doubles compute per B load at cost of 2 more LUT lookups per row.

3. **Using vpshufb for different purpose**: Could use vpshufb to accelerate the PACKING
   of A data (reordering ternary bytes) rather than for the compute kernel.

4. **Complete byte LUT (256-entry)**: Instead of nibble splitting, precompute a 256-entry
   LUT per (a_pos, a_neg) pair using vpermb (vpermt2b). vpermb works on full bytes.
   However vpermb has high latency (4 cycles) and port 5 throughput similar to vpshufb.

5. **Port-5-free approach**: Replace vpshufb with vector AND/XOR chains. For 4-bit
   contributions, can compute via bit-parallel carry-save arithmetic without any shuffle.
   This completely avoids port 5 but requires many more instructions.
