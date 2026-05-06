---
title: Bruxism CAP pass48 control-expanded A1 replication
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass48-control-expanded-a1-replication.md
  - ../projects/bruxism-cap/reports/loso-cv-pass48-emg-a1-control-expanded.json
  - queries/bruxism-cap-pass47-control-expanded-rerun-2026-05-06.md
---

# Bruxism CAP pass48 control-expanded A1 replication

Question: if the repaired `A3-only` control-expanded branch survived its first specificity stress test, does a matched repaired `A1-only` replication on the same 7-subject contract confirm a robust benchmark direction or close the CAP branch instead?

Short answer: it closes the branch.

## Exact frozen contract
- subjects: `brux1`, `brux2`, `n1`, `n2`, `n3`, `n5`, `n11`
- channel: `EMG1-EMG2`
- slice: exclusive `SLEEP-S2 + MCAP-A1-only`
- selector: repaired percentile-band / time-aware `cap=10`, `q=[0.10, 0.90]`
- representation: repaired record-relative surface plus the fixed pass42 event trio
- train-time exclusions: base exclusions plus the same no-shape exclusions used by pass45/pass47
- model/eval: `logreg` with subject-level `LOSO` and the current uncertainty outputs

## Verified table construction
- full exclusive `A1-only` candidate pool before selector: `466` rows total
  - `brux1=27`, `brux2=29`, `n1=139`, `n2=94`, `n3=29`, `n5=134`, `n11=14`
- final selected / trained table: `70` rows total, exactly `10` per subject
- merge integrity: all three kept event features merged on `subject_id,start_s,end_s,window_index` with zero nulls

## Main result
- pass48 subject-level metrics: balanced accuracy `0.400`, sensitivity `0.000`, specificity `0.800`
- best bruxism subject: `brux2` at `0.311`
- highest control: `n2` at `0.614`
- best-bruxism-minus-highest-control margin: `-0.302`
- `brux2 - highest_control`: `-0.302`

## Failure surface
- `brux1`: `0.108`, predicted `control`
- `brux2`: `0.311`, predicted `control`
- `n2`: `0.614`, predicted `bruxism`
- only `4/5` controls stay below threshold, so the first repaired control-expanded `A1-only` replication reopens specificity while also missing both bruxism subjects

## Comparison against the repaired control-expanded A3 anchor
Against `pass47`:
- balanced accuracy drops `0.750 -> 0.400`
- sensitivity drops `0.500 -> 0.000`
- specificity drops `1.000 -> 0.800`
- margin flips from `+0.335` to `-0.302`
- `brux1` collapses `0.669 -> 0.108`
- `brux2` rises slightly `0.212 -> 0.311`, but still remains far below the new highest control
- the decisive new failure is control reopening through `n2` (`0.614`)

## Comparison against the older repaired A1 anchor
Against `pass42` on the shared original five subjects:
- balanced accuracy drops `0.750 -> 0.400`
- sensitivity drops `0.500 -> 0.000`
- margin drops `+0.339 -> -0.302`
- `brux2` collapses `0.825 -> 0.311`
- `n3` rises `0.155 -> 0.427`

So the control-expanded repaired `A1-only` replication does not merely fail to improve on the older repaired `A1-only` read; it materially breaks it.

## Interpretation
This is the strongest honest stop signal the current CAP branch has produced.

The pass47 result kept the branch alive because it stress-tested specificity without collapsing the repaired `A3-only` surface. Pass48 answers the last meaningful bounded question and answers it negatively: once the same 7-subject pressure is moved onto repaired `A1-only`, the benchmark no longer preserves either bruxism sensitivity or full control specificity. That means the current dataset is not supporting a stable cross-family benchmark story; it is supporting a narrow repaired `A3-only` ambiguity plus a clear positive-set ceiling. [[bruxism-cap-pass47-control-expanded-rerun-2026-05-06]] [[bruxism-cap-pass47-control-expanded-branch-verdict-2026-05-06]] [[bruxism-cap-source-audit-cap-expansion-2026-05-06]]

## Final project-status read
The public CAP benchmark should now be treated as complete.

Complete does not mean useless. The repo now has a reproducible, leakage-aware, subject-level benchmark history that established all of the following:
- public CAP honestly supports only `brux1` and `brux2` as positive subjects
- repaired `A3-only` can preserve an ambiguous but real `1/2` subject-level signal under a first bounded control expansion
- the same story does not survive a matched repaired `A1-only` control-expanded replication
- therefore further bounded CAP passes are unlikely to convert this into a stronger scientifically honest detector claim

## Exact next-step read
Do not keep grinding new CAP micro-passes.

Preserve pass48 as the closure artifact for the bounded benchmark loop, then move the project forward by treating CAP as the completed public benchmark scaffold and shifting active design energy toward the deferred privacy-preserving wearable jaw-EMG branch and its supporting data/measurement roadmap. [[bruxism-cap-next-data-strategy-2026-05-06]] [[bruxism-cap-privacy-pets-roadmap-2026-05-05]]
