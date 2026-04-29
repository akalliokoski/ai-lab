# Unsloth Self-Learning Path

Date: 2026-04-28
Primary source: https://unsloth.ai/docs

## Why this path

The goal is to learn Unsloth by doing, in increasing layers of complexity:
1. understand the moving parts
2. run a tiny local or notebook example
3. prepare your own small dataset
4. fine-tune a small model with LoRA/QLoRA
5. evaluate results
6. move the workflow to remote GPU infrastructure when needed

## What the docs say at a high level

From the current docs snapshot:
- Unsloth is for running and training models locally and supports many model families.
- The docs push beginners first toward the beginner path, requirements, and notebooks.
- Unsloth emphasizes efficient LoRA/QLoRA-style tuning and broader RL/training support.
- Install entrypoint on macOS/Linux is `curl -fsSL https://unsloth.ai/install.sh | sh`.
- There are dedicated docs for requirements, beginner guidance, notebooks, and model-specific pages such as Gemma.

## Start here today

Based on the current docs snapshot, the best beginner entry sequence is:
1. `get-started/fine-tuning-llms-guide`
2. `get-started/fine-tuning-llms-guide/what-model-should-i-use`
3. `get-started/fine-tuning-llms-guide/datasets-guide`
4. `get-started/beginner-start-here/unsloth-requirements`
5. `get-started/unsloth-notebooks`
6. `basics/running-and-saving-models`

Why this order:
- the docs themselves point beginners first to the fine-tuning guide, requirements, and notebooks
- the model-choice page gives simple rules for base vs instruct
- the dataset guide answers the usual “how much data do I need?” question early
- the requirements page prevents picking a path your hardware cannot run
- the saving/running page closes the loop so you actually use the result

## Current environment fit

Checked on 2026-04-28 from the VPS:
- this machine has no NVIDIA GPU
- `MODAL_TOKEN_ID` and `MODAL_TOKEN_SECRET` are set
- `HF_TOKEN` is currently missing in the environment check

Practical implication:
- use the VPS for reading docs, data prep, notes, and orchestration
- use the MacBook for lightweight local notebook experiments
- use Modal for the first real GPU-backed Unsloth training run

## Recommended learning sequence

### Stage 0 — orientation
Read these first:
- docs landing page: `https://unsloth.ai/docs`
- beginner start page
- requirements page
- notebooks catalog
- Gemma page if you want a familiar model family first

Deliverable:
- add one note to the wiki summarizing which exact model family you want to start with

### Stage 1 — vocabulary and constraints
Learn these terms well enough to explain them simply:
- base model
- instruct model
- tokenizer
- dataset formatting
- LoRA
- QLoRA
- quantization
- VRAM budget
- checkpoint / adapter
- eval set

Deliverable:
- create a short glossary page in the wiki

### Stage 2 — first tiny run
Goal:
- run the smallest realistic example possible

Suggested default:
- do not start with a large ambitious dataset
- start with a tiny instruction dataset and a small model/notebook example
- aim only to complete one end-to-end pass: load model, format data, train briefly, save adapter

Deliverable:
- a notebook or script under `notebooks/` or `scripts/`
- a one-page run log in the wiki

### Stage 3 — your own dataset
Goal:
- build a tiny dataset you actually care about

Good starter dataset types:
- question/answer pairs from your own notes
- domain-specific formatting tasks
- concise tutoring examples
- transformation tasks with clear before/after pairs

Avoid at first:
- giant scraped corpora
- mixed-quality examples
- unclear targets

Deliverable:
- a versioned dataset folder under `data/`
- a README describing source, purpose, and schema

### Stage 4 — first real LoRA/QLoRA experiment
Start with one controlled experiment:
- one model
- one dataset
- one prompt style
- one eval set

Track:
- what changed
- what stayed fixed
- training time
- hardware used
- whether outputs actually improved

Deliverable:
- an experiment note with exact commands and outputs

### Stage 5 — evaluation habit
Before scaling up, learn to compare:
- base model vs tuned adapter
- good examples vs failure cases
- cheap eval checks vs subjective impressions

Deliverable:
- a simple evaluation rubric in the wiki

### Stage 6 — move to Modal when needed
Once the local path is clear, move the same experiment to Modal:
- package the code as a small Python-first job
- pin dependencies
- use env-based auth
- record cost and runtime

Deliverable:
- a reproducible Modal training entrypoint in `modal/`

## Recommended first project

Start with: “Hermes AI lab tutor adapter”

Idea:
- create a small dataset that teaches a model to explain ML concepts clearly, briefly, and step-by-step
- tune only enough to observe behavior changes
- evaluate on 20-30 held-out prompts

Why this is good:
- the data is easy to author
- quality is easy to inspect manually
- it fits the learning-by-doing goal

## First week plan

Day 1
- read docs + requirements
- choose first model family
- write wiki note: goals, hardware assumptions, first hypothesis

Day 2
- install core tooling
- verify Hugging Face and Modal auth paths
- inspect one official notebook

Day 3
- build a tiny dataset (20-50 examples)
- define eval prompts

Day 4
- run a tiny training pass
- save adapter
- write failure notes

Day 5
- compare base vs tuned outputs
- decide whether to improve data, prompts, or training config

Day 6-7
- package the same workflow more cleanly
- decide whether the next run belongs on Mac or Modal GPU

## Decision rules

Use Mac first when:
- you are reading, prototyping, or running tiny experiments
- you want fast iteration with notebooks

Use VPS first when:
- you are orchestrating, documenting, or automating
- you want Hermes/Telegram access and long-lived coordination

Use Modal first when:
- the experiment needs real GPU horsepower
- you want reproducible serverless training runs
- local hardware becomes the bottleneck
