# Pass 28 — softer percentile-band timing control for `EMG1-EMG2` exclusive `A1-only`

Date: 2026-05-05
Status: bounded EMG-first timing-control rerun completed; extending the selector with a percentile-band mode successfully avoids the pass27 extraction collapse (`10` windows per subject instead of `2`), but the honest LOSO result still misses both held-out bruxism subjects, so this is a useful scaffold patch and a preserved negative benchmark result rather than a new best baseline

## Why this pass exists

Pass27 showed that the current hard shared-absolute-interval selector is too brittle for the verified `EMG1-EMG2` exclusive `SLEEP-S2 + MCAP-A1-only` subset:
- the uncapped pool exists locally (`233` rows total)
- but the strict common interval shrinks the usable scaffold to only `2` windows per subject
- that makes a new LOSO rerun too small to trust

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep `EMG1-EMG2` as the primary channel
- keep exclusive `SLEEP-S2 + MCAP-A1-only`
- patch `src/select_time_position_matched_windows.py` so timing control can use a relative per-subject percentile band instead of only one global shared absolute interval
- test one concrete softer scaffold: relative-time percentile band `0.10` to `0.90`, capped at `10` windows per subject

## Artifacts
- Patched selector: `projects/bruxism-cap/src/select_time_position_matched_windows.py`
- Metadata hardening patch: `projects/bruxism-cap/src/train_baseline.py`
- Percentile-band matched dataset: `projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv`
- Selector summary: `projects/bruxism-cap/reports/time-position-match-pass28-emg-a1-pct10-90.json`
- Random CV: `projects/bruxism-cap/reports/random-window-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
- LOSO CV: `projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json`
- Strict-feasibility comparator: `projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md`

## What changed in code

### `select_time_position_matched_windows.py`
New options:
- `--mode shared-interval|percentile-band`
- `--lower-quantile`
- `--upper-quantile`

New behavior:
- `shared-interval` preserves the old pass25/pass27 behavior unchanged
- `percentile-band` sorts each subject's windows by `start_s`, computes `relative_time_quantile` inside that subject, keeps only rows within the requested band, then applies the same evenly-spaced per-subject sampling step
- the JSON summary now records the matching mode and, for percentile-band runs, the candidate and selected relative-time quantile ranges per subject

### `train_baseline.py`
- `relative_time_quantile` is now treated as metadata rather than a train feature, so the new selector does not accidentally leak its own matching coordinate into the model

## Command path verified

```bash
source /home/hermes/work/ai-lab/.venv/bin/activate
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/select_time_position_matched_windows.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py --help
```

Then I ran:

```bash
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/select_time_position_matched_windows.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_full_envelope.csv \
  --subjects brux1,brux2,n3,n5,n11 \
  --cap 10 \
  --mode percentile-band \
  --lower-quantile 0.1 \
  --upper-quantile 0.9 \
  --out-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv \
  --out-json /home/hermes/work/ai-lab/projects/bruxism-cap/reports/time-position-match-pass28-emg-a1-pct10-90.json

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv \
  --cv random \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/random-window-cv-pass28-emg-a1-pct10-90-timepos10-selected.json \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_'

python /home/hermes/work/ai-lab/projects/bruxism-cap/src/train_baseline.py \
  --features-csv /home/hermes/work/ai-lab/projects/bruxism-cap/data/window_features_pass28_emg_s2_mcap_a1_only_pct10_90_timepos10_envelope.csv \
  --cv loso \
  --out /home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass28-emg-a1-pct10-90-timepos10-selected.json \
  --exclude-features-regex '^bp_' \
  --exclude-features-regex '^rel_bp_' \
  --exclude-features-regex '^ratio_'
```

## Extraction result: the softer scaffold is usable

Relative-time percentile band `0.10` to `0.90` keeps enough rows for a matched `10`-windows-per-subject` scaffold:
- `brux1`: `21` candidate rows -> `10` selected
- `brux2`: `23` -> `10`
- `n3`: `23` -> `10`
- `n5`: `106` -> `10`
- `n11`: `10` -> `10`
- total matched rows written: `50`

This is the key extraction win versus pass27:
- pass27 strict shared interval: only `2` windows per subject (`10` rows total)
- pass28 percentile band: `10` windows per subject (`50` rows total)

So the selector patch does what it was meant to do: it preserves a bounded timing-control idea without collapsing the benchmark surface immediately.

## Evaluation result: the honest EMG benchmark still does not transfer

### Random-window CV
Best random result:
- model: `random_forest`
- balanced accuracy: `0.825`
- sensitivity: `0.850`
- specificity: `0.800`

As in earlier passes, this surface still looks flattering and is not the decision criterion.

### LOSO window-level CV
Best LOSO window-level result:
- model: `svm`
- balanced accuracy: `0.600`
- sensitivity: `0.000`
- specificity: `0.600`

### LOSO subject-level aggregation
Best LOSO subject-level result on the same best model:
- balanced accuracy: `0.500`
- sensitivity: `0.000`
- specificity: `1.000`

Subject means on the best LOSO model (`svm`):
- `n3` (`control`): `0.422`
- `n11` (`control`): `0.319`
- `n5` (`control`): `0.264`
- `brux1` (`bruxism`): `0.222`
- `brux2` (`bruxism`): `0.209`

So the softer scaffold fixes pass27's extraction-collapse problem, but it does **not** fix the transfer problem:
- both bruxism subjects are still below all three controls
- honest subject-level sensitivity remains `0.000`
- the score ordering still looks like control-above-bruxism collapse rather than threshold fragility

## Interpretation

1. The EMG-first direction remains intact: the main blocker on `A1-only` was worth testing as a selector problem first, and the repo now has a reproducible softer timing-control scaffold.
2. The selector patch is a real infrastructure and measurement improvement because it turns an unusable `10`-row strict artifact into a reproducible `50`-row matched scaffold.
3. But it is **not** a new honest benchmark win. On the best LOSO model, pass28 ties pass25's best window-level balanced accuracy (`0.600`) and ties the same subject-level balanced accuracy (`0.500`), while still missing both held-out bruxism subjects.
4. Relative timing control by itself is therefore still not enough to make `EMG1-EMG2 A1-only` transferable on the verified subset.
5. Compared with pass13's earlier count-matched `A1-only` EMG run, this softer timing-aware rerun is more validity-conscious but less favorable on the honest window-level metric (`0.600` vs pass13 `0.543` improves slightly, yet subject-level sensitivity still stays `0.000`). The main value here is the more auditable scaffold, not a better end verdict.

## Best next bounded step

Keep the new percentile-band selector as infrastructure and preserve pass28 as a first-class negative result.

The cleanest next experiment is:
- keep the same pass28 percentile-band mode and verified subject subset
- rebuild the matched comparison channel on `C4-P4`
- compare `EMG1-EMG2` versus `C4-P4` on the same `A1-only` percentile-band scaffold before inventing another timing rule or changing model family

That would answer whether the softer `A1-only` scaffold still favors EMG-first framing when the timing control is no longer collapsed to `2` windows per subject.
