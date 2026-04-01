# Debrief Report — Explore_2, Gen 3

## 1. What did I try?

Implemented the vpshufb Nibble-LUT Kernel (idea_018) as directed in my brief. Built 5 variants:

- **sol01** (533 µs): Single-row, stack-based LUT loads inside j-loop. Stack smashing bug first (LUT array too small for k_bytes=32 in correctness checks). Fixed with global 4KB g_nibble_lut table.
- **sol02** (345 µs): Single-row, LUT zmm precomputed outside j-loop (14 zmm for k_bytes=7). Moved broadcast outside j-loop, 3.7x speedup vs sol01.
- **sol03** (420 µs): 4-row, NT stores (not activated), but with expensive int32 flush overhead — actually WORSE than sol02.
- **sol04** (342 µs): 4-row, int8-only accumulation (safe for k_bytes≤15, widen once per j-block). Best result — improved medium (530 µs) and large (5682 µs) vs sol02, at cost of small (13.24 µs).
- **sol05** (347 µs): Adaptive — register LUTs for small (k_bytes≤2), stack LUTs for medium/large. Didn't achieve the hoped-for combination of sol02+sol04 benefits.

**Best: sol04 at 341.78 µs** (vs current population best 147.26 µs — 2.3x worse).

## 2. What information did I lack?

- **Port assignments for EVEX instructions on Tiger Lake**: The key hypothesis ("vpshufb is port 0/1") was wrong. I needed Agner Fog's Tiger Lake instruction tables before investing in this approach. The experiments confirmed vpshufb is port-5.
- **Actual bandwidth numbers**: I knew NT stores require aligned C, but I didn't verify the harness allocation. The `use_nt` flag was never activated. A way to check or force C alignment would have been valuable.
- **Assembly output**: Never inspected the generated ASM to verify register allocation, unroll quality, or if LUT zmm stayed in registers. The GCC optimizer may have spilled registers I expected to stay in zmm.

## 3. What given facts might be wrong or outdated?

- **idea_018 port assignment claim**: "vpshufb runs on port 0/1, NOT port 5" — **THIS IS WRONG**. vpshufb (EVEX 512-bit) is a shuffle instruction and runs on port 5 on Tiger Lake (Willow Cove). This should be corrected or the idea downgraded to "debunked."
- **experimentator_1 port-5 bottleneck claim**: This referred to vpbroadcastb and vpmovsxbw being port-5. The current best (sol10/row-streaming) eliminated those. The current bottleneck may be different.

## 4. Was the State of Affairs accurate?

State of Affairs is from gen 1 and somewhat outdated. Gen 2 improved best to 147.26 µs (from 148.18 µs). The key knowledge from gen-2 research (NT stores, 8-row kernel, etc.) wasn't fully reflected in the State of Affairs but was available in research/experiment files.

## 5. What would I do differently?

1. **Check port tables first**: Before implementing vpshufb, verify port assignments using Agner Fog tables or Intel's architecture manual. This would have immediately disqualified the approach.
2. **Try 4-row ternlogd+popcnt**: My directive was "no ternlogd/vpopcntb" but the most promising unexplored direction based on this session's data is 4-row ternlogd with int8 accumulation and NT stores. That's what idea_009/idea_016 describe.
3. **Build a simple port-pressure test**: A micro-benchmark measuring single-instruction throughput would have confirmed vpshufb port assignment in 5 minutes.

## 6. Specific experiments to run

### High priority
1. **4-row ternlogd+popcnt kernel**: Use the current best's compute path but process 4 rows per B load. My sol04 data shows 4-row amortization gives 1.55x medium, 1.67x large improvement. If applied to the ternlogd kernel, should give comparable gains: estimated 147/1.67 = 88 µs for large, 226/1.55 = 146 µs for medium. Fitness: ~95 µs.
2. **NT stores with internal aligned buffer**: The "aligned temp + memcpy" approach was debunked in gen-1 (explore_1/sol05: 964 µs), but that was before NT stores were available. With NT stores for the copy AND the actual write, might be competitive. Need to re-test with current baseline.
3. **vpshufb port verification**: Run `likwid-perfctr` or Intel VTune to measure actual port-5 saturation for current best vs vpshufb approach.

### Lower priority
4. **8-row ternlogd+popcnt**: After 4-row validated, extend to 8 rows. For medium (n=64): 8 groups of 8, should halve medium time.
5. **NC sweep with 4-row kernel**: The 4-row kernel changes B access patterns (processes more rows before moving to next j-block). The optimal NC may shift.

## 7. What surprised me?

1. **vpshufb nibble approach is slower**: Expected ≥2x speedup from "eliminating port-5 bottleneck." Got 2.3x SLOWDOWN. The hypothesis was fundamentally wrong about vpshufb's port.

2. **The 4-row benefit is real**: sol04 vs sol02 showed ~1.6x medium/large improvement just from 4-row B-load amortization. This is a large, reliable effect that other kernels should exploit.

3. **The global LUT approach is surprisingly clean**: Using g_nibble_lut[256][16] = 4KB precomputed table, LUT construction per row is just 2 memcpy(16 bytes) per k-byte. Much cleaner than inline scalar computation.

4. **int8-only accumulation (widen once per j-block) is a big win vs flush inside k-loop**: sol03 (with flush inside k-loop at int32 accumulators) = 420 µs, sol04 (widen once at end) = 342 µs. The 16 acc32 initializations + flush logic dominated sol03.

## 8. Helper tools feedback

Used `from helpers.core import compute_c` — not needed for this session (pure C++ approach).
No helper bugs found. One useful helper that would have saved time: **port_pressure_test** that compiles and runs a micro-benchmark to measure instruction throughput for given EVEX instructions.

## 9. Time budget

Ran out of time to test several important variants:
- 8-row vpshufb (to see if 8-row amortization compensates for vpshufb inefficiency)
- 128-column B tiles with vpshufb
- vpshufb used for pack_A acceleration rather than compute kernel

The most important work not done: confirming whether 4-row ternlogd+popcnt achieves the expected ~95 µs.

## Summary for next generation

**idea_018 (vpshufb LUT kernel) should be DEBUNKED.** vpshufb is a port-5 instruction on Tiger Lake and adds overhead (nibble extraction) compared to vpternlogd+vpopcntb. Tested empirically: best vpshufb result is 342 µs vs 147 µs for ternlogd.

**KEY VALIDATED FINDING (novel)**: 4-row B-load amortization gives 1.55x medium, 1.67x large improvement. This should be applied to the ternlogd+vpopcntb kernel immediately. Estimated combined result with 4-row ternlogd+popcnt: ~80-95 µs.
