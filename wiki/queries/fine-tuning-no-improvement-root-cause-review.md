---
title: Fine-Tuning No-Improvement Root-Cause Review
created: 2026-04-29
updated: 2026-04-29
type: query
tags: [training, evaluation, dataset, unsloth, experiment, workflow, research]
sources: [raw/articles/unsloth-docs-2026-04-28.md]
---

# Fine-Tuning No-Improvement Root-Cause Review

Fresh review of why the Hermes tutor-adapter runs are not showing reliable improvement. [[hermes-ai-lab-tutor-adapter]] [[artifact-driven-experiment-debugging]] [[unsloth]]

Main conclusion:
- the problem now looks more like objective-plus-dataset mismatch than infrastructure failure

Most likely causes:
- The current `SFTConfig` does not set `assistant_only_loss=True`, so the conversational SFT run may be spending too much gradient on repeated system and user tokens instead of the assistant answers.
- The 40-row train set is over-scoped: it mixes generic ML definitions, workflow tutoring, repo-specific heuristics, and style control in one tiny dataset.
- The weakest eval concepts still only have a few anchor rows each, which makes phrase drift and partial copying more likely than stable concept transfer.
- The current 1B instruct base may be too weak for the desired level of concise, precise tutoring with such a small adapter dataset.
- The run length is high for the dataset size: 40 rows with effective batch size 8 and `max_steps=60` is about 12 epochs.
- The eval loop is still thin because only a few sample evals are saved per run, which makes it hard to separate real gains from local noise.

Implication for next experiments:
- fix loss masking first
- shorten the run
- narrow the dataset to one real adaptation target
- only then do more dataset rewriting
- if quality still plateaus, test a stronger instruct base

Implemented follow-up:
- `modal/train_unsloth_tutor.py` now uses `assistant_only_loss=True`, saves `full_eval`, accepts `--dataset-name`, and defaults to a shorter `max_steps=20`
- `data/hermes-tutor-v2/` now provides a narrower train/eval split focused on concise repo-specific beginner tutoring behavior

Detailed note:
- `docs/fine-tuning-no-improvement-root-cause-review-2026-04-29.md`
