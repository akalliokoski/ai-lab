# Pass 45 — source-verified jaw-EMG burst-organization literature memo for the repaired cross-family scaffold

Date: 2026-05-05
Status: literature-only review completed after pass44. This memo keeps the CAP benchmark framing, `EMG1-EMG2` primary channel, repaired five-subject cross-family scaffold, and current LOSO evaluation contract fixed. The question is not whether to switch datasets or models; it is whether a very small burst-organization or episode-summary increment could improve the current repaired `pass42/pass44` surface.

## Repo state held fixed before reading the literature
- `pass42` on repaired `A1-only` kept exactly three event features: `evt_active_fraction`, `evt_burst_duration_median_s`, `evt_interburst_gap_median_s`.
- `pass44` rebuilt repaired `A3-only` on the same time-aware scaffold and recovered the same honest subject-level headline as `pass42`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`.
- The remaining repaired-scaffold bottleneck is now asymmetric by family: on repaired `A3-only`, `brux1` is recovered (`0.532`) but `brux2` collapses (`0.123`), while controls remain below threshold.
- So the right literature question is narrower than "add more EMG features": which temporal-organization idea is small enough to fit this repo and specifically plausible for the unresolved `brux2`-on-`A3` miss without sacrificing the repaired control surface or the new `brux1` gain?

## 1) Verified papers/sources most relevant to burst organization

### 1. Ikeda T et al. Criteria for the detection of sleep-associated bruxism in humans.
- Journal: Journal of Orofacial Pain
- Year: 1996
- PMID: 9161232
- DOI: not listed in PubMed fetch
- Why it matters here: classic home masseter-EMG paper. The abstract explicitly frames sleep bruxism detection through subject-specific thresholds and event counts/durations rather than only coarse fixed-window averages. This directly supports keeping subject-relative burst summaries in the scaffold.

### 2. Lavigne GJ et al. Rhythmic masticatory muscle activity during sleep in humans.
- Journal: Journal of Dental Research
- Year: 2001
- PMID: 11332529
- DOI: 10.1177/00220345010800020801
- Why it matters here: direct RMMA organization reference. The abstract defines RMMA episodes as three or more consecutive masseter-EMG bursts and distinguishes normal low-frequency RMMA from sleep bruxism. This is the strongest source-level rationale for adding one cluster/episode-organization term rather than only per-window occupancy and median duration.

### 3. Yamaguchi T et al. Validity of single-channel masseteric electromyography by using an ultraminiature wearable electromyographic device for diagnosis of sleep bruxism.
- Journal: Journal of Prosthodontic Research
- Year: 2020
- PMID: 31085074
- DOI: 10.1016/j.jpor.2019.04.003
- Why it matters here: portable jaw-EMG validation paper that still relies on burst rules, thresholding, and episode-style counting logic. It supports a bounded handcrafted event representation inside the current CAP frame.

### 4. Ommerborn MA et al. Polysomnographic scoring of sleep bruxism events is accurate even in the absence of video recording but unreliable with EMG-only setups.
- Journal: Sleep & Breathing
- Year: 2020
- PMID: 31402440
- DOI: 10.1111/j.1365-2842.2008.01897.x
- Why it matters here: guardrail source. It supports using event structure as a benchmark feature family, but warns against overclaiming from EMG-only event counts as if they were a clinical gold standard. In repo terms: use episode organization as a bounded discriminative feature, not as a one-number pseudo-diagnostic endpoint.

### 5. Raphael KG et al. Instrumental assessment of sleep bruxism: A systematic review and meta-analysis.
- Journal: Sleep Medicine Reviews
- Year: 2024
- PMID: 38295573
- DOI: 10.1016/j.smrv.2024.101906
- Why it matters here: strongest recent summary showing portable EMG is the practical sensing direction, but methodology and thresholds vary substantially across studies. This argues for one narrow feature increment with strong auditability, not a broad feature explosion.

### 6. Smardz J et al. A case-control study on the effect of rhythmic masticatory muscle activity (RMMA) clusters on sleep fragmentation and severity of orofacial muscle pain in sleep bruxism.
- Journal: Journal of Sleep Research
- Year: 2024
- PMID: 37859534
- DOI: 10.1111/jsr.14072
- Why it matters here: directly relevant cluster paper. The abstract distinguishes single events, pairs, and clusters. This is the strongest source-specific reason to test one compact cluster-density or bursts-per-episode feature on top of the already validated `pass42/pass44` trio.

### 7. Wieckiewicz M et al. Moving beyond bruxism episode index: Discarding misuse of the number of sleep bruxism episodes as masticatory muscle pain biomarker.
- Journal: Journal of Sleep Research
- Year: 2025
- PMID: 39134874
- DOI: 10.1111/jsr.14301
- Why it matters here: explicit warning against collapsing the phenomenon into one crude episode index. For this repo, that means raw `evt_episode_count_30s` should not be the first rescue move; if anything is added, it should be a small organization descriptor that complements the current trio.

### 8. Tsujisaka A et al. Temporal patterns of bruxism behaviors: multiple day recording with portable electromyography.
- Journal: Scientific Reports
- Year: 2026
- PMID: 41495115
- DOI: 10.1038/s41598-025-30704-z
- Why it matters here: multi-day portable EMG paper that emphasizes temporal patterning and the separation of grinding/clenching episodes across time. This supports keeping timing/organization explicit and cautions against treating all active EMG windows as exchangeable.

Supporting but secondary timing-context source:
- Yamaguchi T et al. Number of masseteric electromyographic waveforms during analysis periods with/without excluding time zones after going to bed and before getting up in sleep bruxism assessment. Cranio. 2026. PMID 40062531. DOI 10.1080/08869634.2025.2473728.
- Why secondary: useful confirmation that analysis-period choice changes event counts, which reinforces the repo's repaired time-aware scaffold, but it is less directly informative for the next single feature choice than the RMMA cluster/episode papers above.

## 2) What temporal-organization ideas best fit the existing repaired scaffold?

Best fit, in order:

### A. Keep the current validated trio as the base organization block
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

Why this remains the base:
- It already survived both the same-table pass42 ablation and the repaired A3 rebuild in pass44.
- The literature supports exactly these kinds of descriptors: active occupancy, burst duration, and spacing/gap structure are closer to how jaw-EMG bruxism is operationalized than the older coarse 30 s magnitude-only summaries.
- These three features are the most audit-friendly organization terms already proven not to reopen the repaired control surface.

### B. The best next candidate is one cluster-density / episode-composition term, not a raw count
Recommended candidate: `evt_bursts_per_episode_mean`

Why this is the best literature-backed next idea:
- Lavigne 2001 and Smardz 2024 both make burst grouping and RMMA clustering central, not incidental.
- The current trio captures occupancy, duration, and spacing, but it does not directly encode whether the kept bursts are organized as isolated events or denser multi-burst episodes.
- `evt_bursts_per_episode_mean` is already much closer to the RMMA cluster idea than `evt_burst_count_30s` or `evt_episode_count_30s`, while staying compact and interpretable.

Why not start with raw counts:
- `evt_burst_count_30s` and `evt_episode_count_30s` are more exposed to analysis-period and density confounds.
- Wieckiewicz 2025 is a direct warning against over-trusting one episode index.
- In this repo, raw counts are more likely to track kept-window opportunity or timing-surface differences than the underlying organization signal of interest.

### C. Phasic-like episode fraction is a possible second follow-up, but not the first one
Candidate: `evt_phasic_like_episode_fraction`

Why it is interesting but not first:
- It matches the RMMA literature conceptually.
- On this tiny `10`-windows-per-subject scaffold it is probably sparser and more brittle than bursts-per-episode density.
- The smallest increment should prefer the feature with the strongest organization meaning and the least sparsity risk.

## 3) Could any idea plausibly rescue `brux2` on repaired `A3` without giving up `brux1` or reopening controls?

Short answer: yes, plausibly, but only one idea currently deserves that claim.

Most plausible idea:
- Add exactly one cluster-density term, `evt_bursts_per_episode_mean`, on top of the fixed pass42/pass44 trio and audit it on the repaired cross-family scaffold.

Why this is the most plausible rescue hypothesis:
1. `pass44` already shows that repaired `A3-only` can protect controls and even recover `brux1`; the unresolved miss is now disproportionately `brux2`.
2. That makes a missing organization variable more plausible than a missing generic amplitude variable.
3. The literature repeatedly distinguishes isolated events from grouped RMMA bursts/clusters, which the current trio still only captures indirectly.
4. A one-feature add-back is small enough to test whether `brux2` needs denser episode organization information without reopening the whole pass41 seven-feature bundle.

What would count as success in this repo:
- `brux2` rises materially above the current repaired A3 value (`0.123`), ideally above threshold.
- `brux1` does not fall back below the current repaired A3 gain (`0.532`).
- highest control stays at or below the current repaired A3 control surface (`n11` at `0.395`; no control crosses threshold).

Why I would not promise success:
- The same literature also says episode-style signals are threshold- and timing-sensitive.
- The scaffold is still only `10` windows per subject.
- If the add-back fails, that failure should be read as evidence that the repaired cross-family branch is already near its small-feature limit, not as a reason to reopen the full seven-feature block.

## 4) One smallest feature/audit increment that still fits this repo

Recommended next increment:
- Do one repaired cross-family add-back audit with exactly four event features:
  - keep `evt_active_fraction`
  - keep `evt_burst_duration_median_s`
  - keep `evt_interburst_gap_median_s`
  - add only `evt_bursts_per_episode_mean`

Why this is the smallest credible increment:
- It uses one already-defined feature from the pass41 event family; no dataset, model, privacy, or broad feature rewrite is needed.
- It tests the exact organization concept the literature keeps pointing to: clustered multi-burst episode density.
- It avoids the two literature-backed bad moves: reopening the full seven-feature bundle or collapsing the representation to one raw episode count.

Recommended audit shape:
1. Keep the repaired `A1-only` and repaired `A3-only` scaffolds fixed.
2. Keep the base exclusions, LOSO contract, and subject-level reporting fixed.
3. Evaluate only one add-back: current pass42/pass44 trio plus `evt_bursts_per_episode_mean`.
4. Compare directly against the frozen pass42 and pass44 tables.
5. Gate interpretation on three conditions:
   - `brux2` improvement on repaired `A3-only`
   - no loss of repaired `brux1` on `A3-only`
   - no control reopening on either family

Rejected smallest increments:
- raw `evt_episode_count_30s` add-back: too close to the criticized episode-index shortcut
- full pass41 seven-feature reopen: too wide for the current evidence state
- new waveform family or deep model branch: violates the bounded-scope constraint

## 5) Exact files likely to touch next

If the repo takes the recommended smallest increment, the most likely next files are:
- `projects/bruxism-cap/src/run_pass45_repaired_cross_family_episode_density_audit.py`
  - new bounded runner for the four-feature add-back audit
- `projects/bruxism-cap/src/run_pass44_repaired_a3_event_subset_rebuild.py`
  - likely reference template for rebuilding or reusing the repaired A3 scaffold and merge path
- `projects/bruxism-cap/src/run_pass42_same_table_event_subset_ablation.py`
  - likely reference template for subset bookkeeping and comparison framing
- `projects/bruxism-cap/src/run_pass41_event_conditioned_feature_block_audit.py`
  - likely reuse point for `EVENT_FEATURES`, event-column loading, and merge helpers
- `projects/bruxism-cap/reports/pass45-repaired-cross-family-episode-density-audit.md`
  - next memo/report artifact
- `projects/bruxism-cap/reports/pass45-repaired-cross-family-episode-density-audit.json`
  - next summary JSON artifact

Files that probably do not need to change for this smallest increment:
- `projects/bruxism-cap/src/features.py`
  - only if the audit reveals that the existing `evt_bursts_per_episode_mean` definition is itself too brittle and needs a later extraction rewrite
- `projects/bruxism-cap/src/train_baseline.py`
  - evaluation/reporting contract should stay fixed

## Bottom line
The fresh verified literature no longer points toward another coarse amplitude tweak and does not justify a broad event-feature reopening. It points to one narrower move: preserve the current repaired pass42/pass44 trio as the validated base burst-organization block, then test exactly one RMMA-cluster-style add-back, `evt_bursts_per_episode_mean`, because it is the smallest literature-backed organization term that could still plausibly rescue `brux2` on repaired `A3-only` without sacrificing the repaired `brux1` gain or reopening controls.