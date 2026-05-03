---
title: Karpathy LLM Wiki Pattern and Autoresearch Improvements
created: 2026-05-01
updated: 2026-05-01
type: query
tags: [research, workflow, notes, training, evaluation, agent]
sources: [raw/articles/karpathy-llm-wiki-2026-05-01.md, ../docs/autoresearch-karpathy-and-training-patch-2026-05-01.md]
---

## Question
How should the local `autoresearch` workflow and the artifact-card training loop be improved after re-reading Andrej Karpathy's original `LLM Wiki` pattern?

## Short answer
The main lesson is to optimize for persistent compiled knowledge, not just autonomous action. For `ai-lab`, that means every training pass should preserve three layers: immutable evidence, maintained research notes, and an explicit operating schema. [[artifact-card-sft]] [[artifact-driven-experiment-debugging]] [[ai-lab-learning-path]]

## What Karpathy's original note emphasizes
- keep a maintained wiki between raw sources and future questions
- treat the wiki as the compiled knowledge layer
- file valuable answers back into the wiki instead of letting them die in chat
- maintain index and chronology so future sessions can resume cheaply
- lint the knowledge base for stale claims, missing links, and contradictions

## Improvements made in this pass
1. `modal/train_unsloth_artifact_card.py` now aligns training with `generation_prefix` by stripping the prefix from assistant targets when the dataset pre-fills it at inference time.
2. The same training entrypoint now loads eval metadata and writes `task_aware_eval` directly into run summaries for forced-top-2 datasets.
3. The local `autoresearch` skill now states the Karpathy-style persistence rules explicitly: keep durable compiled artifacts, file useful answers back into docs/wiki, and maintain navigation plus linting discipline.

## Why this matters for the artifact-card project
The current bottleneck is not only model behavior. It is also how quickly the repo can notice, compare, and preserve branch-specific failures. The forced-top-2 family already showed that generic row-validity metrics can overstate progress while branch-aware legality still fails. The new built-in `task_aware_eval` reduces that gap. [[artifact-card-v2-vs-v3]] [[fine-tuning-improvement-strategies-2026-04-30]]

## Cron workflow lesson from the first live autoresearch runs
The first live cron rollout added an important operational lesson to the Karpathy pattern: a persistent compiled knowledge layer also needs a reliable execution loop. In this profile, `hermes cron status` alone was not sufficient evidence that scheduled jobs would actually fire. The practical fix was to keep a local ticker running with `scripts/cron_tick_loop.sh`, which repeatedly executes `hermes cron tick --accept-hooks` from the repo workdir. [[artifact-card-sft]] [[artifact-driven-experiment-debugging]]

The same repair surfaced a second lesson: real Modal commands launched from cron needed the repo `.env` exported in the launch shell (`set -a && source .env && set +a`), even though the local env-check script already reported the required variables as present. That means future autoresearch prompts should treat wiki updates as required bookkeeping and should verify execution with concrete evidence in this order: cron-created session files, live app/process state, and then surfaced artifacts. [[artifact-card-sft]]

This changes the expected documentation contract for unattended passes. The wiki is not only where training conclusions live; it is also where autoresearch operating rules, scheduler repairs, and negative results from autonomous runs should be preserved so later passes do not rediscover the same infrastructure failure.

## Files touched
- `modal/train_unsloth_artifact_card.py`
- `docs/autoresearch-karpathy-and-training-patch-2026-05-01.md`
- `~/.hermes/profiles/ai-lab/skills/research/autoresearch/SKILL.md`
- `raw/articles/karpathy-llm-wiki-2026-05-01.md`
- `scripts/cron_tick_loop.sh`
- `~/.hermes/profiles/ai-lab/cron/jobs.json`

## Related pages
- [[artifact-card-sft]]
- [[artifact-driven-experiment-debugging]]
- [[fine-tuning-improvement-strategies-2026-04-30]]
- [[ai-lab-learning-path]]
