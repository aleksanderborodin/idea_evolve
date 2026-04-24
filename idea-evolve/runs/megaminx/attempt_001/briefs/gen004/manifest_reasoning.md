# Manifest Reasoning — Gen 004

## Situation

Three generations run. Best = **44094** (gen003_explore_2_sol01), improved by 20 moves over the 44114 compression floor that 7 solutions converge on. Gap to target (15000) is 29094 moves. Gap to Kaggle top-3 equivalent (8050 proxy) is 5.5×.

The pipeline has a concrete, verified plan of attack — **idea_013 (combined recipe)** — assembled by research_1 in gen003 from four verified components (BFS data, embedding MLP, built-in MITM, compression fallback). Every individual component is confirmed to work. **The combined recipe has never been executed end-to-end.** That is the single most valuable piece of information gen004 can produce.

Gen003 was also a catastrophic execution failure: **three of five agents consumed 6300s each across work+wrap_up+debrief with zero output** (experimentator_1, explore_1, exploit_1). The root cause was "implement the full pipeline in one session" with no intermediate milestones — when the agent got stuck at the 40-minute mark, there was no scored checkpoint to fall back to. The System Critic's REC-1 mandates a Milestone Protocol for every complex brief, and I am enforcing it on every brief in this generation.

## Agent mix (5 total — well within the 3–8 budget)

### Track A — Directed (3 agents)

- **exploit_1 (opus, 2100s):** Execute idea_013 end-to-end. Highest-value task. Milestone protocol: sol01 must exist before scaling. Timeout 2100s (35 min) — shorter than gen003's 3600s, forcing the milestone discipline. If sol01 lands but iteration stalls, wrap-up keeps the result.
- **experimentator_1 (opus, 1500s):** Build a corrected helper (`output/helpers/embedding_predictor_beam.py`) that bundles the combined recipe behind one function call. Addresses REC-3. Scope is strictly bounded: one file, one entry point, one smoke test. If it works, gen005 agents call the helper directly and skip the boilerplate. The existing broken helper stays (to avoid breaking in-flight references) and gets deprecated post-validation.
- **explore_2 (sonnet, 1800s):** Track A directed — per-bucket hybrid strategy, explicitly targeting the very_hard bucket (74.8% of score). Complementary to exploit_1's "does the recipe work at all?" with the question "where is compute best spent?" First milestone is compression-only sol01 → guaranteed 44114. Runs in group 2 so it can reuse anything group 1 deploys (helper, trained model, findings).

### Track B — Radical (2 agents, minimum 1 explore + 1 research enforced)

- **explore_1 (sonnet, 1800s):** Radical exploration via GNN predictor. Answers open question #6. Forbidden from using flat MLPs (any flavor), from refining current best, and from starting from any population/top file. Uses the free BFS data (shared with idea_010) to train a small graph neural network on a generator-induced adjacency. If the flat embedding MLP plateaus, we need a structurally different predictor class — this scouts that direction. Milestone 1 is compression-only sol01 for insurance.
- **research_1 (sonnet, 900s):** Track B research mission. Survey Kaggle top-3 for the cayley-py-megaminx competition and adjacent permutation-puzzle problems. Also survey algorithmic alternatives to beam search on Cayley graphs (IDA\*, phased solving, pattern databases). The gap between 44094 and 8050 is almost certainly a paradigm gap, not a tuning gap. This research informs gen005's strategy.

## Parallel groups

```
group 1: [exploit_1, experimentator_1, research_1]   # concurrency=3, fully utilised
group 2: [explore_1, explore_2]                       # 2 agents; light eval runs between
```

Reasoning: concurrency budget is 3 (GPU with MPS). Group 1 holds the heavy GPU work (exploit_1's full pipeline + experimentator_1's training run) alongside research_1 which does no GPU. Group 2 pulls the explores, which benefit from seeing group 1's output — the light evaluator will surface any helper deployment or model training results as ideas/patterns that explore_1 and explore_2 read before starting. In particular:

- If experimentator_1's helper validates, explore_2 calls it directly instead of re-training.
- If exploit_1 finds the best `(beam_width, max_steps)`, explore_2 uses that as the default for its per-bucket sweep.
- If exploit_1 hits an OOM at a specific beam size, explore_1 and explore_2 avoid it.
- If research_1 finds a Kaggle write-up, it becomes context for both explores via the group_notes.

## Timeouts

Gen003 timing showed that agents either finish in < 2000s or hang to the full timeout. Raising timeouts is not the answer — milestone protocol is. Chosen values:

| Agent | Timeout | Reasoning |
|---|---|---|
| exploit_1 | 2100s | Full pipeline has real computational cost (BFS ~1s, training ~2min, 101 beam searches at 5–60s each ~15min). 2100s leaves room for one tune-then-rescore iteration. Below gen003's 3600s to force milestone discipline. |
| experimentator_1 | 1500s | Helper + test on 3 puzzles is ~5min of actual compute. 1500s is 3× cushion for debugging API issues. |
| research_1 | 900s | Research was 1507s in gen003 — tight but feasible. Narrower scope (6–10 findings) should fit in 900s comfortably. |
| explore_1 | 1800s | GNN is untried — need debugging slack but must not spiral. Milestone 1 guarantees sol01 on disk regardless of GNN working. |
| explore_2 | 1800s | Per-bucket sweep is multi-iteration by nature. Milestones 1 and 2 both produce scored solutions before the complex hybrid. |

## What I deliberately did NOT do

- **No genetic agent.** We only have 3 distinct approaches on disk (compression, suffix-predictor, plain compression). Crossover between them is unlikely to find a new basin — better to invest in executing the verified plan (exploit_1) and exploring a structurally different predictor (explore_1). Reconsider in gen005 once we have GNN + full-recipe results.
- **No additional explore for compression variants.** Compression ceiling (44114) is empirically confirmed by 7 solutions. More compression exploration is waste.
- **No Hamming predictor revisit.** Debunked (idea_006).
- **No multiple redundant exploits.** One exploit running idea_013 at full fidelity is more valuable than two exploits splitting the recipe.

## Risks

1. **GPU memory contention with MPS.** Three simultaneous cayleypy processes may hit MPS VRAM limits. Each process allocates its own BFS + model. If exploit_1 uses beam_width=8192 (uses ~3 GB) while experimentator_1 is training (uses ~2 GB) while explore_1 is eventually building a GNN (uses ~1 GB), that is ~6 GB on a 16 GB card — fine in isolation but with cayleypy's own overhead could fragment. Mitigation: the group 2 explore agents start AFTER group 1, so peak concurrent GPU work is 3 processes in group 1, then 2 in group 2.
2. **Hasher seed mismatch.** If any agent creates multiple CayleyGraph instances and uses BFS from one with beam_search on another, MITM silently fails. Every brief calls this out explicitly (idea_012).
3. **Model naming mismatch between cayleypy and Kaggle.** cayleypy uses `M_U`, `M_U_inv`; Kaggle uses `U`, `-U`. `GENERATOR_NAMES` from `helpers.core` is the source of truth. Every brief mentions this.
4. **exploit_1's Milestone 1 failure mode.** If the embedding MLP trains fine but beam_search crashes on state dtype, sol01 can't be produced from the recipe. The brief explicitly permits (as a last resort) falling back to the compression-only solution so there is ALWAYS a scored sol01.
5. **Research depth vs. time.** 900s is tight for WebSearch + paper reading. If research_1 goes over, it gets one 300s wrap-up. Narrow scope (headline paradigm + 6–10 findings) makes this achievable.

## Success criteria for gen004

- **Minimum viable outcome:** every agent produces at least one scored solution. (Not achieved in gen003.)
- **Core outcome:** exploit_1 produces a scored combined-recipe solution — whether or not it beats 44114, the experiment is resolved either way.
- **Best outcome:** combined recipe scores ≤ 40000, proving the predictor paradigm is viable and worth extending in gen005. GNN result (explore_1) informs gen005 architecture choice. experimentator_1's helper is deployed. research_1 identifies a new paradigm for gen005–006 exploration.

The pipeline has spent 3 generations circling the combined recipe. Gen004 must resolve it.
