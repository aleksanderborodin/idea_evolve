---
generation: 3
best_score: 141.0
trajectory: improving (plateauing)
last_updated_gen: 3
---

# State of Affairs — Generation 3

## Current Standing

Best score: **141.0 µs** (gen003/exploit_1/sol02), a 5.46x speedup over the 770 µs baseline. Achieved in generation 3 using the row-streaming architecture with a runtime NT alignment check (likely a compiler layout artifact, not a real NT store benefit). 3 generations completed, 41 valid solutions total. Trajectory: improving but plateauing — gen002→gen003 was only 4.3% (147.26→141.0 µs), within measurement noise. Target is 24 µs but multiple agents independently calculate the **physical minimum at ~50-80 µs** given DRAM bandwidth constraints. User confirmation needed on realistic target.

## What Works

**Established (use in all new solutions):**
- **AVX-512 popcount** (idea_001, conf 0.95) — foundational; all 41 solutions use it.
- **int8/int16 deferred widening** (idea_004, conf 0.95) — int8 accumulation with flush every 15 k-iters. Monolithic function critical (no helper function calls).
- **Row-streaming no-pack architecture** (idea_014, conf 0.85) — process 1 row of A, sweep all B columns. No packing, no tiling buffers. Best for 2 consecutive generations.
- **Skip memset** (idea_010, conf 0.95) — direct stores eliminate 32 MB zeroing. 1.72x single-step improvement.
- **Skip KC tiling** (idea_008, conf 0.9) — k_bytes ≤ 7, entire k fits in registers.
- **Vectorized pack_B** (idea_007, conf 0.85) — relevant only for BLIS path; row-streaming doesn't pack.

**Confirmed patterns:**
- Memset dominates large cost (pattern_001). Kernel+store is 93-95% of time (pattern_006).
- BLIS approach at local optimum — 12 exploit variants failed to improve it (pattern_007).
- Row-streaming kernel at memory bandwidth wall — compute optimizations yield <5% (pattern_011).
- C write scatter destroys multi-row benefit; 4-row is sweet spot over 8-row (pattern_010).

## Current Frontier

The pipeline is **memory-bandwidth-bound**, not compute-bound. Three gen003 agents independently confirmed this. All optimization effort must target memory traffic reduction.

**Highest-priority untested combinations:**
1. **SSE 128-bit NT stores + row-streaming** (idea_021) — bypasses 64-byte alignment constraint. Research estimates large: 3841→~1350 µs, geomean ~105 µs. Never tested.
2. **4-row ternlogd+popcnt kernel** (idea_022) — 1.55-1.67x B-load reduction on med/large confirmed in vpshufb kernel. Not yet applied to the winning kernel. Estimated geomean ~80-95 µs.
3. **Multi-threading** (idea_020) — cgexec has cores 0+1. Untested. Estimated 1.3-1.8x on large.

**Critical infrastructure gap:** No agent has ever inspected compiler-generated assembly. Register spilling, missed inlining, and instruction scheduling are completely unknown. All 4 code-producing agents in gen003 requested this independently.

## Coverage Map

Well-explored: idea_001+idea_004+idea_014 (17 trials, best 141.0 µs). idea_001+idea_004+idea_007+idea_010 BLIS (8 trials, best 148.18 µs). idea_018 vpshufb (5 trials, debunked at 341 µs).

Under-explored: idea_021 SSE NT stores (1 trial, unconditional only — size-adaptive untested). idea_022 4-row with correct kernel (0 trials). idea_020 multi-threading (0 trials).

## Dead Ends

- **VNNI** (idea_003) — bit-packed format incompatible with integer dot-product.
- **vpshufb LUT** (idea_018) — 2.3x worse than popcnt; vpshufb is port 5, same bottleneck as vpbroadcastb.
- **512-bit NT stores** — blocked by 64-byte alignment constraint on C allocation (fact_006).
- **Aligned-buffer + memcpy NT workaround** — memcpy from DRAM-cold buffer costs more than RFO savings. Three independent failures (exploit_1, experimentator_1 ×2).
- **Template k-specialization** — I-cache pressure from multiple kernel copies (pattern_003).
- **No-pack direct BLIS** (idea_013, archived) — superseded by row-streaming.

## Open Questions

1. **Is the 141.0 µs score real or compiler noise?** The improvement may come from a dead `if(use_nt)` branch changing code layout (pattern_009). Explore_1 reported 30-40% run-to-run variance. Scores <30% apart may not be meaningfully different.
2. **What does the compiler actually emit?** Assembly has never been inspected. Register spilling, missed inlining, and instruction scheduling are unknown. This is the biggest blind spot.
3. **Can SSE 128-bit NT stores help large without hurting medium?** 16 SSE stores vs 4 ZMM stores per 64 bytes — store port saturation risk. Needs empirical test with size-adaptive dispatch.
4. **Does the cgexec cgroup allow 2 concurrent threads?** Blocks multi-threading (idea_020).
5. **Is the 24 µs target achievable?** Independent calculations from 3+ agents place the physical minimum at ~50-80 µs. User should confirm realistic target.
6. **fact_004 port assignments are wrong.** vpopcntb is port 0/1, not port 5 (corrected by fact_008). vpbroadcastb (port 5) is the actual bottleneck. fact_004 needs a deprecation notice.
7. **Exploit_1 lost 12 of 13 solution scores** (no .score files). REC-5 (auto-write .score) unimplemented for 2 generations. Pipeline is losing data.
