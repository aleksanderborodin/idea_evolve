## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` -> fitness = 102 (Singer q=101 truncation)
Published constructive lower bound: possibly 105 (Rokicki-Dogon, UNVERIFIED)
Upper bound: ~109 (Carter-Hunter-O'Bryant 2023, arXiv:2310.20032)
**The pipeline has never successfully retrieved the published best Sidon set for N=10000.**

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/history/coverage_matrix.md` (see "Unexplored Promising Combinations")
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_004.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_019.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_020.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/reports/gen004/research_1.md` (previous research attempt)

## Directive

**This is a Track B research mission. Find approaches the system has NEVER tried. Read
the coverage matrix and dead ends in the State of Affairs to know what has been tried.
Look for ideas from adjacent fields, recent papers, or mathematical theory that could apply.**

### Primary objectives (in order of priority)

1. **Find the published best Sidon set for N=10000.** This is the single most important
   unknown — four generations of research agents have failed to retrieve F(10000). Search for:
   - OEIS sequences related to Sidon sets / B2 sequences / Golomb rulers for specific N values
   - Papers by O'Bryant, Cilleruelo, Helm, or Ruzsa that tabulate optimal or near-optimal sizes
   - The "modular Sidon set" literature which tracks exact values
   - Computational results databases (beyond Rokicki-Dogon)
   If you find F(10000) or a tight bound, this immediately calibrates whether 102 is close
   to optimal or far below.

2. **Find construction methods the pipeline has never tried.** The coverage matrix shows
   these approaches are UNTESTED:
   - Bose-Chowla construction (correct integer version, not the broken group version)
   - Cilleruelo's constructions using irreducible polynomials over finite fields
   - Lindström's construction
   - Constructions from perfect difference sets
   - Random algebraic constructions (e.g., random polynomials over GF(q))

3. **Find practical algorithms from the combinatorial optimization literature.** Search for:
   - Papers on maximum independent set in difference graphs
   - Constraint programming approaches to Sidon sets / Golomb rulers
   - Metaheuristics that have been specifically applied to Golomb ruler construction
   - The "Distributed.net" OGR project — how did they search for optimal Golomb rulers?

4. **Investigate the gap between Singer and optimal.** For which N values is Singer known
   to be optimal? For which is it known to be suboptimal? Is there a pattern?

### Deliverables

Write your findings to `output/findings.md` with:
- Each finding as a separate section with source citation
- Concrete actionable recommendations (not vague suggestions)
- For each construction method found, include the explicit formula/algorithm
- Priority ranking of which approaches are most likely to exceed 102

If you find an explicit Sidon set construction that could score 103+, also implement it
as `output/sol01.py` and evaluate it:
```bash
cd /home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem
python3 evaluate.py /path/to/your/output/sol01.py
```

### What NOT to do
- Do NOT re-derive Singer constructions — they are exhausted at 102.
- Do NOT implement greedy algorithms — they ceiling at 69.
- Do NOT spend all your time on one source. If a paper is paywalled, move on.
- Write findings.md INCREMENTALLY — after each significant discovery, append to the file.
  Do not wait until the end to write everything. Previous research agents lost all findings
  due to session timeouts.
