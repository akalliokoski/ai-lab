---
title: Bruxism CAP Next Data Strategy (2026-05-06)
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, dataset, evaluation, workflow, notes]
sources:
  - queries/bruxism-cap-source-audit-cap-expansion-2026-05-06.md
  - queries/bruxism-cap-dataset-decision-rubric-2026-05-06.md
  - queries/bruxism-scout-results-2026-05-06.md
---

# Bruxism CAP Next Data Strategy

## Question
After the CAP positive-set ceiling audit and the external dataset scout, what should the broader bruxism-detection project do next?

## Answer
Public CAP cannot honestly grow its bruxism-positive set beyond `brux1` and `brux2`.

That ceiling does not force an immediate dataset pivot. The best current move is one bounded CAP-adjacent expansion branch: keep `brux1` and `brux2` fixed as the full public positive set, then audit and add only extra healthy controls plus any verified channel/stage compatibility that strengthens specificity pressure without pretending the positive cohort is larger than it is. [[bruxism-cap-source-audit-cap-expansion-2026-05-06]] [[bruxism-cap-dataset-decision-rubric-2026-05-06]] [[bruxism-cap]]

## Why not pivot now?
No external candidate is both scientifically stronger enough and open/reproducible enough to replace CAP as the active public benchmark now.

Ranked external directions under the explicit rubric:
1. portable jaw-EMG / masseter-EMG branch (`72.6 / 100`) — strongest deferred scientific direction, but not open/runnable enough now
2. wireless/mmWave branch (`61.4 / 100`) — ecologically interesting, but still closed and less directly jaw-muscle aligned
3. earable branch (`52.4 / 100`) — attractive future modality, but too indirect and too closed right now
4. generic open sleep repositories with relabeling ambition (`45.0 / 100`) — open but weak on bruxism-label validity

CAP itself remains only `58.2 / 100`, but it keeps one decisive advantage over every active external contender: it is the only currently open, runnable, already-audited public benchmark surface in the repo. [[bruxism-scout-results-2026-05-06]] [[bruxism-cap-dataset-decision-rubric-2026-05-06]]

## Primary branch now
Open one bounded CAP-adjacent expansion branch.

Definition:
- keep the positive class fixed at `brux1` and `brux2`
- audit additional `n*` controls only
- verify `EMG1-EMG2`, `C4-P4`, and stage/annotation compatibility
- report the result as a control-side specificity stress test, not as a larger bruxism dataset

## Deferred backup branch
Deferred backup: one portable jaw-EMG dataset-acquisition/evidence-pack branch.

Activate it only if a candidate cohort proves:
- real access and licensing now
- direct jaw-muscle signal with documented label provenance
- subject-held-out evaluation support
- rubric score at least `80 / 100`
- at least `12` weighted points above CAP
- no worse honesty than CAP on subject-level evaluation

## Exact next operational task
Create one downstream task to audit additional CAP healthy controls for bounded control-side expansion. The task should verify channel availability, annotation compatibility, and manifest updates, then preserve a clear admissible/excluded subject report in repo and wiki. [[bruxism-cap]]

## Exact files to update next
Repo:
- `projects/bruxism-cap/README.md`
- `projects/bruxism-cap/data/README.md`
- `projects/bruxism-cap/data/subject_manifest.example.csv`
- `projects/bruxism-cap/reports/cap-control-side-expansion-audit-2026-05-06.md`

Wiki:
- `wiki/concepts/bruxism-cap.md`
- `wiki/queries/bruxism-cap-control-side-expansion-audit-2026-05-06.md`
- `wiki/index.md`
- `wiki/log.md`

## Bottom line
CAP is honestly capped on the positive side, but not yet exhausted as a bounded public benchmark. The next right move is control-side expansion inside CAP, while portable jaw-EMG stays the deferred non-CAP branch behind explicit evidence gates.
