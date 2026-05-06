# Pass 19 — matched `EMG1-EMG2` `A3-only` envelope family under stricter train-time feature selection

Date: 2026-05-04
Status: bounded EMG-first rerun completed; keeping the new envelope / burst family while excluding the older spectral / ratio family slightly improves the best LOSO window metric, but still does **not** rescue the honest subject-level baseline

## Why this pass exists

Pass18 showed that add-only EMG feature expansion was not enough:
- the new envelope / burst family entered the model
- but the older `bp_*`, `rel_bp_*`, and `ratio_*` family still dominated too much of the decision surface
- the safest next step was therefore to keep the new EMG-oriented features and rerun the same scaffold under stricter train-time feature selection

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
- keep the same matched `14`-windows-per-subject cap
- keep the same `EMG1-EMG2` channel and exclusive `SLEEP-S2 + MCAP-A3-only` extraction rule
- keep the same pass18 feature table with the new envelope / burst family
- change only the train-time feature set by excluding `bp_*`, `rel_bp_*`, and `ratio_*`

## Artifacts
- Feature table reused: `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`
- Reference reports:
  - `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`
  - `projects/bruxism-cap/reports/loso-cv-pass17-emg-a3-timeonly-matched14.json`
  - `projects/bruxism-cap/reports/loso-cv-pass18-emg-a3-envelope-matched14.json`

## Command path verified

```bash
source /home/hermes/work/ai-lab/.venv/bin/activate
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py --help

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv \
  --cv random \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_' \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/random-window-cv-pass19-emg-a3-envelope-selected-matched14.json

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv \
  --cv loso \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_' \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json
```

## Feature set used

The pass19 rerun used `17` trainable features:
- time-domain core: `mean`, `std`, `min`, `max`, `ptp`, `rms`, `line_length`, `zero_crossing_rate`, `sample_entropy`
- EMG-oriented family from pass18: `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `envelope_cv`, `burst_fraction`, `burst_rate_hz`, `p95_abs`

Removed at train time only:
- `bp_delta`, `bp_theta`, `bp_alpha`, `bp_beta`
- `rel_bp_delta`, `rel_bp_theta`, `rel_bp_alpha`, `rel_bp_beta`
- `ratio_theta_beta`, `ratio_alpha_beta`, `ratio_alpha_delta`

## Key results

### Random-window CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `svm` | `0.954` | `0.933` | `0.975` |
| pass17 time-only | `svm` | `0.967` | `0.933` | `1.000` |
| pass18 envelope / burst add-on | `logreg` | `0.933` | `0.867` | `1.000` |
| pass19 envelope + strict selection | `logreg` | `0.933` | `0.867` | `1.000` |

Random-window CV stayed unrealistically high again, so it remains the wrong surface to optimize.

### LOSO window-level CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `logreg` | `0.629` | `0.057` | `0.571` |
| pass17 time-only | `logreg` | `0.614` | `0.043` | `0.571` |
| pass18 envelope / burst add-on | `logreg` | `0.600` | `0.043` | `0.557` |
| pass19 envelope + strict selection | `logreg` | `0.629` | `0.043` | `0.586` |

This does recover the best pass14 LOSO balanced accuracy and improves specificity over pass14 (`0.571` -> `0.586`), but it does **not** improve sensitivity and therefore does not change the honest subject-level verdict.

### LOSO subject-level aggregation
| Run | Best model(s) | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | all models still | `0.500` | `0.000` | `1.000` |
| pass17 time-only | all models still | `0.500` | `0.000` | `1.000` |
| pass18 envelope / burst add-on | all models still | `0.500` | `0.000` | `1.000` |
| pass19 envelope + strict selection | all models still | `0.500` | `0.000` | `1.000` |

So the honest subject-level baseline still does **not** improve.

## Subject score ordering (`logreg`)
- `n3` (`control`): `0.280`
- `n5` (`control`): `0.222`
- `brux1` (`bruxism`): `0.151`
- `n11` (`control`): `0.147`
- `brux2` (`bruxism`): `0.088`

Comparison with prior runs:
- `brux1`: `0.176` (pass14) -> `0.148` (pass17) -> `0.158` (pass18) -> `0.151` (pass19)
- `brux2`: `0.074` (pass14) -> `0.055` (pass17) -> `0.092` (pass18) -> `0.088` (pass19)
- `n3`: `0.267` (pass14) -> `0.328` (pass17) -> `0.245` (pass18) -> `0.280` (pass19)
- `n5`: `0.266` (pass14) -> `0.221` (pass17) -> `0.267` (pass18) -> `0.222` (pass19)
- `n11`: `0.095` (pass14) -> `0.144` (pass17) -> `0.104` (pass18) -> `0.147` (pass19)

What changed usefully:
- the stricter selection keeps `n5` well below its pass18 score and below `n3`
- `n11` remains below `brux1`, so the ranking is slightly less hostile than pass18 on that edge
- but both `n3` and `n5` still outrank `brux1`, and `brux2` remains far below the honest decision threshold

## Interpretation

1. The selection-aware idea was worth testing because it recovered the best pass14 LOSO balanced accuracy while keeping the new EMG-oriented family in play.
2. But this is still **not** an honest EMG baseline win: subject-level bruxism sensitivity remains `0.000` for every model.
3. The practical lesson is narrower: the pass18 envelope / burst family works better when the older spectral / ratio family is excluded at train time than when it is simply added on top.
4. The remaining blocker is still score ordering: `n3` and `n5` stay above `brux1`, and `brux2` is still too low.
5. This is therefore a useful partial-validity result, not a performance breakthrough.

## Best next bounded step

Keep the same matched `EMG1-EMG2 A3-only` scaffold and the same selection-aware train-time filter, but change only one small thing next:
- audit whether `mean` should be excluded or robustly centered for EMG, because it remains the most suspicious large negative driver on `brux1`, or
- run one matched comparison between the current pass19 selection-aware EMG recipe and the honest pass12 `C4-P4 A1-only` anchor using a shared subject-score summary table so the remaining gap is clearer

The safer next experiment is the first one: keep pass19 fixed and test one bounded `mean`-handling audit or ablation before touching model family or dataset scope.
