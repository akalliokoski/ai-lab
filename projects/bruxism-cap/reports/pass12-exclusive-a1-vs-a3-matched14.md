# Pass 12 — matched exclusive `SLEEP-S2 + MCAP-A1-only` vs `MCAP-A3-only`

Date: 2026-05-04
Status: bounded validity-focused comparison; `A1-only` improved honest held-out transfer relative to matched `A3-only`, but the result is still too small and subject-fragile to treat as a stable baseline win

## Why this pass exists

Pass10 and pass11 left a tighter next question than before:
- exclusive `S2 + A3-only` windows were cleaner than broader overlap rules, but still failed LOSO transfer
- the rule-survival audit showed that overlap-family choices also change availability, not just event semantics
- a fairer family comparison therefore needed the same verified subject set and the same per-subject cap

This pass tests exactly one bounded experiment:
- compare exclusive `SLEEP-S2 + MCAP-A1-only` against exclusive `SLEEP-S2 + MCAP-A3-only`
- keep the same verified 5-subject set: `brux1`, `brux2`, `n3`, `n5`, `n11`
- cap both families at `14` windows per subject because `n11` has only `14` eligible `A1-only` windows locally
- reuse the current no-`n_samples` / no-`duration_s` training path in `src/train_baseline.py`

## Datasets used

### `A1-only` matched set
- Feature CSV: `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv`
- Rule: in-range `SLEEP-S2` windows that overlap `MCAP-A1` and do **not** overlap `MCAP-A2` or `MCAP-A3`
- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Windows per subject: `14`
- Total windows: `70`

### `A3-only` matched companion set
- Feature CSV: `projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv`
- Rule: in-range `SLEEP-S2` windows that overlap `MCAP-A3` and do **not** overlap `MCAP-A1` or `MCAP-A2`
- Subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- Windows per subject: `14`
- Total windows: `70`

## Feasibility check

Eligible exclusive-family windows on the verified 5-subject subset:

| Subject | Label | `A1-only` eligible | `A3-only` eligible |
|---|---|---:|---:|
| brux1 | bruxism | 27 | 31 |
| brux2 | bruxism | 29 | 111 |
| n3 | control | 29 | 76 |
| n5 | control | 134 | 38 |
| n11 | control | 14 | 42 |

The matched comparison therefore uses `14` windows per subject because `n11` is the limiting `A1-only` case.

## Commands run

```bash
source .venv/bin/activate

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A1 \
  --exclude-overlap-events MCAP-A2,MCAP-A3 \
  --subject-id brux1 --label bruxism --channel C4-P4 \
  --window-seconds 30 --limit-windows 14 \
  --out projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv
# repeated with --append for brux2, n3, n5, n11

python projects/bruxism-cap/src/prepare_windows.py \
  --edf projects/bruxism-cap/data/raw/capslpdb/brux1.edf \
  --annotation-txt projects/bruxism-cap/data/raw/capslpdb/brux1.txt \
  --annotation-events SLEEP-S2 \
  --require-overlap-events MCAP-A3 \
  --exclude-overlap-events MCAP-A1,MCAP-A2 \
  --subject-id brux1 --label bruxism --channel C4-P4 \
  --window-seconds 30 --limit-windows 14 \
  --out projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv
# repeated with --append for brux2, n3, n5, n11

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a1-only-matched14.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass12_s2_mcap_a1_only_matched14.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv \
  --cv random \
  --out projects/bruxism-cap/reports/random-window-cv-pass12-s2-mcap-a3-only-matched14.json

python projects/bruxism-cap/src/train_baseline.py \
  --features-csv projects/bruxism-cap/data/window_features_pass12_s2_mcap_a3_only_matched14.csv \
  --cv loso \
  --out projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a3-only-matched14.json
```

## Key results

### Random-window CV
- `A1-only` best balanced accuracy: `0.917` (`logreg` and `svm`)
- `A3-only` best balanced accuracy: `0.910` (`logreg`)
- Both families still look strong under random window splits, so neither should be interpreted from random CV alone

### LOSO window-level CV
- `A1-only` best balanced accuracy: `0.686` (`logreg`)
- `A3-only` best balanced accuracy: `0.514` (`svm`)
- `A1-only` best held-out bruxism sensitivity: `0.186` (`logreg`)
- `A3-only` held-out bruxism sensitivity: `0.000` for every tested model

### LOSO subject-level aggregation
- `A1-only` best subject-level result: `logreg` at balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- `A3-only` best subject-level result: `svm` / `random_forest` at balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- `A1-only logreg` correctly called `brux2` positive while keeping all three controls negative, but still missed `brux1`

## Comparison to prior exclusive-`A3` reading

This pass changes the interpretation of the overlap-family question:
1. The earlier `A3-only` failure was not just a consequence of the `20`-window cap. A matched `14`-window `A3-only` rerun still gave `0.000` held-out bruxism subject sensitivity.
2. On the same subject set and same per-subject cap, `A1-only` is materially less brittle than `A3-only` in LOSO.
3. But the improvement is still narrow and unstable: it relies on recognizing `brux2` while still missing `brux1`, so it is not yet a transferable subject-level solution.

## Interpretation

This is the first overlap-family comparison in the repo that improves the honest measurement surface without changing model family:
1. Exclusive family choice matters. `S2 + A1-only` and `S2 + A3-only` are not interchangeable subsets.
2. The earlier project bias toward `A3` was too narrow. In this tiny CAP subset, `A1-only` survives as the stronger transfer candidate under matched conditions.
3. The result is still a caution, not a victory. Subject-level sensitivity only rose from `0.000` to `0.500`, and only because one of two bruxism subjects now crosses threshold.
4. The next validity question is no longer “does any exclusive-family comparison matter?” It is “why does `brux1` still fail under the stronger `A1-only` rule, and is the gain robust to thresholding or to a more explicit per-subject score audit?”

## Best next bounded step

Stay on validity work. The next safest increment is a compact subject-score audit on the pass12 `A1-only` and matched `A3-only` LOSO outputs:
- compare mean score margins for `brux1` vs `brux2`
- check whether the apparent `A1-only` improvement is threshold-fragile or reflects a broader ranking improvement
- preserve the family-survival context so future comparisons keep event availability and event semantics separate
