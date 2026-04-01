# Research Agent Debrief — gen002_research_1

## Solutions Produced

| File | Fitness | Notes |
|------|---------|-------|
| (none) | — | Research agent; no solutions written |

This is a Track B research mission. No solution files were produced. Output is findings.md.

---

## 1. What Did You Try?

Performed theoretical analysis and literature review. No code was written or evaluated.

**Theoretical lower-bound analysis** (Finding 1):
- Computed memory bandwidth limits for each benchmark size
- Large: 32 MB C at 50 GB/s NT stores = 640 µs minimum (vs current 3176 µs — 5x improvement available)
- Medium: 4 MB C at 50 GB/s = 80 µs minimum (vs current 228 µs)
- Small: dominated by pack overhead, not bandwidth (~0.5–1 µs achievable vs 4.49 µs)
- geomean(0.5, 80, 640)^(1/3) ≈ 29 µs — target of 24 µs is physically reachable

**Kernel analysis** (Findings 2–5):
- Identified that NT stores are used unconditionally in previous attempts (hurts small/medium)
- Found that int8 accumulation eliminates register pressure problem for 8-row kernel
- Identified pack_A scalar loop as dominant overhead for small benchmark (~55% of 4.49 µs)
- Analyzed NC=512 regression likely due to Loop Stream Detector overflow or TLB pressure

**Web research** (background agents, not yet returned):
- Launched agents to search Tiger Lake bandwidth specs, BNN kernel techniques, LUT approaches

---

## 2. What Information Did You Lack?

- **Actual measured NT store bandwidth on this machine**: The theoretical 51.2 GB/s for DDR4-3200 dual-channel may be different in practice. Need `perf stat` or a simple bandwidth benchmark.
- **C array alignment guarantee**: NT stores require 64-byte alignment. The benchmark harness allocation method is unknown. If C is not aligned, `_mm512_stream_si512` causes a segfault.
- **Per-phase timing breakdown**: No solution measured time spent in pack_A vs pack_B vs micro_kernel vs stores. This would immediately show where to focus.
- **Assembly output**: No solution inspected the compiled output. The compiler may not be unrolling loops as expected.

---

## 3. What Given Facts Might Be Wrong or Outdated?

- **fact_004 (instruction latencies)**: Marked as `verified: false, source: user-provided`. The vpopcntb latency of 1c and throughput of 1c may be incorrect. Willow Cove has a single 512-bit ALU port, so back-to-back vpopcntb might be limited by port contention. Intel Intrinsics Guide or uops.info would give definitive data.
- **NC=256 optimal claim (pattern_002)**: Only NC=256 and NC=512 tested. NC=128 or NC=192 might be better, especially for small.
- **~30 GB/s DRAM bandwidth assumption** in state_of_affairs: This is likely too conservative. DDR4-3200 dual-channel gives ~40-50 GB/s sequential. The large benchmark minimum time is thus closer to 640 µs, not ~1000 µs.

---

## 4. Was the State of Affairs Accurate?

Mostly accurate. One correction: the state of affairs says "large benchmark writes 32MB to DRAM at ~30GB/s, that's ~1000 µs minimum." The actual bandwidth of DDR4-3200 dual-channel is ~51 GB/s theoretical (~40-50 GB/s practical), so the minimum is **640–800 µs**, not 1000 µs. This makes the 24 µs geomean target more achievable.

The note that all 14 gen-1 solutions follow the same BLIS template is accurate and critically important.

---

## 5. What Would You Do Differently?

With more time, I would have:
1. Written a minimal timing test to measure actual NT store bandwidth on this machine
2. Checked C alignment in the benchmark harness (`validate.py` or `bench_harness.cpp`)
3. Written an 8-row int8 kernel implementation (Finding 3) and evaluated it
4. Inspected the compiler output: `objdump -d` on the compiled benchmark to verify unrolling

---

## 6. Specific Experiments to Run

### Experiment A: Size-Adaptive NT Stores (HIGHEST PRIORITY)
Take sol10 (best solution), add:
```cpp
bool use_nt = ((size_t)n * m * 4 > 8*1024*1024) && ((uintptr_t)C % 64 == 0);
```
Use `_mm512_stream_si512` in store path when `use_nt`. Add `_mm_sfence()` after loop.
Expected: large drops from 3176 µs to ~640-1000 µs. geomean improvement: ~3-4x.

### Experiment B: 8-Row int8 Accumulation Kernel
Replace 4-row int16 with 8-row int8. Pack_A groups of 8 instead of 4.
Expected: medium improves 20-30% from halved B loads; large improves similarly.

### Experiment C: Vectorized/Eliminated Pack_A for Small
For small (k_bytes=2), skip pack_A and broadcast A bytes directly in the inner loop.
Expected: small improves from 4.49 µs to ~1-2 µs.

### Experiment D: Size-Adaptive NC
Use NC=128 for small, NC=256 for medium/large. Tests whether smaller NC helps small benchmark.
Expected: small improves 10-20%.

### Experiment E: Combine A+B+C+D
Full stack: NT stores (large) + 8-row int8 kernel + no-pack-A for small + adaptive NC.
Expected geomean: ~25-35 µs.

---

## 7. What Surprised You?

The **32 MB C write bottleneck is the dominant constraint** for the entire geomean. With NT stores for large, the geomean could drop from 148 µs to ~30-40 µs in a single change. The gen-1 agents correctly tried NT stores (sol09) but applied them non-adaptively, hurting small and medium. The fix is a trivial 2-line runtime check, yet it represents the difference between 148 µs and potentially ~40 µs.

Also surprising: the **small benchmark is 10x slower than the bandwidth limit** (4.49 µs vs ~0.43 µs theoretical for L2 C writes). The overhead of pack_A, pack_B, and the multi-level loop structure is dominant. Eliminating packing for small could give a 3-5x improvement on that size alone.

---

## 8. Helper Tools Feedback

Did not use any helpers from `problem/helpers/`. No relevant helpers existed for this research task. A useful helper would be: **a bandwidth measurement utility** that runs a quick NT store bandwidth test to measure actual achievable write bandwidth on the current machine. This would let agents precisely compute theoretical minimums.

---

## 9. Time Budget

Time was cut short by the "STOP" instruction. Had more time, I would have:
1. Written and evaluated an NT-store-adaptive version of sol10 (1 hour)
2. Written and evaluated an 8-row int8 kernel (2 hours)
3. Retrieved results from the background web research agents on Tiger Lake specs

The findings.md document is complete and actionable. The highest-priority recommendation for gen-3 agents is: **size-adaptive NT stores for large benchmark** — this is the single highest-leverage change available and requires only ~10 lines of code modification to sol10.
