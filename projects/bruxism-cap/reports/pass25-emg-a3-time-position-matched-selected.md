# Pass 25 — shared-time-position `EMG1-EMG2` `A3-only` rerun on the verified 5-subject subset

Date: 2026-05-05
Status: bounded EMG-first extraction-validity rerun completed; enforcing a shared absolute time-position interval across subjects did **not** rescue the honest EMG baseline, although it did improve `brux2` relative to pass19 and showed that time-position mismatch alone is not the whole failure

## Why this pass exists

Pass24 tightened the current EMG failure surface to one dominant reversal:
- the strongest pass19 `EMG1-EMG2 A3-only` working point still loses mainly because `brux2` falls below `n3`
- the matched-14 scaffold is count-matched but not time-position-matched

This pass makes exactly one primary increment:
- keep the same verified subject subset (`brux1`, `brux2`, `n3`, `n5`, `n11`)
- keep the same `EMG1-EMG2` channel
- keep the same exclusive `SLEEP-S2 + MCAP-A3-only` extraction rule
- keep the same pass19 train-time exclusions (`^bp_`, `^rel_bp_`, `^ratio_`)
- change only the extraction scaffold so every subject is sampled from the same shared absolute `start_s` interval before rerunning the classical baselines

## Artifacts
- Selection script: `projects/bruxism-cap/src/select_time_position_matched_windows.py`
- Measurement hardening patch: `projects/bruxism-cap/src/train_baseline.py` now treats `time_match_rank` as metadata rather than a train feature
- Uncapped feature table: `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_full_envelope.csv`
- Shared-interval matched feature table: `projects/bruxism-cap/data/window_features_pass25_emg_s2_mcap_a3_only_timepos10_envelope.csv`
- Matching summary JSON: `projects/bruxism-cap/reports/time-position-match-pass25-emg-a3.json`
- Random CV report: `projects/bruxism-cap/reports/random-window-cv-pass25-emg-a3-timepos10-selected.json`
- LOSO report: `projects/bruxism-cap/reports/loso-cv-pass25-emg-a3-timepos10-selected.json`
- Reference baseline: `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`

## Command path verified

```bash
source /home/hermes/work/ai-lab/.venv/bin/activate
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/prepare_windows.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/select_time_position_matched_windows.py --help
```

## Shared-interval extraction summary

First, I regenerated the uncapped exclusive `SLEEP-S2 + MCAP-A3-only` `EMG1-EMG2` pool for the same verified 5-subject subset.

Eligible windows in the uncapped pool:
- `brux1`: `31`
- `brux2`: `111`
- `n3`: `76`
- `n5`: `38`
- `n11`: `42`

The strict shared absolute interval across all five subjects is:
- `start_s` `3210.0` to `12230.0`

That interval does **not** support the old `14`-windows-per-subject cap:
- `brux1`: `25` candidate windows in the shared interval
- `brux2`: `29`
- `n3`: `10`
- `n5`: `10`
- `n11`: `12`

So the largest valid shared-interval cap is only `10` windows per subject. This is itself a useful validity result: absolute time-position matching on the current verified subset is feasible, but only on a smaller scaffold than pass19.

## Timing shift versus pass19

### Pass19 matched-14 timing means
- `brux1`: `4067.9`
- `brux2`: `4377.9`
- `n3`: `8327.1`
- `n5`: `7915.7`
- `n11`: `5335.7`

### Pass25 shared-interval matched-10 timing means
- `brux1`: `8537.0`
- `brux2`: `7581.0`
- `n3`: `5946.0`
- `n5`: `9291.0`
- `n11`: `8832.0`

This confirms that pass25 is not just a relabel of pass19: the kept windows move materially later for both bruxism subjects and for `n11`, while `n3` becomes earlier than before because its shared-interval support is sparse and bimodal.

## Key results

### Random-window CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 matched-14 selection-aware | `logreg` | `0.933` | `0.867` | `1.000` |
| pass25 shared-time-position matched-10 | `logreg` | `0.808` | `0.650` | `0.967` |

Random-window CV drops sharply again, which is expected and healthy when the scaffold becomes stricter.

### LOSO window-level CV
| Run | Best model | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 matched-14 selection-aware | `logreg` | `0.629` | `0.043` | `0.586` |
| pass25 shared-time-position matched-10 | `svm` | `0.600` | `0.080` | `0.520` |

Interpretation:
- pass25 does **not** beat pass19 on the best honest window-level metric
- sensitivity rises slightly (`0.043` -> `0.080`) but specificity regresses materially
- the stricter scaffold still does not produce a clearly better leakage-aware baseline

### LOSO subject-level aggregation
| Run | Best model(s) | Balanced accuracy | Sensitivity | Specificity |
|---|---|---:|---:|---:|
| pass19 matched-14 selection-aware | all models still | `0.500` | `0.000` | `1.000` |
| pass25 shared-time-position matched-10 | `logreg` / `svm` | `0.500` | `0.000` | `1.000` |

So the honest subject-level verdict stays unchanged: both held-out bruxism subjects are still missed.

## Subject score ordering

### Pass19 `logreg`
- `n3` (`control`): `0.280`
- `n5` (`control`): `0.222`
- `brux1` (`bruxism`): `0.151`
- `n11` (`control`): `0.147`
- `brux2` (`bruxism`): `0.088`

### Pass25 `logreg`
- `n11` (`control`): `0.417`
- `n5` (`control`): `0.416`
- `n3` (`control`): `0.400`
- `brux1` (`bruxism`): `0.282`
- `brux2` (`bruxism`): `0.215`

What changed:
- `brux2` improves materially (`0.088` -> `0.215`)
- `brux1` also improves (`0.151` -> `0.282`)
- but **all three controls also rise**, and every control still outranks both bruxism subjects
- the failure therefore changes shape, but it does not disappear

## Interpretation

1. Time-position mismatch was a real validity hole worth testing, but fixing it this simply is **not** sufficient to rescue the honest EMG-first baseline.
2. The strict shared-interval requirement forces the scaffold down from `14` to `10` windows per subject because `n3` and `n5` only have `10` valid candidates in the common interval. That is a durable measurement constraint, not just an implementation detail.
3. The result is mixed in a useful way: both bruxism subjects rise relative to pass19, especially `brux2`, so the earlier/later window mismatch was contributing something real.
4. But the controls rise too, and the subject-level verdict stays flat at sensitivity `0.000`, which means the pass24 `brux2`-versus-`n3` story was incomplete rather than wrong.
5. The best current honest EMG baseline therefore remains pass19, not pass25.

## Best next bounded step

Keep the new pass25 shared-interval scaffold as a preserved negative result, then run one matched comparison next:
- rebuild the same shared-interval / `10`-windows-per-subject scaffold on `C4-P4`
- compare `EMG1-EMG2` versus `C4-P4` on that exact stricter time-position-matched subset

That is the cleanest next step because it separates a channel effect from a scaffold effect without adding model complexity.
