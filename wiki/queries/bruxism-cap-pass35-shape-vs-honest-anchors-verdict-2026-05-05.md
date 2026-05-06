---
title: Bruxism CAP pass35 shape vs honest anchors verdict (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass35-shape-vs-honest-anchors-verdict.md
  - queries/bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05.md
  - queries/bruxism-cap-emg-a1-record-relative-audit-2026-05-05.md
  - queries/bruxism-cap-c4-record-relative-comparator-2026-05-05.md
  - comparisons/bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05.md
  - concepts/bruxism-cap.md
---

# Question
After the new pass35 EMG shape-feature expansion, does the run actually become the new honest EMG anchor once it is checked against the repaired EMG baseline, the pass34 mixed result, and the stronger matched `C4-P4` comparator?

# Short answer
No. Pass35 shape is a real directional improvement over the older repaired EMG anchors, but it does not materially beat the current honest anchor set.

Relative to pass28 and pass33, it sharply repairs the two named EMG score-ordering failures: `brux2 - n3` flips positive and `n3 - brux1` nearly closes. But relative to pass34 it does not improve the subject-level decision outcome at all (`0.500` balanced accuracy, `0.000` sensitivity, `1.000` specificity in both runs), and it still stays clearly behind pass29 `C4-P4`, which remains the only repaired-scaffold anchor with positive subject-level sensitivity (`0.500`). [[bruxism-cap]] [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]] [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]]

# What changed
The main change is interpretive, not just numerical. Earlier local comparison work treated pass35 shape as the likely new EMG mixed-result anchor because it repaired both named EMG gaps more symmetrically than pass34.^[../projects/bruxism-cap/reports/pass35-shape-vs-honest-anchors-verdict.md]

After an explicit honest-anchor check, the preserved conclusion becomes narrower:
- pass35 shape is better than pass28 and pass33 on score ordering
- pass35 shape ties pass34 on the subject-level outcome that actually matters
- pass35 shape still does not beat the stronger matched `C4-P4` honest comparator

So the repo should preserve pass35 as a useful mixed representation result, but not rewrite the benchmark story as if EMG has already established a new honest anchor.

# Why the understanding changed
The direct honest-anchor comparison adds the missing guardrail: it evaluates the new EMG pass against both kinds of anchors at once.

Those anchors are:
- repaired EMG scaffold baseline: pass28
- narrower repaired EMG ablation anchor: pass33
- prior mixed representation anchor: pass34
- stronger non-EMG honest comparator: pass29 `C4-P4`

That fuller frame matters because pass35 looks stronger if judged only by the two repaired EMG score gaps, but weaker if judged by threshold-crossing subject sensitivity and the best available comparison-channel outcome. [[bruxism-cap-c4-record-relative-comparator-2026-05-05]] [[bruxism-cap-patched-emg-vs-matched-c4-anchor-comparison-2026-05-05]]

# How improvement and failure showed up
## Real improvement
- pass35 shape improves subject-level balanced accuracy from `0.333` to `0.500` versus pass28/pass33
- `brux2 - n3` improves from about `-0.49` to `+0.174`
- `n3 - brux1` shrinks from `+0.260` / `+0.497` to `+0.009`
- `n3` is no longer a false positive

## Preserved failure
- both bruxism subjects still stay below the `0.5` subject threshold:
  - `brux1` `0.216`
  - `brux2` `0.399`
- subject-level sensitivity remains `0.000`, exactly matching pass34 rather than exceeding it
- `n5` still interleaves with the bruxism scores (`0.387` vs `brux2` `0.399`)
- pass29 `C4-P4` still remains stronger overall because it keeps `0.500` sensitivity with `1.000` specificity on the repaired scaffold

So the bottleneck is no longer just gross score inversion. It is now threshold-crossing subject sensitivity: the shape-family improvement changes the ranking geometry, but not enough to produce a held-out positive bruxism subject. ^[../projects/bruxism-cap/reports/pass35-shape-vs-honest-anchors-verdict.md]

# Verdict
Preserve pass35 shape as a first-class mixed result and as a first-class negative result at the decision layer.

It is a positive representation clue because the repaired EMG scaffold gets meaningfully cleaner on both named score gaps without selection drift. But it is also a negative result because the honest subject-level verdict does not improve versus pass34 and still trails the stronger matched `C4-P4` anchor. [[bruxism-cap]] [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]]

# Exact next step
Do not spend another cycle deciding whether pass34 or pass35 should win as the single forward anchor. Preserve that both are useful but incomplete, then combine the two best EMG ideas in one bounded rerun:
- start from the pass34 record-relative scaffold
- add the same four compact shape features used in pass35
- keep the same repaired five-subject percentile-band `A1-only` subset, LOSO split, model family, and subject-score gap checks
- compare only pass34 versus `record-relative + shape`

That is now the exact next bounded step because the honest-anchor verdict shows that pass35 fixed ordering more than threshold crossing, while pass34 fixed `brux2` more than `brux1`. The next useful question is whether those gains compose honestly on the same scaffold. [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]] [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]]
