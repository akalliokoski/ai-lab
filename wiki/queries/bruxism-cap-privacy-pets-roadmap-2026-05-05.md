---
title: Bruxism CAP Privacy PETs Roadmap
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, workflow, infrastructure, notes, experiment]
sources:
  - raw/transcripts/bruxism-pets-openmined-report-2026-05-05.md
---

# Bruxism CAP Privacy PETs Roadmap

This report is best treated as a future-branch roadmap for `bruxism-cap`, not as an immediate replacement for the current leakage-aware CAP benchmark loop. The current project still needs a stronger honest EMG benchmark anchor first. But the report is important because it defines a credible next research surface once the benchmark is stable: privacy-preserving learning, storage, and cohort analysis for wearable jaw EMG. This should be treated as a differentiating direction for the project, not as optional polish or a generic afterthought. [[bruxism-cap]] [[bruxism-cap-translational-framing-check-2026-05-05]]

## Best Hermes-native home for this material

The clean split is:
- Wiki: durable research understanding, architecture sketches, threat models, regulatory notes, and candidate future branches.
- Kanban: only bounded executable tasks with a clear output, owner, and dependency graph.
- Cron/autoresearch: periodic re-checks or bounded literature maintenance once a concrete question already exists.

So this report belongs in the wiki first. It is too strategic and too branchy to live only as kanban tasks, and too important to remain only in chat.

## Practical intake rule

Use a three-stage promotion path:
1. Report or literature synthesis enters the wiki as a durable query/concept page.
2. Candidate task ideas are listed on the wiki page as possible future branches.
3. Only the next bounded question gets promoted to kanban when it becomes concrete enough to execute.

That keeps the board focused on action while the wiki stays the long-term memory for why the branch exists.

## What should go to kanban later

Promote only tasks that satisfy all of these:
- one primary output
- small enough to finish in one bounded worker pass or one short dependency chain
- directly tied to the repo or to a saved report/memo
- no unresolved ambiguity about whether the goal is research, implementation, or preservation

Good future kanban prefixes for this branch would be:
- `privacy:` threat model / leakage audit / DPIA memo work
- `literature:` PET/OpenMined/FL/DP scan updates
- `prototype:` local simulations on CAP-derived features
- `preserve:` wiki/report updates after a privacy branch result

## Candidate future tasks from this report

These belong in the wiki now and can later be promoted individually to kanban.

### 1. Privacy threat-model memo for the current CAP repo
Question: if the current repo ever moved from public CAP benchmark work toward user or wearable EMG, what exact sensitive surfaces would appear first?
Output shape: one memo covering waveform leakage, biometric re-identification, health-state inference, metadata leakage, and what should never leave device/phone.
Why it matters: it translates the report into repo-specific design constraints rather than generic privacy talk.

### 2. PySyft/OpenMined feasibility note for this project shape
Question: which parts of the current report still map cleanly onto the modern PySyft 0.9 Datasite model, and which parts would need other tools or custom glue?
Output shape: one compatibility memo with a minimal prototype plan and explicit caveats about API churn and on-device realities.
Why it matters: it prevents overcommitting to an outdated OpenMined mental model.

### 3. CAP-to-wearable transition architecture sketch
Question: how would the current offline CAP benchmark evolve into a JawSense-like future stack without breaking the current reproducible benchmark discipline?
Output shape: one architecture note separating benchmark loop, phone-side feature extraction, federated rounds, secure aggregation, and clinician/research access.
Why it matters: it connects today's repo to a realistic future product/research direction. [[bruxism-better-project-and-data-options-2026-05-04]]

### 4. Minimal privacy-preserving prototype on derived features
Question: can a tiny local experiment simulate one PET layer on the existing project without pretending we already have a wearable fleet?
Output shape: one bounded prototype, for example DP noise on cohort summaries or a toy federated split on derived CAP features.
Why it matters: it creates a learning-by-doing bridge between the current benchmark and the future privacy branch.

### 5. Regulatory/DPIA prep memo
Question: what would a first-pass GDPR Article 9 / DPIA-style checklist look like for a Jaw EMG project, even before any product work?
Output shape: one structured memo listing data classes, processing purposes, storage boundaries, legal bases, and controls.
Why it matters: for jaw EMG, privacy is not just an ML add-on; it is part of system design.

## What should not go to kanban yet

Do not create board tasks yet for:
- broad "implement federated learning for bruxism"
- vague "use OpenMined with JawSense"
- heavy crypto integration without a narrow benchmark or prototype goal
- product/regulatory work that is still detached from the repo's immediate benchmark questions

Those are roadmap themes, not bounded tasks.

## Recommended board strategy

Near term:
- keep the active `bruxism-cap` board focused on the current honest EMG benchmark loop.
- preserve the PET/privacy direction as an explicit high-priority future branch in the wiki, not as a vague someday idea.
- add privacy/PET items only when they directly support a concrete research memo or prototype.

Activation rule:
- as soon as the current benchmark reaches a good-enough state for handoff or temporary stabilization, promote the first `privacy:` task immediately instead of letting the branch drift.

If this branch becomes active later, use one of two Hermes-native patterns:
1. Same board, low-priority task family with `privacy:` / `prototype:` prefixes if the work remains tightly coupled to `bruxism-cap`.
2. Separate board such as `bruxism-pets` if the privacy branch becomes its own campaign with literature, prototyping, policy, and architecture substreams.

My default recommendation is: wiki first, then same board only for one bounded privacy task at a time, and only create a separate board if the PET branch becomes a real subproject.
## Best first bounded task when this branch activates

The cleanest first promotion to kanban would be:
- `privacy: write a repo-specific threat model and transition memo for moving from CAP benchmark work toward wearable jaw-EMG learning without raw waveform export`

Why this first:
- it is concrete
- it is non-mutating and safe
- it preserves the report into project-specific constraints
- it gives later prototype tasks a sharper scope

## Current recommendation

Preserve this report in the wiki now. Keep the active kanban campaign centered on the current EMG benchmark. Promote only one privacy/PET task at a time once the benchmark loop is ready for a future branch. [[bruxism-cap-emg-within-record-normalization-ideas-2026-05-05]] [[bruxism-better-project-and-data-options-2026-05-04]]
