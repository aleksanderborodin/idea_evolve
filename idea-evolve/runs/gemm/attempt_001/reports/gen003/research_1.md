# Research Agent 1, Gen 3 — Debrief Report

## Solution Table

| File | Fitness (µs) | Valid | Notes |
|------|-------------|-------|-------|
| (none) | — | — | Pure research session; no code written |

## 1. What I tried

No code was written. This session was entirely research-focused:

1. **Read all required context files**: problem description, state_of_affairs, all 3 cluster docs, coverage matrix, gen002 research findings, experimentator observations, active ideas (014–019), patterns (007–008), bench harness source.

2. **Analyzed the 64-byte alignment constraint** (the root cause of all NT store failures): Bench harness uses `std::vector<int>`, which glibc allocates at 16-byte alignment. `_mm512_stream_si512` requires 64-byte alignment → fault. Solution: use `_mm_stream_si128` (16-byte aligned SSE NT store). This is the correct fix for idea_015.

3. **Derived bandwidth ceilings** using fact_007 measurements. Found the 24 µs target is bandwidth-impossible (requires medium < 46 µs while floor is 220 µs). Realistic target: 50–80 µs.

4. **Identified multi-threading as completely unexplored**: cgexec cgroup contains cores 0+1. Pthreads inside gemmCandidate can use core 1. Dual-channel DDR4 can serve 2 write streams, potentially 1.3–1.8× bandwidth improvement for large.

5. **Template specialization for k_bytes**: Compile-time dispatch for k_bytes ∈ {2,4,7} eliminates loop overhead and register stack spills for small. Expected small improvement: 3.69 → 1.0–1.5 µs.

6. **Column-outer B reuse analysis**: Theoretically reduces B reads from 56 MB → 448 KB, but since B is already L3-resident (~200 GB/s), savings are only ~278 µs. Net effect similar to row-outer + NT stores.

## 2. What information I lacked

- Actual assembly output of the current best solution (perf stat / objdump). Would confirm whether the k-loop is being unrolled by the compiler already.
- Actual memory bandwidth with 2 threads on this specific machine. The 1.3–1.8× estimate is from general DDR4 literature, not measured on this Tiger Lake.
- Whether the cgexec cgroup actually allows 2 cores or just 1 (cpuset vs cpu bandwidth limit).

## 3. What given facts might be wrong or outdated

- **idea_015 confidence of 0.7 is overestimated** given that SSE NT stores were never tried. The failure was purely an alignment issue, not an architectural mismatch. Confidence should be 0.9 once the 128-bit fix is applied.
- **Research_1 gen002 estimated 24 µs is achievable** — this was optimistic. Using theoretical 50 GB/s bandwidth (not the measured 24.84 GB/s) and not accounting for medium's bandwidth floor. The achievable target is closer to 50–80 µs.
- **pattern_003 (template specialization hurts I-cache)** — may not apply when only 3 specializations exist and only one executes per benchmark run. The pattern was observed with many simultaneous template instances.

## 4. State of Affairs accuracy

Mostly accurate. Key gap: it lists 24 µs as target without flagging that bandwidth analysis shows this is physically impossible given measured hardware. The SoA should include a note that ~50–80 µs is the realistic best-achievable target.

## 5. What I would do differently with more time

- Write and evaluate a concrete solution: row-streaming + size-adaptive 128-bit NT stores (idea_015 fix). This is the single highest-leverage change.
- Measure actual 2-thread bandwidth on the machine before writing multi-threaded code.
- Check the assembly of the best solution with `objdump -d` to confirm port pressure assumptions.

## 6. Specific experiments to run

**Experiment A (critical, highest priority)**: Row-streaming best (sol01) + size-adaptive 128-bit NT stores. Only change: replace `_mm512_storeu_si512` with 4× `_mm_stream_si128` when `n*m*4 > 8MB`. Add `_mm_sfence()` at end. Expected large: 3841 → ~1350 µs, geomean: ~105 µs.

**Experiment B (high priority, unexplored)**: 2-thread gemmCandidate with static thread pool. Thread 0: rows 0..n/2-1. Thread 1: rows n/2..n-1. Each thread does NT stores for its slice. Main thread does `_mm_sfence()` after join. Measure vs single-thread on large. If bandwidth scales to 40+ GB/s: large → ~840 µs.

**Experiment C**: Template dispatch on k_bytes (compile-time). Measure small time with k_bytes=2 fully unrolled. Expected: 3.69 → 1.0–1.5 µs.

**Experiment D**: Combine A+C: template dispatch + NT stores for large. Expected geomean: ~80 µs.

## 7. What surprised me

The experimentator's NT store result (sol01 analog with NT stores → 4226 µs) is WORSE than the current row-streaming best (3841 µs without NT stores). This means the previous NT store experiments were on the old BLIS solutions, not the row-streaming architecture. The key combination (row-streaming + size-adaptive NT stores) has NEVER been tested. This is the most surprising gap in the coverage matrix.

Also surprising: medium at 225.55 µs is essentially AT the bandwidth floor (220–230 µs). This makes medium improvement nearly impossible via any approach that still writes 4 MB of int32 output.

## 8. Helper tools feedback

Did not use any helpers. No helpers were needed for a pure research session.

## 9. Time budget

Time ran out before I could write and evaluate any solution code. The research was thorough but the most valuable contribution would have been Experiment A (row-streaming + 128-bit NT stores). If given more time, I would immediately implement and evaluate that solution, as it is the most impactful single change available.
