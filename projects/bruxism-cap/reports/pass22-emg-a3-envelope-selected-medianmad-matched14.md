# Pass 22 — matched `EMG1-EMG2` `A3-only` selection-aware rerun with robust per-window `median_mad` normalization

Date: 2026-05-04
Status: bounded EMG-first normalization-aware rerun completed; robust per-window `median_mad` normalization does **not** improve the honest baseline and instead makes both bruxism subjects rank even lower than the stronger pass19 working point

## Why this pass exists

Pass21 narrowed the next EMG-only move to one specific extraction change:
- keep the stronger pass19 matched `EMG1-EMG2 A3-only` scaffold fixed
- preserve the retained envelope / burst family
- test one normalization-aware extraction change instead of more blind feature deletion

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
- keep the same matched `14`-windows-per-subject cap
- keep the same `EMG1-EMG2` channel and exclusive `SLEEP-S2 + MCAP-A3-only` rule
- keep the same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
- change only the extraction path by adding robust per-window `median_mad` normalization before feature computation

## Code / artifact changes
- Patched feature extraction support:
  - `projects/bruxism-cap/src/features.py`
  - `projects/bruxism-cap/src/prepare_windows.py`
  - `projects/bruxism-cap/src/train_baseline.py`
- New feature CSV: `projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json`

## Normalization rule tested

Per window, the raw signal is transformed before feature extraction as:
- center = `median(signal)`
- scale = `1.4826 * MAD(signal)`
- fallback scale = `std(signal)` when MAD is effectively zero
- final normalized window = `(signal - center) / scale`

This is recorded in the feature CSV as `signal_transform=median_mad`.

## Command path verified

```bash
source /home/hermes/work/ai-lab/.venv/bin/activate
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/prepare_windows.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py --help

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/prepare_windows.py \
  --edf /home/hermes/work/ai-lab/projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt /home/hermes/work/ai-lab/projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A3 \
  --exclude-overlap-events MCAP-A1,MCAP-A2 \
  --subject-id brux1 --label bruxism --channel EMG1-EMG2 \
  --window-seconds 30 --limit-windows 14 \
  --normalize-mode median_mad \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv
# repeated with --append for brux2, n3, n5, n11

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv \
  --cv random \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_' \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/random-window-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass22_emg_s2_mcap_a3_only_matched14_medianmad.csv \
  --cv loso \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_' \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass22-emg-a3-envelope-selected-medianmad-matched14.json
```

## Dataset shape held constant
- subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- channel: `EMG1-EMG2`
- rule: exclusive `SLEEP-S2 + MCAP-A3-only`
- windows per subject: `14`
- total rows: `70`
- signal transform: `median_mad`
- train-time exclusions: `^bp_`, `^rel_bp_`, `^ratio_`

## Key results

### Random-window CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 envelope + strict selection | `logreg` | `0.933` | `0.867` | `1.000` |
| pass22 `median_mad` extraction + same selection | `logreg` | `0.933` | `0.867` | `1.000` |

Random-window CV stayed unrealistically high again, so it remains the wrong surface to optimize.

### LOSO window-level CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 envelope + strict selection | `logreg` | `0.629` | `0.043` | `0.586` |
| pass22 `median_mad` extraction + same selection | `svm` | `0.571` | `0.000` | `0.571` |

So the normalization-aware rerun does **not** preserve the stronger pass19 window-level result; it regresses below it and removes the small remaining positive-window sensitivity.

### LOSO subject-level aggregation
| Run | Best model(s) | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 envelope + strict selection | all models still | `0.500` | `0.000` | `1.000` |
| pass22 `median_mad` extraction + same selection | all models still | `0.500` | `0.000` | `1.000` |

The honest subject-level verdict still does **not** improve.

## Subject score ordering

### Pass19 `logreg`
- `n3` (`control`): `0.280`
- `n5` (`control`): `0.222`
- `brux1` (`bruxism`): `0.151`
- `n11` (`control`): `0.147`
- `brux2` (`bruxism`): `0.088`

### Pass22 `logreg`
- `n11` (`control`): `0.270`
- `n5` (`control`): `0.251`
- `n3` (`control`): `0.195`
- `brux2` (`bruxism`): `0.033`
- `brux1` (`bruxism`): `0.009`

### Pass22 best LOSO model (`svm`)
- `n11` (`control`): `0.288`
- `n5` (`control`): `0.203`
- `n3` (`control`): `0.143`
- `brux2` (`bruxism`): `0.133`
- `brux1` (`bruxism`): `0.117`

## Interpretation

1. The normalization-aware idea was worth testing because pass21 specifically suggested that subject-specific amplitude scaling might be the remaining blocker.
2. On this matched scaffold, robust per-window `median_mad` normalization is a preserved negative result, not an improvement.
3. The change hurts the strongest EMG-first working point in the most important way: both bruxism subjects move even farther below the controls, especially under `logreg` (`brux1` `0.151 -> 0.009`, `brux2` `0.088 -> 0.033`).
4. This suggests the pass19 signal is **not** rescued by simply normalizing each window's amplitude scale before extracting the retained envelope family; that normalization appears to discard or distort the little useful separation still present.
5. The stronger EMG-first working point therefore remains pass19, not pass22.

## Best next bounded step

Do **not** keep the new `median_mad` extraction as the working recipe.

Best next experiment:
- keep pass19 as the EMG-first working point
- build one shared subject-score comparison between pass19 `EMG1-EMG2 A3-only` and the honest pass12 `C4-P4 A1-only` anchor so the remaining gap is explicit at the subject level

That is safer than another extraction rewrite because the normalization-aware hypothesis has now been tested directly and preserved as a negative result.
