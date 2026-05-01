---
title: Model Swap: Qwen3 vs Gemma 3 for Artifact-Card SFT
created: 2026-05-01
updated: 2026-05-01
type: query
tags: [training, evaluation, modal, huggingface, unsloth, research, notes]
sources: [../docs/model-swap-qwen3-vs-gemma3-2026-05-01.md]
---

## Question
Which newer replacement models from the latest Qwen and Gemma families fit the current artifact-card SFT project best, and how much implementation or data churn would a swap cause?

## Short answer
The best immediate replacement model is `unsloth/Qwen3-4B-Instruct-2507-bnb-4bit` with chat template `qwen3`.

The best low-risk Gemma comparison is `unsloth/gemma-3-1b-it-bnb-4bit` with chat template `gemma-3`.

`gemma-3-4b-it` is less attractive as a first Gemma swap because its Hugging Face metadata marks it as `image-text-to-text` with `Gemma3ForConditionalGeneration`, which is a weaker fit for the repo's current text-only `FastLanguageModel` path.

## Why Qwen3-4B looks best
- It is newer and substantially stronger than the current `Llama-3.2-1B` starting point.
- HF metadata marks it as plain `text-generation` with architecture `Qwen3ForCausalLM`, so it fits the current trainer assumptions cleanly.
- The official model card emphasizes instruction following, tool usage, multilingual coverage, and very long context.
- Unsloth upstream explicitly supports a `qwen3` chat template.
- An Unsloth 4-bit mirror exists, so it fits the current `load_in_4bit=True` workflow without a new packaging path.

## Why Gemma 3 is mixed for this repo
Gemma 3 itself looks promising at the family level:
- Google positions it as portable, single-GPU friendly, multilingual, and function-calling capable.
- Unsloth upstream explicitly supports `gemma-3` / `gemma3` templates.

But the safest candidate is not the most obvious size:
- `gemma-3-1b-it` is text-generation / `Gemma3ForCausalLM`, so it is a clean drop-in control.
- `gemma-3-4b-it` is multimodal / conditional-generation shaped, which adds implementation risk in this text-only training script.

## Impact on the SFT code and data
For `Qwen3-4B-Instruct-2507` and `Gemma-3-1B-it`, the implementation change should be small:
- change `--model-name`
- change `--chat-template`
- keep dataset, task config, evaluators, and reconstruction logic the same

For `gemma-3-4b-it`, expect medium risk:
- it may need loader/path validation beyond a simple CLI swap
- the current training entrypoint assumes a plain text conversational SFT flow

Data impact should stay low across the text-only candidates:
- no reason to rebuild the ontology or evaluator
- only light prompt tightening if a new family adds extra prose or exposes a new confusion pattern

## Recommended experiment order
1. redesign the target to remove the all-`out` escape hatch
2. rerun the redesigned branch on the current 1B Llama baseline
3. run the exact same branch on `Qwen3-4B-Instruct-2507`
4. optionally run `Gemma-3-1B-it` as a family-control comparison
5. only then consider a larger 8B-class escalation

## Related pages
- [[artifact-card-sft]]
- [[fine-tuning-lessons-from-first-project]]
- [[first-fine-tuning-project-options]]
