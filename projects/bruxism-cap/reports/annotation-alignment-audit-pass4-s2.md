# Annotation alignment audit for pass4 SLEEP-S2 subset

Date: 2026-05-03
Scope: audit EDF duration versus RemLogic sidecar coverage for the bounded `SLEEP-S2` stage-aware rerun used in `window_features_pass4_s2.csv`.

## Why this audit exists

The first annotation-aware rerun (`pass4`) was scientifically worse than the earlier leak-fixed pass3 baseline. That can mean the task is genuinely harder under better window selection, but it can also mean the local EDF files and sidecar scoring exports do not line up cleanly for all subjects. This audit checks that before more modeling work.

## Audit rule

For each subject, count `SLEEP-S2` rows from the sidecar that satisfy all of:
- onset is on or after the record start
- event duration is at least `30` seconds
- `start_s + 30 <= EDF duration`

These are the windows that are actually eligible for the current `prepare_windows.py` stage-aware extraction path.

## Per-subject audit

| subject | sfreq_hz | EDF duration (min) | total S2 rows | in-range 30s S2 rows | out-of-range S2 rows | status |
|---|---:|---:|---:|---:|---:|---|
| brux1 | 512 | 239.02 | 482 | 144 | 338 | partial truncation / sidecar mismatch |
| brux2 | 256 | 522.02 | 298 | 298 | 0 | ok |
| n3 | 512 | 551.02 | 347 | 347 | 0 | ok |
| n5 | 512 | 524.02 | 413 | 413 | 0 | ok |
| n10 | 512 | 63.05 | 261 | 0 | 261 | truncated or mismatched |
| n11 | 512 | 527.00 | 266 | 266 | 0 | ok |

## Important timing details

- `brux1`
  - EDF duration: `14341` s (~`239.0` min)
  - earliest `SLEEP-S2` start: `2180` s
  - latest in-range `SLEEP-S2` start: `12680` s
  - latest scored `SLEEP-S2` start in the sidecar: `31970` s
  - interpretation: the sidecar contains many later `S2` rows that extend well beyond the locally available EDF, but there are still enough valid in-range windows for a bounded pass.

- `n10`
  - EDF duration: `3783` s (~`63.1` min)
  - earliest scored `SLEEP-S2` start in the sidecar: `5550` s
  - in-range `SLEEP-S2` windows: `0`
  - interpretation: for the current local files, `n10` cannot contribute any `SLEEP-S2` windows at all. This is consistent with truncation or a mismatched/local-incomplete EDF rather than a normal late-night scoring pattern.

## What this means for pass4

- The stage-aware extraction code is still a real improvement and should be kept.
- The `pass4` 5-subject subset is valid as a bounded negative-result experiment, because all included subjects had enough in-range `SLEEP-S2` windows.
- `pass4` should not be interpreted as a clean apples-to-apples physiological comparison against pass3 for every intended subject, because `n10` had to be excluded for data-validity reasons.
- The worsening LOSO result (`0.600` balanced accuracy, `0.030` bruxism sensitivity) still matters, but it now carries a sharper interpretation: stage matching alone did not fix subject leakage, and part of the next bottleneck is dataset / file alignment quality.

## Best next bounded step

1. preserve the annotation-aware extraction path added in `src/prepare_windows.py`
2. treat `n10` as excluded from `SLEEP-S2` experiments unless a fuller matching EDF is found
3. keep `brux1` in the stage-aware subset, but document that only its earlier `S2` period is usable locally
4. rerun future stage-aware baselines only on subjects whose chosen events are confirmed in-range
5. only after that, decide whether to try a different stage/event filter or subject-level aggregation

## Files tied to this audit

- `projects/bruxism-cap/src/prepare_windows.py`
- `projects/bruxism-cap/data/window_features_pass4_s2.csv`
- `projects/bruxism-cap/reports/random-window-cv-pass4-s2.json`
- `projects/bruxism-cap/reports/loso-cv-pass4-s2.json`
- `projects/bruxism-cap/reports/annotation-alignment-audit-pass4-s2.md`
