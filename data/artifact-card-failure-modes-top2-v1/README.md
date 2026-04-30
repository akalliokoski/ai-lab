# artifact-card-failure-modes-top2-v1

Third decomposition branch for the artifact-card project.

Goal
- keep the task focused on `primary_failure_modes`
- force the model to make the final decision structure directly: exactly two distinct labels, ranked as first_label and second_label
- test whether a stronger final decision rule works better than both direct list output and unconstrained binary per-label judgments

Why this branch exists
- `artifact-card-failure-modes-v1` kept the field isolated but still stayed at 0.125 exact-match accuracy
- `artifact-card-failure-modes-binary-v1` improved local binary judgment strongly, but reconstructed top-2 label-set accuracy still stayed at 0.0
- that suggests the next bottleneck is not output format alone but the final selection structure itself

What changed from earlier branches
- source rows still come from `artifact-card-v3`
- output is now one strict JSON object with exactly two keys: `first_label`, `second_label`
- prompts explicitly require exactly two distinct labels and rank them by strength of support
- prompts add sharper contrast notes for the main observed confusion boundaries, especially `no-material-change` vs `missing-required-detail`

Current shape
- train examples: 26
- eval examples: 8
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only

Success criterion
- exact-match accuracy on the final two-label decision should beat both:
  - `artifact-card-failure-modes-v1` direct pair accuracy (`0.125`)
  - reconstructed top-2 accuracy from `artifact-card-failure-modes-binary-v1` (`0.0`)
- if this branch improves clearly, the repo has a better supervision format for the weakest field
- if it still fails, the next branch should likely move to pairwise ranking or evidence-conditioned per-label scoring
