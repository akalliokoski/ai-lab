# bruxism-cap

A completed public benchmark project for small, leakage-aware bruxism detection experiments on the PhysioNet CAP Sleep Database.

Status: closed after the final bounded pass on 2026-05-06.

This repo branch should be read as a reproducible benchmark history and methodology scaffold, not as a clinically meaningful detector.

Main closure artifact:
- `projects/bruxism-cap/reports/bruxism-cap-final-closure-report-2026-05-06.md`

## Final verdict

The current public CAP benchmark is complete.

The final matched repaired control-expanded replication (`pass48`) failed in a way that closes the branch rather than merely leaving it ambiguous:
- balanced accuracy: `0.400`
- sensitivity: `0.000`
- specificity: `0.800`
- both bruxism subjects were missed
- `n2` reopened the control surface as a false positive at `0.614`

The durable scientific read is:
- CAP was useful as a reproducible public pilot benchmark
- CAP exposed a large leakage gap between random-window CV and subject-aware LOSO
- CAP supported a repaired but still ambiguous `A3-only` line under first control expansion
- CAP did not support a stronger stable detector claim under matched cross-family control expansion

So the right next move is not more CAP micro-passes. The right next move is to preserve CAP as the completed public scaffold and shift future work toward the privacy-preserving wearable jaw-EMG branch.

## Project goal

The project goal was to build the smallest honest baseline that could:
- use a reproducible CAP subset
- keep the positive class fixed at `brux1` and `brux2`
- extract one primary jaw-muscle-aligned channel into fixed windows
- compute classical handcrafted features
- train simple models
- compare leakage-prone random-window validation against honest subject-held-out validation

This project was explicitly benchmark-first, not deployment-first.

## Important terms

### CAP
The PhysioNet CAP Sleep Database used as the public source dataset.

### `brux1`, `brux2`
The only public bruxism-positive subjects available to this project in CAP.

### `n1`, `n2`, `n3`, `n5`, `n11`
The bounded healthy control set eventually admitted under the repo’s annotation-aware and dual-channel-compatible contract.

### `EMG1-EMG2`
The primary benchmark channel and the main EMG-first line explored in the project.

### `C4-P4`
The comparison EEG channel used to test whether the same benchmark scaffold behaved differently on a different signal family.

### `SLEEP-S2`
Stage-2 sleep windows selected from the annotation sidecars.

### `MCAP-A1`, `MCAP-A3`
CAP micro-event family labels used as overlap filters for window selection. In this repo they are event-slice definitions, not bruxism labels.

### `A1-only`, `A3-only`
Exclusive event-family window-selection rules used in later passes.

### Random-window CV
A leakage-prone validation surface that splits windows without respecting subject identity. It remained in the repo only as a reference showing how flattering leakage can be.

### LOSO
Leave-one-subject-out cross-validation. This is the main honest evaluation surface because the held-out subject is excluded from training entirely.

### Record-relative
A within-record robust normalization used on a bounded feature subset. This was one of the key repaired-scaffold improvements in later passes.

### Shape features
The compact waveform-shape feature family added in pass35:
- `skewness`
- `kurtosis`
- `hjorth_mobility`
- `hjorth_complexity`

### Event trio
The retained three-feature event-conditioned subset validated in pass42:
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

### No-shape exclusions
Later repaired `A3-only` and final control-expanded lines excluded the four shape features above at train time.

### Percentile-band selector
The repaired time-aware selector that restricted windows to a per-subject relative-time band `q=[0.10, 0.90]` and then capped each subject to a fixed number of windows.

### Control-expanded
The final bounded `7`-subject stress-test setup:
- positives: `brux1`, `brux2`
- controls: `n1`, `n2`, `n3`, `n5`, `n11`

## Hard dataset ceiling

The positive set never expanded.

The source audit established:
- CAP public filenames: `108`
- public bruxism-positive files: only `brux1` and `brux2`

That means the honest public positive ceiling for this project was always exactly two subjects. Control-side expansion was possible. Positive-side expansion was not.

## Final benchmark anchors

| Pass | Subject set | Family | Channel | Balanced acc. | Sensitivity | Specificity | Margin | Read |
|---|---|---|---|---:|---:|---:|---:|---|
| `pass42` | `brux1, brux2, n3, n5, n11` | repaired `A1-only` | `EMG1-EMG2` | `0.750` | `0.500` | `1.000` | `+0.339` | strongest repaired `A1-only` anchor |
| `pass45` | `brux1, brux2, n3, n5, n11` | repaired `A3-only` no-shape | `EMG1-EMG2` | `0.750` | `0.500` | `1.000` | `+0.295` | strongest repaired `A3-only` anchor |
| `pass47` | `brux1, brux2, n1, n2, n3, n5, n11` | repaired `A3-only` no-shape | `EMG1-EMG2` | `0.750` | `0.500` | `1.000` | `+0.335` | ambiguity survived first control expansion |
| `pass48` | `brux1, brux2, n1, n2, n3, n5, n11` | repaired `A1-only` no-shape | `EMG1-EMG2` | `0.400` | `0.000` | `0.800` | `-0.302` | closure artifact |

## Final implementation preserved by pass48

The closure run held the following contract fixed:
- subjects: `brux1`, `brux2`, `n1`, `n2`, `n3`, `n5`, `n11`
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A1-only`
- selector: repaired percentile-band / time-aware `q=[0.10, 0.90]`, `cap=10`
- representation: repaired record-relative surface plus the fixed pass42 event trio
- train-time exclusions:
  - base exclusions: `^bp_`, `^rel_bp_`, `^ratio_`
  - no-shape exclusions: `skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`
- model/eval: `logreg` with subject-level `LOSO`

Exact pass48 construction facts:
- full exclusive `A1-only` candidate pool before selection: `466` rows
- final selected table: `70` rows
- exactly `10` windows per subject
- event-feature merge nulls: zero

Key pass48 artifacts:
- `projects/bruxism-cap/src/run_pass48_control_expanded_a1_replication.py`
- `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.md`
- `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.json`
- `projects/bruxism-cap/reports/loso-cv-pass48-emg-a1-control-expanded.json`
- `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.md`

## Recommended interpretation

Use this project as:
- a completed public benchmark history
- a reproducible leakage-aware biosignal baseline
- a methodology reference for future private or wearable jaw-EMG work

Do not use this project as evidence that CAP now supports a stronger stable bruxism detector.

## Read next

For the full project write-up, terminology, history, final implementation details, and closure rationale, read:
- `projects/bruxism-cap/reports/bruxism-cap-final-closure-report-2026-05-06.md`

For the exact closure query in the wiki, read:
- `wiki/queries/bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06.md`
