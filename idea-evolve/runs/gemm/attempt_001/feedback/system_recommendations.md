# System Recommendations — Generation 3

Supersedes gen002 recommendations where noted. Prioritized by impact.

---

## REC-1 [CRITICAL] Implement .score Auto-Write in evaluate.py

**What:** Modify `problem/evaluate.py` to always write a `.score` JSON sidecar at `{solution_path}.score` immediately after every evaluation, unconditionally. The agent may also write it (idempotent), but the evaluator's write happens regardless of agent behavior.

**Why:** exploit_1 in gen003 had 12 of 13 solutions with no `.score` file — identical to the explore_1 issue in gen002 that REC-5 (gen002) flagged as HIGH. Two consecutive generations with the same data loss pattern confirms the prompt-level fix doesn't work. A code-level fix is required.

**Expected impact:** Eliminates the score data loss entirely. Ensures all evaluated solutions appear in rankings. Allows the evaluator to skip re-evaluation. Zero behavioral change for compliant agents.

**Status:** Gen002 REC-5 — UNIMPLEMENTED. Escalating to CRITICAL.

---

## REC-2 [CRITICAL] User Must Confirm Realistic Target Score

**What:** Present the following to the user and request confirmation:

> Three independent analyses across generations 2-3 show the 24 µs target is physically impossible. Medium benchmark is within 8% of its memory bandwidth floor (~220-230 µs). The achievable geomean minimum, assuming perfect large optimization, is ~50-80 µs. The recommended realistic target is **60-70 µs**. Should we optimize toward this target, or is there a constraint relaxation (different output format, harness modification) that would allow reaching 24 µs?

**Why:** Agents that correctly compute the bandwidth floor are concluding the problem is unsolvable, then not proposing the creative solutions that would actually push below 80 µs. A confirmed realistic target re-energizes the search. Gen002 REC-2 made this same point — two generations have passed without action.

**Expected impact:** Agents stop chasing impossible physics. Effort concentrates on achievable 60-80 µs range.

**Status:** Gen002 REC-2 — UNIMPLEMENTED. Escalating to CRITICAL.

---

## REC-3 [CRITICAL] Gen003 Consistency Review Must Rewrite State of Affairs

**What:** The gen003 consistency review (triggered by gen % 3 == 0 rule) MUST produce an updated `state_of_affairs.md`. Verify the consistency reviewer session actually launched and produced output. If it was skipped or failed, re-run it manually.

**The updated SoA must include at minimum:**
- generation: 3, best_score: 141.0
- Row-streaming as the established best architecture (idea_014: established)
- Memory bandwidth wall as the defining constraint (pattern_011)
- Correct bandwidth floor calculations (medium floor: 220µs, large floor: ~2000µs)
- Debunked: vpshufb (idea_018), 8-row direct (high C-scatter cost), aligned-buffer-memcpy NT stores
- Realistic target: 60-80 µs (not 24 µs)
- Top untested priorities: 4-row ternlogd, SSE NT stores, multi-threading

**Why:** gen002 consistency review failed (0 output in 31.9s). The SoA is two generations stale. Every gen004 agent will read wrong context first.

**Expected impact:** Each agent saves 10-20 context-reading turns. Strategic context is accurate.

---

## REC-4 [HIGH] Add bench_harness.cpp to Preflight Check

**What:** In `orchestrator.py`, extend `_preflight_check()` to verify `fast-conv/bench_harness.cpp` exists and has size > 0.

**Why:** Gen002 architect noted bench_harness.cpp was found in the Trash and restored by exploit_1. Root cause still unknown. Without preflight, silent evaluation failure could occur if it disappears again.

**Status:** Gen002 REC-3 (investigate), REC-11 (preflight) — still unresolved.

---

## REC-5 [HIGH] Update fact_004 — vpopcntb Port Assignment Was Wrong

**What:** The evaluator should have deprecated `fact_004` and created `fact_008` with the correct assignments (experimentator_1 confirmed via microbenchmark):
- vpopcntb: port 0/1, throughput 0.5c (NOT port 5 as fact_004 stated)
- vpbroadcastb: port 5 only, throughput 1c (confirmed bottleneck)
- vpternlogq: ports 0/5, throughput 0.5c (confirmed)

Verify `fact_008` exists in `knowledge/facts/`. If fact_004 is still present and not deprecated, the evaluator must fix this before gen004 agents read it.

**Why:** Gen004 agents reading fact_004 will optimize away from vpopcntb (wrong bottleneck) instead of vpbroadcastb (actual bottleneck). This would direct gen004 effort to the wrong target.

---

## REC-6 [HIGH] Brief Gen004 with Concrete Implementation Specs for Top Priorities

The gen004 Architect should brief exploit agents with concrete, step-by-step implementation specs for the three highest-priority experiments. Vague "try idea_022" briefs lead to wasted turns on direction-finding.

**Priority 1: 4-row ternlogd+vpopcntb kernel (idea_022)**
```
Start from population/best.py (141.0 µs row-streaming kernel).
Modify gemmCandidate to process 4 rows simultaneously per B-panel load:
- Load B[j..j+NC] once (same as 1-row kernel)
- For rows r, r+1, r+2, r+3: broadcast A[r][t], A[r+1][t], A[r+2][t], A[r+3][t]
- Compute 4 independent ternlogd+popcnt operations per k-byte
- Accumulate 4 separate int8/int16 acc registers
- Flush all 4 accumulators to C[r..r+3] after j-loop
Expected: large ~2300 µs (1.67x from B-amortization), geomean ~80-95 µs.
```

**Priority 2: SSE 128-bit NT stores, size-adaptive (idea_021)**
```
Start from the 4-row kernel above (or best.py if 4-row fails).
Replace _mm512_storeu_si512 writes to C with:
  if (n*m*4 > 8*1024*1024) {  // large benchmark only
    // Decompose zmm to 4 xmm and stream-store (16-byte aligned)
    _mm_stream_si128((__m128i*)(C + offset), _mm512_extracti64x2_epi64(acc, 0));
    _mm_stream_si128((__m128i*)(C + offset+4), _mm512_extracti64x2_epi64(acc, 1));
    _mm_stream_si128((__m128i*)(C + offset+8), _mm512_extracti64x2_epi64(acc, 2));
    _mm_stream_si128((__m128i*)(C + offset+12), _mm512_extracti64x2_epi64(acc, 3));
  } else {
    _mm512_storeu_si512(C + offset, acc);  // unchanged for small/medium
  }
Add _mm_sfence() after the j-loop.
Expected: large ~1350 µs (2.3x from NT stores), geomean ~105 µs.
```

**Priority 3: Combined (4-row + SSE NT stores)**
```
Combine priorities 1+2. Expected geomean: ~60-80 µs.
```

---

## REC-7 [HIGH] Measure C Alignment Per Benchmark Size Definitively

**What:** Create a diagnostic solution that adds `fprintf(stderr, "C=%p mod64=%zu n=%d m=%d\n", C, (uintptr_t)C%64, n, m)` to gemmCandidate and run evaluate.py. Read the stderr output to determine alignment for all 4 benchmark sizes (correctness + 3 benchmark sizes).

**Why:** Three gen003 agents independently requested this measurement. The NT store strategy depends entirely on knowing whether large C is 64-byte aligned (mmap behavior) or only 16-byte aligned. Without it, every NT store experiment is guessing. This is a 5-minute experiment that should have been done in gen001.

**Expected output:** Confirms whether size-adaptive NT stores (SSE 128-bit for large, regular for small/medium) are safe.

---

## REC-8 [MEDIUM] Investigate gen002 Consistency Review Failure Root Cause

**What:** Check the timeout configuration for the consistency review session. The gen002 reviewer produced zero output in 31.9s — a full session should run much longer. Check whether: (a) the timeout was accidentally set to 32s, (b) the session crashed immediately due to a missing file, or (c) the agent was launched but wrote no files due to a path issue.

**Why:** If the root cause isn't fixed, gen003's consistency review will also fail, leaving the SoA stale for another generation.

---

## REC-9 [MEDIUM] Research_1 Role Clarification for gen004

**What:** If a research agent is included in gen004, brief it with: "Write and evaluate at least one solution before writing the research report. The highest-priority implementation is [specific experiment]. Research findings should accompany code, not replace it."

**Why:** research_1 in gen003 correctly identified the #1 experiment (row-streaming + SSE NT stores) but ran out of time to implement it. The analysis was valuable but the execution slot was wasted.

---

## Recommendations Superseding Gen-2

| Gen-2 Rec | Status | Action |
|-----------|--------|--------|
| REC-1 (verify scoring metric) | **RESOLVED** — Architect read validate.py, confirmed geometric mean. Documented in gen003 briefs. | Add metric_formula to metrics.yaml |
| REC-2 (24µs infeasibility) | **UNRESOLVED** — now REC-2 above, escalated | User confirmation required |
| REC-3 (bench_harness preflight) | **PARTIALLY RESOLVED** — investigate complete, preflight still not added | Now REC-4 above |
| REC-4 (exploit from row-streaming) | **RESOLVED** — gen003 exploit_1 briefed on row-streaming from start | Continue |
| REC-5 (.score auto-write) | **UNRESOLVED** — same data loss recurred in gen003 | Now REC-1 above, escalated to CRITICAL |
| REC-6 (aligned-buffer NT) | **RESOLVED experimentally** — tested, failed (memcpy too slow). Dead end confirmed. | Don't retry |
| REC-7 (8-row int8 kernel) | **RESOLVED experimentally** — explore_1/sol02 tested 8-row: 168µs (wins on large, hurts small). 4-row may be better balance. | Now REC-6/Priority 1 |
| REC-8 (metric_formula field) | **UNRESOLVED** — still missing from metrics.yaml | Minor; add when convenient |
| REC-9 (fact_004 disputed) | **RESOLVED experimentally** — vpopcntb confirmed port 0/1 via microbenchmark. fact_004 wrong. | Now REC-5 above |
| REC-10 (vpshufb explore) | **RESOLVED** — implemented by explore_2, debunked. 342µs worst result. | Closed |
| REC-11 (bench_harness preflight) | **UNRESOLVED** | Now REC-4 above |

## Summary Table

| ID | Priority | Action | Owner |
|----|----------|--------|-------|
| REC-1 | CRITICAL | Auto-write .score in evaluate.py | orchestrator/evaluate.py |
| REC-2 | CRITICAL | User confirms realistic target (60-80µs) | User review |
| REC-3 | CRITICAL | Consistency review rewrites State of Affairs | Gen003 consistency reviewer |
| REC-4 | HIGH | Add bench_harness.cpp to preflight | orchestrator.py |
| REC-5 | HIGH | Fix/deprecate fact_004, verify fact_008 exists | Evaluator/Consistency Review |
| REC-6 | HIGH | Brief gen004 with concrete implementation specs | Gen004 Architect |
| REC-7 | HIGH | Measure C alignment per benchmark size | Gen004 diagnostic agent/exploit |
| REC-8 | MEDIUM | Investigate consistency review failure root cause | User/orchestrator |
| REC-9 | MEDIUM | Clarify research agent role: implement first | Gen004 Architect |
