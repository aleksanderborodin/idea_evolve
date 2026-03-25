# System Recommendations — Generation 1 → 2

## Priority 1: CRITICAL — Fix the evaluate-immediately breakdown

**Problem**: All 3 solution agents wrote batches of solutions before evaluating any.
This caused cascading timeouts (work + wrap-up both timing out), wasted compute, and
prevented in-session iteration on results.

**Root cause**: Agents under exploration pressure default to writing code first. With training
runs of 40k–80k steps per solution, one evaluation takes real time. Agents rationalize deferring.

**Recommended changes**:

1. **Reduce the per-session solution target**. Change agent prompts (explore.md, full.md,
   exploit.md) to target **4–6 solutions maximum**, with evaluate-immediately enforced between
   each. Better to have 4 evaluated solutions than 13 unevaluated ones.

   Current language seems to allow open-ended exploration. Add explicit cap: "Write at most
   6 solutions total. Evaluate each before writing the next. Quality over quantity."

2. **Add early-stop self-check**. Add instruction: "After writing each solution, check your
   remaining time estimate. If you have evaluated at least 3 solutions and time is getting
   short, stop writing new solutions and write your report."

3. **Make evaluate-immediately the very first bullet point** in the workflow section, bolded
   and on its own line. It's currently embedded in a larger workflow section.

**Expected impact**: Reduces timeout rate from 3/3 to ~0–1 per generation. Saves ~4000s of
wrap-up + debrief compute. Gives agents real feedback to iterate on.

---

## Priority 2: CRITICAL — Add "read best current solution" as step 0 for solution agents

**Problem**: explore_2 didn't read the baseline before writing sol01, producing C=2.0 (vs
baseline 1.5185). The agent wasted its first and only scored run on a known dead end.

**Root cause**: Agent prompts list files to read but don't mandate reading the best current
solution *before* writing anything.

**Recommended change**: Add to the top of explore.md, exploit.md, full.md, genetic.md:

> **Step 0 (mandatory before writing any solution):**
> Read the best current solution at `population/best.py` (gen 2+) or the baseline at
> `problem/initial_programs/optimize.py` (gen 1). Note its score, approach, and structure.
> Your first solution should either improve on it directly or explore a meaningfully different
> direction.

**Expected impact**: Eliminates cold-start dead ends where agents re-discover known bad
approaches. Saves 1–3 wasted evaluations per session.

---

## Priority 3: MODERATE — Update State of Affairs after gen 1

**Problem**: `knowledge/state_of_affairs.md` still shows "generation: 0" and "Pre-Generation"
content. The gen-2 Architect will read stale Layer 0 content, not knowing about multi-scale
Adam (idea_004), the C=2 dead end (pattern_001), or the best gen-1 score (~1.5167).

**Root cause**: Either the evaluator was supposed to write it but didn't, or the finalize
phase didn't trigger an update. The evaluator produced ideas and patterns but not a State
of Affairs update.

**Recommended change**: Ensure the Consistency Reviewer or Finalize phase writes a
gen-1 State of Affairs before gen 2 runs. At minimum, manually update the file with:
- best_score: ~1.5167
- trajectory: improving (baseline 1.5185 → 1.5167)
- what works: multi-scale Adam (N=600→N=2000), Adam > L-BFGS cold start
- dead ends: symmetric unimodal init → C=2.0

**Expected impact**: Gen-2 Architect can plan a coherent strategy. Without this update,
gen-2 agents may repeat gen-1 mistakes.

---

## Priority 4: MODERATE — Steer gen 2 toward untested high-value directions

Based on the research findings (which were excellent) and gen-1 results, gen-2 agents
should specifically target:

1. **Symmetry + bimodal init** (untested combination): enforce even symmetry by optimizing
   half-domain and mirroring, but initialize with two-bump function (not unimodal). This is
   the theoretically predicted optimal structure.

2. **softplus/exp reparameterization** (research-recommended, untested in multi-scale context):
   replace relu(g) with softplus(g) in the standard multi-scale Adam pipeline.

3. **Sidon-inspired 4-bump initialization**: bumps at x ≈ {-0.25, -0.167, 0, 0.25} per
   research_1/findings.md. Zero gen-1 agents tried this specific initialization.

**Recommended change**: In the gen-2 Architect brief, explicitly direct at least one
explore agent to try each of these. Don't let gen-2 be another round of multi-scale Adam
with slight variations — those all cluster around 1.517x.

---

## Priority 5: MINOR — Evaluator should write evaluator_report.md

**Problem**: No evaluator_report.md exists in reports/gen001/ despite the evaluator running
for 554s. The report is how the Architect learns evaluator insights and strategic recommendations
for the next generation. Missing it leaves strategic guidance out of the planning loop.

**Recommended change**: Verify evaluator.md template correctly instructs writing evaluator_report.md
(not report.md or another filename). Check the orchestrator's phase detection to ensure the
evaluator is prompted to complete its report before timing out.

---

## Priority 6: MINOR — Monitor coverage matrix creation in gen 2

The coverage matrix was not created in gen 1 (expected for gen 1 bootstrap). The gen-2
Evaluator should create it. Verify that `history/coverage_matrix.md` exists after gen 2.
If not, investigate whether the evaluator prompt clearly instructs its creation and format.
