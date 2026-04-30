---
title: Artifact Card v1 vs v2
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment, workflow]
sources: [raw/articles/first-fine-tuning-use-case-research-2026-04-30.md]
---

# Artifact Card v1 vs v2

Side-by-side comparison of the first two `artifact-card-sft` dataset passes. This page exists so the lab can learn from the actual iteration path rather than only the latest run. [[artifact-card-sft]] [[hermes-ai-lab-tutor-adapter]] [[artifact-driven-experiment-debugging]] [[ai-lab-learning-path]]

## What stayed fixed
- model family: `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`
- training entrypoint: `modal/train_unsloth_artifact_card.py`
- run length: `20` steps
- output schema:
  - `run_id`
  - `dataset_name`
  - `model_name`
  - `verdict`
  - `primary_failure_modes`
  - `key_evidence`
  - `next_action`
- evaluation style: full eval scoring from saved `run_summary.json`

## What changed between v1 and v2
- `artifact-card-v1` asked for one strict JSON card but still left too much room for paraphrastic summarization.
- `artifact-card-v2` kept the same schema but rewrote the task into constrained label-and-phrase selection.
- `artifact-card-v2` added explicit allowed vocabularies for:
  - `verdict`
  - `primary_failure_modes`
  - `key_evidence`
  - `next_action`
- `artifact-card-v2` explicitly told the model to copy exact allowed strings rather than invent nearby synonyms.

## Run summary

| pass | run_id | train_loss | valid_json_rate | exact_card_match_rate |
|---|---|---:|---:|---:|
| v1 | `20260430T072526Z` | `2.496953636407852` | `1.0` | `0.0` |
| v2 | `20260430T073913Z` | `2.108652096986771` | `1.0` | `0.0` |

## Tuned field accuracy comparison

| field | v1 | v2 | change |
|---|---:|---:|---:|
| `run_id` | `1.0` | `1.0` | `0.0` |
| `dataset_name` | `1.0` | `1.0` | `0.0` |
| `model_name` | `1.0` | `1.0` | `0.0` |
| `verdict` | `0.375` | `0.75` | `+0.375` |
| `primary_failure_modes` | `0.0` | `0.125` | `+0.125` |
| `key_evidence` | `0.0` | `0.875` | `+0.875` |
| `next_action` | `0.0` | `0.125` | `+0.125` |

## Main interpretation
- `artifact-card-v1` already proved the new task choice was better than the tutor adapter because it taught structure very clearly.
- `artifact-card-v2` showed that the remaining weakness was not mostly infrastructure, optimizer configuration, or raw training length.
- The big gain came from changing the target design, not from changing the hardware or trainer.
- The strongest evidence is that `key_evidence` rose from `0.0` to `0.875` and `verdict` rose from `0.375` to `0.75` while the schema and run budget stayed almost the same.

## What v1 was really teaching
- return valid JSON
- fill in the required top-level keys
- imitate the outer card structure

That is useful, but it is only structural success.

## What v2 additionally taught
- choose a tighter label from a small vocabulary
- copy a canonical evidence phrase instead of paraphrasing it
- stay inside a narrower action space

That is closer to actual task success.

## Why exact-card match is still zero
- the model still misses the exact second choice inside `primary_failure_modes`
- the model still picks a nearby but wrong `next_action`
- a few outputs still normalize strings slightly differently from the target

This matters because it shows the next bottleneck is now concentrated and easy to describe.

## Practical conclusion
- keep `artifact-card-sft` as the first success-oriented project
- keep the schema fixed
- spend the next patch budget on contrast rows for:
  - second-label selection inside `primary_failure_modes`
  - exact choice among neighboring `next_action` labels
- do not broaden the task back into open summarization

## Why this comparison matters for learning
This is the cleanest example so far of a useful fine-tuning lesson in `ai-lab`: when a small SFT run learns structure but not semantics, the first thing to tighten is the target vocabulary and phrase space, not the ambition of the task. [[fine-tuning-lessons-from-first-project]] [[first-fine-tuning-project-options]]
