---
title: Bruxism CAP annotation alignment audit 2026-05-03
created: 2026-05-03
updated: 2026-05-03
type: query
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - raw/articles/cap-sleep-database-physionet-2012.md
  - raw/articles/bruxism-single-channel-eeg-2024.md
---

# Bruxism CAP annotation alignment audit 2026-05-03

Question: after the first `SLEEP-S2` stage-aware rerun (`pass4`) made honest LOSO performance worse, was the result purely physiological difficulty, or were some local EDF files and sidecar annotations only partially aligned?

Related pages: [[bruxism-cap]] [[bruxism-cap-first-baseline-lessons-2026-05-03]] [[bruxism-eeg-emg-starter-project-2026-05-03]]

## Short answer

The stage-aware rerun is still a useful negative result, but it is not just a story about physiology. A follow-up EDF-versus-sidecar audit shows that at least one intended subject (`n10`) is unusable for local `SLEEP-S2` extraction and one included subject (`brux1`) is only partially usable because many later scored `S2` rows extend beyond the local EDF duration.

## What was audited

For each subject in the intended subset (`brux1`, `brux2`, `n3`, `n5`, `n10`, `n11`), the audit compared:
- EDF sampling rate and total duration
- sidecar `SLEEP-S2` row count
- how many `30` second `S2` windows actually fall inside the available EDF

The audit artifact is saved in:
- `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md`

## Main findings

### 1. `n10` is unusable for local `SLEEP-S2` reruns
- local `n10.edf` duration: about `3783` seconds (`63.05` minutes)
- earliest scored `SLEEP-S2` sidecar event: about `5550` seconds after record start
- in-range `30` second `S2` windows: `0`

Interpretation: for the current local files, `n10` cannot contribute any `SLEEP-S2` windows. That looks like truncation or a mismatched/incomplete local EDF rather than a normal bounded-experiment exclusion.

### 2. `brux1` is only partially usable
- local `brux1.edf` duration: about `14341` seconds (`239.02` minutes)
- total scored `SLEEP-S2` rows in sidecar: `482`
- in-range `30` second `S2` windows: `144`
- out-of-range `S2` rows: `338`

Interpretation: `brux1` still has enough early `S2` windows for bounded stage-aware extraction, but the local sidecar continues far beyond the usable EDF segment. So `brux1` can stay in the subset only with explicit in-range filtering and a documented caveat.

### 3. The other stage-aware subjects look clean for this bounded use
- `brux2`, `n3`, `n5`, and `n11` all have fully in-range `SLEEP-S2` coverage for the current audit rule.

## Why this matters for interpreting pass4

This audit sharpens the meaning of the pass4 negative result:
- it is still true that simple `SLEEP-S2` matching did not fix the leakage gap
- it is also true that the local data-validity surface is uneven across subjects
- therefore future stage-aware reruns should be compared against pass4 as stricter, better-audited subsets, not as naive extensions of pass2/pass3

## Best next step

1. keep the annotation-aware extraction path in `src/prepare_windows.py`
2. preserve `n10` as excluded from local `SLEEP-S2` reruns unless a fuller matching EDF is found
3. keep `brux1` only with explicit in-range filtering
4. rebuild future stage-aware CSVs only from subjects whose chosen events are confirmed in-range
5. rerun the same baseline code before changing model family or adding modality fusion

## Practical lesson

For small public biosignal baselines, annotation-aware reruns are not automatically more trustworthy just because they use scored events. First verify that the scored events actually land inside the local signal files. In this project, the alignment audit became part of the measurement pipeline itself.
