## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` -> fitness = 102 (Singer q=101 truncation)
Non-Singer best: fitness = 69 (min-blocking greedy / Fibonacci ordering)
ET(71) + local search best: fitness = 75
**All greedy variants ceiling at 66-69 (pattern_011). Beam search is untested.**

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_002.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_016.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_005.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen004.md` (see EXP-B)
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem/helpers/core.py`

## Directive

**Implement beam search greedy for Sidon sets.** This is the highest-priority untested
non-algebraic approach. Multiple agents across gens 3-4 independently estimate it could
reach 75-85 elements. No one has implemented it.

### Core algorithm

```python
def beam_search_sidon(N, k_beams):
    # Each beam is (sorted_elements, used_differences_set)
    beams = [([0], set())]

    for step in range(1, N+1):
        next_beams = []
        for elems, diffs in beams:
            # Try adding each valid candidate
            for c in range(elems[-1] + 1, N + 1):
                new_diffs = {c - e for e in elems}
                if not new_diffs & diffs:
                    # Valid extension — compute heuristic score
                    blocking = count_blocked(c, elems, diffs, N)
                    next_beams.append((blocking, elems + [c], diffs | new_diffs))
        if not next_beams:
            break
        # Keep k_beams best (lowest blocking score)
        next_beams.sort()
        beams = [(e, d) for _, e, d in next_beams[:k_beams]]

    return max(beams, key=lambda b: len(b[0]))[0]
```

### What to implement

1. **Start with k_beams=10** to verify correctness and get a baseline score. Compare to
   greedy (k=1) which should give 66.

2. **Scale up**: k_beams = 20, 50, 100, 200. Record score and runtime for each. If runtime
   is too long for large k, implement pruning (e.g., only expand candidates near the
   current frontier, not the full range).

3. **Optimize for speed**: The inner loop is O(k_beams * N * |S|) per step. Use numpy
   or sets for fast difference checking. Consider only candidates in a window around the
   last element to reduce branching.

4. **Try different heuristics** for beam scoring:
   - Min-blocking: how many future candidates does adding c invalidate?
   - Max-gap: prefer candidates that leave large gaps in the difference set
   - Balanced: combination of blocking and spread

5. **Try different starting points**: Start from [0], but also try [0, 1], [0, 2], etc.
   The first element choice can significantly affect the beam search trajectory.

6. Write EACH best solution to `output/sol*.py` and evaluate immediately with:
   ```bash
   cd /home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem
   python3 evaluate.py /path/to/your/output/solNN.py
   ```

### Performance expectations
- k=1 (greedy): 66 elements (baseline)
- k=10: 70-75 elements (expected)
- k=50: 75-80 elements (expected)
- k=100+: 80-85 elements (optimistic)

If beam search also plateaus at 69-72, that confirms the greedy ceiling is structural
and not just a one-beam artifact. This is an important finding either way.

### What NOT to do
- Do NOT start from Singer or any existing top solution. Build from scratch.
- Do NOT try SA, LNS, or random restarts — those are debunked directions.
- Do NOT spend more than 5 minutes on any single beam width if it's clearly not improving.
