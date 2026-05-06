---
title: Bruxism CAP privacy threat-model activation memo (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, workflow, infrastructure, notes, experiment]
sources:
  - ../projects/bruxism-cap/reports/privacy-threat-model-cap-to-wearable-transition-2026-05-05.md
  - queries/bruxism-cap-privacy-pets-roadmap-2026-05-05.md
  - queries/bruxism-cap-campaign-handoff-2026-05-05.md
  - concepts/bruxism-cap.md
---

# Question
After the repo-specific privacy threat-model memo was completed, what durable project conclusions should the wiki preserve about why the privacy branch was activated now, what the memo concluded, what stays on the benchmark loop, and the exact gate for the next privacy task?

# Short answer
Activate the privacy branch now only in memo form, not as a benchmark pivot.

The branch was activated because pass36 answered the campaign's last pre-privacy composition question cleanly enough to preserve repo-specific privacy constraints without pretending the benchmark is finished. The project is still a public CAP benchmark with explicit caveats: `EMG1-EMG2` remains the primary benchmark channel, `pass29 C4-P4` remains the honest comparison anchor, and `brux1` remains the unresolved benchmark bottleneck. [[bruxism-cap]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]

# Why the privacy branch was activated now

## 1. The campaign gate changed after pass36
The earlier campaign handoff said privacy/PET work should wait until one more bounded benchmark question was answered. Pass36 answered that question narrowly: the pass34 record-relative and pass35 compact-shape clues do compose honestly on the repaired five-subject scaffold, but only partially, because `brux2` recovers while `brux1` still fails.

That is enough to justify one preservation-grade privacy memo now. It is not enough to claim the benchmark is done, to demote the benchmark caveats, or to start pretending the repo already operates a private wearable pipeline. [[bruxism-cap-campaign-handoff-2026-05-05]] [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]]

## 2. The activation is additive, not a replacement branch
The durable read is:
- activate exactly one bounded privacy branch artifact now: the repo-specific threat-model and transition memo
- keep the main modeling loop on the current CAP benchmark
- keep negative and cautionary privacy findings as first-class results rather than waiting for a prototype

This follows the roadmap rule from [[bruxism-cap-privacy-pets-roadmap-2026-05-05]]: strategic privacy material belongs in the wiki first, then moves to kanban only one bounded task at a time.

# What the memo concluded

## 1. The privacy boundary appears immediately once the data stops being public CAP
The memo's main warning is that the project posture changes sharply as soon as the repo would ingest user-specific or wearable jaw EMG. At that point, not only raw waveforms but also timestamps, dense per-window feature tables, subject-score tables, device/app metadata, and later model updates become health-data-bearing artifacts.

So the repo should not carry over its current CAP habit of saving dense CSV/JSON/report artifacts into a private-user setting by default. [[bruxism-cap]] [[bruxism-cap-privacy-pets-roadmap-2026-05-05]]

## 2. Raw waveform and dense timing structure should stay local
The memo treats the following as local-by-default surfaces for any future wearable branch:
- raw jaw-EMG waveforms and long segments
- exact per-window timestamps and event-aligned selections
- full per-night window-level feature tables
- personalized calibration state and dense debug plots
- stable identifiers or per-subject score dumps that could act like biometric traces

This is a cautionary result, not just a design preference: the same feature families that help the benchmark (`mean`, `ptp`, `zero_crossing_rate`, envelope statistics, shape descriptors, record-relative summaries) are exactly the ones likely to preserve person- and night-specific information. [[bruxism-cap]]

## 3. The first off-device layer should be minimized summaries, not CAP-style exports
If anything leaves device first, it should be coarse nightly, weekly, or cohort summaries with strong minimization rather than raw waveform or dense pass-style tables. The memo's recommended bridge is a minimized export surface such as nightly risk bins, wear-time bins, clipped counts, and cohort-gated aggregates.

Just as important, the memo preserves two negative findings as first-class project knowledge:
- derived features are not automatically safe just because they are not raw waveform
- federated learning or PET language does not erase leakage from updates, small cohorts, or reconstructive exports

# What stays on the current benchmark loop
The privacy memo does not replace the active benchmark loop. The durable benchmark commitments remain:
- CAP stays the public reproducible benchmark scaffold
- `EMG1-EMG2` stays the primary benchmark channel
- `pass29 C4-P4` stays the honest comparison anchor
- benchmark caveats stay explicit, especially that `brux1` still fails on the repaired five-subject scaffold
- the next benchmark-side question remains localization of the remaining `brux1` bottleneck rather than another broad pivot

So the right project framing is two-track but asymmetric: one preserved privacy memo now, and the main ongoing loop still on the benchmark side. [[bruxism-cap]] [[bruxism-cap-campaign-handoff-2026-05-05]]

# Exact next privacy task gate
Do not broaden immediately into federated learning, product architecture, or multi-task privacy implementation.

The exact next privacy task is already named by the memo:
- `privacy: design a minimized off-device export schema for future wearable bruxism-cap experiments`

But that task should clear only after the current benchmark reaches a handoff or temporary stabilization point following the bounded post-pass36 `brux1` localization loop. In other words:
1. preserve the threat-model conclusions now
2. keep the live benchmark loop focused on the remaining `brux1` bottleneck
3. once that benchmark subloop is handed off or temporarily stabilized, promote the export-schema memo as the next privacy task

That preserves the roadmap's one-task-at-a-time discipline while preventing the privacy branch from drifting back into a vague someday idea. [[bruxism-cap-privacy-pets-roadmap-2026-05-05]] [[bruxism-cap-campaign-handoff-2026-05-05]]
