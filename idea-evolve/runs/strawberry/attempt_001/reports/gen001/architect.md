# Architect Report — Generation 1

## Confidence: High
This is a well-structured cold start. The prior experiments (exp1-exp8) provide a solid evidence base to bootstrap from. The problem definition contains specific, actionable findings. The main risk (explore_2's longer runtime) is acceptable given the high information value of testing a larger model.

## Data Anomalies
None — this is a fresh start with no prior population data.

## What Didn't Fit
- **Two-track mandate**: With no solutions yet, both tracks collapsed into cold-start defaults. Track A (exploitation) is essentially "establish a baseline" and Track B (radical exploration) is "test a larger model" — both are exploratory in this context.
- **Class imbalance**: The 15x imbalance is the core challenge, but only one agent (explore_1) addresses it directly. The others assume copy-paste=0.5 handles it adequately.
- **Research focus**: Without a populated knowledge base, research is doing foundational survey work rather than filling specific gaps.

## Strategic Risks
1. **explore_2's 50-epoch from-scratch run** takes ~9 min vs 3.6 min for fine-tune. If it crashes or underperforms, we've spent 2.5x the compute for potentially worse results. The nano model might already be at ceiling, but we don't know that yet.
2. **No diversity anchor**: Without an exploit agent, we don't defend the best known approach (exp5). If explore_2 fails badly, the population has no safe fallback.
3. **Research findings may be slow**: Literature survey without a populated knowledge base means research_1 is doing general domain survey, not gap-filling. Results may not be actionable for gen 2.

## Open Questions for the System Critic
1. Is the proxy metric (20 fine-tune epochs from exp5) a reliable predictor of 100-epoch performance? exp5 converged slowly — will 20 epochs be enough to differentiate approaches?
2. The description mentions "proxy mAP50 ≈ 0.94 (current exp5 proxy baseline ~0.92-0.94)" but exp5 itself achieved 0.945 at 100 epochs. What's the expected mAP50 at 20 epochs from the converged model?
3. Should we be running more epochs for the baseline comparison? The description suggests PROXY_EPOCHS_EXTENDED=40 for "promising configs" — should full_1 use that instead of 20?
