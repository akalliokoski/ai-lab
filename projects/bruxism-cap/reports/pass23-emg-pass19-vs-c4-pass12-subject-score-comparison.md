# Subject-score comparison — pass19 EMG1-EMG2 A3-only selection-aware vs pass12 C4-P4 A1-only anchor

## Compared reports
- Primary: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json` (`logreg`)
- Anchor: `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json` (`logreg`)

## Why this comparison exists
- `pass19 EMG1-EMG2 A3-only selection-aware` is the current EMG-first working point, but it still fails the honest subject-level bar.
- `pass12 C4-P4 A1-only anchor` is the strongest current honest comparison anchor in the same 5-subject / 14-window matched family scaffold.
- The goal is benchmark clarity: make the remaining subject-level gap explicit before trying another extraction rewrite.

## Shared subject score table
| Subject | Label | Primary mean score | Anchor mean score | Delta (primary-anchor) | Primary positive-window fraction | Anchor positive-window fraction |
|---|---|---:|---:|---:|---:|---:|
| brux1 | bruxism | 0.151 | 0.018 | +0.134 | 0.214 | 0.000 |
| brux2 | bruxism | 0.088 | 0.795 | -0.708 | 0.000 | 0.929 |
| n11 | control | 0.147 | 0.273 | -0.126 | 0.000 | 0.143 |
| n3 | control | 0.280 | 0.245 | +0.036 | 0.071 | 0.000 |
| n5 | control | 0.222 | 0.433 | -0.212 | 0.000 | 0.357 |

## Score-surface summary
- Primary best bruxism subject: `brux1` at `0.151`.
- Primary highest control: `n3` at `0.280`.
- Primary best-bruxism-minus-highest-control margin: `-0.129`.
- Anchor best bruxism subject: `brux2` at `0.795`.
- Anchor highest control: `n5` at `0.433`.
- Anchor best-bruxism-minus-highest-control margin: `+0.362`.
- Margin delta (primary-anchor): `-0.491`.

## Main takeaways
1. The EMG working point improves one hard case locally: `brux1` rises from `0.018` on the anchor to `0.151` on the EMG surface, but this does not rescue the overall ranking.
2. The anchor remains stronger as an honest benchmark because `brux2` stays decisively separated (`0.795`) above the highest control (`0.433`), while the EMG surface still leaves its best bruxism subject below the highest control (`0.151` vs `0.280`).
3. The main regression from anchor to EMG is concentrated in `brux2`: its mean subject score falls from `0.795` to `0.088`.
4. The highest-score control also shifts: the anchor is mostly limited by `n5` (`0.433`), while the EMG surface is limited most by `n3` (`0.280`).
5. This keeps `pass19 EMG1-EMG2 A3-only selection-aware` as the current EMG-first working point, but only as a negative-yet-useful comparator; it does not beat `pass12 C4-P4 A1-only anchor` on the current honest baseline criterion.

## Window-level / subject-level summaries
- Primary window-level balanced accuracy: `0.629`; subject-level balanced accuracy: `0.500`; subject-level sensitivity: `0.000`.
- Anchor window-level balanced accuracy: `0.686`; subject-level balanced accuracy: `0.750`; subject-level sensitivity: `0.500`.

## Best next bounded step
Keep the pass19 EMG extraction / feature-selection recipe fixed and investigate why `brux2` collapses under EMG while `n3` becomes the dominant control, preferably with one compact validity audit or matched extraction check rather than another broad feature rewrite.
