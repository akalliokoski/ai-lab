# artifact-card-failure-modes-forced-top2-v3

Forced-top-2 anti-fence patch branch for the artifact-card failure-mode project.

Goal
- keep the task focused on `primary_failure_modes`
- preserve the no-abstention forced top-2 target that first beat the `pairwise-v1` downstream baseline
- harden strict raw-JSON compliance after the Qwen3 comparison regressed by wrapping answers in Markdown fences
- test whether prompt-level anti-fence pressure plus generation-prefix steering improves raw output validity without redesigning the target

Why this branch exists
- `artifact-card-failure-modes-forced-top2-v2` was the first decomposition branch to beat `pairwise-v1` downstream, so the target shape itself is worth keeping
- the direct Qwen3 rerun on `forced-top2-v2` did not fail mainly on label semantics; it failed because 5/8 tuned rows wrapped plausible JSON in Markdown code fences
- the next disciplined patch is to harden the output contract before spending more budget on more model swaps or a fresh target redesign

What changed from `forced-top2-v2`
- source rows still come from `artifact-card-failure-modes-v1` plus the same train-only calibration cases introduced for rank-select-v2
- labels, evidence keys, and reconstruction metadata stay the same so downstream comparisons remain apples-to-apples
- the instruction, system prompt, and decision rules now explicitly ban Markdown fences and prose wrappers
- the task config now sets `generation_prefix` to `{` so inference starts inside a JSON object instead of leaving room for ```json preambles
- `max_new_tokens` is reduced from `64` to `48` to tighten the response budget around the fixed four-field object

Current shape
- train examples: 34
- eval examples: 8
- source examples before train-only supplements: 26 train / 8 eval
- train-only supplemental source examples: 8
- mean train input length: 4737.2 chars

Success criterion
- top-2 set match should beat the current best downstream baseline from `artifact-card-failure-modes-pairwise-v1` (`0.25`)
- ordered top-2 match should finally rise above `0.0`
- evidence-key accuracy matters as a grounding check, but label-pair recovery is the main success criterion
- if this branch still fails, the next redesign should likely become a staged shortlist / tournament selector rather than another flat one-shot target
