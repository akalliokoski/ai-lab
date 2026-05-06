---
title: Bruxism CAP strict EMG A1-only time-position feasibility (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md
---

# Question
Can the pass25/pass26-style strict shared-time-position scaffold be rebuilt on `EMG1-EMG2` exclusive `SLEEP-S2 + MCAP-A1-only` without collapsing the benchmark?

# Short answer
Not on the current verified 5-subject subset with the current simple selector.

The strict shared-interval rule is reproducible, but it collapses the `A1-only` scaffold to only `2` windows per subject (`10` total rows), which is too sparse to trust as a new LOSO benchmark. [[bruxism-cap]] [[bruxism-cap-emg-vs-c4-a1-only-matched14-2026-05-04]] [[bruxism-cap-emg-a3-time-position-matched-rerun-2026-05-05]] [[bruxism-cap-c4-vs-emg-timepos-a3-2026-05-05]]

# What I checked
I regenerated the uncapped `EMG1-EMG2` exclusive `A1-only` pool for the same verified subjects used in the recent strict-scaffold work: `brux1`, `brux2`, `n3`, `n5`, `n11`.

Before strict time matching, the pool is not small:
- `brux1`: `27` windows
- `brux2`: `29`
- `n3`: `29`
- `n5`: `134`
- `n11`: `14`

So the problem is not “A1-only is absent locally.” The problem appears when the same shared absolute `start_s` interval rule from pass25/pass26 is enforced.^[../projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md]

# What changed under the strict interval rule
The shared interval across all five subjects becomes only `7650.0` to `12650.0` seconds.

Inside that interval, support collapses sharply:
- `brux1`: `16 / 27`
- `brux2`: `3 / 29`
- `n3`: `2 / 29`
- `n5`: `26 / 134`
- `n11`: `2 / 14`

That means the largest valid strict shared-time-position cap is only `2` windows per subject. The resulting selected scaffold has just `10` rows total, which is too small to treat as a meaningful next EMG-first benchmark.^[../projects/bruxism-cap/reports/pass27-emg-a1-time-position-feasibility.md]

# Why this matters
This sharpens the interpretation of the recent EMG-first sequence:
- pass12 showed that `A1-only` can look stronger than `A3-only` under count-matched `C4-P4` conditions
- pass13 showed that the corresponding matched `EMG1-EMG2 A1-only` rerun was still a negative result
- pass25 and pass26 then showed that the stricter global time-position scaffold itself is a real validity axis, not just a channel choice
- pass27 now shows that applying that same hard scaffold to `EMG1-EMG2 A1-only` collapses the benchmark before modeling even begins

So the repo should not read “A1-only was better earlier” as “strict time-position-matched A1-only is the immediate next honest rerun.” On the current subset, the first blocker is extraction feasibility, not classifier choice alone. [[bruxism-cap-emg-vs-c4-a1-only-matched14-2026-05-04]] [[bruxism-cap-emg-a3-time-position-matched-rerun-2026-05-05]] [[bruxism-cap-c4-vs-emg-timepos-a3-2026-05-05]]

# Best next bounded step
Stay EMG-first, keep `A1-only` in scope, but stop using the current all-subject hard shared-interval rule as the only timing-control option.

The cleanest next move is to extend `projects/bruxism-cap/src/select_time_position_matched_windows.py` with a softer timing-control mode such as rank-based or percentile-band matching, then rerun `EMG1-EMG2 A1-only` on that scaffold before spending more effort on `C4-P4` again.
