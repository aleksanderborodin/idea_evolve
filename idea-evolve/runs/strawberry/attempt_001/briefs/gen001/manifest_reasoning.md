# Manifest Reasoning — Generation 1 (Strawberry Disease Segmentation)

## Situation Assessment

This is a **cold start** — generation 0 had no evaluated solutions. The system has strong prior knowledge from 8 prior experiments done outside idea-evolve:
- Best known: exp5 (copy_paste=0.5) → val mAP50=0.945 at 100 epochs
- Proxy metric: 20 epoch fine-tune from exp5 gives ~0.90 test mAP50 in ~3.6 min

The problem is instance segmentation of 7 strawberry diseases with 15x class imbalance. The dominant solution direction (copy-paste augmentation) is well-established. However, the **model scale** has never been explored beyond yolo11n.

## Agent Mix Rationale

Following cold start rules: **2 explore + 1 full + 1 research**.

| Agent | Type | Purpose |
|-------|------|---------|
| explore_1 | Track B | Larger model (yolo11s) — never tested |
| explore_2 | Track A | Copy-paste parameter refinement |
| full_1 | Full | Solid baseline from proven best config |
| research_1 | Track B | Survey untested techniques for future gens |

## Why These Directions

**explore_1 (yolo11s):** All 8 prior experiments used nano model (2.9M params). Small model (10.1M params) could capture subtler disease features. Completely orthogonal direction — not a refinement of anything tested.

**explore_2 (copy_paste tuning):** Only tested copy_paste=0.3 and 0.5. The parameter space between 0.5 and higher values (0.6, 0.7) or different modes (mixup) is unexplored. This is Track A exploitation of the known-best technique.

**full_1 (baseline):** Establish a solid reference point combining exp5's best augmentation with exp3's optimal lr0. If Track B agents beat this, we know they're finding real improvements.

**research_1 (survey):** Eight experiments covered augmentation, LR, and self-collected data. Techniques like TTA, ensemble, progressive resizing, and custom loss weighting were never tested. The next generation needs actionable options from this research.

## What I'm NOT Doing (Deliberately)

- **No exploit agent:** Nothing to refine yet — no evaluated solutions exist
- **No genetic agent:** No parent solutions to crossover
- **No experimentator:** No specific question to test yet — research_1 will generate those questions
- **No yolo11m-seg:** Larger model (22.4M params) at batch=4 would be too slow for 20-epoch proxy; start with small (s) model first

## Timeout Choices

- Explore agents: 600s — 20-epoch fine-tune + eval runs in ~4 min, 10 min buffer is ample
- Full agent: 600s — same reason
- Research agent: 300s — reading/writing only, no training

## Risks

1. yolo11s at batch=8 might not fit GPU memory with copy_paste — if it OOMs, the agent should reduce batch to 4
2. copy_paste=0.65 might not improve over 0.5 — the imbalance is already addressed at 0.5
3. Research findings might not be actionable — mitigates by asking for concrete implementation details

## Confidence: High

The cold-start structure is clear, and the prior experiments give a strong foundation. The two-track strategy (Track A exploitation + Track B radical) ensures we both refine known good approaches and search for breakthroughs.