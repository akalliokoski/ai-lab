# Pass 29 — `C4-P4` matched comparison on the pass28 percentile-band `A1-only` scaffold

Date: 2026-05-05
Status: bounded matched-channel comparison completed; rebuilding the same percentile-band `SLEEP-S2 + MCAP-A1-only` / `10`-windows-per-subject scaffold on `C4-P4` materially outperforms matched `EMG1-EMG2` on the honest LOSO surface, but the gain is still partial and does not clearly beat the older best honest baseline because `brux1` remains missed

## Why this pass exists

Pass28 fixed an extraction-validity problem without solving transfer:
- the new percentile-band selector restored a usable `EMG1-EMG2 A1-only` scaffold (`10` windows per subject instead of `2`)
- but both bruxism subjects still ranked below all three controls under honest LOSO
- the cleanest next question was therefore channel-comparative, not a new timing rule: on the exact same percentile-band scaffold, does `C4-P4` still outperform `EMG1-EMG2`?

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep the same exclusive `SLEEP-S2 + MCAP-A1-only` rule
- keep the same percentile-band selector (`0.10` to `0.90`) and the same `10` windows per subject
- keep the same train-time exclusions (`^bp_`, `^rel_bp_`, `^ratio_`)
- change only the extracted channel from `EMG1-EMG2` to `C4-P4`

## Artifacts
- Full `C4-P4` pool: `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_full_envelope.csv`
- Percentile-band matched subset: `projects/bruxism-cap/data/window_features_pass29_c4_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- Matching summary: `projects/bruxism-cap/reports/time-position-match-pass29-c4-a1-pct10-90.json`
- Random CV: `projects/bruxism-cap/reports/random-window-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`
- LOSO CV: `projects/bruxism-cap/reports/loso-cv-pass29-c4-a1-pct10-90-timepos10-selected.json`
- Matched EMG comparator: `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`

## Command path verified

```bash
source /home/hermes/work/ai-lab/.venv/bin/activate
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/prepare_windows.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/select_time_position_matched_windows.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/prepare_windows.py \
  --edf /home/hermes/work/ai-lab/projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --list-channels
# verified `C4-P4` exists locally
```

Then I rebuilt the uncapped exclusive `A1-only` `C4-P4` pool for the verified subset, applied the same percentile-band selector from pass28, and reran random-window plus LOSO evaluation with the same feature exclusions.

## Matched scaffold check

The percentile-band timing surface is intentionally the same as pass28:
- full pool rows: `233`
- percentile band: `0.10` to `0.90`
- cap: `10` windows per subject
- matched rows written: `50`
- candidate rows after filtering: `brux1 21`, `brux2 23`, `n3 23`, `n5 106`, `n11 10`

The selected `start_s` summaries are also identical to pass28, so this is a real channel comparison on the same scaffold rather than a hidden availability change.

## Key matched results

### Random-window CV
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `EMG1-EMG2` pass28 | `random_forest` | `0.825` | `0.850` | `0.800` |
| `C4-P4` pass29 | `svm` | `0.792` | `0.650` | `0.933` |

Random-window CV now slightly favors EMG on balanced accuracy, which is a useful reminder that this surface is still not the decision criterion.

### LOSO window-level CV
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `EMG1-EMG2` pass28 | `svm` | `0.600` | `0.000` | `0.600` |
| `C4-P4` pass29 | `logreg` | `0.760` | `0.260` | `0.500` |

Interpretation:
- on the same scaffold, `C4-P4` improves the honest best-model LOSO balanced accuracy by `+0.160`
- `C4-P4` also recovers non-zero held-out bruxism window sensitivity (`0.260` vs `0.000`)
- the cost is slightly worse specificity (`0.500` vs `0.600`), but the net honest result is still clearly better than matched EMG

### LOSO subject-level aggregation
| Channel | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| `EMG1-EMG2` pass28 | `svm` | `0.500` | `0.000` | `1.000` |
| `C4-P4` pass29 | `logreg` | `0.750` | `0.500` | `1.000` |

This is the main result:
- pass29 is the first percentile-band `A1-only` scaffold on which the comparison channel recovers one held-out bruxism subject (`brux2`) without creating a control false positive
- matched EMG still misses both bruxism subjects on the same timing-controlled surface

## Subject score ordering on the best LOSO model

### `EMG1-EMG2` pass28 (`svm`)
- `n3` (`control`): `0.422`
- `n11` (`control`): `0.319`
- `n5` (`control`): `0.264`
- `brux1` (`bruxism`): `0.222`
- `brux2` (`bruxism`): `0.209`

### `C4-P4` pass29 (`logreg`)
- `brux2` (`bruxism`): `0.959`
- `n3` (`control`): `0.417`
- `brux1` (`bruxism`): `0.405`
- `n5` (`control`): `0.212`
- `n11` (`control`): `0.188`

What changed:
- `C4-P4` flips the top of the ranking from control-dominant to bruxism-led by strongly recovering `brux2`
- `brux1` also improves materially versus matched EMG (`0.222` -> `0.405`), but still stays just below `n3` and therefore remains a miss at the subject threshold
- the remaining failure surface is now much narrower than in pass28: it is mainly `brux1` staying slightly below `n3`, not total bruxism collapse

## Relationship to the current best honest baseline

Pass29 does **not** clearly beat the current best honest baseline criterion overall.

Compared with the older matched `C4-P4 A1-only` pass12 anchor:
- pass12 subject-level LOSO summary: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass29 subject-level LOSO summary: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

So pass29 ties the pass12 honest subject verdict rather than beating it. It does improve benchmark validity by keeping the stronger percentile-band timing control, and it improves window-level LOSO balanced accuracy relative to pass12 (`0.760` vs `0.686`), but it still misses `brux1`, so this should be read as a measurement-hardening comparison win over pass28, not a new overall project-best detector.

## Interpretation

1. The EMG-first framing should **not** be abandoned because pass28 was unusable; pass28 was a valid negative result, and the matched comparison was the right next question.
2. But on this specific percentile-band `A1-only` scaffold, `C4-P4` is currently the stronger channel: it recovers `brux2`, improves `brux1`, and reaches the same honest subject-level verdict as the older pass12 anchor.
3. The key new validity lesson is narrower than “EEG beats EMG”: the percentile-band timing control itself is viable, and the remaining matched gap is now concentrated in `brux1` vs `n3` rather than broad EMG collapse.
4. This is therefore a useful benchmark-clarity increment, not a reason to revert the whole project framing back to EEG-first.

## Best next bounded step

Keep the EMG-first project framing, preserve pass29 as the current `C4-P4` comparison-channel result on the stronger timing-controlled `A1-only` scaffold, and do one compact validity audit next:
- compare pass28 `EMG1-EMG2` versus pass29 `C4-P4` feature/score behavior on the exact same percentile-band `A1-only` rows
- focus specifically on why `brux1` stays below `n3` under both channels while `brux2` recovers only under `C4-P4`

That keeps the repo grounded in one shared scaffold and directly explains the remaining EMG-first transfer gap instead of jumping to a new model family.
