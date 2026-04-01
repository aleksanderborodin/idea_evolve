# Solution-Idea Map

## Generation 1

### explore_1/sol01 (fitness: 654.75 µs)
- Central: idea_001 (AVX-512 popcount), idea_005 (NC=512 tiling)
- Peripheral: idea_008 (skip KC tiling)
- Novel elements: None — basic AVX-512 port of V14opt with int32 accumulation in hot loop

### explore_1/sol02 (fitness: 400.68 µs)
- Central: idea_001 (AVX-512 popcount), idea_011 (vpternlogd 0xD8/0xE4), idea_004 (int16 accum)
- Peripheral: idea_005 (NC=256), idea_008 (skip KC)
- Novel elements: First use of ternarylogic instructions

### explore_1/sol03 (fitness: 493.42 µs)
- Central: idea_001 (AVX-512 popcount), idea_009 (8x64 kernel)
- Peripheral: idea_004 (int16 accum), idea_008 (skip KC)
- Novel elements: 8-row micro-kernel attempt — register pressure caused regression

### explore_1/sol04 (fitness: 381.32 µs)
- Central: idea_001 (AVX-512 popcount), idea_011 (vpternlogd)
- Peripheral: idea_004 (int16 accum), idea_005 (NC=256), idea_008 (skip KC)
- Novel elements: Direct store (no C load-add) — precursor to idea_010

### explore_1/sol05 (fitness: 964.47 µs)
- Central: idea_001 (AVX-512 popcount), idea_006 (streaming stores)
- Peripheral: idea_004, idea_008
- Novel elements: Aligned temp C buffer + memcpy — memcpy too expensive, regression

### explore_1/sol06 (fitness: 465.65 µs)
- Central: idea_001 (AVX-512 popcount), idea_005 (NC=512)
- Peripheral: idea_004, idea_008, idea_010 (direct store)
- Novel elements: NC=512 with direct stores — still worse than NC=256

### explore_1/sol07 (fitness: 306.60 µs)
- Central: idea_001 (AVX-512 popcount), idea_007 (vectorized pack_B), idea_010 (direct store)
- Peripheral: idea_004, idea_005 (NC=256), idea_008, idea_011 (vpternlogd)
- Novel elements: First vectorized pack_B — major improvement

### explore_1/sol08 (fitness: 178.28 µs)
- Central: idea_001, idea_007, idea_010 (memset skip), idea_004
- Peripheral: idea_005 (NC=256), idea_008, idea_011
- Novel elements: Removed memset entirely — biggest single-step improvement

### explore_1/sol09 (fitness: 171.04 µs)
- Central: idea_001, idea_007, idea_010, idea_004, idea_002 (pragma unroll)
- Peripheral: idea_005, idea_008, idea_011
- Novel elements: thread_local buffers (slight TLS overhead on small benchmark)

### explore_1/sol10 (fitness: 148.18 µs) — GEN1 BEST
- Central: idea_001, idea_007, idea_010, idea_004, idea_011 (vpternlogd), idea_012 (stack buffers)
- Peripheral: idea_002 (pragma unroll), idea_005 (NC=256), idea_008
- Novel elements: alignas(64) stack-allocated pack buffers

### full_1/sol01 (fitness: 602.29 µs)
- Central: idea_001 (AVX-512 popcount)
- Peripheral: idea_005 (NC=512), idea_008
- Novel elements: int32 accumulation in hot loop — widening overhead dominated

### full_1/sol02 (fitness: 339.09 µs)
- Central: idea_001, idea_004 (int8 accum), idea_006 (streaming stores)
- Peripheral: idea_005 (NC=512), idea_008, idea_010 (partial — direct store mode)
- Novel elements: First int8 accumulation approach

### full_1/sol03 (fitness: 442.43 µs)
- Central: idea_001, idea_002 (template k-unroll), idea_004
- Peripheral: idea_005, idea_008
- Novel elements: Template specialization with switch dispatch — I-cache pressure regression

### full_1/sol04 (fitness: 167.23 µs)
- Central: idea_001, idea_004 (int8 accum), idea_010 (memset skip), idea_006 (streaming stores)
- Peripheral: idea_005 (NC=512), idea_008, idea_007 (partial — pack_B uses memcpy fallback)
- Novel elements: Runtime detection of alignment for streaming store path

---

## Generation 2

### gen002/exploit_1/sol01 (fitness: 254.97 µs)
- Central: idea_001, idea_013 (no-pack B, direct access), idea_004 (int16 accum)
- Peripheral: idea_005 (NC=256), idea_008, idea_010, idea_011
- Novel elements: Removed pack_B entirely — strided B access kills large

### gen002/exploit_1/sol02 (fitness: 292.93 µs)
- Central: idea_001, idea_004 (int8 accum, 4-row), idea_007, idea_010
- Peripheral: idea_005 (NC=256), idea_008, idea_011, idea_012
- Novel elements: Switched to int8 accumulation but int8→int32 widen more expensive

### gen002/exploit_1/sol03 (fitness: 242.34 µs)
- Central: idea_001, idea_009 (6-row kernel), idea_004 (int16 accum)
- Peripheral: idea_005, idea_007, idea_008, idea_010, idea_011, idea_012
- Novel elements: 6-row micro-kernel — more register pressure than 4-row

### gen002/exploit_1/sol04 (fitness: 274.11 µs)
- Central: idea_001, idea_019 (NC=128), idea_004, idea_007
- Peripheral: idea_008, idea_010, idea_011, idea_012
- Novel elements: NC=128 — more jc iterations dominate for large

### gen002/exploit_1/sol05 (fitness: 393.77 µs)
- Central: idea_001, idea_004, idea_007
- Peripheral: idea_005, idea_008, idea_010, idea_012
- Novel elements: pack_A moved outside jc loop — Ap too large for L1

### gen002/exploit_1/sol06 (fitness: 287.71 µs)
- Central: idea_001, idea_006 (NT stores for large), idea_004, idea_007
- Peripheral: idea_005, idea_008, idea_010, idea_012
- Novel elements: Non-sequential store pattern defeats NT stores in BLIS layout

### gen002/exploit_1/sol07 (fitness: 295.27 µs)
- Central: idea_001, idea_004, idea_007
- Peripheral: idea_005, idea_008, idea_010, idea_011, idea_012
- Novel elements: Software prefetching for B panels — Bp already L1-resident

### gen002/exploit_1/sol08 (fitness: 286.99 µs)
- Central: idea_001, idea_004, idea_007 (4×128 kernel)
- Peripheral: idea_005, idea_008, idea_010, idea_012
- Novel elements: 128-column kernel — 16+ accumulator regs cause spilling

### gen002/exploit_1/sol09 (fitness: 241.78 µs)
- Central: idea_001, idea_013 (direct B, k-first loop), idea_004 (int16)
- Peripheral: idea_005 (NC=256), idea_007 (partial), idea_008, idea_010
- Novel elements: K-first loop structure — k-row strided access causes misses

### gen002/exploit_1/sol10 (fitness: 249.73 µs)
- Central: idea_001, idea_013 (no pack_A, direct A access), idea_004
- Peripheral: idea_005, idea_007, idea_008, idea_010, idea_012
- Novel elements: A loads scatter, compiler misses optimizations

### gen002/exploit_1/sol11 (fitness: 350.58 µs)
- Central: idea_001, idea_002 (named acc vars, explicit unroll), idea_004
- Peripheral: idea_005, idea_007, idea_008, idea_010, idea_012
- Novel elements: I-cache regression from explicit unrolling (pattern_003 confirmed)

### gen002/exploit_1/sol12 (fitness: 354.02 µs)
- Central: idea_001, idea_005 (MC=32), idea_004, idea_007
- Peripheral: idea_008, idea_010, idea_012
- Novel elements: MC=32 — more pack_A calls, worse small benchmark

### gen002/explore_1/sol01 (fitness: 147.26 µs) — GEN2 BEST
- Central: idea_014 (row-streaming no-pack), idea_001 (AVX-512 popcount), idea_004 (int8 accum), idea_011 (vpternlogd)
- Peripheral: idea_008, idea_010 (implicit — no memset needed)
- Novel elements: 1-row streaming architecture — simplest and best performing variant

### gen002/explore_1/sol02 (fitness: 172.02 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004 (int8 accum)
- Peripheral: idea_008, idea_011
- Novel elements: 2-row with stack pre-broadcast arrays — spilling regressed

### gen002/explore_1/sol03 (fitness: 175.65 µs)
- Central: idea_014 (row-streaming, 2-row inline A), idea_001, idea_004
- Peripheral: idea_008, idea_011
- Novel elements: 2-row inline A loading — competitive but not best

### gen002/explore_1/sol04 (fitness: 195.22 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_006 (streaming stores for large)
- Peripheral: idea_008, idea_011
- Novel elements: NT stores for m≥4096 — store overhead on medium

### gen002/explore_1/sol05 (fitness: 165.59 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004 (int8 accum)
- Peripheral: idea_008, idea_011
- Novel elements: Optimized variant — smallest small time (3.37 µs)

### gen002/explore_1/sol06 (fitness: 177.02 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_017 (B micro-pack for large)
- Peripheral: idea_008, idea_011
- Novel elements: 2-row + B 64-col micro-pack — improved large but worsened overall

### gen002/explore_1/sol07 (fitness: 201.81 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_017 (B micro-pack for medium too)
- Peripheral: idea_008, idea_011
- Novel elements: Micro-pack applied to medium — regressed due to stride C writes

### gen002/explore_1/sol08 (fitness: 180.07 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_019 (NC=256 panel pack)
- Peripheral: idea_005, idea_008, idea_011
- Novel elements: NC=256 panel pack for medium — still worse than simple row-streaming

### gen002/explore_2/sol01 (fitness: 207.32 µs)
- Central: idea_013 (no-pack direct B), idea_001, idea_004 (int16), idea_009 (8-row)
- Peripheral: idea_008
- Novel elements: jc-outer, 8-row, stack B_reg[128] — register spilling

### gen002/explore_2/sol02 (fitness: 318.96 µs)
- Central: idea_013 (no-pack), idea_001, idea_004 (int8), idea_002 (template+always_inline)
- Peripheral: idea_008
- Novel elements: Template specialization — I-cache bloat from 3 inlined branches

### gen002/explore_2/sol03 (fitness: 200.38 µs)
- Central: idea_013 (no-pack), idea_001, idea_004 (int16)
- Peripheral: idea_008
- Novel elements: Named b0..b6 zmm vars for best register allocation

### gen002/explore_2/sol04 (fitness: 182.31 µs)
- Central: idea_013 (no-pack, ic-outer), idea_001, idea_004 (int16), idea_006 (streaming NT stores)
- Peripheral: idea_008
- Novel elements: ic-outer loop for sequential C writes — best small time (3.66 µs)

### gen002/experimentator_1/sol01 (fitness: 223.17 µs)
- Central: idea_001, idea_004 (int8 accum), idea_019 (NC=128)
- Peripheral: idea_005, idea_007, idea_008, idea_010
- Novel elements: Experimental byproduct — NC=128 hurts large more than int8 helps

---

## Generation 3

### gen003/exploit_1/sol02 (fitness: 141.0 µs) — GEN3 BEST, OVERALL BEST
- Central: idea_014 (row-streaming), idea_001 (AVX-512 popcount), idea_004 (int8 accum), idea_011 (vpternlogd), idea_015 (size-adaptive NT stores — runtime check)
- Peripheral: idea_008 (skip KC), idea_010 (implicit — no memset), idea_012 (stack arrays)
- Novel elements: Runtime C alignment check for NT stores. Improvement likely from compiler code layout change (pattern_009), not NT stores actually triggering.

### gen003/explore_1/sol01 (fitness: 220.33 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004 (int8 accum)
- Peripheral: idea_008, idea_011
- Novel elements: Clean reimplementation of gen002 baseline

### gen003/explore_1/sol02 (fitness: 168.35 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004 (int8 accum), idea_016 (8-row int8 kernel)
- Peripheral: idea_008, idea_011
- Novel elements: **First empirical 8-row int8 kernel.** Best 8-row result ever (168 µs vs prior 207/493 µs). Large 16% better, small/medium worse due to C scatter.

### gen003/explore_1/sol03 (fitness: 204.52 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004 (int8 accum), idea_022 (4-row B amortization)
- Peripheral: idea_008, idea_011
- Novel elements: 4-row variant — middle ground between 1-row and 8-row

### gen003/explore_1/sol04 (fitness: 184.84 µs)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_006 (NT stores for large)
- Peripheral: idea_008, idea_011
- Novel elements: 1-row + NT stores, size-adaptive. NT stores didn't help sequential writes.

### gen003/explore_2/sol01 (fitness: 533.93 µs)
- Central: idea_018 (vpshufb LUT kernel), idea_001 (AVX-512 popcount)
- Peripheral: idea_004 (int8 accum)
- Novel elements: First vpshufb implementation. Stack LUT, single-row. Very slow.

### gen003/explore_2/sol02 (fitness: 345.25 µs)
- Central: idea_018 (vpshufb LUT), idea_001
- Peripheral: idea_004
- Novel elements: LUT precomputed outside j-loop, 3.7x faster than sol01

### gen003/explore_2/sol03 (fitness: 419.67 µs)
- Central: idea_018 (vpshufb LUT), idea_001, idea_022 (4-row)
- Peripheral: idea_004
- Novel elements: 4-row vpshufb with int32 flush overhead

### gen003/explore_2/sol04 (fitness: 341.78 µs)
- Central: idea_018 (vpshufb LUT), idea_001, idea_022 (4-row), idea_004 (int8-only accum)
- Peripheral: none
- Novel elements: Best vpshufb result. 4-row + int8 accum. Validated multi-row B sharing benefit.

### gen003/explore_2/sol05 (fitness: 347.49 µs)
- Central: idea_018 (vpshufb LUT), idea_001
- Peripheral: idea_004
- Novel elements: Adaptive register/stack LUT — no improvement over sol04

### gen003/experimentator_1/sol01 (fitness: ~400 µs, from report)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_006 (NT stores + per-rep _mm_malloc)
- Peripheral: idea_008
- Novel elements: NT stores with per-rep aligned buffer allocation. Catastrophic — 8192 page faults.

### gen003/experimentator_1/sol01b (fitness: ~251 µs, from report)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_006 (NT stores + static BSS buffer)
- Peripheral: idea_008
- Novel elements: Static pre-allocated buffer. Still worse — memcpy of cold data.

### gen003/experimentator_1/sol02 (fitness: ~197 µs, from report)
- Central: idea_014 (row-streaming), idea_001, idea_004, idea_022 (4-row pack-free small kernel)
- Peripheral: idea_008
- Novel elements: 4-row pre-broadcast. Function call overhead dominated.
