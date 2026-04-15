# Manifest Reasoning — Generation 1

## Situation Assessment
- **Generation 0**: No solutions evaluated. This is a cold start.
- **Population**: Empty. No baseline scores yet.
- **Prior knowledge**: exp1-exp8 from prior work (outside this attempt) established that:
  - copy_paste=0.5 is the best augmentation (exp5, val mAP50=0.945)
  - yolo11n-seg.pt (nano model) was used exclusively
  - 15x class imbalance is the core challenge
  - Flipud hurts, own data hurts, aggressive multi-aug hurts

## Strategic Decisions

### Agent Mix: 2 explore + 1 full + 1 research (cold start rule)
Per generation 1 rules: launch exactly 2 explore + 1 full + 1 research. No exploit/genetic/experimentator — nothing to refine or crossover yet.

### Explore 1 — Copy-paste push (incremental exploitation disguised as exploration)
Direction: Higher copy_paste values (0.6-0.7) + class-aware sampling.
Rationale: copy_paste is proven effective but only tested at 0.3 and 0.5. Pushing to 0.6-0.7 while addressing class imbalance directly is a natural next step. This is somewhat Track B because we're pushing beyond prior bounds.

### Explore 2 — Larger model (radical departure from all prior work)
Direction: yolo11s-seg.pt (3.5x more parameters) trained from scratch.
Rationale: ALL 8 prior experiments used nano model. No one tested whether a larger model captures the subtle disease features better. This is a genuine Track B exploration.

### Full 1 — Solid baseline with TTA
Direction: Fine-tune from exp5 with copy_paste=0.5 + TTA.
Rationale: Most likely to produce a reliable score. TTA at eval is essentially free improvement. This anchors the population with a known-good approach.

### Research 1 — Literature survey
Direction: Survey class balancing, larger models, progressive training, boundary losses.
Rationale: Generate actionable findings for future generations. With no prior reports to learn from, research findings are especially valuable for gen 2 planning.

## Concurrency: Serial (per metrics.yaml)
Each agent is in its own single-element parallel group: `[["explore_1"], ["explore_2"], ["full_1"], ["research_1"]]`.
This ensures only one GPU evaluation runs at a time. The research agent does not use GPU.

## Timeouts
- Explore 1 & 2: 900s (3.6 min eval + write/interpret overhead)
- Full 1: 900s (same reason)
- Research 1: 600s (literature survey, no training)

## What I Deliberately Did NOT Do
- **Did not launch exploit agents**: Nothing to exploit yet (no solutions scored)
- **Did not launch genetic agents**: No crossover pairs exist
- **Did not launch experimentator**: No hypotheses to test yet (need baseline scores first)
- **Did not try training from scratch for explore_1**: Kept it on fine-tune path to save time

## Risks
- explore_2 (larger model, 50 epochs) takes ~9 min. If it fails, we lose a full generation slot with no score.
- Research findings may not be actionable within YOLO11's framework.
- All 4 agents running serially means we only get 4 solutions in gen 1.
