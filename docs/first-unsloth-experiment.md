# First Unsloth Experiment

Date: 2026-04-29

## Goal

Turn the reading plan into the first concrete project artifact set.

The chosen default project is:
- `Hermes AI lab tutor adapter`

This project fine-tunes a small instruct model to explain ML and fine-tuning concepts in a concise, beginner-friendly way.

## Why this is the right next step

It matches the current repo state:
- the learning path is documented
- a Modal smoke-test file already exists
- the VPS is good for data prep and orchestration
- the first missing pieces were a small dataset, an experiment brief, and a GPU-run scaffold

It also matches the Unsloth beginner guidance already captured in this repo:
- start small
- prefer an instruct model for tiny datasets
- complete one end-to-end supervised fine-tuning cycle before doing anything ambitious

## Current chosen default model target

Recommended first remote target:
- `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`

Why this default:
- it is a small instruct model
- it matches the current small-dataset strategy
- it keeps the first GPU run focused on workflow validation rather than scale

## Artifacts created for this step

- `data/hermes-tutor-v1/train.jsonl`
- `data/hermes-tutor-v1/eval.jsonl`
- `data/hermes-tutor-v1/README.md`
- `scripts/preview_tutor_dataset.py`
- `modal/train_unsloth_tutor.py`

## Current dataset status

- train rows: 40
- eval rows: 10
- format: JSONL with `instruction`, `input`, `output`

## Current status

Completed on 2026-04-29:
- HF read-token auth is configured and working.
- Modal smoke test passed.
- First short Modal SFT run completed successfully.
- The training script now saves artifacts to a persistent Modal volume.
- The Modal image was pinned to a compatible Python/Torch/xFormers stack, so Unsloth used xFormers instead of falling back to plain PyTorch attention.

Most recent successful run summary:
- Modal run URL: `https://modal.com/apps/akalliokoski/main/ap-2S6vphyY4aVXCinbQdkUt1`
- model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- chat template: `llama-3.2`
- train rows: `40`
- eval rows: `10`
- max steps: `60`
- train runtime: `74.6704s`
- train loss: `1.6594930599133173`
- artifact volume: `ai-lab-unsloth-artifacts`
- artifact dir: `/artifacts/hermes-tutor-v1/20260429T094629Z`
- saved files:
  - `adapter/adapter_model.safetensors`
  - `adapter/adapter_config.json`
  - `adapter/tokenizer.json`
  - `adapter/tokenizer_config.json`
  - `adapter/special_tokens_map.json`
  - `adapter/chat_template.jinja`
  - `adapter/README.md`
  - `run_summary.json`
- local helper scripts:
  - `scripts/list_modal_runs.py`
  - `scripts/show_modal_run_summary.py`

## Current blockers

1. The run now succeeds, but the sample tuned outputs still show that the dataset needs another quality pass before scaling up.
2. Artifacts are persisted in a Modal volume, but not yet uploaded to Hugging Face Hub.
3. The VPS still has no NVIDIA GPU, so all real training remains Modal-first.

## Recommended next action order

### 1. Review and lightly edit the dataset

Target:
- keep the current seed quality high
- optionally grow toward 50+ train rows only after review

Quality rules:
- each answer should be short, specific, and beginner-friendly
- avoid duplicate phrasings
- keep train and eval prompts meaningfully separate

### 2. Validate auth and remote execution path

On the machine where you want to launch the run:
- set `HF_TOKEN`
- verify with `hf auth whoami`
- verify Modal with a smoke test such as `set -a && source .env && set +a && source .venv/bin/activate && modal run modal/hello_gpu.py`

### 3. Run the first short SFT pass

The current `modal/train_unsloth_tutor.py` file now contains a real first-pass training structure:
- it loads the dataset
- converts rows into conversational records
- applies an Unsloth chat template
- configures a small SFT training run

Start with a short run only.

### 4. Write a run log immediately after the first training pass

Capture:
- chosen model
- dependency versions
- train/eval row counts
- hardware target
- runtime
- 3-5 base vs tuned comparisons
- failure notes

## Minimal command checklist

Preview the dataset:

```bash
python scripts/preview_tutor_dataset.py
```

Re-run environment check:

```bash
python3 scripts/check_env.py
```

Smoke-test Modal GPU connectivity:

```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/hello_gpu.py
```
