# artifact-card-failure-modes-v1

First decomposed branch from the artifact-card project.

Goal
- isolate the weakest remaining semantic field from the full-card task
- predict only `primary_failure_modes`
- keep the output scoreable with an exact two-label match

Why this branch exists
- `artifact-card-v2` was the best full-card baseline, but `primary_failure_modes` only reached 0.125 field accuracy
- `artifact-card-v3` improved `next_action` but left `primary_failure_modes` flat at 0.125 while regressing other fields
- that pattern suggests cross-field interference on the joint task
- this branch tests whether the model can learn the failure-label decision boundary once the other card fields are removed

What changed from the full-card task
- source rows come from `artifact-card-v3`, but the prompt is narrowed to failure-label selection only
- removed verdict, evidence-list, and next-action output requirements
- kept the same underlying run evidence and the same 8-label failure-mode vocabulary
- output is now one strict JSON object with exactly one key: `primary_failure_modes`

Current shape
- train examples: 26
- eval examples: 8
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only

Success criterion
- exact-match accuracy on `primary_failure_modes` should beat the 0.125 full-card baseline
- if this branch improves sharply, it supports decomposing the remaining hard fields before any recombination attempt
- if it still fails badly, the bottleneck is more likely the label semantics or the evidence framing itself, not just multi-field interference
