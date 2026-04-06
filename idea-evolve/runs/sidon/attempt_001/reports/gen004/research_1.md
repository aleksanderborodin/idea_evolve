# Research Agent Debrief — Gen 4, research_1

## 1. What Did I Try?

**Primary mission**: Find published F(10000) and algebraic constructions beyond Singer q=101.

**Literature search** (via web agents):
- Fetched arXiv:2310.20032 (Carter-Hunter-O'Bryant 2023): upper bound = 109 for N=10000.
- Fetched Rokicki-Dogon "Possibly Optimal Golomb Rulers" database (cube20.org/golomb).
- Searched OEIS A143824 (b-file only covers n=0..500, useless for N=10000).
- Researched Bose-Chowla, Ruzsa, Cilleruelo, Paley constructions.

**Solution attempt** (sol01.py):
- Implemented Singer q=103 with optimal cyclic shift search.
- Result: fitness=102. Singer q=103 has minimum span 10290 > 10000, so only 102 elements fit (same as current best).

## 2. What Information Did I Lack?

**The actual mark lists from the Rokicki-Dogon database.** I found that 104-mark and 105-mark rulers with spans ≤ 10000 exist, but I only got the parameters (q, span, type, offset) — not the actual integer sequences. To directly use these constructions, agents need either:
- The actual mark lists (downloadable from cube20.org/golomb-all-00.zip)
- Or a reimplementation of the search process

Without the actual mark lists, the Rokicki-Dogon finding cannot be directly implemented.

## 3. What Given Facts Might Be Wrong or Outdated?

- **problem/description.md says "theoretical maximum is approximately 100 elements"** — this is WRONG. The upper bound is 109, and constructive lower bound is 105 (Rokicki-Dogon). The 100 figure was the old sqrt(N) approximation.
- **CLAUDE.md target: >= 108** — achievable with Rokicki-Dogon 105-mark construction + possible extension, but the "108" target is not supported by any known construction. 106+ would require genuine new search beyond known algebraic constructions.

## 4. Was the State of Affairs Accurate?

Mostly accurate. It correctly identified:
- Singer q=101 ceiling at 102
- Literature search as the top priority
- Gap to theoretical upper bound as 7 elements

**What it missed**: The state_of_affairs says "the theoretical upper bound is ~109" but doesn't note that the CONSTRUCTIVE lower bound is 105 (not 102). This is a major gap — there are published constructions that achieve 105 elements in N=10000 that the system has never tried.

## 5. What Would I Do Differently?

With more time:
1. **Download the Rokicki-Dogon zip file** from cube20.org/golomb-all-00.zip and parse it to get the actual 104-mark and 105-mark ruler sequences. This is a web download task.
2. **Implement a search** that modifies Singer q=103 (104 elements, span 10290) to reduce span below 10000: try removing 1-3 high elements and replacing them with elements below 10000, while maintaining the Sidon property.

## 6. Specific Experiments to Run

| Priority | Experiment | Expected Gain |
|----------|------------|---------------|
| **CRITICAL** | Download cube20.org/golomb-all-00.zip, parse 104-mark and 105-mark entries, extract actual integer sequences | Direct 104–105 score |
| **HIGH** | Singer q=103: try removing the 2-3 elements > 10000 after optimal shift, then greedily extend | Possible 103–104 |
| **HIGH** | Singer q=107 (108 marks): find rotation maximizing elements within {0,...,10000}, count what fits | Estimate potential |
| **MEDIUM** | Bose-Chowla for q=107: implement and search for 105-element subset fitting in N=10000 | 105 if correct impl |
| **LOW** | Download Golomb ruler databases from other sources (e.g., Distributed.net OGR project) | Cross-validation |

## 7. What Surprised Me?

- **Singer q=103 span is 10290, not 9581**: My assumption that the Rokicki-Dogon "type=pp, q=103" entry directly represents the Singer construction was wrong. Near-optimal Golomb ruler research uses Singer as a SEED and then applies further search. The raw Singer set doesn't achieve the near-optimal span.
- **The constructive gap to theory is only 4 elements**: F(10000) ≥ 105 (Rokicki-Dogon) and ≤ 109 (theory). The actual optimum is likely 105–109, much tighter than the run currently knows about.
- **The system's current best (102) is 3 elements behind the best published construction (105)**: This is very actionable. Downloading the Rokicki-Dogon mark list is probably the single highest-value action available.

## 8. Helper Tools Feedback

- `helpers/singer.py`: Correct and worked well. Used `find_singer_set(103)` successfully.
- **Missing helper**: A `helpers/rokicki_dogon.py` that downloads/parses/caches the Rokicki-Dogon database and returns actual mark lists for any (marks, q) pair would be extremely valuable. This could unlock 103–105 immediately.
- **Missing helper**: A `helpers/golomb_search.py` that implements the near-optimal Golomb ruler search (span minimization via metaheuristic) would let agents go beyond algebraic constructions.

## 9. Time Budget

Insufficient. The research phase was productive (found the Rokicki-Dogon database showing 105 is achievable) but I ran out of time before implementing a working 103+ solution. The Singer q=103 attempt failed (span too large). The correct next step — downloading and parsing the Rokicki-Dogon zip file — was not completed.

**If I had 20 more minutes**: I would download cube20.org/golomb-all-00.zip, parse the 104-mark and 105-mark entries, extract the integer sequences, and submit them directly as solutions. Expected result: fitness=104 or 105.

---

## Solution Table

| File | Fitness | is_valid | Strategy |
|------|---------|----------|----------|
| sol01.py | 102 | 1 | Singer q=103 with optimal cyclic shift — span 10290 > 10000, truncated to 102 elements |
