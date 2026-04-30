# Better first fine-tuning use case recommendation

Date: 2026-04-30

## Question

What is a better first fine-tuning project for this repo than the current tiny repo-tutor adapter, given that repeated Unsloth + Modal runs have not produced reliable qualitative improvement?

## Short answer

Yes. The current tutoring project is a weak fit for a first tiny SFT project.

The best replacement is:
- `experiment-artifact to structured experiment card`

In plain language:
- feed the model a short run summary, a few eval comparisons, and a brief operator note
- train it to emit one strict JSON or markdown experiment card
- keep the task narrow: extract verdict, failure modes, next action, and evidence

This is a much better first project than “be a good repo tutor” because it is narrower, easier to score, and much more aligned with what small LoRA/QLoRA runs are actually good at.

## Why the current tutor topic is a poor first fit

The current project asks a tiny adapter to do too many things at once:
- explain general ML concepts
- teach repo-specific workflow heuristics
- stay concise and beginner-friendly
- express the right causal idea in held-out prompts
- generalize across wording variation

That is a broad knowledge-plus-behavior task.

The local run history now points in the same direction repeatedly:
- infra is working
- `assistant_only_loss=True` is working
- a narrower v2 dataset still did not produce reliable concept wins
- a stronger 3B base improved fluency more than correctness

That pattern suggests the first project is poorly scoped, not just poorly worded.

## What the external research suggests

The same lesson shows up in the references most relevant to small SFT:

1. LIMA (`https://arxiv.org/abs/2305.11206`)
- small, high-quality instruction tuning is strongest at steering response behavior and format
- it is not mainly a way to inject a large amount of new knowledge

2. LoRA (`https://arxiv.org/abs/2106.09685`)
- LoRA is an efficient adaptation method
- it does not remove the need for a sharply defined task

3. QLoRA (`https://arxiv.org/abs/2305.14314`)
- small efficient fine-tunes can work well
- but evaluation quality matters a lot, especially on narrow tasks

4. Practical fine-tuning guidance across HF/PEFT and OpenAI docs
- narrow format-control, extraction, transformation, and classification tasks are strong first projects
- broad “make the model know my repo/domain and teach it well” tasks are weak first projects for tiny datasets

## Selection criteria for a better first project

A better first project for this repo should have all of these:
- short outputs
- one stable output schema
- correctness that can be checked automatically or with a very small rubric
- hand-authorable examples in the 20 to 100 range
- real usefulness inside the repo, not a toy unrelated to the lab
- a clean fit with Modal artifact review and iteration notes

## Candidate use cases

### Option 1: experiment-artifact to structured experiment card

Task:
- input: a run summary, a few base-vs-tuned eval pairs, and a short operator note
- output: one strict JSON record or fixed markdown card

Example output fields:
- `run_id`
- `dataset_name`
- `model_name`
- `verdict` (`improved`, `same`, `regressed`, `inconclusive`)
- `primary_failure_modes`
- `key_evidence`
- `next_action`

Why it fits:
- highly structured output
- narrow task boundary
- directly useful for the repo's artifact-driven workflow
- uses the exact iteration-history habit the user wants to strengthen

How to evaluate:
- JSON validity
- exact match or field-level accuracy for core fields
- label accuracy for `verdict`
- overlap/F1 for `primary_failure_modes`
- required-evidence field present or absent

Main risk:
- if the inputs are too long or too noisy, the task becomes summarization-plus-judgment instead of extraction-plus-formatting

Verdict:
- best fit

### Option 2: eval-answer failure-mode classifier

Task:
- input: prompt, reference answer, base response, tuned response
- output: short structured labels such as `generic`, `wrong-causal-point`, `missed-required-detail`, `phrase-copy`, `hallucinated-detail`, `better-than-base`

Why it fits:
- short output space
- directly useful for artifact review
- easy to author with existing run summaries

How to evaluate:
- per-label precision/recall/F1
- exact set match for multi-label outputs

Main risk:
- label taxonomy must be very crisp or annotation consistency will collapse

Verdict:
- strong second choice

### Option 3: raw repo note to issue/experiment brief template

Task:
- input: messy notes about an experiment idea or failure
- output: fixed template with goal, setup, blocker, next test

Why it fits:
- style plus structure
- useful inside the lab
- outputs stay short and templated

How to evaluate:
- section presence
- length limits
- human preference check

Main risk:
- more subjective than pure extraction or classification

Verdict:
- decent, but weaker than Options 1 and 2

### Option 4: repo-specific tutor/explainer

Task:
- input: question about the workflow or fine-tuning concepts
- output: concise correct tutor answer

Why it seemed attractive:
- easy to imagine
- easy to author by hand
- feels aligned with the learning mission

Why it is a bad first project:
- broad task boundary
- knowledge-heavy
- hard to separate style errors from factual errors
- held-out evaluation is much noisier
- tiny datasets mostly perturb wording instead of reliably teaching the right concept

Verdict:
- poor first-project fit; better as a later project, likely retrieval-backed rather than tiny SFT-only

## Recommendation

Recommended new first project:
- `artifact-card-sft`

Recommended concrete framing:
- convert experiment evidence into a strict lab card
- keep the model's job to structure and label, not to invent knowledge
- treat this as a format-and-analysis adaptation task, not a tutoring task

Why this is the best fit for `ai-lab`
- it is tied to the repo's real workflow
- it reuses existing Modal artifacts immediately
- it reinforces disciplined iteration notes
- it is narrow enough that a small Unsloth run has a realistic chance to show a visible win
- it is easy to compare base vs tuned behavior with automatic checks

## Suggested dataset shape

Start smaller and sharper than the tutor project:
- 40 to 60 train examples
- 10 to 15 eval examples
- one fixed schema only
- one stable label taxonomy only

Suggested example sources:
- existing `run_summary.json` files under `tmp/modal-artifacts/`
- existing docs notes about runs and regressions
- hand-written synthetic variations derived from real runs, but not near-duplicates of eval inputs

## Suggested schema v1

```json
{
  "run_id": "string",
  "dataset_name": "string",
  "model_name": "string",
  "verdict": "improved | same | regressed | inconclusive",
  "primary_failure_modes": ["string"],
  "key_evidence": ["string"],
  "next_action": "string"
}
```

Keep v1 intentionally small.
Do not start with nested rubrics, free-form essays, or too many labels.

## Minimal success criterion

The smallest useful outcome should be:
- a tiny dataset
- one short Modal run
- a saved adapter
- automatic scoring on the full eval split
- a visible improvement in JSON validity and field accuracy versus the base model

That is a much cleaner first win than trying to prove the model became a better tutor.

## What not to do next

Do not immediately start another broad tutoring dataset.
Do not treat a lower train loss as success if the eval card fields are still wrong.
Do not mix multiple tasks like note cleanup, tutoring, classification, and schema extraction into one dataset.

## Recommended next action order

1. Freeze the tutor project as a useful negative result.
2. Define the exact `artifact-card-sft` schema and failure-mode labels.
3. Build 10 hand-written examples first and preview them locally.
4. Add an eval script before the training run so every field is scored automatically.
5. Run one short Unsloth/Modal diagnostic pass.
6. Review errors by field, not just overall loss.

## Bottom line

The better first fine-tuning topic is not another explanation-style adapter.

It is a narrow, structured, evaluation-friendly task built from the repo's real experiment workflow.

Best recommendation:
- `experiment-artifact to structured experiment card` as the new first serious Unsloth/Modal project for this repo.
