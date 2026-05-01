# hermes-tutor-v2

Narrower dataset for the next tutor-adapter experiment.

Goal
- teach one specific behavior: concise, concrete beginner tutoring for this repo's fine-tuning workflow
- stop spending scarce rows on broad ML term coverage that the base model should mostly already know
- make the next run easier to diagnose by reducing task sprawl

Shape
- train examples: 20
- eval examples: 10
- format: JSONL with `instruction`, `input`, `output`

What changed from v1
- removed most generic definition rows
- concentrated the dataset on workflow tutoring, evaluation discipline, artifact review, and crisp success criteria
- kept short direct outputs so regression is easier to spot
- made the dataset intentionally narrow rather than larger

Target answer style
- 1 short paragraph or 1–2 sentences
- concrete and technically correct
- explicit about workflow details when they matter
- no vague project-reflection filler

Main hypotheses behind v2
1. the adapter should mostly steer response behavior, not re-teach broad ML knowledge
2. a narrow tiny dataset should be easier for a small instruct model to learn cleanly
3. assistant-only loss plus this narrower data should make the next run more interpretable

Suggested next run
```bash
set -a && source .env && set +a && source .venv/bin/activate && modal run modal/train_unsloth_tutor.py --dataset-name hermes-tutor-v2 --max-steps 20
```

Post-run refinement status
- after reviewing run `20260430T061418Z`, the training rows were sharpened to restore clearer canonical wording for:
  - why instruct models help on tiny datasets
  - the minimum end-to-end success condition
  - why eval-prompt reuse breaks evaluation
  - Modal's exact job in the workflow
- the goal of this patch was to improve answer precision without broadening the dataset or reintroducing overlap-heavy train/eval phrasing

Preview locally
```bash
python3 scripts/preview_tutor_dataset.py hermes-tutor-v2
```
