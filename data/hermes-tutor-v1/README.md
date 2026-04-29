# hermes-tutor-v1

Seed dataset for the first Unsloth experiment in `ai-lab`.

Goal
- teach a small instruct model to explain ML and fine-tuning concepts clearly, briefly, and step-by-step
- create a dataset that is small enough to inspect manually
- preserve a clean split between training and evaluation prompts

Current shape
- train examples: 40
- eval examples: 10
- format: JSONL with `instruction`, `input`, `output`

Why this dataset exists
- it matches the recommended first project in `docs/unsloth-self-learning-path.md`
- it is easy to extend from personal notes and wiki pages
- it supports fast manual inspection before any GPU-backed run

Style target
- concise
- beginner-friendly
- technically correct
- step-by-step when useful

How to grow it next
1. Expand the train split toward 50+ examples only if quality stays high.
2. Keep the writing style consistent: concise, clear, beginner-friendly.
3. Add more held-out eval prompts that are not paraphrases of the train set.
4. Version changes in git and keep a short note on what changed.

Suggested next data sources
- wiki notes under `wiki/`
- distilled explanations written while reading Unsloth docs
- short before/after tutoring examples authored by hand
