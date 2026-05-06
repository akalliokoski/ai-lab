---
title: Bruxism CAP pass47 control-expanded rerun
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass47-control-expanded-rerun.md
  - ../projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-control-expanded.json
---

# Bruxism CAP pass47 control-expanded rerun

Question: once the bounded CAP control-side expansion is activated with locally verified `n1` and `n2`, does the repaired `A3-only` pass45 anchor survive a first exact 7-subject specificity stress test?

Short answer: yes, narrowly but clearly enough to continue the branch.

## Exact frozen contract
- subjects: `brux1`, `brux2`, `n1`, `n2`, `n3`, `n5`, `n11`
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A3-only`
- selector: repaired percentile-band / time-aware `cap=10`, `q=[0.10, 0.90]`
- representation: repaired record-relative surface plus the fixed pass42 event trio
- train-time exclusions: base exclusions plus pass45 shape-drop exclusions
- model/eval: `logreg` with subject-level `LOSO` and the current uncertainty outputs

## Verified table construction
- full exclusive `A3-only` candidate pool before selector: `403` rows total
  - `brux1=31`, `brux2=111`, `n1=56`, `n2=49`, `n3=76`, `n5=38`, `n11=42`
- final selected / trained table: `70` rows total, exactly `10` per subject
- merge integrity: all three kept event features merged on `subject_id,start_s,end_s,window_index` with zero nulls

## Main result
- pass47 subject-level metrics: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- best bruxism subject: `brux1` at `0.669`
- highest control: `n5` at `0.334`
- best-bruxism-minus-highest-control margin: `+0.335`
- `brux2 - highest_control`: `-0.123`

## New controls read
- `n1`: `0.196`, stays below threshold
- `n2`: `0.120`, stays below threshold
- all five controls remain predicted control under the default subject threshold

## Comparison against the 5-subject repaired-A3 anchors
Against `pass45`:
- margin improves from `+0.295` to `+0.335`
- `brux1` improves `0.641 -> 0.669`
- `brux2` improves `0.178 -> 0.212`
- shared controls all move down or stay essentially flat (`n3 -0.053`, `n5 -0.003`, `n11 -0.062`)

Against `pass46`:
- margin improves from `+0.292` to `+0.335`
- `brux1` improves `0.639 -> 0.669`
- `brux2` improves `0.196 -> 0.212`
- shared controls all move down (`n3 -0.050`, `n5 -0.013`, `n11 -0.062`)

## Interpretation
This is not a benchmark breakthrough: `brux2` still stays below the highest control, so the honest subject-level headline remains fixed at `0.750 / 0.500 / 1.000`.

But it is a meaningful branch-survival result. The feared immediate fragility did not show up when the verified new controls were added. Instead, the first bounded control expansion leaves all controls below threshold, slightly improves both bruxism subject scores on the shared repaired-A3 surface, and raises the best-bruxism-minus-highest-control margin rather than shrinking it. [[bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05]] [[bruxism-cap-pass46-one-feature-addback-2026-05-05]] [[bruxism-cap-control-side-expansion-audit-2026-05-06]] [[bruxism-cap-control-side-download-verification-2026-05-06]]

## Exact next-step read
The next exact card should be a matched `A1-only` replication on the same 7-subject control-expanded set, not another broad feature rewrite. The new question is whether this preserved specificity story is genuinely repaired-`A3-only` specific or survives on the repaired `A1-only` scaffold too. [[bruxism-cap-next-data-strategy-2026-05-06]] [[bruxism-cap-pass45-honest-benchmark-verdict-2026-05-05]]
