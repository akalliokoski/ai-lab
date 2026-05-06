# Pass 42 — same-table 3-feature event subset ablation analysis

Date: 2026-05-05
Status: bounded same-table subset sweep completed on the existing pass41 feature table.

## Scope
This analysis keeps the repaired five-subject `SLEEP-S2 + MCAP-A1-only` `EMG1-EMG2` scaffold fixed and uses the existing pass41 table:
- `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- same `logreg` LOSO subject-level contract as pass36/pass40/pass41
- same pass36 base feature set
- exactly one bounded change: evaluate every 3-feature subset of the 7 appended pass41 event features (`35` subsets total)

## Honest anchors
- pass36 subject-level: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass40 subject-level: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass41 subject-level: balanced accuracy `0.583`, sensitivity `0.500`, specificity `0.667`
- matched C4 pass29 subject-level: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

## Best pass42 subset by the stated objective
Recommended subset:
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

Subject-level result for this subset:
- balanced accuracy `0.750`
- sensitivity `0.500`
- specificity `1.000`
- subject probability brier `0.215`

Subject scores:
- `brux1`: `0.136` (`+0.025` vs pass36, `+0.019` vs pass41 baseline EMG event-full run)
- `brux2`: `0.825`
- `n3`: `0.155`
- `n5`: `0.199`
- `n11`: `0.486`

Predicted labels:
- `brux1` -> `control`
- `brux2` -> `bruxism`
- `n3` -> `control`
- `n5` -> `control`
- `n11` -> `control`

## Interpretation against pass36 / pass40 / pass41
1. This subset does not create a new honest benchmark win over pass36/pass40; it ties them on the subject-level headline metrics (`0.750 / 0.500 / 1.000`).
2. It does beat pass41 in the only place pass41 got worse: control protection is restored (`n11` falls from `0.546` back to `0.486`, below threshold).
3. It keeps a real but still sub-threshold `brux1` lift relative to pass36/pass40 (`0.136` vs `0.112` / `0.112`).
4. So the narrowed event block is best read as a cleaner diagnostic improvement, not a solved benchmark improvement.

## Read versus the matched C4 anchor
The subset does not close the matched C4 gap:
- pass29 `C4-P4` still has the same subject-level headline metrics (`0.750 / 0.500 / 1.000`)
- but its `brux1` score remains much stronger (`0.405` vs `0.136` here)
- and its `n3` / `n11` controls remain comparably or more comfortably separated in aggregate

So this pass42-style subset keeps the EMG branch honest and less damaging, but it still does not catch the stronger matched C4 anchor on the unresolved `brux1` bottleneck.

## Verdict
The narrowed event block produced an honest improvement in diagnosis quality, but only as a cleaner negative result:
- yes, it preserves a small `brux1` lift
- yes, it restores control protection
- no, it does not convert that lift into a better subject-level benchmark than pass36/pass40
- no, it does not erase the matched C4 anchor advantage

## Exact next bounded task
Freeze the best 3-feature subset (`evt_active_fraction`, `evt_burst_duration_median_s`, `evt_interburst_gap_median_s`) as the pass42 working point, then run one fold-level attribution audit on the same table focused only on held-out `brux1` versus `n3`/`n11` to test whether the remaining miss is still dominated by the old record-relative amplitude block rather than the retained event subset itself.
