---
title: Bruxism CAP Next Data Strategy (2026-05-06)
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, dataset, evaluation, workflow, notes]
sources:
  - queries/bruxism-cap-source-audit-cap-expansion-2026-05-06.md
  - queries/bruxism-cap-dataset-decision-rubric-2026-05-06.md
  - queries/bruxism-scout-results-2026-05-06.md
  - queries/bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06.md
---

# Bruxism CAP Next Data Strategy

## Question
After the CAP positive-set ceiling audit, the external dataset scout, and the final matched control-expanded replication, what should the broader bruxism-detection project do next?

## Answer
Do not open another CAP micro-pass branch.

Public CAP cannot honestly grow its bruxism-positive set beyond `brux1` and `brux2`, and the final matched repaired control-expanded replication already answered the last meaningful bounded within-CAP question in the negative direction. The correct next move is to preserve CAP as the completed public benchmark scaffold and shift active design energy toward the deferred privacy-preserving wearable jaw-EMG branch and its supporting data/measurement roadmap. [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]] [[bruxism-cap-source-audit-cap-expansion-2026-05-06]] [[bruxism-cap]]

## What changed from the earlier strategy read?
The earlier same-day strategy memo recommended one bounded CAP-side control expansion. That recommendation was executed through `pass47` and then resolved by `pass48`.

The updated read is:
- control-side expansion was worth trying
- repaired `A3-only` survived the first stress test in `pass47`
- matched repaired `A1-only` failed decisively in `pass48`
- therefore CAP is now complete as a benchmark branch rather than still open as an active tuning surface

## Why not keep iterating inside CAP?
Because the benchmark now has both a structural ceiling and a decisive final failure mode:
- structural ceiling: only `brux1` and `brux2` are honest public positives
- decisive failure: the final matched repaired `A1-only` control-expanded replication falls to `0.400` balanced accuracy, `0.000` sensitivity, and `0.800` specificity, misses both bruxism subjects, and reopens the control surface through `n2`

That is stronger than “further gains seem unlikely.” It means the last meaningful bounded within-CAP test has already been run and failed.

## Primary branch now
Primary branch now: post-CAP successor design, not more CAP tuning.

Practical meaning:
- keep CAP artifacts and documentation intact
- use CAP as the public baseline and methodology history
- shift active work toward privacy-preserving wearable jaw-EMG design and better future data surfaces

## Deferred and active successor directions
Most relevant next direction:
- portable / wearable jaw-EMG branch with privacy-preserving data design, minimized off-device exports, and a stronger future dataset strategy

Still useful background directions:
- external dataset scouting for better future cohorts
- privacy-aware adaptive modeling ideas, but only once they are tied to a better data surface than the current public CAP branch

## Bottom line
CAP is honestly capped on the positive side and now also exhausted as an active benchmark branch. The right next move is no longer CAP-side expansion. It is to preserve CAP as the completed public scaffold and move forward on the wearable/privacy/data-roadmap side. [[bruxism-cap-privacy-pets-roadmap-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]
