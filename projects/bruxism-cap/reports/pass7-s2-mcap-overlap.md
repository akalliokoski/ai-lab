# Pass 7 — SLEEP-S2 windows constrained to overlap CAP micro-events

Date: 2026-05-04
Scope: test whether a tighter annotation-aware extraction rule improves held-out-subject transfer by keeping only `SLEEP-S2` windows that overlap CAP micro-events (`MCAP-A1`, `MCAP-A2`, `MCAP-A3`).

## What changed

- Patched `projects/bruxism-cap/src/prepare_windows.py` with two new CLI options:
  - `--require-overlap-events`
  - `--min-overlap-seconds`
- Regenerated a new feature table:
  - `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`
- Reran the current no-`n_samples` / no-`duration_s` baseline path:
  - `projects/bruxism-cap/reports/random-window-cv-pass7-s2-mcap.json`
  - `projects/bruxism-cap/reports/loso-cv-pass7-s2-mcap.json`

## Extraction rule

A window is kept only if all of the following are true:
1. it is an in-range `SLEEP-S2` row
2. its duration is at least `30` seconds
3. it overlaps at least one `MCAP-A1`, `MCAP-A2`, or `MCAP-A3` annotation by a positive amount

This is intentionally the smallest event-aware extension of the existing stage-aware path.

## Eligible in-range S2+MCAP windows before the 20-window cap

| subject | label | eligible windows |
|---|---|---:|
| brux1 | bruxism | 77 |
| brux2 | bruxism | 181 |
| n3 | control | 166 |
| n5 | control | 194 |
| n11 | control | 96 |
| n10 | control | 0 |

`n10` remains unusable for this rule because the local EDF still has no in-range `SLEEP-S2` windows at all.

## Final pass7 dataset

- subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- labels: `2` bruxism, `3` control
- windows: `20` per subject, `100` total
- channel: `C4-P4`
- annotation event: `SLEEP-S2`
- overlap requirement: `MCAP-A1|MCAP-A2|MCAP-A3`

## Results

### Random-window CV

Best model: logistic regression
- balanced accuracy: `1.000`
- sensitivity: `1.000`
- specificity: `1.000`
- subject-aggregation balanced accuracy: `1.000`

### LOSO CV

Best window-level balanced accuracy: logistic regression at `0.590`
- sensitivity: `0.000`
- specificity: `0.590`

Best subject-level balanced accuracy: all models tied at `0.500`
- subject sensitivity: `0.000`
- subject specificity: `1.000`

## Interpretation

This tighter event-aware extraction rule did **not** narrow the leakage gap.

Compared with the earlier stage-aware pass4 subset:
- random-window CV stayed effectively perfect
- LOSO balanced accuracy fell slightly from `0.600` to about `0.590`
- held-out bruxism sensitivity fell from already-poor `0.030` to `0.000`
- subject-level held-out bruxism sensitivity stayed at `0.000`

So the new rule is still useful as infrastructure and as a negative result, but not as a performance improvement. The current evidence says that simply restricting windows to `SLEEP-S2` plus CAP micro-event overlap is still not enough to produce a transferable held-out-subject boundary.

## Best next bounded step

Prefer measurement hardening over model growth:
1. keep the new overlap-aware extraction support in `prepare_windows.py`
2. add a small artifact that audits which overlap event types (`A1` vs `A2` vs `A3`) dominate the kept windows by subject and label
3. then test one narrower extraction variant rather than another broad model change
