---
title: Bruxism CAP
created: 2026-05-03
updated: 2026-05-06
type: concept
tags: [dataset, evaluation, experiment, workflow, notes]
sources:
  - raw/articles/cap-sleep-database-physionet-2012.md
  - raw/articles/bruxism-single-channel-eeg-2024.md
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
---

# Bruxism CAP

`bruxism-cap` is a completed public benchmark project in `ai-lab`. It used the PhysioNet CAP Sleep Database to build a deliberately small, leakage-aware bruxism-versus-control baseline centered on subject-level evaluation rather than flattering window-level scores. It should now be read as a finished benchmark history and methodology scaffold, not as an active CAP tuning loop. [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]] [[bruxism-cap-source-audit-cap-expansion-2026-05-06]] [[bruxism-cap-next-data-strategy-2026-05-06]]

## Final status
- Status: closed after `pass48` on `2026-05-06`
- Primary public positives: `brux1`, `brux2`
- Final bounded control-expanded subject set: `brux1`, `brux2`, `n1`, `n2`, `n3`, `n5`, `n11`
- Final closure verdict: current public CAP supports a useful benchmark history, but not a stronger stable detector claim under matched cross-family control expansion

## Why this project mattered
- It established a reproducible public biosignal benchmark inside the repo.
- It made the random-window versus subject-held-out leakage gap explicit.
- It forced careful annotation-aware and event-aware extraction.
- It preserved negative results rather than smoothing them away.
- It produced a reusable methodology scaffold for future private or wearable jaw-EMG work.

## Glossary
- `CAP`: the PhysioNet CAP Sleep Database.
- `brux1`, `brux2`: the only public bruxism-positive CAP subjects used here.
- `n1`, `n2`, `n3`, `n5`, `n11`: the bounded admitted controls under the repo’s current contract.
- `EMG1-EMG2`: the primary benchmark channel.
- `C4-P4`: the comparison channel.
- `SLEEP-S2`: stage-2 sleep windows selected from annotation sidecars.
- `MCAP-A1`, `MCAP-A3`: CAP micro-event family filters used for window selection, not bruxism labels.
- `A1-only`, `A3-only`: exclusive event-family overlap rules used in later passes.
- `LOSO`: leave-one-subject-out cross-validation, the main honest evaluation surface.
- random-window CV: the leakage-prone reference surface kept only for comparison.
- record-relative: within-record robust normalization on a bounded feature set.
- shape features: `skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`.
- event trio: `evt_active_fraction`, `evt_burst_duration_median_s`, `evt_interburst_gap_median_s`.
- no-shape exclusions: train-time removal of the four shape features above.
- percentile-band selector: per-subject time-aware downselection using `q=[0.10, 0.90]` and fixed per-subject caps.

## Hard ceiling that shaped the whole project
Public CAP never offered more than two honest bruxism-positive subjects for this branch. That is the key scientific constraint behind every later decision. Control-side expansion was possible. Positive-side expansion was not. [[bruxism-cap-source-audit-cap-expansion-2026-05-06]]

## Key benchmark anchors
| Pass | Subject set | Family | Channel | Balanced acc. | Sensitivity | Specificity | Margin | Read |
|---|---|---|---|---:|---:|---:|---:|---|
| `pass42` | `brux1, brux2, n3, n5, n11` | repaired `A1-only` | `EMG1-EMG2` | `0.750` | `0.500` | `1.000` | `+0.339` | strongest repaired `A1-only` anchor |
| `pass45` | `brux1, brux2, n3, n5, n11` | repaired `A3-only` no-shape | `EMG1-EMG2` | `0.750` | `0.500` | `1.000` | `+0.295` | strongest repaired `A3-only` anchor |
| `pass47` | `brux1, brux2, n1, n2, n3, n5, n11` | repaired `A3-only` no-shape | `EMG1-EMG2` | `0.750` | `0.500` | `1.000` | `+0.335` | ambiguity survived first control expansion |
| `pass48` | `brux1, brux2, n1, n2, n3, n5, n11` | repaired `A1-only` no-shape | `EMG1-EMG2` | `0.400` | `0.000` | `0.800` | `-0.302` | closure artifact |

## Final closure read
The branch stayed alive through `pass47` because repaired `A3-only` preserved specificity under the first bounded control expansion. The final matched repaired `A1-only` control-expanded replication in `pass48` then answered the last meaningful question in the negative direction:
- both bruxism subjects stayed below threshold
- `n2` reopened as a false positive at `0.614`
- subject-level balanced accuracy fell from `0.750` to `0.400`
- the best-bruxism-minus-highest-control margin flipped from `+0.335` to `-0.302`

That means the public CAP branch should now be treated as complete rather than extended through more micro-passes. [[bruxism-cap-pass47-control-expanded-rerun-2026-05-06]] [[bruxism-cap-pass47-control-expanded-branch-verdict-2026-05-06]] [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]]

## Project history in one paragraph
The early project learned that random-window CV was highly misleading. The middle project hardened around `SLEEP-S2`, event-family filtering, matched family comparisons, repaired time-aware selection, record-relative representation, and compact event-conditioned features. The late project found two real but partial repaired anchors: `pass42` on repaired `A1-only` and `pass45`/`pass47` on repaired `A3-only`. The final matched repaired `A1-only` control-expanded replication (`pass48`) then showed that the benchmark ceiling had been reached. [[bruxism-cap-first-baseline-lessons-2026-05-03]] [[bruxism-cap-exclusive-a1-vs-a3-matched14-2026-05-04]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]] [[bruxism-cap-pass45-honest-benchmark-verdict-2026-05-05]]

## Successor direction
Do not keep running new CAP micro-passes. Preserve CAP as the completed public scaffold, and shift active future work toward the privacy-preserving wearable jaw-EMG branch and the broader data/measurement roadmap. [[bruxism-cap-privacy-pets-roadmap-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]

## Best pages to read next
- [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]] — final closure page
- [[bruxism-cap-source-audit-cap-expansion-2026-05-06]] — positive-set ceiling and admissible expansion constraints
- [[bruxism-cap-next-data-strategy-2026-05-06]] — post-closure strategic direction
- [[bruxism-cap-first-baseline-lessons-2026-05-03]] — earliest leakage and measurement lesson
- [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]] — repaired scaffold turning point
