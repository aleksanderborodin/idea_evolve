# System Critic Debrief — Generation 5

## 1. What did I try?

Read all 5 agent debrief reports (architect, exploit_1, exploit_2, explore_1, research_1),
the evaluator report and debrief, the current system_recommendations.md (gen 4), the
state_of_affairs.md (gen 3), population summary, score progression, agent_gaps/gen005.md,
and spot-checked .score files for eval_time anomalies.

Approach: started by reading all reports in parallel, identified the most critical anomalies
(eval_time=792s, float32 bugs, SoA staleness), then cross-referenced to find root causes
vs. symptoms.

All 3 output files produced: system_analysis.md, system_recommendations.md, experiment_suggestions.md.

## 2. What information did I lack?

- **history/timing.json** — did not read. Would have confirmed whether phase timings show
  the Consistency Review has been attempted and how long it took if so.
- **knowledge/clusters/** and **knowledge/ideas/** current state — did not read. Would have
  confirmed whether evaluator outputs were correctly merged into knowledge base.
- **The actual eval_cache.json** — did not check whether exploit_2/sol01's array is somehow
  recoverable from the cache. The cache stores scores, not arrays, so it wouldn't help, but
  worth confirming.
- **Whether finalize phase has already run for gen 5.** Score progression and population
  summary both appear stale (missing gen 5 data). Could not determine if this is because
  finalize hasn't run yet (expected) or because it ran and failed silently.

## 3. What given facts might be wrong or outdated?

- **Pattern_007's confidence level.** This is the most important uncertain fact. The entire
  pipeline strategy depends on it. All evidence was float32. If float64 re-test revises it,
  the gen 4 and 5 exploit strategies were partially wasted.
- **"exploit type: best is 1.5032"** in population summary — the summary doesn't include
  gen 5 exploit results (exploit_2/sol01 at 1.5028628894 is a research-category solution
  that was converted to exploit via coordinate descent, but is listed under exploit in
  population). This is a categorization question, not a correctness error.
- **The score progression table.** Shows gen 4 as last entry. Either finalize hasn't run
  for gen 5, or there's a bug. Noted but not investigated.

## 4. Was the State of Affairs accurate?

No. The SoA is gen 3 and is significantly stale on multiple fronts:
- Recommends warm-start smooth-max Adam as Priority 1 (closed by gen 4 pattern_007)
- Says TTT-Discover array is unavailable (retrieved in gen 4)
- Missing: pattern_007, pattern_008, pattern_009, the float64 insight, 5 intermediate arrays
- Open Question 1 ("Can warm-start push 1.5032 below 1.503?") was answered: not with smooth-max Adam

The Consistency Review MUST run before gen 6.

## 5. What would I do differently with more context?

- Read history/timing.json to check if the Consistency Review was attempted and what happened.
- Read the actual knowledge files (clusters, ideas) to check whether evaluator outputs from
  gen 4 were correctly merged. The gen 4 SoA staleness may indicate a broader merge failure.
- Check whether the orchestrator's Consistency Review trigger condition (gen % interval == 0
  or strategic_shift) was met and whether it ran.

## 6. Specific experiments to run?

See experiment_suggestions.md. In priority order:
1. Float64 coordinate descent extension (high probability of incremental improvement)
2. Float64 re-test of Pattern_007 (binary, highest strategic value)
3. Bulk LP residual cleanup (quick, should be bundled with #1)
4. LP-based refinement (high effort, high ceiling)

## 7. What surprised me?

1. **The 792.6s eval_time is not caught anywhere.** The finalize phase, ranking system, and
   population summary all accept this solution without any warning. There is no eval_time
   threshold check in the pipeline. A future agent could easily submit a solution that
   takes hours to evaluate, and the system would silently accept it.

2. **exploit_1 was remarkably thorough given a null result.** Six distinct approaches tested
   and documented. This is better than most positive-result agents. The pipeline is producing
   high-quality negative results — the knowledge base is getting denser even without score improvements.

3. **The Consistency Review has not run in at least 2 complete generations despite being
   flagged as Priority 1 twice.** This suggests either (a) the trigger condition isn't
   being met, (b) the review is running but its outputs aren't being integrated, or (c)
   the system critic's recommendations are advisory and the user has chosen not to act on
   Priority 1. The third possibility is worth considering — the user may be prioritizing
   agent runs over meta-level consistency updates.

4. **All gen 5 agents completed within budget** — this is the first clean generation with
   no timeouts. The compute budget references in briefs genuinely resolved the timeout problem.

## 8. Helper tools feedback

I did not use helpers directly (system critic does not run optimization).

Based on reports, critical helper issues:

**Deployed helpers with bugs:**
- `helpers/sensitivity.py`: float32 gives wrong sensitivity rankings for micro-optimization.
  This is a correctness bug, not a precision trade-off. Needs float64 mode.
- `helpers/core.py (compute_c)`: float32 precision insufficient for accept/reject at this
  optimization level (~1e-8 improvements). Not suitable as an oracle for optimization.

**Missing helpers (by priority):**
1. `compute_c_f64`: numpy float64 compute_c matching validate.py. #1 request, trivial to implement.
2. `autoconv_analysis`: returns autoconvolution peak position, near-tight constraint indices,
   contributing element pairs. Needed for LP-based refinement.
3. `load_cached_solution(path)`: loads the numpy array from a solution without re-running
   entrypoint(). Needed because exploit_2/sol01 takes 13 minutes to evaluate.
4. `benchmark_step_time(N)`: returns ms/step for gradient operations at given N.
5. `prepare_warm_start(array, target_n)`: inv_softplus + optional interpolation in one call.

**Helpers README**: Still says "none yet" — must be updated to list inv_softplus, sensitivity,
interpolation with their precision notes and known limitations.
