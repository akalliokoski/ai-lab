# artifact-card-failure-modes-binary-v1

Second decomposition branch for the artifact-card project.

Goal
- redesign supervision for `primary_failure_modes` instead of only narrowing the output
- turn the 2-label selection problem into repeated binary judgments over one candidate label at a time
- test whether the weak field improves once each label decision is made independently

Why this branch exists
- `artifact-card-failure-modes-v1` kept the field isolated but still stayed at 0.125 exact-match accuracy
- the tuned model collapsed onto the repeated pair `missing-required-detail` + `phrase-copy-or-template-collapse`
- that suggests the next issue is label-semantic ambiguity or evidence framing, not just multi-field interference

What changed from failure-modes-v1
- source rows still come from `artifact-card-v3`
- each original row is expanded into 8 binary label-judgment examples, one per allowed failure mode
- output is now one strict JSON object with exactly two keys: `candidate_label`, `belongs`
- this supervision asks the model to solve one label boundary at a time instead of selecting the final pair directly

Current shape
- train examples: 208
- eval examples: 64
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only

Success criterion
- exact-match accuracy on the binary judgments should beat the direct pair-selection branch
- if this branch improves clearly, the next recomposition step can derive the final top-2 labels from per-label judgments
- if it still fails badly, the remaining bottleneck is likely in the evidence wording or label taxonomy itself
