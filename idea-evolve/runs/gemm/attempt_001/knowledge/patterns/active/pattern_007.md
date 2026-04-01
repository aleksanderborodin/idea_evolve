---
type: pattern
id: pattern_007
name: "BLIS best solution is highly robust; 12 exploit variants failed to improve it"
lifecycle: active
confidence: 0.8
first_seen: generation_2
last_updated: generation_2
evidence: [gen002/exploit_1/sol01 through gen002/exploit_1/sol12]
related_ideas: [idea_001, idea_004, idea_007, idea_010, idea_012]
tags: [diminishing-returns, exploitation, robustness, BLIS]
---

Exploit_1 (gen002) tested 12 different modifications of the gen001 best solution
(sol10, 148.18 µs). None improved the score:

| Variant | Score | Description |
|---------|-------|-------------|
| No-pack B | 254.97 | Strided B access kills large |
| Int8 accum, 4-row | 292.93 | int8→int32 widen overhead |
| 6-row int16 kernel | 242.34 | More register pressure |
| NC=128 | 274.11 | More jc iterations dominate |
| pack_A outside jc | 393.77 | Ap too large for L1 |
| NT stores for large | 287.71 | Non-sequential pattern defeats NT |
| SW prefetch B panels | 295.27 | Bp already L1-resident |
| 4×128 kernel | 286.99 | 16+ acc regs cause spilling |
| K-first loop, direct B | 241.78 | k-row strided misses |
| No pack_A, direct A | 249.73 | A loads scatter |
| Named acc vars, unroll | 350.58 | I-cache regression |
| MC=32 | 354.02 | More pack_A calls |

The combination of NC=256, MC=64, 4-row int16 kernel, vectorized pack_B,
stack buffers, memset skip, and pragma unroll appears to be a local optimum
for the BLIS architecture. Further BLIS improvements require either:
1. Changing the compute path (int8 accum, 8-row kernel)
2. Changing the store path (size-adaptive NT stores)
3. Both simultaneously

Note: the exploit agent's attempt at NT stores (sol06) FAILED because the
store pattern was non-sequential within the BLIS tiling. NT stores require
sequential writes (ic-outer loop order), which conflicts with BLIS's jc-outer
structure. This is a key architectural constraint.
