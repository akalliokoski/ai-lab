---
title: Bruxism CAP LLM and RL Roadmap
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, workflow, infrastructure, notes, experiment]
sources:
  - raw/transcripts/bruxism-llm-rl-pets-report-2026-05-05.md
---

# Bruxism CAP LLM and RL Roadmap

This report should be treated as a second future-branch roadmap for `bruxism-cap`, parallel to the privacy/PET roadmap rather than separate from it. The current project still needs a stronger honest EMG benchmark anchor first. After that, a distinctive next direction is not just privacy-preserving wearable EMG, but privacy-preserving adaptive intelligence for wearable jaw EMG: synthetic-data generation, time-series fine-tuning, and reinforcement-learning-guided biofeedback under strong safety and privacy constraints. [[bruxism-cap]] [[bruxism-cap-privacy-pets-roadmap-2026-05-05]]

## Best Hermes-native home for this material

The same split applies here:
- Wiki: durable research understanding, architecture sketches, future-branch design, and candidate task ideas.
- Kanban: only the next bounded memo, prototype, or implementation step once the branch is concrete.
- Cron/autoresearch: recurring literature maintenance only after the questions are already sharply scoped.

So this report also belongs in the wiki first. It is too broad to turn directly into multiple board tasks today, but too central to leave as chat-only context.

## Why this track matters

This is one of the clearest ways for the project to become more than a generic bruxism detector benchmark. The long-term differentiated shape is:
- privacy-preserving wearable EMG
- adaptive biofeedback / RL-controlled stimulation or cueing
- synthetic-data and time-series foundation-model support for low-data biosignal learning
- strong safety and regulatory framing from the beginning

In other words, the future story is not "just add an LLM" and not "just do RL". The stronger branch is a privacy-aware adaptive wearable-learning stack. [[bruxism-cap-translational-framing-check-2026-05-05]]

## Practical intake rule

Use the same three-stage promotion path:
1. Preserve the report as a wiki roadmap/query page.
2. List candidate future tasks on the wiki page.
3. Promote only the next bounded question to kanban once it has one primary output, a clear owner, and tight scope.

## What should go to kanban later

Promote only tasks that have:
- one primary output
- a bounded prototype or memo scope
- a direct connection to the repo or to a saved report
- a clear distinction between research, prototype, and preservation work

Good future prefixes for this branch would be:
- `llm:` foundation-model / fine-tuning / reward-modeling memos
- `rl:` bandit / policy / safety-shield / reward-design tasks
- `prototype:` tiny local simulations on CAP-derived features or synthetic data
- `preserve:` wiki/report updates after a branch result

## Candidate future tasks from this report

These belong in the wiki now and can later be promoted individually to kanban.

### 1. Repo-specific adaptive-biofeedback framing memo
Question: if `bruxism-cap` eventually grows from offline benchmark work into a JawSense-like wearable program, what is the smallest credible RL problem formulation?
Output shape: one memo defining state, action, reward, safety shield, and what should remain hard-coded rather than learned.
Why it matters: it turns a broad RL idea into a concrete, auditable control problem.

### 2. Synthetic EMG feasibility memo
Question: which synthetic-data path best matches this repo first: Chronos/Lag-Llama style fine-tuning, ChatEMG-like autoregressive modeling, or a smaller DP-aware GAN baseline?
Output shape: one comparison memo with recommended first prototype and evaluation criteria.
Why it matters: it keeps the branch grounded in a realistic first experiment instead of jumping straight to a giant foundation-model plan.

### 3. CAP-derived toy prototype for privacy-preserving synthetic-data learning
Question: can the current CAP-derived feature tables support a tiny learning-by-doing prototype that simulates one part of the future synthetic-data branch?
Output shape: one small prototype, for example a toy generative augmentation check or a privacy-audited summary-generation pipeline on derived features rather than raw wearable data.
Why it matters: it creates continuity from the current repo into the future LLM/synthetic-data branch.

### 4. Contextual-bandit design note for vibration-only cueing
Question: what would the safest v1 adaptive policy look like if the future wearable branch started with low-risk vibration cues rather than CES?
Output shape: one design memo covering state/context, action set, reward proxies, safety constraints, and offline evaluation needs.
Why it matters: it identifies a safer first RL surface before stimulation-heavy ideas.

### 5. LLM-as-explainer and preference-capture memo
Question: where can LLMs help without being inline controllers?
Output shape: one memo on reward shaping, clinician/patient preference capture, explanation, and anomaly summarization, with explicit "not for real-time control" boundaries.
Why it matters: it channels LLM use toward high-leverage supporting roles instead of vague hype.

## What should not go to kanban yet

Do not create board tasks yet for:
- broad "build RL for bruxism treatment"
- vague "fine-tune an LLM on bruxism data"
- real-time controller claims detached from safety and regulation
- synthetic-data releases without privacy-audit plans
- inline LLM control loops for stimulation decisions

Those are roadmap themes, not bounded tasks.

## Recommended board strategy

Near term:
- keep the active `bruxism-cap` board focused on the current honest EMG benchmark loop.
- preserve this LLM/RL direction as an explicit high-priority future branch in the wiki.
- treat it as coupled to the privacy/PET branch, not as a separate hype track.

Activation rule:
- as soon as the current benchmark reaches a good-enough state for handoff or temporary stabilization, promote one bounded `llm:` or `rl:` task promptly instead of letting this branch remain aspirational.

Board shape later:
1. Use the same `bruxism-cap` board with low-priority `llm:` / `rl:` / `prototype:` tasks while the work is still tightly coupled to the benchmark.
2. Split into a dedicated board such as `bruxism-adaptive` only if this becomes a real subproject with multi-step prototyping, policy design, and synthetic-data workstreams.

My default recommendation is: wiki first, then same board only for one bounded LLM/RL task at a time until the branch proves it deserves its own campaign.

## Best first bounded task when this branch activates

The cleanest first promotion to kanban would be:
- `rl: write a repo-specific adaptive-biofeedback problem formulation and safety-shield memo for a future JawSense-style branch`

Close second:
- `llm: compare the smallest credible synthetic-EMG prototype paths for this repo (Lag-Llama/Chronos-style fine-tuning vs DP-GAN-style baseline)`

Why this ordering:
- the RL memo sharpens the control problem before implementation fantasies
- the synthetic-data comparison memo creates a realistic bridge into fine-tuning work
- both are non-mutating and safe first steps

## Current recommendation

Preserve this report in the wiki now. Keep the current board centered on the honest EMG benchmark loop. Treat LLM/fine-tuning/RL as a standout next branch that should be activated soon after benchmark stabilization, but only via one bounded memo or prototype task at a time. [[bruxism-cap-emg-within-record-normalization-ideas-2026-05-05]] [[bruxism-cap-privacy-pets-roadmap-2026-05-05]]
