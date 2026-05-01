---
title: Hermes AI Lab Tutor Adapter
created: 2026-04-29
updated: 2026-04-30
type: concept
tags: [training, unsloth, dataset, evaluation, modal, experiment, workflow]
sources: [raw/articles/unsloth-docs-2026-04-28.md]
---

# Hermes AI Lab Tutor Adapter

The current default first experiment for `ai-lab` is a tiny tutoring adapter project: fine-tune a small instruct model so it explains ML and fine-tuning concepts clearly, briefly, and step-by-step. It is intentionally narrow and small so the full workflow can be completed once before the project expands. [[unsloth]] [[ai-lab-learning-path]] [[artifact-driven-experiment-debugging]]

Why this project is a good fit
- It matches the repo's learning-by-doing focus.
- It is easy to author and inspect by hand.
- It encourages disciplined comparison between base and tuned outputs.
- It cleanly fits the VPS/MacBook/Modal split already defined in the workspace.

Current implementation status
- Two dataset tracks now exist:
  - `data/hermes-tutor-v1/` is the broader first-pass dataset used in the earlier runs
  - `data/hermes-tutor-v2/` is a narrower dataset focused on concise repo-specific beginner tutoring behavior
- A dataset preview script exists in `scripts/preview_tutor_dataset.py` and now accepts a dataset name.
- Local helper scripts exist to inspect Modal artifacts: `scripts/list_modal_runs.py` and `scripts/show_modal_run_summary.py`.
- A Modal training entrypoint exists in `modal/train_unsloth_tutor.py` using a small Llama 3.2 instruct default.
- The training entrypoint now supports dataset selection, uses `assistant_only_loss=True` for conversational SFT, saves `full_eval` outputs, and defaults to a shorter 20-step diagnostic run.
- Durable artifacts are saved in the Modal volume `ai-lab-unsloth-artifacts`.
- Local artifact pulls for deep inspection go under `tmp/modal-artifacts/<run_id>/`.

Why the artifacts matter
- For this project, `run_summary.json` is the main debugging artifact.
- The `sample_eval` block is the fastest way to see whether a dataset pass helped, drifted, or confused the model.
- Repeated stable runs with the same 40-row dataset showed that the infra was working and the dataset had become the bottleneck.

Iteration history
- `20260429T093147Z`: first durable successful run on the 36-row dataset. This validated the end-to-end path and saved the first adapter artifacts.
- `20260429T094629Z`, `20260429T101846Z`, and `20260429T101953Z`: stable 40-row runs with nearly identical outcomes. This showed that repeating the same run was not the best use of GPU time and that dataset quality was the limiting factor.
- `20260429T103541Z`: a 46-row targeted patch run that completed successfully but gave worse qualitative results. Artifact review showed drift on three weak eval concepts: instruct models for tiny datasets, the smallest useful fine-tuning outcome, and eval contamination.
- `20260429T105620Z`: a cleaned 40-row rerun after artifact-driven cleanup. This recovered from the 46-row regression and improved loss, but the three weak eval concepts still need sharper answers.
- `20260429T110801Z`: a 43-row surgical patch run that added only three anchor rows for the weak concepts. The instruct-model answer improved, but overall loss regressed and the other two weak concepts still showed phrasing distortion or confusion.
- `20260429T112202Z`: a 40-row cleanup rerun after removing the near-paraphrase train additions. This made the evaluation cleaner again, but it also showed that two of the weak concepts still were not taught strongly enough.
- `20260429T172803Z`: a 40-row rerun after rewriting 4 existing rows into scenario-style prompts. This preserved train/eval separation, but loss worsened and all three tracked eval concepts drifted away from the desired canonical answers.
- `20260430T061418Z`: the first narrow `hermes-tutor-v2` run with `assistant_only_loss=True`. The trainer path worked after fixing the conversational dataset key from `conversations` to `messages`, but the tuned answers still drifted into generic or distorted explanations instead of the repo-specific target behavior.

Current status
- The tutor adapter remains a useful negative result and debugging case study, but it is no longer the best candidate for the first success-oriented fine-tuning project.
- The current recommendation is to move the next first-project attempt toward `artifact-card-sft`, a structured experiment-card task with easier scoring. [[first-fine-tuning-project-options]]

What the failed 46-row run taught
- A reasonable-looking targeted patch can still make the model worse if the added rows are too abstract or too loosely phrased.
- Loss alone did not explain the failure clearly enough; the `sample_eval` outputs did.
- Pulling the latest artifacts locally made it easier to compare the regression and justify a stricter cleanup.

What the cleaned 40-row rerun taught
- A tighter core dataset can recover from a bad patch without changing the infra or trainer.
- Better loss does not automatically mean the weak eval concepts are fixed.
- The saved `run_summary.json` still shows that the three weakest concepts need more direct anchor wording in the dataset.

What the 43-row surgical patch taught
- Exact anchor wording helped the instruct-model concept more than before.
- A small additive patch can still produce unwanted phrase-copy artifacts when overlapping rows become too similar.
- For this dataset, the next improvement should probably come from rewriting or replacing overlapping rows, not just adding more near-paraphrases.

What the generalization cleanup rerun taught
- Removing leakage-like overlap made the evaluation more trustworthy.
- The instruct-model concept still improved somewhat, which is a better sign than the 43-row run because it no longer depends on a near-paraphrase train prompt.
- The smallest-useful-outcome and eval-contamination concepts are still weak, which means the underlying training examples need better task framing rather than more overlap with eval wording.

What the scenario-style rewrite rerun taught
- Rewriting rows into scenarios can reduce overlap risk without adding more examples, but it can also blur the target answer if the canonical wording becomes too indirect.
- For this dataset, the model still needs one crisp anchor row for each weak concept; pure scenario diversity was not enough.
- The artifacts suggest the next revision should be hybrid: keep scenario-style prompts where useful, but restore explicit target content for instruction-following, smallest-useful-outcome components, and eval contamination.

What the fresh root-cause review changed
- The next fix is no longer just another dataset wording pass on `hermes-tutor-v1`.
- The training objective itself was tightened by switching the conversational SFT run to `assistant_only_loss=True`, which should stop wasting gradient on repeated system and user tokens.
- The entrypoint now saves `full_eval` outputs and defaults to a shorter 20-step diagnostic run so the next comparison is easier to interpret.
- A narrower dataset, `data/hermes-tutor-v2/`, was created to test whether the adapter learns repo-specific tutoring behavior more cleanly when generic ML definition coverage is stripped out.

What the first v2 run taught
- The `assistant_only_loss=True` path was not actually ready until the dataset key matched TRL's conversational schema; `messages` works, `conversations` does not.
- Once that key mismatch was fixed, the full v2 training run completed successfully and saved durable artifacts under `/artifacts/hermes-tutor-v2/20260430T061418Z`.
- The narrow-dataset reset is easier to interpret, but the first outputs are still weak enough that the next bottleneck is likely answer sharpness or base-model capability, not launch infrastructure.

Current corrective action
- The regressive 46-row patch was rolled back.
- The dataset was tightened back to 40 rows.
- Nine existing rows were rewritten to be shorter, stricter, and more aligned with the desired tutor style.
- A later surgical pass added 3 anchor rows, producing a 43-row dataset for run `20260429T110801Z`.
- Those 3 near-paraphrase rows were then removed again to restore cleaner train/eval separation before run `20260429T112202Z`.
- The latest artifacts were pulled locally under `tmp/modal-artifacts/20260429T112202Z/` for direct comparison against the 43-row and earlier 40-row runs.
- A later pass rewrote 4 existing rows into scenario-style prompts and produced run `20260429T172803Z`, but the artifact review showed that the rewrite weakened the canonical answers instead of improving them.
- The next stage now has a cleaner implementation-and-data pair: `assistant_only_loss=True` plus the narrower `data/hermes-tutor-v2/` dataset.
- The first v2 launch exposed and fixed a schema bug in the training entrypoint (`messages` versus `conversations`), and the successful rerun is now the baseline artifact set for the narrow-dataset stage.
- After reviewing that first v2 baseline, the training set was rewritten again in a targeted way to restore sharper canonical wording for the instruct-model, minimum-success, eval-contamination, and Modal-role concepts before spending more GPU time.
- Rerun `20260430T062717Z` showed that the sharper wording patch alone was not enough: train loss fell only slightly (`3.0707` -> `3.0663`), while the held-out answers remained generic, distorted, or unchanged on the key tracked concepts.
- The new narrow-dataset evidence now points more strongly at base-model capability limits or the need for a more structural dataset redesign, rather than another small wording-only patch.
- A stronger-base comparison run, `20260430T063654Z`, swapped only the model to `unsloth/Llama-3.2-3B-Instruct-bnb-4bit` and lowered loss further to `2.9948`, but the held-out answers still missed the same repo-specific concepts.
- That 3B test improved fluency more than correctness, which makes dataset structure and target-answer design the more likely next bottleneck than raw base-model size alone.

Operating rule for the next stage
- Every future dataset pass should be justified by saved artifact evidence.
- Every important run should be written up with: what changed, how it showed up in the artifacts, and what was changed next. [[artifact-driven-experiment-debugging]] [[ai-lab-learning-path]]
