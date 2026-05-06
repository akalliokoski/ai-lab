---
title: Bruxism CAP dataset decision rubric (2026-05-06)
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - queries/bruxism-better-project-and-data-options-2026-05-04.md
  - queries/bruxism-cap-translational-framing-check-2026-05-05.md
  - queries/bruxism-cap-campaign-handoff-2026-05-05.md
  - ../projects/bruxism-cap/README.md
  - ../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md
  - ../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md
  - ../projects/bruxism-cap/reports/methodology-review-dataset-decision-rubric-2026-05-06.md
---

# Question
How should `bruxism-cap` decide whether to remain a tiny CAP pilot, expand within CAP, or pivot to a new dataset branch, given the current repaired-benchmark state? [[bruxism-cap]] [[bruxism-better-project-and-data-options-2026-05-04]] [[bruxism-cap-translational-framing-check-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]

# Short answer
Use a science-first weighted rubric that treats positive-label validity and tiny-`N` honesty as harder constraints than raw dataset size, model ambition, or wearable trendiness.

Right now the correct outcome is not a dataset pivot. It is to keep the project inside CAP while continuing the benchmark narrowly and honestly. [[bruxism-cap-campaign-handoff-2026-05-05]]

# Current project-state read
The repo is not at dataset exhaustion yet.

What is true now:
- CAP remains the only clearly open, already-runnable corpus in the repo.
- `EMG1-EMG2` remains the right primary signal family for translational alignment, even though CAP is still only a bounded proxy benchmark.^[queries/bruxism-better-project-and-data-options-2026-05-04.md]^[queries/bruxism-cap-translational-framing-check-2026-05-05.md]
- The strongest honest repaired surfaces still stop at subject-level sensitivity `0.500`, with the main learning happening on paired subject-score surfaces rather than on headline count changes.^[../projects/bruxism-cap/reports/pass45-honest-benchmark-verdict-2026-05-05.md]^[../projects/bruxism-cap/reports/pass46-honest-benchmark-verdict-2026-05-05.md]
- The branch's active bottleneck is still benchmark maturity inside the repaired CAP scaffold, not the absence of any scientifically coherent next bounded experiment.^[queries/bruxism-cap-campaign-handoff-2026-05-05.md]

So the next dataset decision should be judged by validity gain per unit complexity, not by novelty alone.

# Weighted dataset-decision rubric
Score each candidate from `0` to `5` on each criterion, then apply the weight. Maximum total = `100`.

## 1. Positive-label validity — weight `25`
Highest priority. Prefer datasets whose positive labels are better anchored to PSG-grade or otherwise auditable bruxism definitions. A larger but weaker-label corpus should lose here.

## 2. Jaw-muscle relevance — weight `20`
Prefer direct jaw-muscle EMG or a similarly validated jaw-activity signal. This repo is already committed to an EMG-first scientific framing.^[queries/bruxism-better-project-and-data-options-2026-05-04.md]

## 3. Subject-level evaluation honesty — weight `20`
Prefer datasets that genuinely support grouped subject-held-out evaluation, explicit subject identities, and honest uncertainty reporting. This repo should never trade that away for easier window-level wins.

## 4. Ecological validity — weight `12`
Prefer home / wearable / multi-night behavior when available, but only after label validity and honesty are protected.^[queries/bruxism-cap-translational-framing-check-2026-05-05.md]

## 5. Openness and reproducibility — weight `10`
Prefer openly downloadable corpora with stable access and enough documentation for another person to rerun the benchmark.

## 6. Portability toward future wearable work — weight `8`
Prefer datasets whose signal family, event logic, or audit methods will still transfer when the repo later moves toward private wearable jaw EMG.

## 7. Implementation tractability — weight `5`
Prefer bounded bring-up cost, but keep this last. Convenience should not outrank scientific grounding.

# Outcome thresholds
## Stay-on-CAP pilot
Choose this if no candidate reaches `70/100`, or if no candidate clearly beats CAP on positive-label validity, or if the candidate improves ecology while weakening openness or subject-level honesty.

## Expand-within-CAP
Choose this if CAP still wins or roughly ties on the weighted rubric and there remains one meaningful within-CAP validity move. This is the best fit for the repo right now: keep the corpus fixed, keep the evaluation contract fixed, and continue narrow repaired-scaffold work. [[bruxism-cap-campaign-handoff-2026-05-05]]

## Pivot-to-new-dataset
Require all of these:
- weighted score at least `80/100`
- at least `12` points better than CAP overall
- at least `4/5` on positive-label validity
- at least `4/5` on jaw-muscle relevance
- no worse than CAP on subject-level evaluation honesty
- real runnable access now, not only a good paper narrative

# What matters most now versus later
## Most important now
1. Positive-label validity
2. Subject-level evaluation honesty
3. Jaw-muscle relevance
4. Openness / reproducibility

This matches the repo's present maturity: the benchmark is still proving its honesty contract, so a less transparent dataset would be backward motion even if it looked more modern.

## More important later
1. Ecological validity
2. Portability toward wearable / privacy-aware work
3. Larger-scale implementation tractability

These should shape the later branch once the current benchmark has either stabilized or been clearly outclassed.

# Seductive but weak criteria to reject explicitly
Do not let the decision be driven by:
- bigger raw `N` without stronger positive labels
- more rows when real positive-subject support stays tiny
- GPU/deep-model temptation
- wearable/intervention trendiness without open reproducible data
- window-level accuracy without subject-held-out survival
- proprietary-device prestige or on-request-only access

Those would create fake progress for this repo.

# Recommendation
Do not open a new dataset branch yet.

The correct durable label is: expand within CAP, not pivot away from CAP. Keep the framing EMG-first, keep tiny-`N` honesty primary, and require evidence-gated branch opening rather than literature-gated aspiration.

# One evidence demand before opening any new dataset branch
Require a one-page evidence pack proving all four:
1. exact access path and license are real now
2. positive-label provenance is materially stronger than CAP's proxy surface
3. jaw-muscle signal relevance is at least as direct as `EMG1-EMG2`
4. the dataset supports a subject-held-out evaluation contract at least as honest as grouped `LOSO`

If that pack is missing, keep the candidate in wiki/planning form only.

# Exact files likely to touch next
If this recommendation holds, the next likely files are:
1. `projects/bruxism-cap/src/run_pass47_repaired_a3_event_trio_swap_phasic_fraction.py`
2. `projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-pct10-90-record-relative-eventsubset-no-shape-phasic-swap.json`
3. `projects/bruxism-cap/reports/pass47-repaired-a3-event-trio-swap-phasic-fraction.json`
4. `projects/bruxism-cap/reports/pass47-repaired-a3-event-trio-swap-phasic-fraction.md`
5. `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.json`
6. `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.md`
7. `projects/bruxism-cap/reports/campaign-handoff-2026-05-05.md`
8. `wiki/concepts/bruxism-cap.md`

# Bottom line
The repo should not switch datasets just because a candidate is bigger, newer, or more fashionable. It should switch only when a candidate clearly improves label validity and jaw-muscle relevance without weakening tiny-`N` honesty or reproducibility.

Under that rule, the current answer is restraint: keep CAP, keep the benchmark EMG-first, and keep future non-CAP branches evidence-gated rather than aspiration-gated.
