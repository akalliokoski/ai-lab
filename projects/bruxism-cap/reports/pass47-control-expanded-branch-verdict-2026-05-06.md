# Post-pass47 verdict — did the first control-expanded rerun preserve specificity, and is repaired-A1 replication justified?

Date: 2026-05-06
Status: completed branch verdict memo.

## Question
Once the first bounded 7-subject control-expanded rerun landed on the frozen repaired `A3-only` no-shape contract, did it preserve an honest benchmark signal strongly enough to justify a repaired `A1-only` replication, or did it mainly expose fragility?

## Verdict in one line
Verdict: the branch stays alive, but only as an ambiguous benchmark line; the correct next move is a matched repaired `A1-only` replication on the same 7-subject control-expanded set.

The rerun does not produce a benchmark breakthrough because `brux2` still remains below the highest control, but it also does not show the feared fragility. Both new controls stay below threshold, the highest control score falls slightly overall, and the best-bruxism-minus-highest-control margin improves versus both repaired `A3-only` 5-subject references.

## 1) Comparison against the 5-subject repaired-A3 references
### Headline subject metrics
- pass45 anchor: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass46 side variant: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass47 control-expanded rerun: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

So the strict honest headline stays fixed even after adding `n1` and `n2`.

### Shared-subject score surface versus pass45
- `brux1`: `0.641 -> 0.669` (`+0.028`)
- `brux2`: `0.178 -> 0.212` (`+0.034`)
- `n3`: `0.134 -> 0.081` (`-0.053`)
- `n5`: `0.337 -> 0.334` (`-0.003`)
- `n11`: `0.345 -> 0.283` (`-0.062`)
- highest control: `n11 0.345 -> n5 0.334`
- best-bruxism-minus-highest-control margin: `+0.295 -> +0.335` (`+0.039`)
- subject prediction flips on shared subjects: `[]`

### Shared-subject score surface versus pass46
- `brux1`: `0.639 -> 0.669` (`+0.030`)
- `brux2`: `0.196 -> 0.212` (`+0.016`)
- `n3`: `0.131 -> 0.081` (`-0.050`)
- `n5`: `0.347 -> 0.334` (`-0.013`)
- `n11`: `0.345 -> 0.283` (`-0.062`)
- highest control: `n5 0.347 -> n5 0.334`
- best-bruxism-minus-highest-control margin: `+0.292 -> +0.335` (`+0.043`)
- subject prediction flips on shared subjects: `[]`

## 2) Did `n1` and `n2` stay below threshold, and did the highest-control subject change?
Yes.

- `n1`: `0.196`, below threshold `0.5`
- `n2`: `0.120`, below threshold `0.5`
- all five controls remain predicted `control`

Highest-control read:
- versus pass45, the highest control changes from `n11` (`0.345`) to `n5` (`0.334`)
- versus pass46, the highest control subject stays `n5`, but its score falls from `0.347` to `0.334`

That is the opposite of a fragility read. The expanded control set does not create a new threshold failure, and it does not raise the control ceiling.

## 3) How the best-bruxism-minus-highest-control margin changed, and whether the verdict stays useful
The best-bruxism-minus-highest-control margin improves in both required comparisons:
- versus pass45: `+0.295 -> +0.335` (`+0.039`)
- versus pass46: `+0.292 -> +0.335` (`+0.043`)

The branch verdict is therefore still useful.

Useful does not mean positive. The result is still benchmark-ambiguous because `brux2` remains below the highest control (`0.212 < 0.334`), so the branch has not earned a stronger claim than `0.750 / 0.500 / 1.000` with one rescued bruxism subject. But it is useful because it answers the specific control-expansion question honestly: the first bounded addition of verified controls `n1` and `n2` did not collapse specificity and did not shrink the repaired `A3-only` separation margin.

## 4) Exactly one next operational move
Chosen move: replicate on repaired `A1`.

Reason:
1. The main uncertainty after pass47 is no longer immediate control-side fragility on repaired `A3-only`; that question was answered narrowly but positively.
2. The next scientifically sharper question is whether this preserved specificity story survives on the repaired `A1-only` scaffold under the same 7-subject control-expanded set and frozen no-shape contract.
3. Another repaired-`A3-only` follow-up before checking repaired `A1-only` would spend more effort inside a branch whose basic stress-test already passed, without resolving whether the signal is scaffold-family specific.

## 5) One deferred move explicitly not chosen
Deferred move: continue the repaired-`A3-only` branch immediately with the previously proposed bounded event-trio swap (`evt_interburst_gap_median_s` out, `evt_phasic_like_episode_fraction` in).

Why it is deferred instead of chosen now:
- pass47 changed the priority order by answering the first control-expanded fragility question better than expected
- the sharper unresolved question is now cross-family robustness on repaired `A1-only`, not another same-family repaired-`A3-only` tweak
- the A3-side swap remains available later if the repaired-`A1-only` replication preserves the same story or cleanly localizes the remaining miss

## 6) Exact files to update next
### Primary implementation path for the repaired-A1 replication
1. `projects/bruxism-cap/src/run_pass48_control_expanded_a1_replication.py`
2. `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_full_envelope_shape_control_expanded.csv`
3. `projects/bruxism-cap/reports/time-position-match-pass48-emg-a1-pct10-90-control-expanded.json`
4. `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_pct10_90_timepos10_shape_control_expanded.csv`
5. `projects/bruxism-cap/data/window_features_pass48_emg_s2_mcap_a1_only_control_expanded.csv`
6. `projects/bruxism-cap/reports/loso-cv-pass48-emg-a1-control-expanded.json`
7. `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.json`
8. `projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.md`
9. `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.json`
10. `projects/bruxism-cap/reports/pass48-vs-pass47-control-expanded-cross-family-audit.md`

### Documentation / preservation path after that run
11. `wiki/queries/bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06.md`
12. `wiki/concepts/bruxism-cap.md`
13. `wiki/index.md`
14. `wiki/log.md`

## Bottom line
The first 7-subject control-expanded rerun preserves specificity well enough to stay informative: `n1` and `n2` remain safely below threshold, the highest control does not worsen, and the best-bruxism-minus-highest-control margin improves versus both pass45 and pass46. That is still not a benchmark win, but it is strong enough to justify one exact next move: a matched repaired-`A1-only` replication on the same 7-subject control-expanded set, with the repaired-`A3-only` phasic-fraction swap explicitly deferred rather than promoted now.
