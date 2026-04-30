# artifact-card-failure-modes-contrast-v1

Confusion-targeted contrast scaffold for the artifact-card failure-mode project.

Goal
- keep the task focused on `primary_failure_modes`
- shrink the supervision space to the four hardest `missing-required-detail` confusion boundaries
- require exactly one local decision per contrast group before reconstruction
- keep tiny canonical evidence keys, but only inside those narrow contrast tasks

Why this branch exists
- `artifact-card-failure-modes-pairwise-v1` was the strongest downstream decomposition result so far, but it still over-promoted `missing-required-detail`
- `artifact-card-failure-modes-evidence-v1` improved row-level structure, but reconstructed held-out top-2 set match fell back to `0.0` because the model over-accepted too many labels
- the next strategy after that negative result was to narrow the supervision to the exact confusion boundaries instead of keeping full 8-label expansion

What changed from earlier branches
- source rows still come from `artifact-card-failure-modes-v1` so the evidence and gold pairs stay aligned with the current failure-mode task
- each original row now becomes exactly 4 contrast-group judgments instead of 8 candidate-label judgments or 28 pairwise comparisons
- each row targets one local contrast group with output keys `contrast_group`, `decision`, and `evidence_key`
- decisions are now one of four local states: anchor label, rival label, `both`, or `neither`
- reconstruction is only scored on source examples whose gold pair stays inside the 5-label contrast universe

Contrast groups
- `missing-required-detail` vs `generic-explanation`
- `missing-required-detail` vs `no-material-change`
- `missing-required-detail` vs `hallucinated-detail`
- `missing-required-detail` vs `overlap-contaminated-eval`

Current shape
- train examples: 104
- eval examples: 32
- source examples before expansion: 26 train / 8 eval
- contrast rows per source example: 4
- reconstructable source examples inside the contrast universe: 10 train / 4 eval
- source format: JSONL with `instruction`, `input`, and `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`

Success criterion
- row-level exact match should beat the noisy comparison behavior from the full pairwise branch while staying interpretable by contrast group
- reconstruction on the in-universe held-out subset should recover the original 2-label set more reliably than the broad evidence branch
- if this branch still fails, the next move should likely be targeted source-case additions or a two-stage rank-then-select scheme rather than another broad prompt rewrite
