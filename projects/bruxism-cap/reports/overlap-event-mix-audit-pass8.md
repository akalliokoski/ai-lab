# Pass 8 — overlap event mix audit for the kept S2+MCAP windows

Date: 2026-05-04
Scope: audit which CAP micro-event overlap types dominate the `window_features_pass7_s2_mcap.csv` subset, both across all eligible in-range `SLEEP-S2` windows and across the first-20-per-subject windows actually kept in pass7.

## Why this audit exists

Pass7 added a tighter extraction rule (`SLEEP-S2` plus overlap with `MCAP-A1|MCAP-A2|MCAP-A3`) but did not improve LOSO transfer.
The next bounded question was whether the kept windows are dominated by different CAP micro-event mixtures across subjects or labels, which would make the pass7 subset harder to interpret and suggest a narrower extraction rule for the next run.

## Audited input

- Feature CSV: `projects/bruxism-cap/data/window_features_pass7_s2_mcap.csv`
- Annotation sidecars: `projects/bruxism-cap/data/raw/capslpdb/*.txt`
- Overlap events audited: `MCAP-A1`, `MCAP-A2`, `MCAP-A3`
- Window duration: `30` seconds

## Subject-level summary

| subject | label | eligible S2+MCAP windows before cap | kept windows | top eligible combo | top kept combo | kept windows with A1 | kept windows with A2 | kept windows with A3 |
|---|---|---:|---:|---|---|---:|---:|---:|
| brux1 | bruxism | 77 | 20 | MCAP-A3 (31) | MCAP-A3 (9) | 9 (45.0%) | 3 (15.0%) | 10 (50.0%) |
| brux2 | bruxism | 181 | 20 | MCAP-A3 (111) | MCAP-A3 (18) | 1 (5.0%) | 1 (5.0%) | 19 (95.0%) |
| n11 | control | 96 | 20 | MCAP-A3 (42) | MCAP-A3 (11) | 5 (25.0%) | 4 (20.0%) | 12 (60.0%) |
| n3 | control | 166 | 20 | MCAP-A3 (76) | MCAP-A3 (9) | 5 (25.0%) | 6 (30.0%) | 11 (55.0%) |
| n5 | control | 194 | 20 | MCAP-A1 (134) | MCAP-A1 (13) | 16 (80.0%) | 2 (10.0%) | 7 (35.0%) |

## Label-level summary

| label | eligible S2+MCAP windows before cap | kept windows | top eligible combo | top kept combo | kept windows with A1 | kept windows with A2 | kept windows with A3 |
|---|---:|---:|---|---|---:|---:|---:|
| bruxism | 258 | 40 | MCAP-A3 (142) | MCAP-A3 (27) | 10 (25.0%) | 4 (10.0%) | 29 (72.5%) |
| control | 456 | 60 | MCAP-A1 (177) | MCAP-A3 (23) | 26 (43.3%) | 12 (20.0%) | 30 (50.0%) |

## Evidence-backed takeaways

1. The pass7 subset is **not** event-type balanced across subjects.
   - `brux2` kept windows are overwhelmingly `MCAP-A3`-overlap (`19/20` windows with `A3`, only `1/20` with `A1`, `1/20` with `A2`).
   - `n5` shows the opposite pattern: its kept windows are mostly `MCAP-A1`-overlap (`16/20` with `A1`).
2. The imbalance already exists in the full eligible pools, not only in the first-20 cap.
   - `brux2` has `111/181` eligible windows with `MCAP-A3` only.
   - `n5` has `134/194` eligible windows with `MCAP-A1` only.
3. The first-20 cap still matters for interpretation because it preserves each subject's earliest local event mix rather than a matched cross-subject mix.
   - Pass7 therefore mixes subjects with materially different overlap-event compositions while keeping the label set tiny.
4. This makes pass7 a stronger negative result than a generic "stage-aware failed" story.
   - The current failure surface is now narrower: even after requiring `SLEEP-S2` plus CAP overlap, the kept windows still reflect different event-family regimes across subjects.

## Best next bounded step

Do **one** narrower extraction variant instead of another broad overlap bucket:
1. keep the current pass7 artifact as a negative baseline
2. add one extraction mode that restricts to a single overlap family such as `MCAP-A3` only, using the verified 5-subject subset
3. rerun random-window CV and LOSO subject aggregation on that single-family table before changing model class

That next test will answer a more interpretable question: does one CAP micro-event family transfer any better than the mixed-family pass7 bucket?
