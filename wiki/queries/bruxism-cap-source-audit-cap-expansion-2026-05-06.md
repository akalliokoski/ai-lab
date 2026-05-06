---
title: Bruxism CAP source audit CAP expansion
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, experiment, evaluation, notes]
sources:
  - raw/articles/cap-sleep-database-physionet-2012.md
  - raw/articles/bruxism-single-channel-eeg-2024.md
---

# Bruxism CAP source audit CAP expansion

Question: does the public CAP Sleep Database contain any honest bruxism-positive expansion beyond `brux1` and `brux2` for `bruxism-cap`?

## Short answer
No meaningful positive expansion is visible in the public CAP release. The PhysioNet CAP description says the pathological recordings include only `2` affected by bruxism, and the public `RECORDS` file exposes only `brux1.edf` and `brux2.edf` under the `brux*` prefix. That means the repo can still expand controls, channels, and within-record slicing, but not the count of honest bruxism-positive subjects. [[bruxism-cap]] [[bruxism-cap-annotation-alignment-audit-2026-05-03]]

## Exact evidence
- The CAP dataset description lists `16` healthy subjects and `92` pathological recordings, including only `2` by bruxism.
- A fresh `RECORDS` audit yields `108` public filenames with prefix counts `brux=2`, `ins=9`, `n=16`, `narco=5`, `nfle=40`, `plm=10`, `rbd=22`, and `sdb=4`.
- The only public `brux*` filenames are `brux1.edf` and `brux2.edf`.
- The 2024 single-channel EEG paper preserved in the wiki also reports using only `2` bruxism patients and `4` healthy controls with compatible channels for its chosen analysis.

Together, those sources make the positive-label ceiling look hard rather than accidental. [[bruxism-cap]]

## What still can expand honestly
### 1. More controls
Possible, but only as negative-control or specificity analysis. This does not enlarge the bruxism-positive class.

### 2. Alternate channels
The current local subset already exposes both `C4-P4` and `EMG1-EMG2` on `brux1`, `brux2`, `n3`, `n5`, `n10`, and `n11`. Channel changes can improve measurement and comparison, but they do not add positive subjects. [[bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05]]

### 3. Alternate stage or CAP-event slices
Also possible, but only as auxiliary analysis. Repo evidence already shows that `S2`, `A1-only`, and `A3-only` filters change per-subject window availability and event semantics, so they are controlled slices rather than new labels. [[bruxism-cap-rule-survival-audit-2026-05-04]] [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]]

## What does not count as honest expansion
- treating other CAP diagnoses as bruxism positives
- using CAP `A1/A2/A3` overlap as proxy bruxism labeling
- using EMG burst or RMMA-like features to relabel unlabeled subjects as positives
- splitting the same two bruxism subjects into pseudo-subjects by window clusters, stages, or channels

All of those would expand rows or views, not independent public bruxism labels. [[bruxism-cap]]

## Hard limit
The main blocker is labels, not channels. Public CAP only gives this repo `2` bruxism-labeled subjects. Annotation issues then tighten the usable surface further: `brux1` is only partially usable for local `SLEEP-S2`, and `n10` is unusable for local `SLEEP-S2`, but those are secondary constraints on top of the already tiny positive class. [[bruxism-cap-annotation-alignment-audit-2026-05-03]]

## Best bounded next step
If the project stays inside CAP, the cleanest honest follow-up is to formalize the ceiling in repo docs and, if desired, run only a control-side expansion audit that keeps `brux1` and `brux2` fixed as the entire positive class. [[bruxism-cap]]

## Artifact
Detailed repo memo: `projects/bruxism-cap/reports/cap-bruxism-source-audit-2026-05-06.md`