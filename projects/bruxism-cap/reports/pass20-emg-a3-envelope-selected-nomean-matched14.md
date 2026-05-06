# Pass 20 — matched `EMG1-EMG2` `A3-only` envelope family with stricter selection plus `mean` ablation

Date: 2026-05-04
Status: bounded EMG-first rerun completed; removing raw `mean` on top of the pass19 selection-aware recipe does **not** improve the honest baseline and instead makes `brux1` much worse

## Why this pass exists

Pass19 narrowed the remaining EMG-first bottleneck to one likely score-ordering driver:
- the newer envelope / burst family looked more useful once the older `bp_*`, `rel_bp_*`, and `ratio_*` family was excluded at train time
- but `n3` and `n5` still outranked `brux1`
- earlier audits repeatedly showed unusually large negative `mean` burden on `brux1`

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
- keep the same matched `14`-windows-per-subject cap
- keep the same `EMG1-EMG2` channel and exclusive `SLEEP-S2 + MCAP-A3-only` extraction rule
- keep the same pass18 feature table with the envelope / burst family
- keep the same pass19 train-time exclusions for `bp_*`, `rel_bp_*`, and `ratio_*`
- change only one thing beyond pass19: also exclude raw `mean`

## Artifacts
- Feature table reused: `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json`
- Reference report: `projects/bruxism-cap/reports/pass19-emg-a3-envelope-selected-matched14.md`

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
  --exclude-features-regex '^mean$' \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/random-window-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv \
  --cv loso \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_' \
  --exclude-features-regex '^mean$' \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass20-emg-a3-envelope-selected-nomean-matched14.json
```

## Feature set used

The pass20 rerun used `16` trainable features:
- retained time / shape features: `std`, `min`, `max`, `ptp`, `rms`, `line_length`, `zero_crossing_rate`, `sample_entropy`
- retained EMG-oriented family: `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `envelope_cv`, `burst_fraction`, `burst_rate_hz`, `p95_abs`

Removed at train time only:
- `mean`
- `bp_delta`, `bp_theta`, `bp_alpha`, `bp_beta`
- `rel_bp_delta`, `rel_bp_theta`, `rel_bp_alpha`, `rel_bp_beta`
- `ratio_theta_beta`, `ratio_alpha_beta`, `ratio_alpha_delta`

## Key results

### Random-window CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 envelope + strict selection | `logreg` | `0.933` | `0.867` | `1.000` |
| pass20 envelope + strict selection + no `mean` | `logreg` | `0.933` | `0.867` | `1.000` |

Random-window CV stayed unrealistically high again, so it remains the wrong surface to optimize.

### LOSO window-level CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 envelope + strict selection | `logreg` | `0.629` | `0.043` | `0.586` |
| pass20 envelope + strict selection + no `mean` | `svm` | `0.600` | `0.000` | `0.600` |

The pass20 `logreg` rerun degrades more sharply still:
- balanced accuracy falls from `0.629` to `0.571`
- sensitivity falls from `0.043` to `0.000`
- specificity falls from `0.586` to `0.571`

So removing `mean` does **not** rescue the ranking problem; it worsens the strongest pass19 result.

### LOSO subject-level aggregation
| Run | Best model(s) | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 envelope + strict selection | all models still | `0.500` | `0.000` | `1.000` |
| pass20 envelope + strict selection + no `mean` | all models still | `0.500` | `0.000` | `1.000` |

So the honest subject-level baseline still does **not** improve.

## Subject score ordering (`logreg`)
- `n3` (`control`): `0.280`
- `n5` (`control`): `0.223`
- `n11` (`control`): `0.150`
- `brux2` (`bruxism`): `0.083`
- `brux1` (`bruxism`): `0.018`

Comparison with pass19:
- `brux1`: `0.151` -> `0.018`
- `brux2`: `0.088` -> `0.083`
- `n3`: `0.280` -> `0.280`
- `n5`: `0.222` -> `0.223`
- `n11`: `0.147` -> `0.150`

The main new lesson is severe and specific:
- excluding `mean` does **not** lower the two high-score controls
- it leaves `n3` and `n5` essentially unchanged
- it collapses `brux1` from the nearest honest contender to the lowest-scoring subject

## Interpretation

1. The pass19 suspicion was testable, but the direct `mean` ablation fails.
2. Raw `mean` was not just a harmful nuisance term on the pass19 scaffold; once the older spectral / ratio family is already removed, dropping `mean` makes the EMG ranking worse.
3. The remaining blocker therefore looks more like an interaction between retained amplitude / envelope features and subject-specific scaling than a simple “delete `mean`” fix.
4. This is another preserved EMG-first negative result, not a baseline win.

## Best next bounded step

Keep the same matched `EMG1-EMG2 A3-only` scaffold fixed again, but do **not** keep deleting single features blindly.

Best next experiment:
- run one compact audit comparing per-subject feature distributions for `brux1` versus `n3` / `n5` on the retained pass20/pass19 feature family, especially `rectified_mean`, `rectified_std`, `envelope_mean`, `envelope_std`, `p95_abs`, and `sample_entropy`

Safer than another ablation:
- preserve the stronger pass19 recipe as the current EMG-first working point
- treat pass20 as evidence that `mean` should not be removed naively; if revisited, it should be via robust centering / normalization-aware extraction rather than simple exclusion
