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

### explore_1/sol10 (fitness: 148.18 µs) — BEST
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
