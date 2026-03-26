## Read first
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_001.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_002.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/knowledge/facts/fact_003.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/description.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/constraints.md`
- `/home/sasha/Desktop/project_alpha/alpha-evolve/problem/helper.py`

## Directive
**Research the mathematical theory behind the first autocorrelation inequality.**

Survey the problem domain and produce structured findings. Focus on:

1. **Known results:** What is the current state of the art for this inequality? The known bounds are 1.28 <= C <= 1.5098. Where do these bounds come from? What constructions achieve the upper bound? What proofs establish the lower bound?

2. **Optimal function properties:** What is known about the shape of the extremal function (the f that minimizes C)? Is it symmetric? Smooth? Compactly supported within [-1/4, 1/4] or does it use the full domain? Does it have a known closed form?

3. **Connection to additive combinatorics:** The problem relates to Sidon sets and sumset problems. What techniques from additive combinatorics might inform function construction? Are there discrete analogues that have been solved?

4. **Relevant papers and authors:** Who has worked on this? Key names, papers, and results. Especially any constructions that come close to the conjectured optimal C.

5. **Optimization landscape:** Is the objective convex? Are there known local minima? Any theoretical results about the optimization landscape that could guide numerical approaches?

6. **Fourier-analytic perspective:** Since autoconvolution relates to squaring the Fourier transform, are there Fourier-space characterizations of the optimal function?

Write your findings to `output/findings.md` in structured format with sections for each topic above. Be specific — cite results, state theorems, give parameter values. Vague summaries are not useful.
