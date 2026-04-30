# artifact-card-failure-modes-pairwise-v1

Fourth decomposition branch for the artifact-card project.

Goal
- keep the task focused on `primary_failure_modes`
- replace direct final-pair emission with true pairwise comparisons between candidate labels
- test whether comparative supervision improves downstream top-2 selection more than binary judgments or direct top-2 prompting

Why this branch exists
- `artifact-card-failure-modes-v1` kept the field isolated but still stayed at 0.125 exact-match accuracy
- `artifact-card-failure-modes-binary-v1` improved local binary judgment strongly, but reconstructed top-2 accuracy still stayed at 0.0
- `artifact-card-failure-modes-top2-v1` forced the final ranked pair directly, but exact final-pair match still stayed at 0.0 and the model collapsed to `missing-required-detail`
- that suggests the next bottleneck is comparative supervision structure rather than output formatting alone

What changed from earlier branches
- source rows come from `artifact-card-failure-modes-v1` so the evidence and rubric stay aligned with the decomposed task
- each original example is expanded into one comparison for every unordered label pair (28 pairs per source example)
- output is now one strict JSON object with exactly one key: `preferred_label`
- prompts explicitly ask which of two candidate labels is better supported by the evidence
- gold ranking is induced from the original ordered final pair: first gold label > second gold label > all non-gold labels
- non-gold vs non-gold comparisons use a deterministic tie-break only to keep the supervision total and scoreable

Current shape
- train examples: 728
- eval examples: 224
- source format: JSONL with `instruction`, `input`, and `output`
- target output: JSON string only
- helper metadata: `train_metadata.json`, `eval_metadata.json`

Success criterion
- pairwise exact-match accuracy should improve over the weaker direct-branch behavior while keeping valid JSON at 1.0
- reconstructing the original final top-2 label decisions from pairwise wins should beat:
  - `artifact-card-failure-modes-v1` direct pair accuracy (0.125)
  - reconstructed top-2 accuracy from `artifact-card-failure-modes-binary-v1` (0.0)
  - `artifact-card-failure-modes-top2-v1` direct final-pair accuracy (0.0)
- if this branch still fails, the next branch should likely move to evidence-conditioned per-label scoring or a smaller contrastive label subset
