# Pass 17 — matched `EMG1-EMG2` `A3-only` time-domain ablation

Date: 2026-05-04
Status: bounded EMG-first ablation completed; dropping the spectral / band-ratio family did **not** rescue honest transfer on the matched pass14 scaffold

## Why this pass exists

Pass16 narrowed the safest next experiment to one small feature-family ablation on the stronger current EMG scaffold:
- keep the same verified `5`-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
- keep the same matched `14`-windows-per-subject cap
- keep the same `EMG1-EMG2` channel and exclusive `SLEEP-S2 + MCAP-A3-only` extraction rule
- change only the trainable feature family by removing the EEG-shaped spectral features (`bp_*`, `rel_bp_*`, `ratio_*`)

This tests the narrow claim that the current honest EMG failure might be mainly caused by spectral / ratio features that are poorly aligned with an EMG-first framing.

## Artifacts
- Patched trainer: `projects/bruxism-cap/src/train_baseline.py`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass17-emg-a3-timeonly-matched14.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass17-emg-a3-timeonly-matched14.json`
- Reference full-feature LOSO report: `projects/bruxism-cap/reports/loso-cv-pass14-emg-s2-mcap-a3-only-matched14.json`

## Command path verified

```bash
/home/hermes/work/ai-lab/.venv/bin/python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py --help

/home/hermes/work/ai-lab/.venv/bin/python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv \
  --cv random \
  --exclude-features-regex ^bp_ \
  --exclude-features-regex ^rel_bp_ \
  --exclude-features-regex ^ratio_ \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/random-window-cv-pass17-emg-a3-timeonly-matched14.json

/home/hermes/work/ai-lab/.venv/bin/python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass14_emg_s2_mcap_a3_only_matched14.csv \
  --cv loso \
  --exclude-features-regex ^bp_ \
  --exclude-features-regex ^rel_bp_ \
  --exclude-features-regex ^ratio_ \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass17-emg-a3-timeonly-matched14.json
```

## Feature set used

The pass17 ablation kept only `9` time-domain features:
- `mean`
- `std`
- `min`
- `max`
- `ptp`
- `rms`
- `line_length`
- `zero_crossing_rate`
- `sample_entropy`

It removed `11` spectral / ratio features:
- `bp_delta`, `bp_theta`, `bp_alpha`, `bp_beta`
- `rel_bp_delta`, `rel_bp_theta`, `rel_bp_alpha`, `rel_bp_beta`
- `ratio_theta_beta`, `ratio_alpha_beta`, `ratio_alpha_delta`

## Key results

### Random-window CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `svm` | `0.954` | `0.933` | `0.975` |
| pass17 time-domain only | `svm` | `0.967` | `0.933` | `1.000` |

Random-window CV stayed very high, so this remains a misleading surface.

### LOSO window-level CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `logreg` | `0.629` | `0.057` | `0.571` |
| pass17 time-domain only | `logreg` | `0.614` | `0.043` | `0.571` |

The best honest window-level result got slightly worse after the ablation.

### LOSO subject-level aggregation
| Run | Best model(s) | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass14 full features | `logreg` / `svm` / `random_forest` | `0.500` | `0.000` | `1.000` |
| pass17 time-domain only | all models still | `0.500` | `0.000` | `1.000` |

So the ablation did **not** improve the honest subject-level verdict at all.

## Subject score ordering after ablation (`logreg`)
- `n3` (`control`): `0.328`
- `n5` (`control`): `0.221`
- `brux1` (`bruxism`): `0.148`
- `n11` (`control`): `0.144`
- `brux2` (`bruxism`): `0.055`

Compared with pass14 full features:
- `brux1` fell from `0.176` to `0.148`
- `brux2` fell from `0.074` to `0.055`
- `n5` fell from `0.266` to `0.221`
- `n3` **rose** from `0.267` to `0.328`

So removing the spectral family did lower one control (`n5`), but it also lowered both bruxism subjects and made `n3` even more dominant.

## Interpretation

1. The pass16 concern was real, but the simplest subtraction patch is not enough. Spectral / ratio features are not the only reason the EMG-first ranking fails.
2. Pure time-domain pruning does **not** rescue `brux1` or `brux2` at the subject level.
3. The strongest negative signal now is that `n3` becomes even harder to separate under the time-only recipe, so at least one useful discriminative signal was removed along with the suspect spectral family.
4. This is a useful negative result to preserve: the next EMG-first step should not be another broad deletion-only ablation.

## Best next bounded step

Keep the same matched `EMG1-EMG2 A3-only` scaffold and the same evaluation path, but change only one thing again:
- add or swap in one compact **EMG-specific burst / envelope / amplitude-variability** family, rather than only subtracting spectral features
- keep the time-domain core plus one new EMG-aligned family so the next result can answer whether replacement works better than deletion

A good next bounded patch would be one EMG-oriented feature addition such as burst-threshold fraction, high-amplitude percentile summaries, or short-horizon rectified-envelope variability, then rerun the same matched LOSO comparison.