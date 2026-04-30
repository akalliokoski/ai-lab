# artifact-card-v2

Second pass on the artifact-card starter task.

Goal
- keep the same strict JSON experiment-card schema
- convert the task from loose paraphrastic summarization into a narrower extraction-and-label-selection task
- reward exact canonical vocabulary instead of plausible free-form rephrasings

What changed from v1
- removed unnecessary semantic freedom from the target task
- added explicit allowed vocabularies inside each prompt:
  - verdict labels
  - failure-mode labels
  - candidate evidence phrases
  - candidate next actions
- rewrote the inputs so the model is asked to copy the exact canonical phrases instead of inventing near-synonyms
- kept the output schema identical so run summaries remain comparable at the field level

Why this change matches the v1 failure
- the first real run taught JSON structure well but not exact semantic normalization
- tuned outputs drifted into near-synonyms like `unreliable`, `no improvement`, `improvement`, and `mixed`
- `primary_failure_modes`, `key_evidence`, and `next_action` stayed at `0.0` field accuracy because the task still rewarded plausible paraphrase more than exact selection

Current shape
- train examples: 20
- eval examples: 8
- source format: JSONL with `instruction`, `input`, `output`
- target output: JSON string only
- output keys:
  - `run_id`
  - `dataset_name`
  - `model_name`
  - `verdict`
  - `primary_failure_modes`
  - `key_evidence`
  - `next_action`

Hypothesis
- v2 should preserve the strong JSON-validity gain from v1
- and improve semantic field accuracy by turning the task into exact label/phrase selection
- if it still fails, the next move is probably to collapse the task even further into smaller subtasks such as verdict-only or failure-mode-only prediction
