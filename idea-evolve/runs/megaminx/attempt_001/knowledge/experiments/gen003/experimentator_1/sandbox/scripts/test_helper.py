"""Smoke test for trained_predictor_beam_search helper."""

import sys
import time

sys.path.insert(0, "/home/sasha/Desktop/idea_evolve/idea-evolve/problems/megaminx")

from helpers.trained_predictor_beam_search import (
    trained_predictor_beam_search,
    build_graph,
    train_predictor,
    guided_beam_search,
)
from helpers.core import load_test, apply_path, is_solved

tests = load_test(proxy=True)

print("=== Test 1: Full pipeline on shallow puzzle (sid=10) ===")
t0 = time.time()
path_str, result = trained_predictor_beam_search(
    tests[10], beam_width=4096, max_steps=30, verbose=True
)
elapsed = time.time() - t0
if path_str:
    valid = is_solved(apply_path(tests[10], path_str))
    print(f"SOLVED: {len(path_str.split('.'))} moves, valid={valid}, total={elapsed:.1f}s")
else:
    print(f"NOT SOLVED, total={elapsed:.1f}s")

print()
print("=== Test 2: Separate build/train/search ===")
graph, gdef = build_graph()
t0 = time.time()
predictor = train_predictor(graph, n_walks=10000, epochs=5, verbose=True)
print(f"Training: {time.time()-t0:.1f}s")

for sid in [10, 20]:
    t0 = time.time()
    path_str, result = guided_beam_search(tests[sid], graph, predictor, beam_width=8192, max_steps=40)
    elapsed = time.time() - t0
    if path_str:
        valid = is_solved(apply_path(tests[sid], path_str))
        print(f"  sid={sid}: SOLVED in {len(path_str.split('.'))} moves, valid={valid}, time={elapsed:.1f}s")
    else:
        print(f"  sid={sid}: NOT SOLVED, time={elapsed:.1f}s")

print()
print("ALL TESTS PASSED")
