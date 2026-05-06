# Pass 14 — matched `EMG1-EMG2` exclusive `SLEEP-S2 + MCAP-A1-only` vs `MCAP-A3-only`

Date: 2026-05-04
Status: bounded EMG-first family comparison completed; `A3-only` is less bad than `A1-only` for `EMG1-EMG2`, but neither family recognizes a held-out bruxism subject at the default subject threshold

## Why this pass exists

Pass13 preserved an important negative result: the first matched EMG rerun on the strongest current `C4-P4` scaffold (`A1-only`) did not beat the current honest `C4-P4` baseline.

That narrowed the next EMG-first question to one bounded comparison:
- keep the same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep the same `14` windows per subject cap
- keep the same model family and evaluation path
- compare exclusive `MCAP-A1-only` vs exclusive `MCAP-A3-only` inside `EMG1-EMG2`

## Datasets compared

### Existing EMG `A1-only` run
- Feature CSV: `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json`
- Rule: in-range `SLEEP-S2` windows overlapping `MCAP-A1` and excluding simultaneous `MCAP-A2` / `MCAP-A3`

### New EMG `A3-only` run
- Feature CSV: `projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
- Rule: in-range `SLEEP-S2` windows overlapping `MCAP-A3` and excluding simultaneous `MCAP-A1` / `MCAP-A2`

## Command path verified

```bash
source .venv/bin/activate

python projects/bruxism-cap/src/prepare_windows.py --help
python projects/bruxism-cap/src/train_baseline.py --help
python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --list-channels
# verified both C4-P4 and EMG1-EMG2 exist locally

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A3 \
  --exclude-overlap-events MCAP-A1,MCAP-A2 \
  --subject-id brux1 --label bruxism --channel EMG1-EMG2 \
  --window-seconds 30 --limit-windows 14 \
  --out projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv
# repeated with --append for brux2, n3, n5, n11

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv-pass14-emg-s2-mcap-a3-only-matched14.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json
```

## Feasibility check

The new `A3-only` EMG table preserved the same matched shape as pass13:
- subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- windows per subject: `14`
- total windows: `70`
- extracted channel: `EMG1-EMG2`

## Key matched results

### Random-window CV
| EMG family | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `A1-only` pass13 | `svm` | `0.882` | `0.833` | `0.931` |
| `A3-only` pass14 | `svm` | `0.954` | `0.933` | `0.975` |

Random-window CV improved for `A3-only`, but this remains the less trustworthy surface.

### LOSO window-level CV
| EMG family | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `A1-only` pass13 | `logreg` | `0.543` | `0.043` | `0.500` |
| `A3-only` pass14 | `logreg` | `0.629` | `0.057` | `0.571` |

### LOSO subject-level aggregation
| EMG family | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `A1-only` pass13 | `logreg` / `svm` | `0.500` | `0.000` | `1.000` |
| `A3-only` pass14 | `logreg` / `svm` / `random_forest` | `0.500` | `0.000` | `1.000` |

## Subject-level score comparison

### `A1-only` pass13 best EMG LOSO model (`logreg`)
- `brux1`: predicted `control`, mean score `0.176`
- `brux2`: predicted `control`, mean score `0.043`
- controls: `n11` `0.373`, `n3` `0.355`, `n5` `0.199`

### `A3-only` pass14 best EMG LOSO model (`logreg`)
- `brux1`: predicted `control`, mean score `0.176`
- `brux2`: predicted `control`, mean score `0.074`
- controls: `n11` `0.095`, `n3` `0.267`, `n5` `0.266`

## Interpretation

1. `EMG1-EMG2` does appear to prefer `A3-only` over `A1-only` on the current matched scaffold, but only weakly and only on window-level LOSO metrics.
2. The improvement is not enough to change the honest verdict. Subject-level bruxism sensitivity remains `0.000` under every tested model and both EMG families.
3. The main difference from pass13 is that `A3-only` lowers control-subject mean scores substantially, especially for `n11`, without lifting either bruxism subject above the default threshold.
4. This is therefore a useful validity result, not a new baseline win: family choice matters inside EMG too, but the current handcrafted EMG feature recipe still fails held-out bruxism subject recognition on the verified subset.

## Best next bounded step

Keep the model family fixed and stay on validity work.

The best next experiment is a compact score-threshold audit on the strongest current EMG LOSO model (`pass14` `A3-only` `logreg`):
- compare score margins for `brux1` and `brux2` against the three controls
- test whether any threshold below `0.5` improves subject sensitivity without immediately collapsing specificity
- preserve the comparison against pass12 `C4-P4 A1-only`, which remains the current best honest baseline
