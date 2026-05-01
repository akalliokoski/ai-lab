# artifact-card-failure-modes-forced-top2-v3

Status
- scaffolded and locally verified on 2026-05-01
- first real Modal run completed and reviewed on 2026-05-01

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
- the raw-JSON-only patch did beat the `forced-top2-v2` Qwen3 rerun on strict validity, but only partially: branch-specific `valid_json_rate` rose from `0.375` to `0.625`
- that was still a clear regression versus the stronger `forced-top2-v2` 1B Llama baseline (`valid_json_rate = 0.875`)
- the downstream task also regressed with the same shape as the Qwen3 rerun: `top2_set_match_rate = 0.125`, `top2_ordered_match_rate = 0.125`, and `invalid_row_rate = 0.375`
- this means the anti-fence patch removed the specific Markdown-wrapper failure mode, but it did not preserve the stronger branch behavior that made `forced-top2-v2` worth continuing

First real run result
- Run ID: `20260501T085312Z`
- Model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- Train loss: `1.913314300775528`
- Built-in auto-eval looked superficially clean on format:
  - `valid_json_rate = 1.0`
  - `exact_card_match_rate = 0.125`
  - field accuracy: `primary_label = 0.25`, `primary_evidence_key = 0.25`, `secondary_label = 0.125`, `secondary_evidence_key = 0.5`
- Branch-specific evaluator gave the real result:
  - `valid_json_rate = 0.625`
  - `top2_set_match_rate = 0.125`
  - `top2_ordered_match_rate = 0.125`
  - `primary_label_accuracy = 0.25`
  - `secondary_label_accuracy = 0.125`
  - `primary_evidence_key_accuracy = 0.25`
  - `secondary_evidence_key_accuracy = 0.125`
  - `invalid_row_rate = 0.375`

What changed relative to the Qwen3 failure
- the specific `invalid-json` / fenced-output failure mode from the Qwen3 rerun did disappear
- but the errors shifted into branch-level contract mistakes: 3/8 tuned rows reused `missing-or-noncanonical-field` as the secondary evidence key for `generic-explanation`, which the branch-specific evaluator marks as `bad-secondary-evidence-key`
- the remaining valid rows still overcollapsed onto the old fallback family: `missing-required-detail` primary with `generic-explanation` or `phrase-copy-or-template-collapse` secondary

Current verdict
- keep `forced-top2-v2` as the best current branch and keep its original 1B Llama run as the best actual result so far
- do not treat `forced-top2-v3` as a successful continuation of that branch; it fixed one surface failure mode but regressed the real downstream objective
- the next patch should be narrower than `v3`: preserve the stronger `v2` prompt shape and target, then add only minimal anti-fence pressure or targeted train rows for evidence-key/label compatibility instead of the heavier contract rewrite
