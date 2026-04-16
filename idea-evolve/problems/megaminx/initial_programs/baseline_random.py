"""Random-walk baseline.

Walks each test puzzle by picking random Kaggle moves until either solved or
the move budget is exhausted. Most scrambled states won't get solved within
500 moves, so this baseline mostly demonstrates the per-row sentinel path —
its purpose is to exercise evaluate.py end-to-end and give agents a concrete
"this is the bad floor" anchor.

Expected fitness on PROXY_SIZE=100: ≈ 100,000,000 (100 puzzles × 1e6 per-row
sentinel). Most rows hit the 500-move cap without solving. is_valid will be 0.
"""

from __future__ import annotations

import random


def entrypoint() -> dict:
    from helpers.core import (
        load_test, apply_move, is_solved, GENERATOR_NAMES,
    )
    rng = random.Random(0)
    tests = load_test(proxy=True)
    out: dict = {}
    for sid, init_state in tests.items():
        state = init_state
        moves: list = []
        for _ in range(500):
            if is_solved(state):
                break
            m = rng.choice(GENERATOR_NAMES)
            moves.append(m)
            state = apply_move(state, m)
        out[sid] = ".".join(moves) if is_solved(state) else ""
    return out
