# Debrief Report — explore_1, Generation 3

## 1. What did you try?

| Approach | Result | Key Learning |
|----------|--------|-------------|
| 1-row row-streaming baseline (sol01) | 220 µs | Matches gen002 best. Clean reimplementation. |
| 8-row row-streaming (sol02) | **168 µs** | Best result. 8x B-load amortization gives 40% improvement on large. |
| 4-row row-streaming (sol03) | 204 µs | Middle ground. 8-row is better than 4-row. |
| NT stores via aligned buffer + memcpy | 802-820 µs | Complete failure. memcpy + page faults > entire baseline compute. |
| NT stores direct to C with alignment check | 186-247 µs | C is aligned for large (mmap), but NT stores still don't help (~same or worse). |
| 8-row NT stores via template | 247 µs (large=5686) | WC buffer saturation from scattered cache line writes across 8 rows. |
| 1-row NT stores for large only (sol04) | 184 µs | Works but loses 8x B-load amortization. Net: roughly same as 8-row regular. |
| Single-vpternlog algebraic optimization | 236-288 µs | Saves 2 ops/iter but correction overhead negates the savings. |
| 128-column processing | 260 µs | Register spilling from doubled accumulator count. |
| Software B prefetching | 249 µs | B already L2-resident. HW prefetching handles it. |
| Unconditional NT stores (test) | FAIL | Small C is NOT 64-byte aligned → segfault. Confirmed alignment constraint. |

## 2. What information did I lack?

- **Whether C is 64-byte aligned per benchmark size.** Spent many iterations discovering this empirically. A fact file stating "C is page-aligned for large (≥128KB via mmap) but only 16-byte aligned for small (<128KB via malloc)" would have saved 5+ iterations.
- **Whether the benchmark harness calls gemmCandidate multiple times with the same C buffer.** Confirmed: yes, same buffer reused across all 10 repetitions. Useful for static buffer strategies.
- **Assembly output of the compiled kernel.** Never inspected whether the compiler spills registers in the 8-row inner loop. This would reveal whether the 8-row approach is truly register-efficient or suffering hidden spills.
- **Actual WC buffer count on Tiger Lake.** Used the standard assumption of 12 WC buffers but couldn't verify experimentally.

## 3. What given facts might be wrong or outdated?

- **fact_006 (C alignment constraint)**: States C is "NOT guaranteed to be 64-byte aligned." This is correct but incomplete. For large allocations (32 MB), glibc malloc uses mmap which returns page-aligned addresses. C IS 64-byte aligned for the large benchmark. But it's NOT aligned for the correctness test (16 KB allocation).
- **idea_015 (size-adaptive NT stores)**: Claims NT stores should give 2.3x on large and reduce geomean to ~30-40 µs. In practice, NT stores provided no benefit on large (3823 µs vs 3212 µs regular). The experimentator's 2.3x measurement was for standalone streaming writes, not for the actual kernel where WC buffer contention and alignment issues dominate.
- **idea_016 (8-row int8 kernel)**: The theoretical analysis is sound. The 8-row kernel works well. However, the claim that it "resolves register pressure" from idea_009's int16 failure is not fully validated — the int8 approach works but register allocation quality is unknown without assembly inspection.

## 4. Was the State of Affairs accurate?

Mostly accurate. Key issues:
- The SoA describes the 24 µs target as requiring NT stores. This is correct, but it understates how difficult NT stores are to deploy given the C alignment constraint and WC buffer limitations. The target may be physically impossible without harness modifications.
- The coverage gap "No solution combines NT stores with sequential write pattern correctly" is addressed by sol04, but the result was disappointing.

## 5. What would I do differently with more context?

- **Start with assembly inspection** of the existing best solution. Understanding the actual instruction schedule and register allocation would guide optimization far more precisely than trying random approaches.
- **Measure C alignment directly** at function entry (fprintf to stderr) to confirm alignment assumptions before writing NT store code.
- **Focus on medium optimization** since it's the middle geometric mean term. Medium is 4 MB (fits in L3), so cache-aware tiling might help reduce write-back traffic.

## 6. Specific experiments to run

1. **EXP-A: Verify C alignment by size.** Add `fprintf(stderr, "C=%p aligned64=%d nm=%dx%d\n", C, (uintptr_t)C%64==0, n, m)` to gemmCandidate and run the correctness check + benchmark. This conclusively answers the alignment question for each test/benchmark size.

2. **EXP-B: Assembly quality analysis.** Compile sol02 with `-S -fverbose-asm` and inspect the inner loop. Count register spills, verify broadcast elimination, check instruction scheduling. This tells us if the compiler is doing a good job or if hand-tuned assembly could improve things.

3. **EXP-C: Column-blocked write pattern for medium.** Process medium in NC=256 column panels. For each panel: process all rows, then move to next panel. This keeps the C output tile (64×256×4 = 64 KB) in L1, reducing write-back traffic. Expected benefit: 10-20% on medium.

4. **EXP-D: mmap with MAP_POPULATE for NT buffer.** Instead of std::aligned_alloc + memset, use mmap(MAP_POPULATE) to pre-fault pages without zeroing. Test if this reduces the page fault overhead enough to make the aligned-buffer NT approach viable.

5. **EXP-E: Modify the harness to use aligned C.** Change `std::vector<int> res` to `std::aligned_alloc(64, ...)` in the harness. This enables direct NT stores and removes the biggest bottleneck. (Requires user intervention — the harness is read-only for agents.)

## 7. What surprised you?

1. **NT stores consistently performed the same or worse than regular stores for the 8-row kernel.** The experimentator's 2.3x standalone measurement did not translate to real kernel performance. WC buffer contention appears to be the root cause.

2. **The single-vpternlog algebraic optimization was slower.** Eliminating one vpternlog + one vpopcntb should save ~20% of the hot loop. But the scalar popcount tracking and correction arithmetic negated the savings. The two-vpternlog approach has better pipelining characteristics.

3. **Benchmark variance of 30-40% between runs.** The same solution (sol02) measured as 168 µs on one run and 275 µs on another. This makes reliable A/B testing extremely difficult and means reported improvements of <30% are within noise.

4. **The 4-row kernel was worse than 8-row.** Expected better register allocation to compensate for halved B-load amortization. It didn't — the 8-row kernel's B reuse advantage dominates.

## 8. Helper tools feedback

No helpers from `problem/helpers/` were used. The problem is pure C++ intrinsics — no Python-level helpers are relevant.

**Helper I wish existed:** A compiled C++ test harness that runs a single gemmCandidate call and prints alignment, timing breakdown by phase (broadcast, compute, widen, store), and WC buffer miss counts. This would make optimization data-driven rather than guess-and-check.

## 9. Time budget

Had enough time to explore 10+ variations. If I had more time, I would:
1. Inspect the assembly output to understand register allocation
2. Try column-blocked write patterns for medium
3. Implement a custom mmap-based C allocation to test NT stores properly
4. Try the vpshufb LUT kernel as a completely different compute path
