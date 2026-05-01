# artifact-card-failure-modes-forced-top2-v3

Status
- scaffolded and locally verified on 2026-05-01

Goal
- keep the `forced-top2` no-abstention target that first beat the old `pairwise-v1` downstream baseline
- patch the new bottleneck exposed by the Qwen3 rerun: strict raw-JSON compliance
- specifically suppress Markdown-fence wrappers like ```json ... ``` without redesigning the label/evidence task again

Why this branch exists
- `artifact-card-failure-modes-forced-top2-v2` is still the strongest decomposition design so far
- the direct Qwen3 rerun on `forced-top2-v2` did not mainly fail on label semantics
- it failed because 5/8 tuned rows wrapped otherwise plausible answers in Markdown code fences, collapsing strict-output validity and downstream recovery
- the next disciplined move is to harden the output contract before spending more budget on further model-family comparisons

What changed from `forced-top2-v2`
- same source dataset family and same train-only calibration cases as `forced-top2-v2`
- same 4-field target object:
  - `primary_label`
  - `primary_evidence_key`
  - `secondary_label`
  - `secondary_evidence_key`
- stronger instruction and system-prompt wording:
  - explicitly requires raw JSON only
  - explicitly bans Markdown fences and prose wrappers
  - explicitly says the first character of the answer must be `{`
- stronger decision-rule block inside each input row:
  - marks fenced/prose-wrapped outputs as invalid examples
- generation-time hardening in `modal/train_unsloth_artifact_card.py`:
  - dataset `task_config.json` now supports `generation_prefix`
  - this branch sets `generation_prefix` to `{` so inference starts inside the JSON object
- tighter response budget:
  - `max_new_tokens` reduced from `64` to `48`

Current shape
- source examples before train-only supplements: `26` train / `8` eval
- train-only supplemental source examples: `8`
- final rows: `34` train / `8` eval
- mean train input length: about `4737.2` chars

Files added or updated for this scaffold
- dataset builder: `scripts/build_failure_mode_forced_top2_v3_dataset.py`
- reusable training-pipeline support: `modal/train_unsloth_artifact_card.py`
- dataset folder: `data/artifact-card-failure-modes-forced-top2-v3/`
- smoke artifact: `tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v3-smoke-run_summary.json`

Local verification completed
- `python3 -m py_compile scripts/build_failure_mode_forced_top2_v3_dataset.py scripts/evaluate_failure_mode_forced_top2_run.py scripts/preview_dataset.py modal/train_unsloth_artifact_card.py` passed
- `python3 scripts/build_failure_mode_forced_top2_v3_dataset.py` generated the dataset successfully
- `python3 scripts/preview_dataset.py artifact-card-failure-modes-forced-top2-v3` showed the anti-fence instruction contract on both train and eval rows
- `python3 scripts/evaluate_failure_mode_forced_top2_run.py tmp/modal-artifacts/artifact-card-failure-modes-forced-top2-v3-smoke-run_summary.json data/artifact-card-failure-modes-forced-top2-v3/eval_metadata.json` returned perfect smoke metrics
- `python3 scripts/check_env.py` passed
- `modal run modal/train_unsloth_artifact_card.py --help` still exposes the expected CLI

Recommended first run command
```bash
set -a && source .env && set +a && source .venv/bin/activate && \
modal run modal/train_unsloth_artifact_card.py \
  --dataset-name artifact-card-failure-modes-forced-top2-v3 \
  --max-steps 20
```

How to judge the first run
- primary check: branch-specific `valid_json_rate` should improve over the `forced-top2-v2` Qwen3 rerun (`0.375`)
- practical baseline to beat on raw compliance: the `forced-top2-v2` 1B Llama run had branch-specific `valid_json_rate = 0.875`
- downstream guardrail: do not accept a formatting win that breaks the task; keep checking `top2_set_match_rate` and `top2_ordered_match_rate` alongside validity
- if raw-JSON validity rises while downstream recovery stays near the `forced-top2-v2` baseline, this patch is worthwhile because it isolates the remaining work back to label/evidence judgment instead of wrapper formatting
