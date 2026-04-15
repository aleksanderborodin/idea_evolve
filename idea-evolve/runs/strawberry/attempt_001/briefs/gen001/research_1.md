## Current Population Status
Best solution: No solutions evaluated yet (gen 1 cold start)
Second best: N/A

## Read first
- `/home/sasha/Desktop/idea_evolve/idea-evolve/problems/strawberry/description.md` — Problem definition and key findings
- Note: All prior experiments (exp1-exp8) used yolo11n-seg.pt with various augmentation strategies. No one has explored larger models, class-balanced sampling, or advanced segmentation techniques.

## Directive
This is a Track B research mission. Find approaches the system has never tried.

**Task: Survey the literature and adjacent fields for techniques that could improve strawberry disease segmentation.**

Focus areas:
1. **Class-balanced sampling strategies**: Given 15x imbalance (Leaf Spot: 1365 vs Anthracnose: 89), what strategies from medical imaging or fine-grained classification could help?
2. **Larger/other model architectures**: yolo11s-seg.pt was mentioned but never tested. Also consider: would a different backbone (e.g., EOLO, not YOLO) be worth exploring? What about DETR-based segmentation?
3. **Progressive training**: Start small (320px), then fine-tune at 640px — could this help with the small disease features?
4. **Boundary-aware loss**: Could adding a boundary loss term to the segmentation loss improve mask quality?
5. **Self-training / pseudo-labeling**: Use high-confidence predictions on test set as pseudo-labels for retraining — viable?
6. **Attention mechanisms**: Are there attention-based segmentation heads that YOLO11 could use?
7. **What works in agricultural disease segmentation**: Search for recent papers on strawberry or crop disease segmentation — what do they do that we haven't?

Produce a findings report with:
- Top 3-5 actionable approaches (specific, not vague)
- For each: what it is, why it might work, how to implement it in YOLO11
- Which approaches are likely to give the biggest mAP50 boost
- Any approaches that are NOT worth trying and why

Output: Write your findings to `output/report.md` in your workspace.