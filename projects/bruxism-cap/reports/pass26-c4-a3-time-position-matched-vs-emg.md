# Pass 26 — shared-time-position `C4-P4` rerun against the strict pass25 `EMG1-EMG2` scaffold

Date: 2026-05-05
Status: bounded matched-channel comparison completed; rebuilding the same shared-interval `A3-only` / `10`-windows-per-subject scaffold on `C4-P4` does **not** rescue the benchmark and actually underperforms the matched `EMG1-EMG2` rerun on the honest LOSO surface

## Why this pass exists

Pass25 tightened the extraction scaffold for `EMG1-EMG2` by forcing every subject onto the same shared absolute `start_s` interval. That preserved a useful negative result, but it also left one clean follow-up question:

- was pass25 mainly worse because the scaffold became stricter?
- or because `EMG1-EMG2` is the wrong channel for this subset?

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep the same exclusive `SLEEP-S2 + MCAP-A3-only` rule
- keep the same shared absolute time interval and the same `10` windows per subject
- keep the same pass19/pass25 train-time exclusions (`^bp_`, `^rel_bp_`, `^ratio_`)
- change only the extracted channel from `EMG1-EMG2` to `C4-P4`

## Artifacts
- Full `C4-P4` pool: `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_full_envelope.csv`
- Shared-interval matched subset: `projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv`
- Matching summary: `projects/bruxism-cap/reports/time-position-match-pass26-c4-a3.json`
- Random CV: `projects/bruxism-cap/reports/random-window-cv-pass26-c4-a3-timepos10-selected.json`
- LOSO CV: `projects/bruxism-cap/reports/loso-cv-pass26-c4-a3-timepos10-selected.json`
- Strict EMG comparator: `projects/bruxism-cap/reports/loso-cv-pass25-emg-a3-timepos10-selected.json`
- Selection script reused unchanged: `projects/bruxism-cap/src/select_time_position_matched_windows.py`

## Command path verified

```bash
source .venv/bin/activate

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --list-channels
# verified `C4-P4` exists locally before the rerun

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A3 \
  --exclude-overlap-events MCAP-A1,MCAP-A2 \
  --subject-id brux1 --label bruxism --channel C4-P4 \
  --window-seconds 30 \
  --out projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_full_envelope.csv
# repeated with --append for brux2, n3, n5, n11

python projects/bruxism-cap/src/select_time_position_matched_windows.py \
  --features-csv projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_full_envelope.csv \
  --subjects brux1,brux2,n3,n5,n11 \
  --cap 10 \
  --out-csv projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv \
  --out-json projects/bruxism-cap/reports/time-position-match-pass26-c4-a3.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv-pass26-c4-a3-timepos10-selected.json \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_'

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass26_c4_s2_mcap_a3_only_timepos10_envelope.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv-pass26-c4-a3-timepos10-selected.json \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_'
```

## Shared-interval check

The new `C4-P4` matching summary is identical to pass25 on the selection surface:
- shared interval: `3210.0` to `12230.0`
- cap: `10` windows per subject
- subject timing means: `brux1` `8537.0`, `brux2` `7581.0`, `n3` `5946.0`, `n5` `9291.0`, `n11` `8832.0`

So this pass really is a channel comparison on the same stricter scaffold, not a new extraction-availability change.

## Key matched results

### Random-window CV
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `EMG1-EMG2` pass25 | `logreg` | `0.808` | `0.650` | `0.967` |
| `C4-P4` pass26 | `logreg` | `0.883` | `0.800` | `0.967` |

Random-window CV favors `C4-P4` again, so it remains the misleading surface.

### LOSO window-level CV
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `EMG1-EMG2` pass25 | `svm` | `0.600` | `0.080` | `0.520` |
| `C4-P4` pass26 | `logreg` | `0.520` | `0.100` | `0.420` |

Interpretation:
- `C4-P4` gets a tiny sensitivity bump relative to strict-scaffold EMG (`0.100` vs `0.080`)
- but it pays for that with much worse specificity (`0.420` vs `0.520`)
- on the best-model honest metric, strict-scaffold `EMG1-EMG2` still comes out less bad than strict-scaffold `C4-P4`

### LOSO subject-level aggregation
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `EMG1-EMG2` pass25 | `svm` | `0.500` | `0.000` | `1.000` |
| `C4-P4` pass26 | `logreg` | `0.333` | `0.000` | `0.667` |

Neither channel recognizes a held-out bruxism subject on this strict scaffold, but `C4-P4` is worse because it also promotes one control subject to a false positive.

## Subject score ordering on the best LOSO model

### `EMG1-EMG2` pass25 (`svm`)
- `n11` (`control`): `0.445`
- `n3` (`control`): `0.442`
- `n5` (`control`): `0.348`
- `brux1` (`bruxism`): `0.329`
- `brux2` (`bruxism`): `0.273`

### `C4-P4` pass26 (`logreg`)
- `n3` (`control`): `0.535`
- `brux2` (`bruxism`): `0.464`
- `n11` (`control`): `0.356`
- `n5` (`control`): `0.337`
- `brux1` (`bruxism`): `0.086`

What changed:
- the strict scaffold does **not** make `C4-P4` recover the old pass12-style subject ordering
- `n3` becomes the dominant false-positive control under `C4-P4`, just as controls dominated under pass25 EMG
- `C4-P4` still keeps `brux2` closer to the top than EMG does, but it collapses `brux1` much harder and still fails the subject threshold

## Interpretation

1. This pass answers the channel-vs-scaffold question more cleanly: the strict shared-time-position `A3-only` scaffold itself is hostile enough that switching back to `C4-P4` does **not** rescue the benchmark.
2. The repo should therefore **not** treat the pass25 negative result as proof that `EMG1-EMG2` is unusable. On the exact same strict scaffold, `EMG1-EMG2` is actually less bad than `C4-P4` on the honest LOSO summary.
3. The main remaining blocker is validity of the `A3-only` / time-position-matched benchmark surface itself, not a simple “wrong channel” story.
4. This is still a negative result overall: neither strict-scaffold channel beats the current honest baseline criterion, and both stay below the older pass12 `C4-P4 A1-only` anchor.

## Best next bounded step

Keep the EMG-first framing and preserve pass25/pass26 as matched negative results.

The cleanest next experiment is:
- rebuild the same shared-time-position scaffold on the stronger `A1-only` family for `EMG1-EMG2`
- keep `C4-P4` as the matched comparison channel only after the `EMG1-EMG2 A1-only` strict-scaffold rerun exists

That stays EMG-first, keeps the stricter time-position discipline, and tests whether the current failure is really `A3-only`-specific rather than a generic EMG problem.
