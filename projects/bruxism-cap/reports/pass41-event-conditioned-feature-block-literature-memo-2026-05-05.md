# Pass 41 literature memo — RMMA / event-structured jaw-EMG and one bounded next feature block

Date: 2026-05-05
Status: literature-only synthesis completed after pass40. This memo keeps the CAP benchmark, `EMG1-EMG2` primary channel, repaired five-subject `A1-only` scaffold, and honest LOSO framing fixed, then asks one bounded next-step question: should the next representation move shift from more coarse 30 s summary tweaking toward a compact event-conditioned jaw-EMG block?

## Repo context held fixed
- Current benchmark scaffold to protect: repaired five-subject percentile-band `SLEEP-S2 + MCAP-A1-only` `EMG1-EMG2` surface from pass28 through pass40.
- Current best composed representation: pass36 `record-relative + compact shape`.
- Closed subloop: pass37/pass38/pass39/pass40 showed that the bounded `mean` / `rectified_std` / `envelope_cv` stabilization and earlier-stage floor family softens the catastrophic early `brux1` trio only directionally, not materially.
- Therefore pass41 should not be another same-family companion-floor swap.

## 1) Verified citations with short relevance notes
1. Ikeda T et al. Criteria for the detection of sleep-associated bruxism in humans. Journal of Orofacial Pain. 1996. PMID 9161232.
   - Relevance: classic automated home jaw-EMG paper that explicitly builds event detection around subject-specific thresholds (activity above 3% MVC) and detected bruxism-event counts/durations, supporting event-conditioned and subject-relative representation rather than only coarse fixed-window summaries.

2. Yamaguchi T et al. Validity of single-channel masseteric electromyography by using an ultraminiature wearable electromyographic device for diagnosis of sleep bruxism. Journal of Prosthodontic Research. 2020. PMID 31085074. DOI 10.1016/j.jpor.2019.04.003.
   - Relevance: direct portable jaw-EMG validation reference. Its abstract explicitly uses burst-level rules (>2x baseline amplitude, duration >=0.25 s, plus MVC-relative variants) and reports episode/hour operating characteristics, which is exactly the kind of translational event structure the repo can mimic in a bounded handcrafted way.

3. Raphael KG et al. Instrumental assessment of sleep bruxism: A systematic review and meta-analysis. Sleep Medicine Reviews. 2024. PMID 38295573. DOI 10.1016/j.smrv.2024.101906.
   - Relevance: strongest recent overview showing portable EMG is the practical sensing direction, but also that thresholds and methodology vary substantially. Good support for testing a compact event block while staying cautious about clinical overclaiming.

4. Ommerborn MA et al. Polysomnographic scoring of sleep bruxism events is accurate even in the absence of video recording but unreliable with EMG-only setups. Sleep and Breathing. 2020. PMCID PMC7426313. DOI 10.1007/s11325-019-01915-2.
   - Relevance: important warning that EMG-only setups are unreliable as full diagnostic gold standards. For this repo that means pass41 can borrow event structure from jaw EMG, but should not collapse into a one-number pseudo-clinical detector.

5. Yamaguchi T et al. Number of masseteric electromyographic waveforms during analysis periods with/without excluding time zones after going to bed and before getting up in sleep bruxism assessment. Cranio. 2026. PMID 40062531. DOI 10.1080/08869634.2025.2473728.
   - Relevance: direct evidence that episode counts depend on the analysis window. This strengthens the case for event-conditioned summaries tied to the repo's explicit kept-window scaffold rather than more generic 30 s aggregates.

6. Tsujisaka A et al. Temporal patterns of bruxism behaviors: multiple day recording with portable electromyography. Scientific Reports. 2026. PMID 41495115. DOI 10.1038/s41598-025-30704-z.
   - Relevance: portable multi-day EMG paper that separates grinding and clenching episodes across nights and hours. Strong translational support for preserving event type / temporal structure rather than only bulk activity magnitude.

7. Smardz J et al. A case-control study on the effect of rhythmic masticatory muscle activity (RMMA) clusters on sleep fragmentation and severity of orofacial muscle pain in sleep bruxism. Journal of Sleep Research. 2024. PMID 37859534. DOI 10.1111/jsr.14072.
   - Relevance: strongest direct RMMA-structure paper in this pass. It distinguishes single events, pairs, and clusters and studies cluster burden specifically, which argues for episode-conditioned density summaries instead of another undifferentiated 30 s feature tweak.

8. Wieckiewicz M et al. Moving beyond bruxism episode index: Discarding misuse of the number of sleep bruxism episodes as masticatory muscle pain biomarker. Journal of Sleep Research. 2025. PMID 39134874. DOI 10.1111/jsr.14301.
   - Relevance: direct caution against replacing the current feature table with one crude episode index. If pass41 moves toward events, it should use a small multi-feature event block, not a single event-rate surrogate.

Optional but supportive device-context citations already aligned with the above:
- Takaesu Y et al. Diagnostic Accuracy of a Portable Electromyography and Electrocardiography Device to Measure Sleep Bruxism in a Sleep Apnea Population. Clocks & Sleep. 2023. PMID 37987398. DOI 10.3390/clockssleep5040047.
- Raphael KG et al. Ambulatory devices to detect sleep bruxism: a narrative review. Australian Dental Journal. 2024. PMID 39976111. DOI 10.1111/adj.13057.

## 2) Explicit verdict: should the next representation step move to burst / event-conditioned summaries?
Yes — but only in one bounded appended block, not as a wholesale rewrite.

Why this is now the best next step:
1. Repo evidence: pass37 through pass40 exhausted the smallest same-family fixes inside coarse record-relative amplitude summaries. They softened the early `brux1` collapse without producing a threshold-relevant rescue.
2. Literature evidence: classic and portable jaw-EMG papers define the phenomenon through burst/event logic, thresholds, durations, and episode grouping; RMMA work also highlights clusters, not just coarse background level.
3. Guardrail evidence: the 2025 episode-index paper argues against reducing the whole problem to one count, and the EMG-only reliability paper argues against pretending event counts are a clinical ground truth. So the right move is a compact event-conditioned block appended to the current pass36 representation, not a one-number detector and not a dataset/model pivot.

Decision framing:
- Move from "more tweaks to coarse 30 s amplitude summaries" to "append one event-conditioned jaw-EMG block on top of pass36".
- Keep the current pass36 raw/record-relative/shape backbone and LOSO audit surface unchanged.
- Evaluate whether the event block specifically helps the remaining `brux1` early-trio failure without reopening `n3` or harming `brux2`.

## 3) One smallest pass41 feature block
### Pass41 concept
Append one compact event-conditioned block to the existing pass36 table. Do not replace the current retained features. Do not change selector rows, labels, subjects, exclusions, model family, or evaluation contract.

### Proposed event logic
Signal basis:
- Channel: `EMG1-EMG2` only.
- Start from the same centered / rectified waveform already used for `rectified_*` and envelope features in `features.py`.
- Smooth envelope remains the same 0.2 s moving average used by the current pipeline.

Burst candidate rule:
- Active sample if rectified amplitude >= max(2.0 * record-median-rectified, record-median-rectified + 2.0 * record-MAD-rectified, 1e-6).
- Burst = contiguous active run lasting >=0.25 s.
- Merge gaps shorter than 0.08 s inside one burst to avoid fragmentation from tiny crossings.

Episode grouping rule:
- Episode = one or more bursts where adjacent bursts are separated by <3.0 s.
- Episode subtype labels for summary only:
  - phasic-like episode: >=3 constituent bursts and each burst duration in [0.25 s, 2.0 s]
  - tonic-like episode: any constituent burst duration >2.0 s
  - mixed-like episode: meets phasic-like condition and also contains a >2.0 s burst

### Exact candidate features for the pass41 block
Keep this block to 7 appended features:
1. `evt_burst_count_30s`
   - number of detected bursts in the 30 s window.
2. `evt_episode_count_30s`
   - number of grouped episodes in the window.
3. `evt_bursts_per_episode_mean`
   - burst-count density inside detected episodes; 0 if no episode.
4. `evt_active_fraction`
   - fraction of the 30 s window covered by burst-active samples.
5. `evt_burst_duration_median_s`
   - median burst duration; 0 if no burst.
6. `evt_interburst_gap_median_s`
   - median within-episode inter-burst gap; use 3.0 if undefined.
7. `evt_phasic_like_episode_fraction`
   - fraction of episodes in the window that are phasic-like; 0 if no episode.

Why this exact block:
- It captures count, density, duration, spacing, and RMMA-like phasic structure.
- It stays small enough to interpret fold-by-fold against the pass36 early `brux1` trio.
- It avoids the clinically over-strong move of replacing the whole representation with one episode index.

### Recommended transform / integration shape
- Compute these seven features per 30 s kept window during feature extraction.
- For the four magnitude-like event features (`evt_burst_count_30s`, `evt_episode_count_30s`, `evt_bursts_per_episode_mean`, `evt_active_fraction`), add record-relative companion versions using the same per-subject median/MAD style as pass34 if needed, but only after first trying the raw event block.
- First pass41 audit should be `pass36` vs `pass36 + event block`, not raw-event-only and not event-block-with-more-floor-tuning.

### Success criteria
Same honest surface as the recent passes:
- subject-level LOSO balanced accuracy / sensitivity / specificity
- `brux1 - n3` gap
- best-bruxism-minus-highest-control margin
- early `brux1` ranks 1-3 mean score and mean contribution block, to test whether the new block specifically softens the catastrophic trio

## 4) Two rejected ideas and why
1. Rejected idea: another same-family `mean` / `rectified_std` / `envelope_cv` floor or cap variant.
   - Why rejected: pass37 through pass40 already answered that family. It can soften the early trio directionally, but it does not rescue `brux1` materially and now risks turning the benchmark into repetitive micro-tuning.

2. Rejected idea: replacing pass41 with one coarse episode/hour or bruxism-index feature.
   - Why rejected: RMMA cluster and episode-index papers argue that event structure is richer than a single count, while EMG-only scoring reliability cautions against treating that one number as a gold-standard proxy. The next move should therefore be a compact event-conditioned block, not a one-number detector.

## 5) Exact repo files likely to change
Most likely:
- `projects/bruxism-cap/src/features.py`
  - add one reusable jaw-EMG event helper and emit the 7-event pass41 block.
- `projects/bruxism-cap/src/prepare_windows.py`
  - only if feature extraction is wired there and the new event columns should be generated alongside the existing window feature CSVs.
- `projects/bruxism-cap/src/run_pass41_event_conditioned_feature_block_audit.py`
  - new bounded audit script cloned structurally from pass34/pass36/pass37-style runners.
- `projects/bruxism-cap/src/audit_pass36_brux1_vs_n5_n11.py`
  - likely useful as the fold-by-fold interpretation helper for checking whether the event block specifically changes the early `brux1` trio and `n5`/`n11` gaps.
- `projects/bruxism-cap/src/train_baseline.py`
  - probably unchanged, unless any new metadata-like helper columns are emitted and need exclusion protection.

## Bottom line
The fresh verified literature pass supports one bounded move outside the now-closed pass37-pass40 floor subloop: append a compact event-conditioned jaw-EMG block that respects RMMA burst/episode structure and portable-EMG practice, while keeping the CAP scaffold and honest LOSO interpretation unchanged. The smallest credible pass41 is `pass36 + 7 event-conditioned features`, not another same-family floor tweak, not a one-number episode index, and not a deep-model rewrite.
