# Model swap note: Qwen3 vs Gemma 3 for artifact-card SFT

Date: 2026-05-01
Repo commit at review time: `22f5552`

## Current training setup

The current artifact-card training entrypoint already supports model swapping from the CLI:
- file: `modal/train_unsloth_artifact_card.py`
- current default model: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- current default chat template: `llama-3.2`
- swap knobs already exposed:
  - `--model-name`
  - `--chat-template`
  - `--dataset-name`
  - `--max-steps`

Important implementation detail from the current script:
- it calls `FastLanguageModel.from_pretrained(...)` with `load_in_4bit=True`
- it then applies `get_chat_template(tokenizer, chat_template=...)`
- it uses a text-only conversational SFT pipeline with `assistant_only_loss=True`
- it assumes the model can be used through the standard text `FastLanguageModel` path

That means a model swap is low-friction only when the replacement is:
- supported by Unsloth
- text-generation / CausalLM shaped
- compatible with a normal text chat template

## Why revisit the base model now

The current branch failures do not look like pure infrastructure problems.
They look like a mix of:
- small-model calibration weakness
- target-design weakness
- structured-output constraint failure under tiny-data SFT

The strongest evidence from recent runs:
- the current 1B Llama family is good enough to validate the pipeline and learn some JSON structure
- but it repeatedly collapses on the actual allocation task
- a previous clean 3B Llama comparison improved fluency more than correctness
- the latest `joint-rank-v1` run still failed structurally even after the target was made joint

So a stronger model may help, but the next base-model test should be treated as a controlled comparison, not as the main fix.

## Current-family research snapshot

### Qwen side

Research checked on 2026-05-01:
- `Qwen/Qwen3-4B-Instruct-2507`
  - lastModified: `2025-09-17T06:56:53Z`
  - pipeline: `text-generation`
  - architecture: `Qwen3ForCausalLM`
  - model_type: `qwen3`
- official README highlights:
  - improved instruction following
  - improved reasoning / tool usage
  - stronger multilingual coverage
  - `262,144` native context
  - non-thinking mode only for the `Instruct-2507` refresh
- Unsloth template support exists in upstream `chat_templates.py` as `qwen3`
- Unsloth 4-bit mirror exists:
  - `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit`
  - ungated on HF API

Also relevant:
- `Qwen/Qwen3-8B` exists and is text-generation / `Qwen3ForCausalLM`
- that is a plausible later escalation if 4B still looks too weak
- but it is a larger jump in cost/risk for the current T4-first loop

### Gemma side

Research checked on 2026-05-01:
- Google’s Gemma 3 announcement says Gemma 3 comes in `1B`, `4B`, `12B`, and `27B`
- blog notes emphasize:
  - single-GPU/TPU portability
  - `128K` context
  - support for over `140` languages
  - function calling
- Unsloth template support exists in upstream `chat_templates.py` as `gemma-3` / `gemma3`

But the family splits in an important way for this repo:

1. `google/gemma-3-1b-it`
- pipeline: `text-generation`
- architecture: `Gemma3ForCausalLM`
- model_type: `gemma3_text`
- this is the safest Gemma drop-in for the current text-only SFT codepath
- Unsloth 4-bit mirror exists:
  - `unsloth/gemma-3-1b-it-bnb-4bit`

2. `google/gemma-3-4b-it`
- pipeline: `image-text-to-text`
- architecture: `Gemma3ForConditionalGeneration`
- model_type: `gemma3`
- this is not as clean a drop-in for the current text-only `FastLanguageModel` pipeline
- Unsloth 4-bit mirror exists:
  - `unsloth/gemma-3-4b-it-bnb-4bit`
- but because it is a multimodal conditional-generation model, it carries more implementation risk than Qwen3-4B or Gemma-3-1B for this exact repo

Also relevant:
- `google/gemma-3n-E4B-it` exists, but it is multimodal / on-device oriented and is not the best first swap target for this text-only artifact-card loop

## Practical fit for this project

### Best low-risk replacement: Qwen3-4B-Instruct-2507

Recommended first replacement model:
- `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit`
- chat template: `qwen3`

Why it fits well:
- newer than the current Llama 3.2 1B starting point
- stronger instruction-following emphasis in the model card
- text-only CausalLM shape, so it matches the current trainer assumptions
- Unsloth template support is explicit
- Unsloth 4-bit mirror exists, so it fits the current `load_in_4bit=True` pattern
- 4B is a meaningful capacity step up without immediately jumping to the heaviest option

What it tests well:
- whether a stronger small instruct model improves constrained label allocation
- whether the current failure is partly a 1B-calibration ceiling
- whether the target redesign is learnable at all on a better base before moving to larger models

### Best low-risk Gemma test: Gemma-3-1B-it

Recommended Gemma control:
- `unsloth/gemma-3-1b-it-bnb-4bit`
- chat template: `gemma-3`

Why it is useful:
- same rough size class as the current 1B Llama baseline
- text-only CausalLM shape
- lower implementation risk than Gemma 3 4B multimodal

What it is good for:
- a family-swap control that isolates “architecture / tokenizer / instruction tuning family” from “just add more parameters”

What it is not good for:
- proving that more capacity solves the task, since it stays in the 1B class

### Higher-risk Gemma option: Gemma-3-4B-it

Candidate:
- `unsloth/gemma-3-4b-it-bnb-4bit`
- nominal template: `gemma-3`

Why I would not make this the first Gemma swap:
- HF API reports it as `image-text-to-text`
- architecture is `Gemma3ForConditionalGeneration`, not the cleaner text-only `Gemma3ForCausalLM`
- the current training entrypoint is designed around a plain text conversational SFT loop
- it may still be usable, but it is more likely to need implementation adjustments or a different loading path

Conclusion:
- if the goal is a clean apples-to-apples replacement test, prefer Qwen3-4B first
- if the goal is a Gemma-family test with minimal code risk, prefer Gemma-3-1B-it first
- defer Gemma-3-4B-it until after the text-only replacement path is working cleanly

## Recommended ranking for this repo

### Option A: best next real experiment
1. `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit`
2. keep dataset/target fixed for one controlled comparison
3. compare against the current Llama-3.2-1B baseline on the same branch

Why:
- strongest combination of recency, text-only fit, and low implementation risk

### Option B: best family-control comparison
1. `unsloth/gemma-3-1b-it-bnb-4bit`
2. same dataset and run length
3. compare whether Gemma-family priors help more than Llama-family priors at the same scale

Why:
- isolates family differences better than parameter-count differences

### Option C: later escalation if target redesign still looks promising
1. `Qwen3` in a larger size class such as 8B
2. only after the target has removed the all-`out` escape hatch
3. likely with reduced batch / shorter seq / more careful runtime tuning on T4

Why:
- if 4B still fails but the outputs look structurally closer, larger capacity may then be worth the spend

## Would the SFT implementation change much?

### For Qwen3-4B-Instruct-2507
Expected change level: low

Likely enough:
- swap `model_name`
- swap `chat_template` from `llama-3.2` to `qwen3`

No expected changes to:
- dataset JSONL format
- task_config structure
- evaluator scripts
- artifact persistence
- training loop structure

### For Gemma-3-1B-it
Expected change level: low

Likely enough:
- swap `model_name`
- swap `chat_template` from `llama-3.2` to `gemma-3`

No expected changes to:
- dataset format
- task_config structure
- evaluation logic

### For Gemma-3-4B-it
Expected change level: medium

Potential extra work:
- verify that the current text-only `FastLanguageModel` path is valid for `Gemma3ForConditionalGeneration`
- verify generation/prompt rendering stays text-only and stable
- check whether the processor/model loading path differs from the current script’s assumptions

## Would the data need to change much?

For all of the text-only candidate swaps above:
- the dataset should stay mostly unchanged
- the branch-specific evaluators should stay unchanged
- the task redesign matters more than the model-family swap

Possible light adjustments only:
- slightly tighter system prompt wording if a new family tends to add extra prose
- shorter `max_new_tokens` if a model becomes too verbose
- a few targeted contrast rows only if a new family shows a distinct new confusion pattern

What should not be necessary just because of the swap:
- rebuilding the full dataset
- changing the label ontology
- changing reconstruction logic

## Exact first commands to try

### Qwen3 4B
```bash
set -a && source .env && set +a && source .venv/bin/activate && \
modal run modal/train_unsloth_artifact_card.py \
  --dataset-name artifact-card-failure-modes-joint-rank-v1 \
  --model-name unsloth/Qwen3-4B-Instruct-2507-bnb-4bit \
  --chat-template qwen3 \
  --max-steps 20
```

### Gemma 3 1B
```bash
set -a && source .env && set +a && source .venv/bin/activate && \
modal run modal/train_unsloth_artifact_card.py \
  --dataset-name artifact-card-failure-modes-joint-rank-v1 \
  --model-name unsloth/gemma-3-1b-it-bnb-4bit \
  --chat-template gemma-3 \
  --max-steps 20
```

## Final recommendation

For this repo, the best immediate replacement model is:
- `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit`

Why:
- most recent high-confidence text-only candidate from the researched set
- best match to the current text-only Unsloth SFT implementation
- meaningful capacity upgrade from the current 1B baseline
- lower implementation risk than Gemma 3 4B multimodal

Secondary recommendation:
- `unsloth/gemma-3-1b-it-bnb-4bit` as a family-control run, not as the main improvement bet

Not recommended as the first swap in this repo:
- `gemma-3-4b-it` as the very first Gemma test, because its multimodal conditional-generation shape makes it a less faithful drop-in for the current trainer.

## What to do next

Best next controlled experiment sequence:
1. redesign the target to remove the all-`out` escape hatch
2. rerun the redesigned branch on the current Llama 1B for continuity
3. run the exact same redesigned branch on `Qwen3-4B-Instruct-2507`
4. if useful, run `Gemma-3-1B-it` as a family control
5. only then consider a larger 8B-class escalation
