---
title: First Fine-Tuning Project Options
created: 2026-04-30
updated: 2026-04-30
type: comparison
tags: [training, dataset, evaluation, unsloth, modal, experiment, research, workflow]
sources: [raw/articles/first-fine-tuning-use-case-research-2026-04-30.md, raw/articles/unsloth-docs-2026-04-28.md]
---

# First Fine-Tuning Project Options

Comparison of better-scoped first-project candidates after the repo-tutor adapter failed to show stable gains across repeated small Unsloth runs. [[hermes-ai-lab-tutor-adapter]] [[artifact-driven-experiment-debugging]] [[ai-lab-learning-path]] [[unsloth]]

## Evaluation criteria
- narrow task boundary
- short outputs
- one stable schema or label space
- easy automatic evaluation
- useful for the real `ai-lab` workflow
- realistic to author by hand in `20-100` examples

## Option A: experiment-artifact to structured experiment card

Task:
- input: a run summary, selected eval comparisons, and a short operator note
- output: one strict JSON or fixed markdown lab card

Why it fits:
- mostly format control, extraction, and light labeling
- directly uses existing Modal artifacts and run notes
- easy to score field by field
- reinforces the repo rule that each iteration should record what changed, what failed, and what to try next

Main risks:
- the input must stay short enough that the task remains structured extraction rather than open-ended summarization
- the label taxonomy for failure modes must stay small and crisp

Verdict:
- best first-project candidate

## Option B: eval-answer failure-mode classifier

Task:
- input: eval prompt, reference answer, base answer, tuned answer
- output: a short set of failure-mode labels

Why it fits:
- tiny output space
- useful for artifact review
- easy to derive examples from saved run summaries

Main risks:
- annotation consistency matters a lot
- a fuzzy label set would make the task harder than it looks

Verdict:
- strong second choice

## Option C: raw note to experiment brief template

Task:
- input: messy project or failure notes
- output: fixed sections such as goal, setup, blocker, evidence, next test

Why it fits:
- useful in the lab
- more structured than tutoring
- still aligned with the repo's note-taking habits

Main risks:
- scoring is more subjective than JSON extraction or label classification

Verdict:
- decent fallback option

## Option D: repo-specific tutor adapter

Task:
- input: workflow or ML question
- output: concise, correct tutor answer

Why it underperformed here:
- it mixes knowledge transfer, response style, repo heuristics, and causal explanation
- tiny datasets mostly shifted wording and fluency instead of reliably teaching the desired concepts
- a stronger 3B base improved fluency more than correctness, which points back to task scope and target design rather than only model size

Verdict:
- weak first-project fit; better approached later with retrieval support or a much more constrained task definition

## Recommendation
- move the first serious project from tutoring to `artifact-card-sft`
- keep the first schema intentionally small: `run_id`, `dataset_name`, `model_name`, `verdict`, `primary_failure_modes`, `key_evidence`, `next_action`
- build automatic scoring before the next remote run so the project is judged by field accuracy, not train loss alone

## Why this is the best fit now
- It is still genuinely useful for `ai-lab`.
- It uses data that already exists in the repo.
- It matches what tiny LoRA/QLoRA SFT usually does well: format control, extraction, and narrow behavioral shaping.
- It produces a much cleaner first-win condition than trying to prove the model became a better repo tutor.
