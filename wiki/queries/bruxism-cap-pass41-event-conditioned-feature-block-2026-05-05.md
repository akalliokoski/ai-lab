---
title: Bruxism CAP pass41 event-conditioned feature block literature memo
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, experiment, evaluation, notes]
sources:
  - raw/articles/sleep-bruxism-detection-criteria-ikeda-1996.md
  - raw/articles/portable-masseter-emg-validity-2019.md
  - raw/articles/sleep-bruxism-portable-emg-meta-analysis-2024.md
  - raw/articles/sleep-bruxism-emg-only-setups-2020.md
  - raw/articles/sleep-bruxism-analysis-window-portable-emg-2026.md
  - raw/articles/portable-emg-temporal-patterns-2026.md
  - raw/articles/rmma-clusters-sleep-fragmentation-pain-2024.md
  - raw/articles/sleep-bruxism-episode-index-misuse-2025.md
---

# Bruxism CAP pass41 event-conditioned feature block literature memo

Historical note: this page records the literature logic that justified the pass41 event-conditioned feature block at the time. That branch later became part of the broader repaired-scaffold history and is now preserved as benchmark archaeology rather than a live representation proposal. [[bruxism-cap-pass48-control-expanded-a1-replication-2026-05-06]] [[bruxism-cap]]

Question: after pass40 closed the bounded `envelope_cv` companion-floor subloop, what was the smallest source-verified next representation step that still fit the repo's fixed CAP scaffold? [[bruxism-cap]] [[bruxism-cap-pass40-envelope-cv-rectified-std-scale-floor-audit-2026-05-05]]

## Answer in one sentence
Yes: the next representation step should move toward burst / event-conditioned jaw-EMG summaries, but only as one compact appended block on top of pass36 rather than as a detector rewrite, dataset switch, or deep model pivot. [[bruxism-cap-record-relative-shape-composition-audit-2026-05-05]] [[bruxism-cap-pass40-envelope-cv-rectified-std-scale-floor-audit-2026-05-05]]

## Why the literature now points there
The recent same-family repo loop already showed that coarse 30 s amplitude-summary tweaks are close to exhausted: pass37 through pass40 can soften the catastrophic early `brux1` trio, but they do not produce a threshold-relevant rescue.^[projects/bruxism-cap/reports/pass40-envelope-cv-rectified-std-scale-floor-audit.md]

The fresh literature pass points toward event structure instead. Classic home jaw-EMG automation used subject-specific event thresholds rather than only coarse window means.^[raw/articles/sleep-bruxism-detection-criteria-ikeda-1996.md] Portable validation work also used burst rules (`>2x` baseline amplitude, duration `>=0.25 s`) and episode-style counts rather than generic 30 s morphology alone.^[raw/articles/portable-masseter-emg-validity-2019.md] RMMA literature further distinguishes single events, pairs, and clusters, which is stronger support for event-conditioned summaries than for another undifferentiated aggregate tweak.^[raw/articles/rmma-clusters-sleep-fragmentation-pain-2024.md]

At the same time, the literature warns against overclaiming. EMG-only setups are unreliable as a clinical gold standard, so the repo should not collapse into a pseudo-diagnostic event counter.^[raw/articles/sleep-bruxism-emg-only-setups-2020.md] And the newer episode-index critique argues against treating one count metric as the meaningful representation by itself.^[raw/articles/sleep-bruxism-episode-index-misuse-2025.md]

## Smallest pass41 block
Append 7 event-conditioned features to the unchanged pass36 table:
- `evt_burst_count_30s`
- `evt_episode_count_30s`
- `evt_bursts_per_episode_mean`
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`
- `evt_phasic_like_episode_fraction`

Recommended rough event logic:
- detect active samples on rectified `EMG1-EMG2` using a record-relative threshold `max(2.0 * median_rectified, median_rectified + 2.0 * MAD_rectified, 1e-6)`
- keep bursts lasting `>=0.25 s`
- merge micro-gaps shorter than `0.08 s`
- group bursts into episodes when inter-burst gap is `<3.0 s`
- mark an episode phasic-like when it contains `>=3` bursts and each burst lasts `0.25-2.0 s`

This keeps the move bounded, physiologically interpretable, and directly aligned with the remaining `brux1` early-window failure surface. [[bruxism-cap]] [[bruxism-cap-brux1-localization-after-pass36-2026-05-05]]

## Explicit rejected ideas
1. Another `mean` / `rectified_std` / `envelope_cv` floor or cap variant.
   - Rejected because pass37 through pass40 already closed that exact same-family loop without a material `brux1` rescue. [[bruxism-cap-pass37-tiny-amplitude-stabilization-audit-2026-05-05]] [[bruxism-cap-pass40-envelope-cv-rectified-std-scale-floor-audit-2026-05-05]]
2. Replacing the current feature table with one episode/hour index.
   - Rejected because RMMA cluster work and the episode-index critique both imply that event structure is richer than one crude count, while EMG-only reliability limits still make a one-number detector too strong a claim. [[bruxism-cap]]

## Exact likely repo touchpoints
- `projects/bruxism-cap/src/features.py`
- `projects/bruxism-cap/src/prepare_windows.py`
- `projects/bruxism-cap/src/run_pass41_event_conditioned_feature_block_audit.py`
- likely reuse of `projects/bruxism-cap/src/audit_pass36_brux1_vs_n5_n11.py` for fold interpretation

## Artifact
Detailed repo memo: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-literature-memo-2026-05-05.md`
