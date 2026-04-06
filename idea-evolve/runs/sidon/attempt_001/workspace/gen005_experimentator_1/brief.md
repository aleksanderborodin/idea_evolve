## Current Population Status
Best solution: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/best.py` -> fitness = 102 (Singer q=101 truncation)
Second best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank02_102.py` -> fitness = 102
Non-Singer best: `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/population/top/rank04_69.py` -> fitness = 69
**Target: 109. Gap: 7 elements. Pipeline is 3+ behind published state of art (105).**

## Read first
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/state_of_affairs.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/ideas/active/idea_020.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/knowledge/clusters/cluster_001.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/reports/gen004/research_1.md`
- `/home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/feedback/experiment_suggestions/gen004.md` (see EXP-A)

## Directive

**MISSION: Download the Rokicki-Dogon Golomb ruler database and extract 104-mark and 105-mark
Sidon sets with span <= 10000.**

This is a pure data-engineering task. No mathematical insight needed. Four consecutive
generations have approached this data without completing the fetch. This is the single
highest-ROI action available to the pipeline.

### Steps

1. **Download** `cube20.org/golomb-all-00.zip` to your workspace using `curl` or `wget`.
   If that URL fails, try `cube20.org/golomb/` for an index page listing alternative downloads.

2. **Extract and parse** the zip file. The format is likely a text file with entries listing
   mark count, span, and the integer mark sequences. Look for entries where:
   - marks >= 104
   - span <= 10000

3. **For each qualifying entry**, extract the integer mark list (the actual Sidon set elements).
   A Golomb ruler with marks M and span S is a set of M integers in {0, ..., S} with all
   pairwise differences distinct — identical to a Sidon set.

4. **Write each qualifying set as a solution file** in the standard format:
   ```python
   def entrypoint():
       return [0, 3, 7, ...]  # the actual mark list
   ```
   Name them `output/sol01.py` (best mark count), `output/sol02.py` (next best), etc.

5. **Run `evaluate.py` on each solution** immediately after writing:
   ```bash
   cd /home/sasha/Desktop/project_alpha/idea-evolve/runs/sidon/attempt_001/problem
   python3 evaluate.py /path/to/your/output/sol01.py
   ```
   Verify `.score` file is created and shows fitness >= 104.

6. If the zip file doesn't contain mark lists directly, look for supplementary files or
   alternative formats. The database may store rulers in compressed or encoded form.

7. If NO qualifying entries exist (all 104+ mark rulers have span > 10000), **that is an
   important negative result**. Document it clearly in your report — it means the Rokicki-Dogon
   constructive lower bound does NOT apply to N=10000, and idea_020 should be debunked.

### Fallback

If the download fails entirely (server unreachable, file corrupted, etc.):
- Try alternative URLs from the Rokicki-Dogon Golomb ruler project page
- Search for "optimal Golomb ruler" databases with downloadable mark lists
- As a last resort, implement a Singer q=103 construction and apply systematic span-reduction
  search: remove 1-2 high elements and try to add replacement elements below 10000 while
  maintaining the Sidon property. This could yield 103.

### What NOT to do
- Do NOT spend time on mathematical theory or new constructions
- Do NOT try to optimize or improve the found rulers — just extract and evaluate them
- Do NOT skip the evaluate.py step — unverified solutions are worthless
