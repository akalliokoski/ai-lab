# Subject-score comparison — pass44-repaired-a3-event-subset vs pass42-repaired-a1-event-subset

## Compared reports
- Primary: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass44-emg-a3-pct10-90-record-relative-shape-eventsubset.json` (`logreg`)
- Anchor: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass42-emg-a1-pct10-90-record-relative-shape-eventblock-subset.json` (`logreg`)

## Why this comparison exists
- `pass44-repaired-a3-event-subset` is the current EMG-first working point, but it still fails the honest subject-level bar.
- `pass42-repaired-a1-event-subset` is the strongest current honest comparison anchor in the same 5-subject / 14-window matched family scaffold.
- The goal is benchmark clarity: make the remaining subject-level gap explicit before trying another extraction rewrite.

## Shared subject score table
| Subject | Label | Primary mean score | Anchor mean score | Delta (primary-anchor) | Primary positive-window fraction | Anchor positive-window fraction |
|---|---|---:|---:|---:|---:|---:|
| brux1 | bruxism | 0.532 | 0.136 | +0.396 | 0.400 | 0.000 |
| brux2 | bruxism | 0.123 | 0.825 | -0.702 | 0.000 | 1.000 |
| n11 | control | 0.395 | 0.486 | -0.091 | 0.400 | 0.300 |
| n3 | control | 0.034 | 0.155 | -0.122 | 0.000 | 0.100 |
| n5 | control | 0.365 | 0.199 | +0.166 | 0.200 | 0.000 |

## Score-surface summary
- Primary best bruxism subject: `brux1` at `0.532`.
- Primary highest control: `n11` at `0.395`.
- Primary best-bruxism-minus-highest-control margin: `+0.138`.
- Anchor best bruxism subject: `brux2` at `0.825`.
- Anchor highest control: `n11` at `0.486`.
- Anchor best-bruxism-minus-highest-control margin: `+0.339`.
- Margin delta (primary-anchor): `-0.201`.

## Main takeaways
1. The EMG working point improves one hard case locally: `brux1` rises from `0.136` on the anchor to `0.532` on the EMG surface, but this does not rescue the overall ranking.
2. The anchor remains stronger as an honest benchmark because `brux2` stays decisively separated (`0.825`) above the highest control (`0.486`), while the EMG surface still leaves its best bruxism subject below the highest control (`0.532` vs `0.395`).
3. The main regression from anchor to EMG is concentrated in `brux2`: its mean subject score falls from `0.825` to `0.123`.
4. The highest-score control also shifts: the anchor is mostly limited by `n5` (`0.199`), while the EMG surface is limited most by `n3` (`0.034`).
5. This keeps `pass44-repaired-a3-event-subset` as the current EMG-first working point, but only as a negative-yet-useful comparator; it does not beat `pass42-repaired-a1-event-subset` on the current honest baseline criterion.

## Window-level / subject-level summaries
- Primary window-level balanced accuracy: `0.560`; subject-level balanced accuracy: `0.750`; subject-level sensitivity: `0.500`.
- Anchor window-level balanced accuracy: `0.720`; subject-level balanced accuracy: `0.750`; subject-level sensitivity: `0.500`.

## Best next bounded step
Keep the pass19 EMG extraction / feature-selection recipe fixed and investigate why `brux2` collapses under EMG while `n3` becomes the dominant control, preferably with one compact validity audit or matched extraction check rather than another broad feature rewrite.
