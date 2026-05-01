# Fine-tuning runs with no clear improvement: fresh root-cause review

Date: 2026-04-29

## Question

Why are the recent tutor-adapter fine-tuning runs not showing reliable qualitative improvement, even though the infrastructure is working and the dataset has been iterated several times?

## Evidence reviewed

Local project evidence:
- `modal/train_unsloth_tutor.py`
- `data/hermes-tutor-v1/train.jsonl`
- `data/hermes-tutor-v1/eval.jsonl`
- local copies of `run_summary.json` for runs:
  - `20260429T103541Z`
  - `20260429T105620Z`
  - `20260429T110801Z`
  - `20260429T112202Z`
  - `20260429T172803Z`
- `docs/first-unsloth-experiment.md`

External references checked during this review:
- Hugging Face TRL `SFTTrainer` docs: conversational SFT should use `assistant_only_loss=True` when the goal is to train only assistant responses; prompt-completion format defaults to completion-only loss.
- LIMA paper (`arXiv:2305.11206`): most knowledge is learned in pretraining, and a relatively small amount of instruction tuning data is mainly used to teach response behavior and format.
- QLoRA paper (`arXiv:2305.14314`): small high-quality datasets can work well, but benchmarking and evaluation quality are major concerns.
- LoRA paper (`arXiv:2106.09685`): LoRA is an efficient adaptation method, but it does not change the basic requirement for a clean task definition and good supervision.

## Bottom line

The main problem does not look like Modal, Unsloth, persistence, or package compatibility anymore.

The strongest current explanation is a three-part mismatch:
1. the training objective is probably diluting the learning signal,
2. the dataset is trying to do too many jobs with too few examples,
3. the base model is weak enough that the tiny adapter mostly perturbs wording instead of cleanly improving behavior.

## Ranked root-cause assessment

### 1. The script is likely training on the full rendered conversation, not just the assistant answer

Why this matters:
- The training script converts every row into a 3-turn conversation with a repeated system prompt and a user instruction.
- The script does not set `assistant_only_loss=True` in `SFTConfig`.
- TRL docs explicitly recommend `assistant_only_loss=True` for conversational datasets when only assistant responses should contribute to loss.

Why this is probably hurting this project:
- The system prompt is repeated in every row.
- The user prompt is also part of the supervised text.
- A rough word-count check on the current 40-row train set shows that about 50% of the rendered sequence is non-answer text:
  - system prompt: about 18 words
  - average user text: about 12.2 words
  - average assistant text: about 30.1 words
  - approximate prompt fraction if full-sequence loss is used: 0.501

Interpretation:
- On a tiny dataset, spending roughly half of the loss budget on reproducing prompt text is expensive.
- That reduces pressure on the model to learn the exact answer content you actually care about.
- This is especially damaging when your eval is checking for crisp answer facts and short canonical wording.

### 2. The dataset is over-scoped for its size

Current dataset size:
- 40 train rows
- 10 eval rows

But the train set is trying to teach multiple different things at once:
- generic ML definitions (`LoRA`, `QLoRA`, `quantization`, `checkpoint`, `SFT`)
- workflow advice (`run logs`, `Modal`, `VPS vs MacBook vs remote GPU`)
- style behavior (brief, beginner-friendly, step-by-step answers)
- repo-specific heuristics (`smallest useful outcome`, `workflow validated`, `held-out prompts`, `artifact review`)

For the three weak eval concepts, the anchor coverage is still very small:
- instruct-model concept: about 5 relevant train rows
- smallest-useful-outcome concept: about 4 relevant train rows
- eval-contamination concept: about 3 relevant train rows

Interpretation:
- The dataset is not really 40 examples per task.
- It is more like a handful of examples per micro-concept.
- That makes it easy for the model to drift toward generic paraphrase, vague summary language, or phrase-copy artifacts instead of learning one stable answer pattern.

### 3. The project may be asking fine-tuning to teach the wrong thing

The current training data is heavy on explanations of concepts that the base model should already broadly know:
- LoRA
- QLoRA
- quantization
- eval sets
- overfitting
- chat templates

The LIMA result is relevant here: most knowledge is learned during pretraining, and small instruction tuning sets mainly teach response style, task framing, and output behavior.

Interpretation:
- If the real goal is "be a concise beginner tutor for this repo's workflow," then the fine-tune should mostly teach:
  - answer shape,
  - what details to include,
  - what details to avoid,
  - how repo-specific workflows are described.
- Right now, a lot of rows are spent re-explaining general ML concepts instead of tightly steering output behavior.

Likely consequence:
- The adapter is not getting a clean signal about the true job.
- It alternates between generic concept tutoring and repo-specific workflow heuristics.
- That is exactly the kind of setting where tiny LoRA runs produce wording drift instead of robust improvement.

### 4. The chosen base model looks weak for the precision you want

The current default model is:
- `unsloth/Llama-3.2-1B-Instruct-bnb-4bit`

Evidence from saved evals:
- base outputs are often long, generic, and rambling
- tuned outputs sometimes get shorter, but they frequently lose the key causal idea or substitute incorrect filler

Examples from the latest saved run `20260429T172803Z`:
- instruct-model answer drifted to memory-efficiency and "supervised models" instead of the key point that instruct models already know instruction-following
- smallest-useful-outcome answer stayed generic and omitted required workflow pieces
- eval-contamination answer introduced unrelated drift such as adapters or target language

Interpretation:
- The adapter is trying to steer a low-capacity model into very specific tutor phrasing with only a few relevant examples.
- A stronger instruct baseline would give the adapter better raw material to steer.
- Right now, some failures may simply be base-model weakness showing through.

This is not yet fully proven, but it is a serious hypothesis supported by the poor base responses already saved in `run_summary.json`.

### 5. The run is probably too long for a 40-row dataset

Current training shape in `modal/train_unsloth_tutor.py`:
- `per_device_train_batch_size=2`
- `gradient_accumulation_steps=4`
- effective batch size: 8
- 40 training rows
- about 5 optimizer steps per epoch
- `max_steps=60`
- about 12 epochs

Interpretation:
- 12 epochs is a lot for a tiny hand-authored dataset with repeated concepts and repeated system prompt text.
- That does not guarantee clean learning; it can amplify whichever supervision is sharpest or most repeated.
- The observed artifacts match this failure mode: phrase distortion, vague restatement, partial template copying, and concept drift rather than stable improvement.

### 6. The evaluation loop is too weak to guide small improvements reliably

What the current pipeline saves well:
- train loss
- 3 base-vs-tuned sample eval comparisons
- adapter artifacts

What it does not currently provide:
- scoring across all 10 eval rows
- a structured rubric for factual coverage
- a concise-style metric
- a clean judge for "did it include the key causal point?"
- any eval during training

Interpretation:
- The experiment is being steered by a very small qualitative sample.
- That was enough to prove infrastructure and catch gross regressions.
- It is not strong enough to distinguish tiny real gains from noise, prompt sensitivity, or wording drift.

## What is probably not the root cause anymore

These now look secondary or already resolved:
- stale remote imports
- Modal auth
- missing persistence
- xFormers mismatch
- HF auth
- dataset file loading or chat-template formatting bugs at the gross pipeline level

The runs are too consistent for infra flakiness to remain the main explanation.

## Fresh interpretation of the repeated failures

The failures are consistent with this sequence:
1. The base 1B instruct model already has broad knowledge but weak precision and weak stylistic discipline.
2. The dataset mixes general concept teaching with repo-specific workflow heuristics.
3. The trainer likely optimizes the whole conversation, so too much gradient goes into repeated prompt text instead of assistant answers.
4. The run lasts long enough to amplify fuzzy or overlapping answer patterns.
5. Because only a few examples teach each weak concept, the model learns fragments of the target wording rather than the full causal idea.
6. Evaluation only inspects a tiny sample, so the loop keeps reacting to noisy local improvements instead of a stable signal.

## Most likely root causes, in one sentence each

1. Loss is aimed too broadly: the model is probably learning prompt reconstruction as much as answer behavior.
2. The dataset is too small for how many concepts and behaviors it is trying to teach.
3. The data teaches knowledge, style, and workflow at once instead of one clear adaptation target.
4. The 1B instruct base is likely too weak for this level of precise answer steering with only a tiny LoRA dataset.
5. The run length is high enough to magnify phrase drift on a tiny hand-authored dataset.
6. The eval loop is too weak to cleanly identify small real gains.

## Recommended next experiments, in order

### Experiment 1: fix the loss target before touching the dataset again

Change:
- use assistant-only loss for conversational SFT
- or convert to a prompt-completion dataset and train completion-only explicitly

Why first:
- This is the cleanest implementation-level issue in the current script.
- It may immediately improve answer sharpness without changing the data at all.

Success criterion:
- same dataset, shorter run, better factual precision on all tracked eval prompts

### Experiment 2: narrow the dataset to one actual job

Recommended choice:
- make the adapter teach concise beginner tutoring plus repo-specific workflow framing
- do not spend many rows re-teaching generic ML definitions the base model already knows

Concrete move:
- split the current data conceptually into:
  - general ML definitions
  - repo/workflow tutoring behavior
- train only on the second slice first

Why:
- this tests whether the adapter is really needed for behavior steering rather than knowledge injection

### Experiment 3: shorten the run sharply

Change:
- reduce from about 12 epochs to something closer to 2 to 4 epochs for the next comparison
- keep the seed fixed

Why:
- on tiny datasets, shorter runs often reveal whether the supervision is clean before phrase drift takes over

### Experiment 4: compare against a stronger instruct baseline

Suggested hypothesis test:
- keep the same narrow dataset and training recipe
- compare the current 1B base against one stronger instruct base

Examples to consider:
- a stronger Llama 3.2 instruct variant
- a stronger Qwen instruct variant in a similar cheap-to-run size band

Why:
- if the stronger base improves even before tuning, then part of the current ceiling is simply model choice

### Experiment 5: strengthen evaluation before more dataset surgery

Minimum improvement:
- evaluate all 10 held-out rows every run
- save base and tuned responses for all 10
- score each row on:
  - key fact present
  - key wrong fact absent
  - answer length acceptable
  - style acceptable

Why:
- this will make it much easier to tell whether a change really helped or just helped one favorite prompt

## Immediate code-level changes worth trying

In `modal/train_unsloth_tutor.py`:
- add assistant-only loss if keeping the conversational format
- add a full-eval artifact, not just the first 3 sample eval rows
- reduce `max_steps`
- keep the generation settings deterministic for comparisons

## Recommended decision rule

Before doing more wording rewrites, first test whether implementation and objective are the bottleneck.

Priority order:
1. fix loss masking
2. shorten the run
3. narrow the task scope
4. only then rewrite or expand the dataset again
5. if quality is still capped, test a stronger base model

## Final judgment

The most likely actual root cause is not "the dataset still needs a few better rows."

It is that the current experiment couples too many small weaknesses at once:
- full-conversation supervision,
- tiny multi-objective data,
- a weak 1B instruct base,
- long training for the dataset size,
- and a thin evaluation loop.

That combination is exactly what produces the pattern seen in the artifacts: small local shifts, no stable concept win, phrase distortion, and repeated failure to reliably improve the same weak answers.
