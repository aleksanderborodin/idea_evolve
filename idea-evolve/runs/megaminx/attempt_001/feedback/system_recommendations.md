# System Recommendations — Generation 4

Ranked by expected impact on the pipeline's ability to improve beyond the 44114 compression ceiling.

---

## REC-1: Pre-inject a compression-only sol01.py into agent workspaces before launch (CRITICAL)

**What to change:** Before each agent session starts, write a pre-built `sol01.py` (compression-only, guaranteed 44114) into the agent's `output/` directory. The agent's brief should say: "sol01.py has been pre-placed in your output directory. Run `python3 evaluate.py output/sol01.py` to score it. Then improve from there."

**Why:** The milestone protocol (write sol01 first) has failed 2 consecutive generations because LLM agents read context instead of writing code. Pre-injecting sol01 eliminates the "write first" step entirely — the agent starts from a scored baseline and only needs to improve it. This converts the agent's default behavior (read → understand → act) from a liability to an asset.

**Expected impact:** Agent success rate should improve from ~40% to 80%+. Even a completely stuck agent will have a scored solution (44114) in its output directory.

**How to implement:** Add a `_inject_compression_baseline()` step in `run_single_agent()` that copies the best compression solution from `population/top/` (or a hardcoded compression solution) into `workspace/genNNN_agentname/output/sol01.py` before the agent session starts. The agent brief notes its existence.

---

## REC-2: Stop assigning the experimentator to the predictor helper task (CRITICAL)

**What to change:** Do not assign any helper-writing task to the experimentator role for gen005. Instead, assign an exploit or full agent to write the corrected predictor code INLINE in a solution file. The solution itself becomes the reference implementation.

**Why:** The experimentator has failed 3 consecutive generations on the same task. The role template apparently encourages over-scoping. Continuing to assign this task to the experimentator is the definition of insanity.

**Expected impact:** The corrected predictor code actually gets written and tested. Even if the solution scores badly, the code exists for future agents to reference.

**How to implement:** Architect brief for gen005 exploit/full agent: "Write sol01 using `from cayleypy.models import MlpModel` (NOT a custom model). Train on path-intermediate data. Beam_width ≥8192. Include all training + beam search code inline in the solution file."

---

## REC-3: Mandate beam_width ≥ 8192 in all beam search solutions (CRITICAL)

**What to change:** Agent briefs for gen005 must explicitly state: "beam_width=4096 has been tested and is insufficient. Use beam_width ≥ 8192, targeting 65536 with batch_size=2048 to manage GPU memory. This is not optional."

**Why:** Every solution for 4 generations has used beam_width ≤4096. The CayleyPy paper is explicit that quality scales log-linearly with beam width. Our beam_width is 16× below competitive levels. No architectural improvement will matter if the beam width is too small.

**Expected impact:** The single cheapest potential improvement — no new model, no new training pipeline, just one parameter change. Could produce the largest single-generation score improvement of the run.

**How to implement:** Add to the architect's prompt context: "CRITICAL: beam_width=4096 is 16× below competitive levels. All beam search solutions MUST use beam_width ≥ 8192. Use batch_size=2048 for memory management."

---

## REC-4: Execute the updated recipe (idea_016 + idea_014 + large beam) as gen005's primary task (CRITICAL)

**What to change:** Gen005 must assign at least one agent to:
1. Extract path-intermediate training data from compressed paths (idea_016)
2. Train `MlpModel` (one-hot, idea_014) on this data
3. Run beam search with beam_width ≥ 65536 (pattern_009) and batch_size=2048
4. Test both `beam_mode='simple'` + MITM and `beam_mode='advanced'` (non-backtracking, idea_015)
5. Fall back to compression for failed puzzles

**Why:** This combines the three highest-priority untested ideas into one experiment. The path-intermediate training data addresses the depth bottleneck (PA-3, KQ-1). MlpModel is the library's proven architecture (EG-2). Large beam width is the dominant parameter (EG-1). Non-backtracking is a free algorithmic boost (EG-3).

**Expected impact:** If path-intermediate data + large beam width works, expect meaningful improvement (possibly 30000-40000 range). If it doesn't work, we know the beam search paradigm is fundamentally limited for Megaminx and must pivot.

---

## REC-5: Correct idea_010 and archive outdated ideas before gen005 (HIGH)

**What to change:**
1. Update idea_010 summary to say "BFS data is useful for MITM backstop only. Useless as sole training source for deep predictor (depth >6)."
2. Move idea_004 (manual MITM) from `active/` to `archived/` with note "Superseded by idea_012 (built-in MITM)."
3. Update idea_013 with actual test result: "Tested gen004: 44111. Conservative estimate confirmed; optimistic estimate was wrong. Training data depth is the binding constraint."
4. Update idea_011 note: "Valid approach but CayleyPy's built-in MlpModel (idea_014) is preferred."

**Why:** Outdated and contradicted knowledge in the active idea directory wastes agent turns and misleads planning. idea_010's incorrect claim influenced 2 generations of strategy.

**Expected impact:** Future agents read accurate knowledge. Prevents re-exploration of debunked approaches.

---

## REC-6: Create a Cayleypy API reference document (HIGH)

**What to change:** Create `problems/megaminx/docs/cayleypy_api.md` documenting:
1. `MlpModel(graph, hidden_dims=[...])` — the correct model class
2. `Predictor(graph, model)` — wrapping any nn.Module
3. `graph.beam_search(...)` — parameters including predictor, bfs_result_for_mitm, beam_mode, beam_width, batch_size
4. `graph.bfs(max_layer_size_to_store=...)` — footgun: default 1000 discards data
5. `graph.random_walks(width, length, mode)` — modes: 'bfs' vs default
6. Known incompatibilities: advanced mode requires predictor; MITM and advanced are mutually exclusive; BFS and beam search must use same graph instance

**Why:** research_1 spent its entire session on API discovery. Multiple agents have made API mistakes (wrong parameters, missing footguns). Every future agent will need this information.

**Expected impact:** Saves 5-10 turns per agent session. Eliminates API-related bugs in solutions.

---

## REC-7: Update State of Affairs to reflect gen004 findings before gen005 architect session (HIGH)

**What to change:** The SoA (currently "Gen 003") must be rewritten to capture:
1. Training data depth is THE binding constraint, not architecture
2. idea_013 combined recipe tested → 44111 (marginal, worse than gen003 best)
3. CayleyPy's MlpModel uses one-hot (idea_014) — use the library model
4. Beam width is the dominant parameter (pattern_009) — competitive = 65536+
5. Non-backtracking quadruples success rate (idea_015)
6. Path-intermediate training (idea_016) is the #1 priority experiment
7. idea_010 (BFS data superiority) was wrong for predictor training
8. Experimentator role is 0/3 on helper tasks — route to exploit/full instead

**Why:** The gen005 architect reads the SoA as its primary strategic input. The current SoA is 1 generation behind and contains incorrect claims (BFS superiority, architecture as primary concern).

---

## REC-8: Reduce default work session timeout to 1200s (MODERATE)

**What to change:** Default work session timeout should be 1200s (20 min) instead of 2100-2700s. Wrap-up stays at 300s. Debrief at 300s. Total max: 1800s (30 min).

**Why:** Gen004 showed improvement with shorter timeouts (explore_1 ran 221s vs gen003's 2700s — same zero output, 12× less wasted time). Agents that produce nothing in 20 minutes won't produce anything in 45 minutes. The architect can still override per-agent for tasks known to need more time (e.g., exploit_1's 400s eval).

**Expected impact:** Faster failure detection, more generations per wall-clock hour, less wasted compute.

---

## Previously Filed Recommendations — Status Update

| REC | Filed | Status | Notes |
|-----|-------|--------|-------|
| REC-1 (milestone protocol) | Gen003 | FAILED | Agents ignored LLM-level instructions; need system enforcement (new REC-1: pre-inject baseline) |
| REC-2 (execute idea_013) | Gen003 | DONE | Tested gen004: 44111, marginal. Recipe insufficient at beam_width=4096 |
| REC-3 (fix helper) | Gen003 | NOT DONE | Experimentator failed 3rd consecutive time. Rerouting per new REC-2 |
| REC-4 (reduce timeouts) | Gen003 | PARTIALLY DONE | Architect reduced some per-agent timeouts; system default unchanged |
| REC-5 (update SoA) | Gen003 | PARTIALLY DONE | SoA updated to gen003 but now behind again |
| REC-6 (Cayleypy API docs) | Gen003 | NOT DONE | Still missing; re-emphasized in new REC-6 |
| REC-7 (compression + beam) | Gen003 | DONE | Tested in gen004 (exploit_1); marginal result |
| REC-8 (archive idea_004) | Gen003 | NOT DONE | Still in active/ |

---

## Priority for Gen005

1. **REC-1:** Pre-inject compression baseline into agent workspaces (stops agent failures)
2. **REC-3:** Mandate beam_width ≥ 8192 (cheapest potential improvement)
3. **REC-4:** Execute updated recipe (idea_016 + idea_014 + large beam) as primary task
4. **REC-2:** Route predictor work to exploit/full agents, not experimentator
5. **REC-5:** Correct outdated knowledge before gen005 architect session
6. **REC-7:** Update SoA before gen005 architect session
7. **REC-6:** Create Cayleypy API reference (saves future agent turns)
8. **REC-8:** Reduce default timeouts (efficiency)

**The pipeline has spent 4 generations and ~14 hours of compute to move from 44114 to 44094 (net 20 moves, 0.05%).** The two biggest levers — beam width and training data depth — remain completely untested. Gen005 must test both or acknowledge the beam search paradigm cannot reach the 15000 target.
