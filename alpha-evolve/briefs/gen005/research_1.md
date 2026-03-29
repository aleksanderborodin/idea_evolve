## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` → C = 1.5029 (TTT-Discover 30k array)
Second best: `/home/sasha/Desktop/project_alpha/alpha-evolve/population/top/rank02_1.5032.py` (AlphaEvolve 1319 array)
Best gradient-descent result: C = 1.5090

## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/clusters/cluster_003.md` — published solutions cluster
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/established/idea_014.md` — warm-start from published solutions
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/ideas/active/idea_018.md` — TTT-Discover method
- `/home/sasha/Desktop/project_alpha/alpha-evolve/reports/gen004/research_1.md` — gen 4 research report (READ THIS — it mapped the arrays but didn't extract them)
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/research/gen004/research_1/observations.md` — detailed notebook analysis
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`

## Directive

**Extract intermediate published arrays from the AlphaEvolve notebook and verify them as solution files.** gen 4 research_1 mapped these arrays but ran out of time before extracting them. You are completing that work.

**Target arrays (in priority order):**

1. **Cell 47 (N=600, C≈1.5053)** — HIGHEST PRIORITY. This is at our gradient pipeline's native resolution. No interpolation needed. Enables direct warm-start experiments for gradient agents.

2. **Cell 50 (N=600, C≈1.5040)** — Second N=600 array. Different LP iteration → potentially different basin.

3. **Cells 52, 54, 56, 58 (N=984 to N=5000, C=1.5036 to 1.5033)** — Higher resolution intermediates. Extract at least 2 of these if time permits.

4. **AlphaEvolve V2 array** — Check if it differs from the 1319-element array in `/home/sasha/Desktop/project_alpha/alpha-evolve/population/best.py` (rank02). The TTT-Discover SOTA table lists AlphaEvolve V2 at C=1.50317 vs ThetaEvolve at C=1.50313. If they're different arrays, extract both. If same, document conclusively.

**For each extracted array:**
1. Wrap in `def entrypoint(): return np.array([...])` format
2. Add header comment: `# fitness: X.XXXX` and source info
3. Save as `output/sol01.py`, `output/sol02.py`, etc.
4. Run `python3 evaluate.py output/solNN.py` to verify the score
5. Save the `.score` file alongside

**Source:** The AlphaEvolve notebook is at the URL gen 4 research_1 used. Check `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/research/gen004/research_1/observations.md` for the exact URL and cell numbers. The notebook is a Colab notebook with arrays stored as Python lists in cells.

**What NOT to do:**
- Do NOT re-retrieve the TTT-Discover array (already have it as population/best.py)
- Do NOT re-retrieve the AlphaEvolve 1319-element array (already have it as rank02)
- Do NOT spend time on the Cell 92 array (that's for the SECOND autocorrelation inequality, not ours)
- Do NOT attempt optimization — just extract, verify, and save

**Success criterion:** At least 2 verified solution files from intermediate arrays, especially Cell 47 (N=600).
