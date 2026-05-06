# Pass 18 — matched `EMG1-EMG2` `A3-only` envelope / burst replacement family

Date: 2026-05-04
Status: bounded EMG-first replacement test completed; adding a compact rectified-envelope / burst family did **not** beat the current honest baseline and did not rescue subject-level bruxism detection

## Why this pass exists

Pass17 showed that subtraction-only cleanup was not enough:
- dropping `bp_*`, `rel_bp_*`, and `ratio_*` features did **not** rescue the honest EMG-first result
- the next bounded step should therefore test one compact **replacement-oriented** EMG family on the same fixed scaffold

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
- keep the same matched `14`-windows-per-subject cap
- keep the same `EMG1-EMG2` channel and exclusive `SLEEP-S2 + MCAP-A3-only` rule
- add one compact EMG-oriented family to the extracted feature table: rectified amplitude, smoothed envelope, and simple burst summaries

## Code / artifact changes
- Patched feature extractor: `projects/bruxism-cap/src/features.py`
- New feature CSV: `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass18-emg-a3-envelope-matched14.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass18-emg-a3-envelope-matched14.json`
- Follow-up audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.json`
- Follow-up audit note: `projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.md`

## New EMG-oriented feature family

Added `8` compact features per window:
- `rectified_mean`
- `rectified_std`
- `envelope_mean`
- `envelope_std`
- `envelope_cv`
- `burst_fraction`
- `burst_rate_hz`
- `p95_abs`

Implementation notes:
- rectification uses `abs(signal - mean(signal))`
- the envelope uses a simple `0.2 s` moving-average smoother
- bursts are samples above `rectified_mean + rectified_std`

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
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv
# repeated with --append for brux2, n3, n5, n11

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv \
  --cv random \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/random-window-cv-pass18-emg-a3-envelope-matched14.json

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv \
  --cv loso \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass18-emg-a3-envelope-matched14.json

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/audit_emg_feature_validity.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/feature-validity-audit-pass18-emg-a3-envelope-logreg.json
```

## Dataset shape held constant
- subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- channel: `EMG1-EMG2`
- rule: exclusive `SLEEP-S2 + MCAP-A3-only`
- windows per subject: `14`
- total rows: `70`
- trainable feature count: `28` (`20` previous trainable features + `8` new EMG-oriented features)

## Key results

### Random-window CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `svm` | `0.954` | `0.933` | `0.975` |
| pass17 time-only | `svm` | `0.967` | `0.933` | `1.000` |
| pass18 envelope / burst family | `logreg` | `0.933` | `0.867` | `1.000` |

Random-window CV stayed very high again, so it remains a misleading surface.

### LOSO window-level CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `logreg` | `0.629` | `0.057` | `0.571` |
| pass17 time-only | `logreg` | `0.614` | `0.043` | `0.571` |
| pass18 envelope / burst family | `logreg` | `0.600` | `0.043` | `0.557` |

So the replacement family did **not** improve the best honest window-level result; it regressed again relative to pass14.

### LOSO subject-level aggregation
| Run | Best model(s) | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `logreg` / `svm` / `random_forest` | `0.500` | `0.000` | `1.000` |
| pass17 time-only | all models still | `0.500` | `0.000` | `1.000` |
| pass18 envelope / burst family | all models still | `0.500` | `0.000` | `1.000` |

The honest subject-level verdict still did **not** improve.

## Subject score ordering (`logreg`)
- `n5` (`control`): `0.267`
- `n3` (`control`): `0.245`
- `brux1` (`bruxism`): `0.158`
- `n11` (`control`): `0.104`
- `brux2` (`bruxism`): `0.092`

Comparison with prior runs:
- `brux1`: `0.176` (pass14) -> `0.148` (pass17) -> `0.158` (pass18)
- `brux2`: `0.074` (pass14) -> `0.055` (pass17) -> `0.092` (pass18)
- `n3`: `0.267` (pass14) -> `0.328` (pass17) -> `0.245` (pass18)
- `n5`: `0.266` (pass14) -> `0.221` (pass17) -> `0.267` (pass18)

This is mixed but not good enough:
- the new family slightly recovers both bruxism subjects relative to pass17
- it lowers `n3` relative to pass14/pass17
- but `n5` remains above `brux1`, and neither bruxism subject crosses the honest subject threshold

## What the follow-up audit adds

The follow-up `logreg` audit on pass18 shows:
- the new family does enter the model meaningfully (`burst_rate_hz`, `envelope_cv`, `burst_fraction`, `envelope_std` appear in top contributors)
- but the high-score controls still keep recurring through a small control-favoring family: `min`, `sample_entropy`, and some envelope/burst terms
- `brux1` is still dominated by extreme negative absolute-power / mean terms (`mean`, `bp_theta`, `bp_alpha`, `ratio_theta_beta`)
- the EMG recipe is therefore still partly trapped by the older EEG-shaped feature family even after adding the new EMG-oriented summaries

## Interpretation

1. The replacement-family idea was worth testing, but this first compact envelope / burst addition does **not** beat the current honest baseline.
2. The result is slightly better than pass17 on `brux1` / `brux2` subject scores, but still worse than pass14 on the main LOSO window metric and still flat on the subject-level verdict.
3. The failure surface is now clearer: adding EMG-oriented summaries alone is not enough when the same old absolute-power / bandpower terms still dominate `brux1` negatively.
4. This is another useful negative result to preserve: simple EMG-oriented feature addition without stricter control of the older feature family does not rescue transfer.

## Best next bounded step

Keep the same matched `EMG1-EMG2 A3-only` scaffold and model family fixed again, but make the next feature step **selection-aware** rather than add-only:
- compare the current pass18 feature table under one constrained train-time filter that keeps the time-domain + new EMG family while excluding `bp_*`, `rel_bp_*`, and `ratio_*`, or
- run one compact audit focused on whether `mean` should be clipped, centered differently, or excluded for EMG because it keeps dominating `brux1` negatively

The safest next experiment is the first option: keep the new EMG family, but test it **without** the older EEG-shaped spectral / ratio family on the same matched pass18 table.