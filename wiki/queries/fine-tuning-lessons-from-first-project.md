---
title: Fine-Tuning Lessons From the First Project
created: 2026-04-30
updated: 2026-04-30
type: query
tags: [training, dataset, evaluation, unsloth, modal, experiment, workflow, notes]
sources: [raw/articles/first-fine-tuning-use-case-research-2026-04-30.md]
---

# Fine-Tuning Lessons From the First Project

This page collects the practical lessons that the repo should retain from the first real fine-tuning project sequence: tutor adapter failure, artifact-card-v1 structural success, artifact-card-v2 semantic improvement, and artifact-card-v3 cross-field tradeoff. It is meant to answer: what should I learn about fine-tuning here by actually doing it? [[artifact-card-sft]] [[hermes-ai-lab-tutor-adapter]] [[artifact-card-v1-vs-v2]] [[artifact-card-v2-vs-v3]] [[artifact-driven-experiment-debugging]] [[ai-lab-learning-path]]

## 1. Pick a task that is small enough to win
- The original tutor task mixed explanation quality, concept accuracy, repo-specific heuristics, tone, brevity, and generalization.
- That was too broad for a tiny starter SFT dataset.
- The first real win came only after the project pivoted to a narrower structured-output task.

Lesson:
- for the first Unsloth/Modal project, prefer extraction, constrained labeling, or fixed-format transformation over open-ended teaching or explanation

## 2. Trust eval artifacts before train loss
- The tutor project showed repeated cases where loss moved a little while held-out answers still missed the intended concepts.
- `artifact-card-v1` had a train loss of `2.496953636407852`, but the more important story was in `run_summary.json`: JSON validity became perfect while semantic fields remained weak.
- `artifact-card-v2` lowered train loss again to `2.108652096986771`, but the important learning was which fields improved and which still failed.

Lesson:
- treat `run_summary.json`, `sample_eval`, `full_eval`, and scored field metrics as the real debugging surface
- use train loss as supporting context, not as the main success signal

## 3. Structural gains and semantic gains are different phases
- `artifact-card-v1` taught the model to emit valid JSON and the right top-level keys.
- It did not yet teach the model to choose the exact canonical labels and phrases.
- `artifact-card-v2` improved semantics by shrinking the target vocabulary and phrase space.

Lesson:
- if a tiny SFT run improves formatting but not labels, the next patch should usually constrain the target space instead of widening the task

## 4. Dataset design matters more than repeating the same run
- The tutor history already showed that stable reruns can prove the infrastructure works but not move the task.
- The main progress in the artifact-card project came from changing dataset design, not from rerunning the same recipe many times.

Lesson:
- once a run is stable, stop spending GPU time on repetition unless you changed the task or data in a meaningful way

## 5. Canonical answer design is part of the task
- In the tutor project, wording-only patches often failed because the target behavior itself was still too broad.
- In `artifact-card-v1`, near-synonyms such as `mixed` or `no improvement` were plausible but still wrong relative to the exact target label.
- In `artifact-card-v2`, explicit allowed vocabularies made the target much easier to learn.

Lesson:
- when building small hand-authored datasets, define the allowed labels and phrases as part of the experiment design
- do not assume the model will infer the exact taxonomy you meant

## 6. Use Modal artifacts as first-class lab artifacts
- Pulling run artifacts locally made it much easier to compare runs and justify dataset changes.
- The repo now has a concrete artifact path pattern and local pull pattern for inspection.

Lesson:
- every important run should leave behind a saved adapter, `run_summary.json`, and enough eval detail to explain what changed, how failure showed up, and what to patch next

## 7. Narrower is usually better for the first project
- Moving from tutor -> artifact-card was the biggest improvement in the whole sequence.
- Moving from artifact-card-v1 -> artifact-card-v2 improved semantics without changing the schema, which shows the value of tightening before expanding.

Lesson:
- the first project should be narrow enough that you can clearly say why it failed, how the failure appears in artifacts, and what the next patch should be

## 8. Keep iteration history, not just final conclusions
The repo learned more from the sequence than from any one run alone:
- tutor adapter: useful negative result; broad tasks can waste early effort
- artifact-card-v1: structure can improve before semantics do
- artifact-card-v2: constrained vocabularies can convert structural gains into semantic gains
- artifact-card-v3: extra full-card scaffolding can improve one field while making others worse

Lesson:
- write down the chain of changes, symptoms, and fixes so later runs can build on real evidence instead of memory

## 9. More prompt scaffolding is not always a cleaner dataset patch
- `artifact-card-v3` added selection hints and targeted contrast rows to improve `next_action` and nearby label selection.
- That did raise `next_action` from `0.125` to `0.5`.
- But `verdict` fell from `0.75` to `0.625`, `key_evidence` fell from `0.875` to `0.625`, and `exact_card_match_rate` stayed at `0.0`.
- The artifacts showed copied scaffolding, malformed labels like `regraded`, and rows where action choice improved while evidence quality regressed.

Lesson:
- once a full-card task starts showing cross-field tradeoffs, do not assume the next move is another round of richer prompts
- at that point, branch into smaller supervised tasks so each field has a cleaner objective

## 10. Decomposition is a diagnostic, not a guaranteed fix
- `artifact-card-failure-modes-v1` stripped the task down to only `primary_failure_modes` while keeping the same underlying evidence.
- The branch kept JSON validity perfect, but exact-match accuracy on the held-out failure-mode labels stayed at `0.125`.
- The tuned model collapsed repeatedly to `missing-required-detail` plus `phrase-copy-or-template-collapse`, which means removing the other card fields did not solve the real confusion boundary.

Lesson:
- use decomposition to test hypotheses, but do not assume a narrower output automatically makes the semantic target learnable
- if the decomposed branch still fails, the next move should redesign the label supervision or evidence framing itself rather than just stripping away more fields

## 11. Better local supervision can still fail at the final decision rule
- `artifact-card-failure-modes-binary-v1` changed the supervision shape from “emit the final 2-label set” to “judge one candidate label at a time.”
- That branch was much easier for the model locally: tuned exact row match rose to `0.71875`, `candidate_label` accuracy reached `0.984375`, and `belongs` accuracy reached `0.734375`.
- But when those binary judgments were recombined back into the original 8 held-out cases, reconstructed exact top-2 set match was still `0.0`.
- The model over-selected `no-material-change` and missed positive `missing-required-detail` labels almost everywhere.

Lesson:
- a subtask can look much better on its own scoring metric while still failing the downstream decision you actually care about
- if local label judgments improve but final label-set reconstruction does not, the next patch should target calibration and selection structure, not just more of the same binary supervision

## 12. A stronger final-decision prompt can still collapse to defaults
- `artifact-card-failure-modes-top2-v1` tried the opposite move: instead of recomposing binary judgments, it forced the model to output the final ranked pair directly with `first_label` and `second_label`.
- Train loss fell to `1.9992237269878388`, but held-out performance did not improve.
- Exact final-pair match stayed at `0.0`.
- `first_label` accuracy stayed at `0.125` and `second_label` accuracy fell to `0.0`.
- The tuned model collapsed to `missing-required-detail` as the first label on 7 of 8 eval rows.

Lesson:
- a lower-loss run with a stricter final output shape can still be a worse supervision design
- if the model collapses to one default dominant label under a direct top-k prompt, the next move should be a true comparison or ranking structure, not just another phrasing pass on the same final-decision format

## 13. Comparison structure can help without fully solving ranking
- `artifact-card-failure-modes-pairwise-v1` changed the supervision shape again: instead of binary belongs/not-belongs judgments or direct final top-2 emission, it asked the model to compare two candidate failure labels at a time.
- The local pairwise task was still hard: tuned exact pairwise row match reached only `0.5580357142857143`.
- But after reconstructing the original 8 held-out decisions from pairwise wins, exact top-2 set match improved from `0.0` to `0.25`.
- Ordered final-pair accuracy still stayed at `0.0`, and `missing-required-detail` still dominated most pairwise tournaments.

Lesson:
- a truer comparison objective can move the downstream task in the right direction even when the local subtask is still weak
- if comparison structure helps but a dominant label still wins too often, the next move should usually narrow the contrast space or condition the score more explicitly on evidence rather than expanding generic pairwise judgments further

## Current best practice for this repo
- choose a narrow task with strict outputs
- keep train/eval small but intentionally designed
- run short diagnostic jobs on Modal
- inspect saved artifacts before touching the dataset again
- document every meaningful run in the wiki with:
  - what changed
  - how the failure or improvement showed up in artifacts
  - what was changed next

## The current open problem
The project is not fully solved yet.
- even after `artifact-card-v3`, `exact_card_match_rate` is still `0.0`
- the full-card task now shows field interference:
  - `next_action` improved
  - `verdict` and `key_evidence` regressed
  - `primary_failure_modes` stayed weak
- the first decomposed branch `artifact-card-failure-modes-v1` also stayed weak at `0.125`, so simple output decomposition did not fix the label-selection problem
- the second decomposed branch `artifact-card-failure-modes-binary-v1` improved row-level binary judgment strongly, but reconstructed final label-set accuracy still stayed at `0.0`
- the third decomposed branch `artifact-card-failure-modes-top2-v1` also stayed at `0.0` exact pair match and collapsed to repeated default labels despite a lower train loss
- the fourth decomposed branch `artifact-card-failure-modes-pairwise-v1` improved reconstructed exact top-2 set match to `0.25`, but ordered pair accuracy still stayed at `0.0` and `missing-required-detail` remained over-dominant

That is still a good place to be because the next branch can stay narrow and testable, but it now needs a more targeted supervision redesign for `primary_failure_modes`: likely evidence-conditioned per-label scoring or a smaller contrastive label subset rather than another round of full-card prompt hints, simple field isolation, unconstrained binary judgment, direct top-2 prompting, or generic full-space pairwise expansion.

## Recommended reading path inside the wiki
1. [[hermes-ai-lab-tutor-adapter]]
2. [[first-fine-tuning-project-options]]
3. [[artifact-card-sft]]
4. [[artifact-card-v1-vs-v2]]
5. [[artifact-card-v2-vs-v3]]
6. [[artifact-card-full-card-vs-failure-modes-branch]]
7. [[artifact-card-failure-modes-v1-vs-binary-v1]]
8. [[artifact-card-failure-modes-binary-v1-vs-top2-v1]]
9. [[artifact-card-failure-modes-top2-v1-vs-pairwise-v1]]
10. [[artifact-driven-experiment-debugging]]

## One-sentence summary
The main practical lesson from this first fine-tuning project is that tiny starter SFT succeeds fastest when the task is narrow, the outputs are strict, the labels are canonical, and every iteration is judged by saved eval artifacts rather than by loss alone.
