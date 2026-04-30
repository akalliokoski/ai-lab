# Fine-tuning improvement strategies

Date: 2026-04-30

## Question

How should the current fine-tuning work improve from here, based on a fresh pass over the repo evidence plus current docs guidance?

## Short answer

The biggest gains are still most likely to come from changing supervision design, label structure, and prompt/example shape, not from another round of generic hyperparameter tweaks.

For this repo, the current bottleneck is no longer:
- launch infrastructure
- adapter wiring
- JSON formatting
- basic trainer setup

The main bottleneck now looks like:
- semantic decision calibration
- overly broad or overlapping labels in the hardest branches
- prompt/input verbosity that may be burying the evidence signal
- train distribution that over-rewards default labels like `missing-required-detail`

## What I reviewed

Repo evidence reviewed:
- `wiki/queries/fine-tuning-no-improvement-root-cause-review.md`
- `wiki/queries/fine-tuning-lessons-from-first-project.md`
- `wiki/concepts/artifact-card-sft.md`
- `docs/first-fine-tuning-use-case-recommendation-2026-04-30.md`
- `docs/first-artifact-card-experiment.md`
- `tmp/modal-artifacts/artifact-card-v2-20260430T073913Z/run_summary.json`
- `tmp/modal-artifacts/artifact-card-failure-modes-pairwise-v1-20260430T125005Z/run_summary.json`

Current docs and external references checked:
- Hugging Face PEFT docs: https://huggingface.co/docs/peft/index
- TRL SFTTrainer docs: https://huggingface.co/docs/trl/en/sft_trainer
- Unsloth datasets guide: https://docs.unsloth.ai/get-started/fine-tuning-llms-guide/datasets-guide
- Semantic Scholar search result for review paper: `The Ultimate Guide to Fine-Tuning LLMs from Basics to Breakthroughs` (2024)

One source was blocked:
- OpenAI fine-tuning best-practices page returned `403`, so it was not relied on directly.

## Fresh diagnosis

### 1. The repo already solved the easy failures
The project has already learned that:
- `assistant_only_loss=True` mattered
- conversational data formatting mattered
- narrowing the task helped a lot
- canonical vocabularies improved field accuracy
- a stronger 3B base improved fluency more than correctness on the tutor task

So the next useful moves should assume the remaining problem is semantic supervision design.

### 2. The best current full-card baseline is still `artifact-card-v2`
From `run_summary.json` for `artifact-card-v2`:
- valid JSON reached `1.0`
- `verdict` reached `0.75`
- `key_evidence` reached `0.875`
- `primary_failure_modes` stayed at `0.125`
- `next_action` stayed at `0.125`
- exact-card match stayed at `0.0`

That means the task family is good, but the hardest fields are still weak.

### 3. The hardest remaining field is a ranking/calibration problem, not just a formatting problem
The pairwise branch is especially revealing.

From local analysis of `artifact-card-failure-modes-pairwise-v1`:
- total pairwise eval rows: `224`
- total errors: `99`
- biggest confusions were:
  - `generic-explanation -> missing-required-detail`: `23`
  - `overlap-contaminated-eval -> missing-required-detail`: `12`
  - `no-material-change -> missing-required-detail`: `11`
  - `hallucinated-detail -> missing-required-detail`: `10`

That is not random noise. It looks like collapse toward a default label with broad surface overlap.

### 4. The data distribution itself likely reinforces the default-label collapse
Training-label frequency in the pairwise branch:
- `missing-required-detail`: `146`
- `no-material-change`: `140`
- `generic-explanation`: `115`
- `overlap-contaminated-eval`: `95`
- `phrase-copy-or-template-collapse`: `82`
- `wrong-causal-point`: `62`
- `hallucinated-detail`: `55`
- `fluency-without-correctness`: `33`

So the weakest label is also the rarest, and the dominant label appears heavily across branches.

### 5. The pairwise prompts may be too verbose for the decision they ask for
Measured average input lengths:
- `artifact-card-v2`: about `2288` chars
- `artifact-card-v3`: about `3489` chars
- `artifact-card-failure-modes-v1`: about `1989` chars
- `artifact-card-failure-modes-top2-v1`: about `4563` chars
- `artifact-card-failure-modes-pairwise-v1`: about `3087` chars

The pairwise examples repeat:
- global decision rules
- full allowed-label list
- candidate meanings
- pairwise selection policy
- failure-mode rubric

for every single row.

That may be making the model learn the global rubric language more strongly than the local evidence distinction.

## What current docs suggest

Useful points from the checked docs:
- PEFT docs remain consistent with the idea that LoRA/adapter tuning is an efficient adaptation method, not a substitute for a crisp task definition.
- TRL SFT docs explicitly emphasize conversational formatting, chat templates, `assistant_only_loss`, and packing as trainer-level levers.
- Unsloth dataset guidance still points back to dataset purpose, data quality, and matching the format to the intended behavior.

Together with the repo evidence, that suggests:
- keep the trainer simple and correct
- spend most effort on dataset objective sharpness
- only optimize packing / run efficiency after the semantic target is learnable

## Recommended strategy changes

### Strategy 1: Freeze the broad recipe and optimize the label objective itself
Do not spend the next iteration budget on:
- another tutor-style dataset
- another full-card prompt-scaffolding pass like `artifact-card-v3`
- another generic “try a bigger base model” comparison

Do spend it on redesigning the weakest field objective.

### Strategy 2: Replace global pairwise ranking with evidence-conditioned per-label scoring
Best next branch:
- input: one evidence bundle + one candidate label
- output: structured judgment such as:
  - `supported`: yes/no
  - `evidence_span_type`: explicit / indirect / contradicted
  - maybe one short canonical reason code

Why this is better than the current pairwise branch:
- easier to balance per label
- easier to mine hard negatives
- easier to calibrate thresholding later
- avoids forcing all distinctions through one repeated giant pairwise rubric

Important difference from the earlier binary branch:
- do not just ask “belongs?” in the abstract
- ask whether the evidence explicitly supports this label under a very small rubric
- make the evidence cue part of the supervision target, not just the final label

### Strategy 3: Build targeted contrast sets for the exact confusion boundaries
The confusion table suggests the next high-value contrast groups are:
- `missing-required-detail` vs `generic-explanation`
- `missing-required-detail` vs `no-material-change`
- `missing-required-detail` vs `hallucinated-detail`
- `missing-required-detail` vs `overlap-contaminated-eval`

Make small mini-datasets where:
- the two labels are near neighbors
- only one is correct
- the evidence sentence that decides it is short and explicit
- the wrong label is tempting but refuted

This should work better than expanding all 28 label pairs uniformly.

### Strategy 4: Shrink prompt mass and move rubric complexity out of every row
For the next branch, cut repeated input text aggressively.

Specifically:
- keep the system prompt short
- keep only the local candidate label meaning for the current row
- remove the repeated full failure-mode rubric from every example if the target is already narrow
- make evidence bullets shorter and more canonical

Principle:
- if the model must choose between two labels, most tokens should be evidence, not policy prose

### Strategy 5: Rebalance by confusion, not just by raw label count
Do not aim for global perfect balance across all labels first.
Instead:
- oversample the exact confusing boundaries
- add more rows for rare but semantically distinct labels like `fluency-without-correctness` and `hallucinated-detail`
- reduce repeated easy wins for already-dominant labels

This is closer to hard-negative mining than to ordinary class balancing.

### Strategy 6: Add evidence-anchoring outputs, not just class outputs
A good intermediate supervision target would be something like:
```json
{"candidate_label":"hallucinated-detail","supported":"yes","evidence_key":"invented-details-not-in-input"}
```

Why:
- it forces the model to bind the label to a reason pattern
- it makes evaluation more diagnostic
- it reduces the chance that the model wins by vague label prior alone

### Strategy 7: Keep automatic reconstruction, but score intermediate quality too
For any decomposed branch, evaluate both:
- local row metrics
- reconstructed original-task metrics

The earlier binary branch taught an important lesson: local success can fail downstream.
So every new branch should report:
- row accuracy
- per-label precision/recall
- reconstructed top-2 set match
- reconstructed order accuracy if ranking is relevant

### Strategy 8: Use curriculum only if it preserves the final decision structure
A reasonable curriculum would be:
1. strict JSON validity
2. per-label evidence support
3. small confusion-set ranking
4. final top-2 reconstruction

An unreasonable curriculum would be:
- teaching a very different easy task and hoping it transfers

### Strategy 9: Hyperparameters are secondary right now, but two small tests are still worth it later
After the next dataset/objective redesign, two low-cost tests are worth running:
- compare `max_steps=20` vs a slightly longer run only after the new objective shows signal
- test packing only as an efficiency optimization, not as a semantic fix

I would not prioritize:
- sweeping learning rates first
- changing LoRA rank first
- jumping to much larger models first

### Strategy 10: If full-card performance matters, recombine late, not early
For now, treat:
- `verdict`
- `key_evidence`
- `next_action`
- `primary_failure_modes`

as partially separable skills.

The repo already showed that recombining too much too early creates cross-field tradeoffs.
So the cleaner path is:
- get `primary_failure_modes` substantially better in isolation
- then retry recombination into the full card
- compare against `artifact-card-v2`, not against the weaker branches

## Concrete next experiments

### Experiment A: evidence-conditioned per-label scorer
Goal:
- solve `primary_failure_modes` with better grounding than binary `belongs`

Shape:
- one candidate label per row
- one short evidence bundle
- output keys: `candidate_label`, `supported`, `evidence_key`
- very small controlled `evidence_key` vocabulary

Success criterion:
- better reconstructed top-2 set match than the current `0.25` pairwise branch

### Experiment B: four-way confusion pack
Goal:
- directly attack the dominant collapse into `missing-required-detail`

Shape:
- only rows involving these boundaries:
  - MDR vs GE
  - MDR vs NMC
  - MDR vs HD
  - MDR vs OCE
- short evidence snippets
- balanced support counts by boundary

Success criterion:
- materially reduce the specific confusion counts seen in the pairwise analysis

### Experiment C: recombine only after a better failure-mode branch exists
Goal:
- test whether a stronger failure-mode module improves the full card without hurting `verdict` and `key_evidence`

Shape:
- keep `artifact-card-v2` as the baseline full-card dataset
- splice in the improved failure-mode supervision carefully
- compare exact-card and field metrics to `artifact-card-v2`

## Priority order

1. Keep `artifact-card-v2` as the full-card baseline.
2. Stop broad full-card prompt accretion.
3. Build an evidence-conditioned per-label branch for `primary_failure_modes`.
4. Mine hard negatives from the exact confusion table.
5. Shorten prompts and remove repeated rubric mass.
6. Recombine only after the failure-mode branch beats the current pairwise downstream result.

## Bottom line

Fresh take:
- the fine-tuning is not mainly asking for “more training” now
- it is asking for better supervision structure

The most promising improvement path is:
- shorter prompts
- sharper evidence-to-label binding
- confusion-targeted contrast data
- delayed recombination into the full card

That is a better bet than another generic data rewrite, another full-card hinting pass, or another early model-size escalation.
