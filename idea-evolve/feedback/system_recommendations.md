# System Recommendations — Generation 1

Prioritized from highest to lowest impact.

---

## REC-1 [CRITICAL] Add "write-first" cap to explore.md

**What to change**: In `agents/explore.md`, add an explicit instruction at the top of the workflow section:

> "Your FIRST priority after reading `problem/description.md` and `problem/initial_programs/optimize.py` is to write `output/sol01.py` and evaluate it immediately. Do NOT read more than 2-3 additional files before writing your first solution. If you are still reading files after turn 10 without having submitted a solution, stop reading and start writing."

**Why**: explore_2 spent its entire session reading 7+ files and was interrupted before producing any code. The evaluate-immediately mandate only kicks in once code exists; it doesn't prevent excessive pre-code reading. This is a pure capacity loss with no benefit.

**Expected impact**: Recovers the full productive capacity of exploration agents. For a problem where each solution provides ~3 data points for the knowledge base, one wasted agent slot is significant.

---

## REC-2 [CRITICAL] Rerun baseline benchmark to confirm the 770 µs figure

**What to change**: Before gen 2, manually run `evaluate.py` on the V14opt baseline solution (`problem/initial_programs/optimize.py`) and record the measured time. Update `problem/metrics.yaml` and the State of Affairs if the figure differs from 770 µs.

**Why**: Both first-attempt AVX-512 solutions (explore_1/sol01: 654 µs, full_1/sol01: 602 µs) beat the baseline without applying the key optimizations (memset skip, vectorized packing). This suggests the 770 µs baseline may be inaccurate or was measured under different conditions.

**Expected impact**: Correct framing for speedup calculations and target-setting. If the real baseline is lower (say 600 µs), the target of 477 µs is ~80% of baseline, much harder than the stated 62%.

---

## REC-3 [HIGH] Canonicalize vpternlogd operand convention

**What to change**:
1. Update `knowledge/ideas/idea_011.md` to document both known conventions (operand order A: explore_1's 0xD8/0xE4; operand order B: research_1's 0xCA/0xAC) and state explicitly which is canonical.
2. Brief gen 2 agents to use the canonical form and add a comment in their code with the truth table derivation.

**Why**: explore_1 and research_1 arrived at different imm8 constants for the same logical operation. Both produce correct results, but agents building on these solutions may mix conventions and introduce silent correctness bugs. This is the hardest class of bug to diagnose.

**Expected impact**: Prevents future correctness failures from convention confusion. Low cost, high insurance value.

---

## REC-4 [HIGH] Brief gen 2 agents to run perf stat on NC=256 vs NC=512

**What to change**: In the gen 2 Architect's brief for at least one exploit or explore agent, include a specific instruction: "Run `perf stat -e L1-dcache-load-misses,dTLB-load-misses,LLC-load-misses,cycles,instructions` comparing NC=256 and NC=512 on the best current solution. Report the hardware counter differences."

**Why**: The NC=512 regression was observed by every agent that tested it but no one understands why. Without understanding the root cause, agents cannot make informed NC decisions for other configurations (e.g., different kernel widths, different problem sizes).

**Expected impact**: Resolves a persistent open question. If the root cause is TLB pressure, we can fix it; if it's L1 conflict misses, we understand the cache geometry better.

---

## REC-5 [HIGH] Prioritize no-packing direct kernel (idea_013) in gen 2

**What to change**: The Architect should assign at least one gen 2 agent to implement idea_013 (read B directly without packing). The brief should include: "For the small benchmark, k_bytes=2, B matrix = 2KB — fits entirely in L1. Try accessing B directly instead of pack_B → micro-kernel. If B columns are strided, test both column-major direct access and transposed one-time copy."

**Why**: Evaluator and multiple solution agents independently ranked this as the highest-priority unexplored idea. pack_B was the second-biggest bottleneck in gen 1. Eliminating it entirely could give another 30-50% speedup on small/medium.

**Expected impact**: Moderate to high. If the direct kernel works, it eliminates packing overhead entirely for small/medium benchmarks.

---

## REC-6 [MEDIUM] Move research agent to a sequential group before solution agents

**What to change**: In the Architect's manifest planning, place `research_1` in group 1 (sequential, runs first), then solution agents (explore, exploit, full) in group 2.

**Why**: In gen 1, research ran in parallel with solution agents. Several research findings (KC tiling removal, int8 accumulation safety, B-fits-in-L2) were re-discovered empirically by solution agents rather than being used proactively. With research findings available before solution agents start, briefs can be more targeted.

**Trade-off**: Adds one research session's wall-clock time (~15 min) before solution agents can start. The benefit is more informed solution agent briefs.

**Expected impact**: Moderate. 1-2 extra optimizations discovered per generation when research findings inform initial solution approaches rather than being rediscovered.

---

## REC-7 [MEDIUM] Add int8 accumulation to gen 2 priority experiments

**What to change**: Brief at least one exploit agent to test int8 accumulation in the micro-kernel inner loop. Specifically: accumulate in `__m512i` int8, widen to int32 once after the k-loop using `_mm512_cvtepi8_epi32`. Verify that k_bytes ≤ 7 → max diff ≤ ±56 < int8 max (±127).

**Why**: research_1 derived this is safe. It halves register pressure (1 zmm accumulator per row vs 2 for int16), potentially enabling wider kernels (6-row, 8-row) or freeing registers for prefetching.

**Expected impact**: Moderate. If register pressure was the bottleneck for 8-row kernels (as explore_1/sol03 indicated), int8 accumulation could unblock them.

---

## REC-8 [LOW] Add score-summary helper to problem/helpers/

**What to change**: Create `problem/helpers/score_summary.py` with a function that reads all `.score` files in a directory and returns a sorted table.

**Why**: The evaluator noted spending "significant turns" reading individual `.score` files to compile solution tables. This is mechanical work that could be automated.

**Expected impact**: Minor time savings for evaluator (~5-10 turns per generation). Cumulative savings grow with population size.

---

## Summary Table

| ID | Priority | Action | Agent/File |
|----|----------|--------|-----------|
| REC-1 | CRITICAL | Add write-first cap | `agents/explore.md` |
| REC-2 | CRITICAL | Re-measure baseline | Manual + `metrics.yaml` |
| REC-3 | HIGH | Canonicalize vpternlogd | `knowledge/ideas/idea_011.md` |
| REC-4 | HIGH | perf stat NC analysis | gen 2 exploit/explore brief |
| REC-5 | HIGH | No-packing kernel (idea_013) | gen 2 agent brief |
| REC-6 | MEDIUM | Research before solution agents | Architect manifest |
| REC-7 | MEDIUM | int8 accumulation test | gen 2 exploit brief |
| REC-8 | LOW | score_summary helper | `problem/helpers/` |
