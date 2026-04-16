# Experiment Notes

- Goal: isolate whether `Predictor(graph, 'hamming')` improves on the established 46312 compressed-sample floor on the full 101-puzzle stratified proxy.
- Control: compressed `sample_submission` paths only.
- Treatment: direct `graph.beam_search(..., predictor=Predictor(graph, 'hamming'))` with the same fallback policy as the best gen001 solver.
- Constant factors held fixed: same proxy set, same fallback source, same scorer, same beam parameters for every puzzle.
- Expected failure mode: the hamming heuristic may be too weak on hard and very_hard rows, producing no usable path or paths no shorter than fallback.
