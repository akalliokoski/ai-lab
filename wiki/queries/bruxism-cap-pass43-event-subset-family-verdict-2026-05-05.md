---
title: Bruxism CAP pass43 event-subset family verdict
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass43-event-subset-family-verdict-2026-05-05.md
  - bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05.md
  - bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05.md
---

# Bruxism CAP pass43 event-subset family verdict

Question: after the pass43 transfer audit, what should the board preserve as the durable verdict about the fixed 3-feature event subset across repaired `A1-only` and old matched14 `A3-only` `EMG1-EMG2` surfaces? [[bruxism-cap]] [[bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05]] [[bruxism-cap-pass42-same-table-event-subset-ablation-2026-05-05]]

## Answer in one sentence
The most honest label is `scaffold-bound`: the exact same event subset is not just repaired-`A1` noise because it carries some directional signal onto `A3`, but it still does not transfer as an honest subject-level benchmark win beyond the repaired `A1-only` scaffold. [[bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05]]

## What was compared
- pass36 repaired `A1-only` EMG scaffold: first repaired percentile-band / time-aware `EMG1-EMG2` surface with honest subject-level sensitivity recovery, but only through `brux2`
- pass42 repaired `A1-only` event-subset anchor: the pass36 scaffold plus exactly `evt_active_fraction`, `evt_burst_duration_median_s`, and `evt_interburst_gap_median_s`
- pass14 old matched14 `A3-only` EMG baseline: closest pre-existing `A3-only` matched surface before the transfer check
- pass43 old matched14 `A3-only` transfer run: the pass14 table plus the exact same three event features, with no broader feature or model-family change
- pass29 `C4-P4` comparator context: stronger non-EMG honest anchor that still matters when judging whether EMG has really become the benchmark leader

## Preserved verdict
Verdict: `scaffold-bound`.

Why this is the right label:
1. Not `A1-specific`: on the old `A3-only` surface, `brux1` holds at `0.176`, `brux2` rises from `0.074` to `0.130`, and both `n3` and `n5` move downward versus pass14.
2. Not `A3-transferable`: the honest subject-level endpoint stays flat on `A3` at `0.500` balanced accuracy and `0.000` sensitivity, and the best control still outranks the best bruxism subject.
3. Stronger than `family-ambiguous`: the dominant confound is scaffold mismatch, because the current comparison is still repaired `A1-only` (`50` rows) versus older matched14 `A3-only` (`70` rows) on the same channel family.
4. So the subset currently looks directionally portable but not yet benchmark-portable.

## Negative findings that matter
- Honest transfer still fails on the old `A3-only` surface: sensitivity remains `0/2`, balanced accuracy remains `0.500`, and the best-bruxism-minus-highest-control margin stays negative at `-0.134`.
- The pass42 gain is still threshold-relevant mainly through `brux2`, and that is exactly what does not transfer: `brux2` drops from `0.825` on repaired `A1-only` to `0.130` on the old `A3-only` surface.
- `n11` worsens sharply on `A3` (`0.095 -> 0.310`) even though it stays below threshold, so the subset is not a universally cleaner control separator across families.
- Pass29 `C4-P4` still matters as the broader honest comparator because it reaches the same `0.750 / 0.500 / 1.000` headline while keeping a much healthier `brux1` score (`0.405`). [[bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05]]

## What the literature lane changed in interpretation
The literature/audit lane narrowed the interpretation in both directions.
- It argues against reading the 3 features as pure `A1`-locked artifacts, because burst occupancy, burst duration, and inter-burst gap look like plausible jaw-EMG organization descriptors rather than raw amplitude quirks.
- It also argues against overclaiming family transfer, because in this repo the CAP family filters change row availability, balance, and timing surfaces in addition to physiology.
- Combined with pass43, that shifts the durable story from “did the subset work?” to “did the repaired scaffold matter more than the family label?” [[bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05]]

## Active benchmark interpretation
- Promote pass42 as the active EMG working surface inside the EMG branch: repaired `A1-only` scaffold plus the fixed 3-feature event subset.
- Do not promote pass42/pass43 as a family-general EMG win yet.
- Do not replace the broader comparator context with this branch yet; pass29 `C4-P4` still anchors the stronger non-EMG read. [[bruxism-cap-pass41-vs-honest-anchors-benchmark-upgrade-verdict-2026-05-05]] [[bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05]]

## Exact next bounded step
Keep the same 3-feature event subset fixed and rebuild only the `A3-only` comparison table on the repaired percentile-band / time-aware `EMG1-EMG2` scaffold. That is the smallest next step that can separate true family dependence from old-surface mismatch without opening broader feature search, model-family change, privacy work, or LLM/RL work.

## Gate status
- Privacy branch: still gated.
- LLM/RL branch: still gated.
- Model-family change: still gated.
- Broader feature expansion: still gated. [[bruxism-cap-privacy-threat-model-activation-2026-05-05]] [[bruxism-cap-llm-rl-roadmap-2026-05-05]]

## Artifacts
- Board-level verdict memo: `projects/bruxism-cap/reports/pass43-event-subset-family-verdict-2026-05-05.md`
- Transfer audit page: `wiki/queries/bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05.md`
- Transfer report JSON: `projects/bruxism-cap/reports/pass43-matched-a1-vs-a3-transfer-audit.json`
- Transfer LOSO report: `projects/bruxism-cap/reports/loso-cv-pass43-emg-a3-matched14-eventsubset.json`
