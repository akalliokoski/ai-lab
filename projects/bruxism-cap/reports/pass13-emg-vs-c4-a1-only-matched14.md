# Pass 13 — matched `EMG1-EMG2` versus `C4-P4` on exclusive `SLEEP-S2 + MCAP-A1-only`

Date: 2026-05-04
Status: first EMG-first comparison run completed; `EMG1-EMG2` did not beat the current `C4-P4` matched `A1-only` baseline and regressed held-out bruxism subject detection to `0.000`

## Why this pass exists

The repo was just reframed as EMG-first, but that framing still needed one real matched channel comparison inside the existing verified CAP scaffold.

This pass tests exactly one bounded increment:
- keep the verified 5-subject subset from pass12: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep the same exclusive annotation rule: in-range `SLEEP-S2` windows overlapping `MCAP-A1` while excluding simultaneous `MCAP-A2` / `MCAP-A3`
- keep the same per-subject cap: `14` windows per subject
- swap only the extracted signal channel from `C4-P4` to `EMG1-EMG2`
- compare the new EMG run against the existing pass12 `C4-P4` matched `A1-only` artifacts

## Datasets compared

### New EMG run
- Feature CSV: `projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv`
- Channel: `EMG1-EMG2`
- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Windows per subject: `14`
- Total windows: `70`

### Existing comparison run
- Feature CSV: `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`
- Channel: `C4-P4`
- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Windows per subject: `14`
- Total windows: `70`

## Command path verified

```bash
source .venv/bin/activate

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --list-channels
# verified `EMG1-EMG2` exists locally before the rerun

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A1 \
  --exclude-overlap-events MCAP-A2,MCAP-A3 \
  --subject-id brux1 --label bruxism --channel EMG1-EMG2 \
  --window-seconds 30 --limit-windows 14 \
  --out projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv
# repeated with --append for brux2, n3, n5, n11

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv-pass13-emg-s2-mcap-a1-only-matched14.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass13_emg_s2_mcap_a1_only_matched14.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv-pass13-emg-s2-mcap-a1-only-matched14.json
```

## Key matched results

### Random-window CV
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `C4-P4` pass12 | `logreg` / `svm` | `0.917` | `0.833` | `1.000` |
| `EMG1-EMG2` pass13 | `svm` | `0.882` | `0.833` | `0.931` |

Random-window CV stayed strong for both channels, so it is still not the trustworthy comparison surface.

### LOSO window-level CV
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `C4-P4` pass12 | `logreg` | `0.686` | `0.186` | `0.500` |
| `EMG1-EMG2` pass13 | `logreg` | `0.543` | `0.043` | `0.500` |

### LOSO subject-level aggregation
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `C4-P4` pass12 | `logreg` | `0.750` | `0.500` | `1.000` |
| `EMG1-EMG2` pass13 | `logreg` / `svm` | `0.500` | `0.000` | `1.000` |

## Subject-level score comparison

### `C4-P4` pass12 best LOSO model (`logreg`)
- `brux1`: predicted `control`, mean score `0.018`
- `brux2`: predicted `bruxism`, mean score `0.795`
- controls stayed below threshold: `n11` `0.273`, `n3` `0.245`, `n5` `0.433`

### `EMG1-EMG2` pass13 best LOSO model (`logreg`)
- `brux1`: predicted `control`, mean score `0.176`
- `brux2`: predicted `control`, mean score `0.043`
- controls stayed below threshold: `n11` `0.373`, `n3` `0.355`, `n5` `0.199`

## Interpretation

1. This first EMG-first matched rerun is a **negative result** on the honest baseline criterion.
2. `EMG1-EMG2` did not beat the current matched `C4-P4` `A1-only` baseline under the same subject set, annotation rule, and cap.
3. The main regression is not random CV. It is subject transfer: `C4-P4` still recognized `brux2` at the subject level, while `EMG1-EMG2` recognized neither bruxism subject.
4. The failure is still informative. It narrows the next question from “should we pivot to EMG first at all?” to “is the current handcrafted feature set or event-family choice too EEG-shaped for EMG, or is this tiny verified subset simply not giving transferable EMG separation under `A1-only`?”

## Best next bounded step

Stay measurement-first and keep the model family fixed.

The cleanest next experiment is:
- run a matched EMG family comparison on the same 5-subject / 14-window scaffold
- compare `EMG1-EMG2` exclusive `A1-only` against `EMG1-EMG2` exclusive `A3-only`
- keep `C4-P4` pass12 and EMG pass13 as the fixed cross-channel anchors

That would answer whether the EMG failure is channel-wide or whether EMG prefers a different overlap family than the current strongest EEG-leaning `A1-only` rule.
