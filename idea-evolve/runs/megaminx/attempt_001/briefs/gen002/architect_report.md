# Architect Report — Generation 2

## Data anomalies

- The architect context again referenced run-local problem files under `runs/megaminx/attempt_001/problem/`, but those files do not exist. The real problem specification is still under `problems/megaminx/`.
- `problems/megaminx/description.md` says CPU-only under hardware, while earlier project-level documentation in `CLAUDE.md` describes GPU availability for Megaminx. For this generation I followed the explicit architect context and `metrics.yaml` contract: `concurrency: parallel`.
- `problems/megaminx/helpers/README.md` still says `PROXY_SIZE = 100` and first-100 semantics, while the problem description and live evaluation logic use the 101-row stratified proxy. Agents could still be misled if they read both.
- Population summary names `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/best.py` conceptually, but the concrete stable best path in `all_scores.json` is `/home/sasha/Desktop/idea_evolve/idea-evolve/runs/megaminx/attempt_001/population/gen001/full_1/sol01.py`. I anchored briefs on concrete files to avoid ambiguity.

## Confidence

Medium.

The strategic center is clear: stop spending effort on unguided beam search and finally test predictors. Confidence is not high because the available docs still contain inconsistencies, and because no agent has yet demonstrated that predictor-guided search is fast enough or strong enough on this proxy.

## What didn't fit

- I did not allocate a second exploit or a genetic agent because there is still too little genuine solution diversity.
- I did not allocate a dedicated MITM-coverage experiment even though it remains a useful secondary question.
- I did not allocate an experimentator specifically to fix the doc inconsistencies; they are real but lower-value than answering the predictor question.

## Strategic risks

- If both predictor-focused agents burn time on interface plumbing instead of measurement, generation 2 may still fail to answer the most important yes/no question.
- The two Track B explores are intentionally radical and may return little score movement. That is acceptable strategically, but it raises the chance of a generation with weak immediate fitness gains.
- If research again cannot access useful Kaggle artifacts, the radical-exploration pipeline could remain underinformed.

## Open questions for the System Critic

- Should the architect prompt stop referencing non-existent `runs/.../problem/*` files entirely and always point to `problems/<id>/...` unless a run-local copy actually exists?
- Is `cayleypy_beam_solver` helper friction best solved by changing shared helpers centrally, or should future briefs keep instructing agents to bypass the helper and use direct cayleypy APIs?
- Which single document should agents trust for Megaminx proxy semantics when `description.md` and `helpers/README.md` disagree?
