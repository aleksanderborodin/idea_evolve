# Debrief — explore_1, gen 004

## What I tried

**Nothing.** Zero solutions were written or evaluated. The session was consumed entirely by reading context files (state_of_affairs, ideas, patterns, helpers, existing solutions, cayleypy API exploration) and never reached the point of writing code.

## Files in output directory

None. Empty directory. No `.py`, `.score`, or `observations.md` files.

## What happened

1. Read state_of_affairs.md, idea_010, idea_011, helpers/core.py, helpers/trained_predictor_beam_search.py, description.md, group0 notes, existing compression solutions, cayleypy API.
2. Explored cayleypy CayleyGraph API to understand BFS, generators_permutations, beam_search parameters.
3. Confirmed torch_geometric is NOT available — would need hand-rolled message passing.
4. Confirmed cayleypy generators_permutations returns list-of-lists (24 perms × 120 entries each).
5. Ran out of turns before writing any solution code.

## Was the State of Affairs accurate?

Yes. The SoA accurately describes the 44114 compression floor, the 44094 marginal predictor result, and the open questions. The group0 notes added critical new information: CayleyPy's built-in MlpModel uses one-hot encoding (idea_014), non-backtracking beam search quadruples success (idea_015), beam width is the dominant parameter (pattern_009), and shallow training data is the real bottleneck (pattern_008).

## What information did I lack?

- I did not know the cayleypy Predictor API contract in detail — specifically how to wrap a custom nn.Module so it works with beam_search. The helpers/trained_predictor_beam_search.py shows `cayleypy.Predictor(graph, model)` but I hadn't confirmed the forward() signature contract (does the model receive encoded or decoded states? batch dimensions?).
- I didn't have a working compression-only solution to import directly (symlinks in population/top/ are broken).

## Helper tools feedback

- `helpers/core.py` — well-documented, useful. `cayleypy_beam_solver` is handy but only supports unguided or hamming predictor. No helper for BFS training data extraction (idea_010 describes the code but it's not in helpers/).
- `helpers/trained_predictor_beam_search.py` — uses raw-integer MLP (pattern_006 confirmed ineffective). Group0 notes say CayleyPy has its own MlpModel with one-hot encoding — this helper should be updated or replaced.

## What would I do with more time

1. **Immediately write sol01.py** — compression baseline (copy the gen002 approach: discover rewrite rules from sample_submission, apply them). Guaranteed 44114.
2. **Write sol02.py** — GNN predictor:
   - Build generator-induced adjacency from `gdef.generators_permutations` (24 generators, union of directed edges, ~240 undirected edges).
   - Hand-rolled message passing (scatter_add, no torch_geometric needed).
   - Train on BFS depth-6 data (idea_010 code, ~1s to compute).
   - Wrap as `cayleypy.Predictor(graph, gnn_model)`.
   - Run beam search with compression fallback.
3. If GNN shows promise, increase beam_width (pattern_009 says quality scales with log(beam_width)).

## Specific experiments to run

1. **GNN architecture sweep**: 2 vs 3 vs 4 message-passing layers, embed_dim 16/32/64. Measure training loss convergence on BFS depth-6 data.
2. **GNN vs flat embedding MLP head-to-head**: Same training data (BFS depth-6), same beam settings (width=8192, max_steps=200). Compare per-bucket fitness.
3. **Edge construction variants**: (a) generator-induced adjacency only, (b) add inverse-generator edges explicitly, (c) add self-loops.

## Time budget

Grossly insufficient. Context reading consumed the entire session. The milestone protocol (sol01 in first 30 min) was not followed. In future, I should write the compression fallback FIRST before any reading beyond the brief.

## What surprised me

- The group0 notes from earlier this generation revealed that `beam_mode='advanced'` is NOT broken when used WITH a predictor — the SoA listed it as a dead end, but research_1's source code analysis showed it quadruples success rate. My brief said "off-limits" based on outdated information.
- experimentator has now failed 3 consecutive generations on building the embedding predictor helper. This is a systemic problem.
