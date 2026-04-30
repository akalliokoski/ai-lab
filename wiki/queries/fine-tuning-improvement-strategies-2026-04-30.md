---
title: Fine-Tuning Improvement Strategies
created: 2026-04-30
updated: 2026-04-30
type: query
tags: [training, dataset, evaluation, unsloth, experiment, workflow, research, notes]
sources: [raw/articles/first-fine-tuning-use-case-research-2026-04-30.md, raw/articles/unsloth-docs-2026-04-28.md]
---

# Fine-Tuning Improvement Strategies

Fresh research-backed strategy pass over the current repo state. Main question: after the tutor pivot and the artifact-card decomposition experiments, what should improve next? [[artifact-card-sft]] [[fine-tuning-lessons-from-first-project]] [[fine-tuning-no-improvement-root-cause-review]] [[artifact-driven-experiment-debugging]]

## Main conclusion
- The next gains are more likely to come from redesigning supervision for the weakest semantic field than from another broad dataset rewrite or generic hyperparameter tweaking.
- The remaining bottleneck is now mostly semantic calibration and evidence-to-label binding.

## Why this looks different from the earlier tutor failure
- The tutor project mainly failed because the task was too broad.
- The artifact-card project already proved that the narrower task family is better: `artifact-card-v2` reached perfect JSON validity and strong gains on `verdict` and `key_evidence`.
- The hard unsolved field is now `primary_failure_modes`, especially selecting the right second label and avoiding collapse onto broad defaults like `missing-required-detail`.

## Fresh evidence from the current branches
### Best current full-card baseline
From `artifact-card-v2`:
- `valid_json_rate = 1.0`
- `verdict = 0.75`
- `key_evidence = 0.875`
- `primary_failure_modes = 0.125`
- `next_action = 0.125`
- `exact_card_match_rate = 0.0`

Interpretation:
- structure is solved enough for now
- some semantics are learnable
- the hardest remaining field should be attacked directly instead of broadening the full card again

### Pairwise branch diagnosis
Local analysis of `artifact-card-failure-modes-pairwise-v1` showed the largest confusion patterns were:
- `generic-explanation -> missing-required-detail` (`23`)
- `overlap-contaminated-eval -> missing-required-detail` (`12`)
- `no-material-change -> missing-required-detail` (`11`)
- `hallucinated-detail -> missing-required-detail` (`10`)

Interpretation:
- the model is not just noisy; it is collapsing toward a dominant broad label
- this looks more like a calibration / supervision-shape problem than a pure formatting problem

### Label-distribution warning
Training-label counts in the pairwise branch were:
- `missing-required-detail`: `146`
- `no-material-change`: `140`
- `generic-explanation`: `115`
- `overlap-contaminated-eval`: `95`
- `phrase-copy-or-template-collapse`: `82`
- `wrong-causal-point`: `62`
- `hallucinated-detail`: `55`
- `fluency-without-correctness`: `33`

Interpretation:
- the rarest labels are also among the hardest semantic distinctions
- a full all-pairs expansion is still not balanced in what it teaches the model to prefer

### Prompt-length warning
Average train input length by branch:
- `artifact-card-v2`: about `2288` chars
- `artifact-card-v3`: about `3489` chars
- `artifact-card-failure-modes-v1`: about `1989` chars
- `artifact-card-failure-modes-top2-v1`: about `4563` chars
- `artifact-card-failure-modes-pairwise-v1`: about `3087` chars

Interpretation:
- the later branches likely spend too much prompt budget on repeated rubric text
- the evidence signal may be getting diluted by policy prose and repeated label definitions

## Strategy recommendations
### 1. Freeze the full-card baseline at `artifact-card-v2`
- Keep `artifact-card-v2` as the comparison point for the full-card task.
- Do not spend the next patch budget on another `artifact-card-v3`-style full-card prompt accretion pass.

### 2. Move to evidence-conditioned per-label scoring
Better next branch:
- input: one evidence bundle + one candidate label
- output: one strict JSON object such as `candidate_label`, `supported`, and one tiny canonical evidence-code field

Why:
- better label calibration
- easier class balancing
- easier hard-negative mining
- more diagnostic than abstract binary `belongs`

### 3. Attack the exact confusion boundaries directly
Highest-value contrast sets now appear to be:
- `missing-required-detail` vs `generic-explanation`
- `missing-required-detail` vs `no-material-change`
- `missing-required-detail` vs `hallucinated-detail`
- `missing-required-detail` vs `overlap-contaminated-eval`

These should get short, explicit, evidence-heavy contrast rows rather than more generic all-label coverage.

### 4. Shrink the prompt mass
For the next branch:
- keep only the local label meaning that matters for the row
- shorten the evidence bullets
- remove repeated full-rubric text wherever possible
- prefer evidence tokens over policy tokens

### 5. Rebalance by confusion, not only by class count
- add rows for the rare and often-overwritten labels
- reduce the relative influence of repeated easy wins for default labels
- treat this more like hard-negative mining than ordinary class balancing

### 6. Score intermediate tasks and reconstructed downstream tasks together
The earlier binary branch already showed that local metrics can improve while the real final decision stays wrong.

So each new branch should report both:
- local row metrics
- reconstructed original-task metrics

### 7. Recombine late
- first improve `primary_failure_modes` in isolation
- only then test whether recombining it into the full card beats `artifact-card-v2`
- do not assume that stronger isolated supervision should be merged back immediately

## Practical next branch
Recommended next experiment:
- evidence-conditioned per-label failure-mode scorer

Reason:
- it fits the current confusion pattern better than another all-pairs expansion
- it keeps the branch narrow and automatically scoreable
- it gives a cleaner place to attach tiny evidence codes and boundary-specific negative examples

## External docs takeaway
Current PEFT / TRL / Unsloth guidance still points to the same broad lesson:
- keep the trainer correct and simple
- match the dataset shape tightly to the intended behavior
- treat task definition and data quality as the main levers once the pipeline is stable

## Bottom line
The next useful improvement is not “more of the same fine-tuning.” It is a sharper supervision redesign:
- shorter prompts
- stronger evidence-to-label binding
- confusion-targeted contrast data
- delayed recombination into the full-card task
