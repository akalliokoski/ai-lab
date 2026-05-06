# Pass46 — science review for `evt_bursts_per_episode_mean` as the one-feature add-back

Date: 2026-05-05
Status: bounded literature and repo-contact review completed. This memo answers only one question: on the frozen repaired `pass42/pass45` scaffold, is `evt_bursts_per_episode_mean` the right single feature to add back next, and what should count as pass46 success or failure beyond the tiny-N headline counts?

## Scope held fixed
- keep the repaired five-subject CAP benchmark frame fixed: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep `EMG1-EMG2` as the primary channel
- keep the frozen repaired cross-family anchors fixed: repaired `A1-only` pass42 and repaired `A3-only` pass45
- keep grouped `LOSO`, threshold `0.5`, and the current exact-CI / Brier reporting contract fixed
- do not reopen raw count families, raw episode-index families, selector changes, channel pivots, or model-family changes

## Current repo state that matters
- `pass42` validated the current base event trio: `evt_active_fraction`, `evt_burst_duration_median_s`, `evt_interburst_gap_median_s`.
- `pass45` then improved the repaired `A3-only` surface without changing the honest headline: `brux1` rose to `0.641`, `brux2` rose only to `0.178`, highest control fell to `0.345`, and the repaired `A3-only` best-bruxism-minus-highest-control margin improved to `+0.295`.
- The active unresolved miss is therefore narrow: `brux2` is still below the repaired `A3-only` control surface even after the shape-only clean-up, while `brux1` is already rescued.

## 1) Verified sources most relevant to burst-density or episode-organization proxies

### 1. Ikeda T et al. Criteria for the detection of sleep-associated bruxism in humans.
- Journal: Journal of Orofacial Pain
- Year: 1996
- PMID: 9161232
- DOI: none listed in PubMed
- Verified abstract point: home masseter EMG over 4 nights used a subject-specific threshold at 3% of each subject's MVC and reported mean number and duration of detected bruxism events.
- Why it matters: this is classic direct support for subject-relative event summaries rather than only coarse fixed-window averages.

### 2. Lavigne GJ et al. Rhythmic masticatory muscle activity during sleep in humans.
- Journal: Journal of Dental Research
- Year: 2001
- PMID: 11332529
- DOI: 10.1177/00220345010800020801
- Verified abstract point: RMMA episodes were defined as three or more consecutive masseter-EMG bursts, and bruxers had about twice as many bursts per episode as controls with RMMA.
- Why it matters: this is the strongest direct source-level rationale for `evt_bursts_per_episode_mean` specifically, because the differentiating unit is burst density within an episode.

### 3. Yamaguchi T et al. Validity of single-channel masseteric electromyography by using an ultraminiature wearable electromyographic device for diagnosis of sleep bruxism.
- Journal: Journal of Prosthodontic Research
- Year: 2020
- PMID: 31085074
- DOI: 10.1016/j.jpor.2019.04.003
- Verified abstract point: wearable single-channel masseter EMG scoring compared burst-unit and episode-unit analyses against PSG-AV reference scoring.
- Why it matters: portable jaw-EMG validation still works in burst and episode units, so one compact event-organization add-back remains biologically and translationally coherent.

### 4. Smardz J et al. A case-control study on the effect of rhythmic masticatory muscle activity (RMMA) clusters on sleep fragmentation and severity of orofacial muscle pain in sleep bruxism.
- Journal: Journal of Sleep Research
- Year: 2024
- PMID: 37859534
- DOI: 10.1111/jsr.14072
- Verified abstract point: RMMA events were analyzed as single events, pairs, or clusters; high-cluster subjects had about three times more phasic RMMA events than the noncluster group.
- Why it matters: this keeps cluster structure central and argues that how bursts group inside episodes is a meaningful physiological surface, not a bookkeeping artifact.

### 5. Wieckiewicz M et al. Moving beyond bruxism episode index: Discarding misuse of the number of sleep bruxism episodes as masticatory muscle pain biomarker.
- Journal: Journal of Sleep Research
- Year: 2025
- PMID: 39134874
- DOI: 10.1111/jsr.14301
- Verified abstract point: in 220 adults, correlation, regression, ROC, and prediction analyses did not support bruxism episode index as a useful biomarker for pain intensity.
- Why it matters: this is the key guardrail against reopening `evt_episode_count_30s` first. The field is explicitly warning against collapsing the representation to one crude episode-rate summary.

## 2) Is `evt_bursts_per_episode_mean` the right next one-feature add-back?
Short answer: yes.

### Why it is biologically coherent
In the repo code, `evt_bursts_per_episode_mean` is defined as:
- number of kept burst runs divided by number of reconstructed episodes
- with episodes built by grouping nearby bursts under the existing event logic in `features.py`

That means the feature is not another coarse activity count. It is an organization term: how densely the retained bursts pack into each episode. This matches the strongest reviewed source most closely:
- Lavigne 2001 distinguishes bruxers from controls partly by bursts per episode.
- Smardz 2024 keeps the cluster/single/pair distinction central.
- Ikeda 1996 and Yamaguchi 2020 support event-thresholded, subject-relative jaw-EMG summaries as the relevant physiological frame.

### Why it fits the current frozen trio
The validated trio already covers:
- occupancy: `evt_active_fraction`
- burst duration: `evt_burst_duration_median_s`
- inter-burst spacing: `evt_interburst_gap_median_s`

What it does not directly encode is episode composition: are the retained bursts mostly isolated or do they arrive in denser multi-burst packets? `evt_bursts_per_episode_mean` is the smallest add-back that covers exactly that missing axis.

### Why it is the right move now, not just in the earlier literature memo
Before `pass45`, repo contact justified trying the smaller same-table shape cleanup first. After `pass45`, that smaller branch is closed: the repaired `A3-only` surface improved materially, but `brux2` still remains below the key control surface and the honest verdict still stays `ambiguous`. At that point the clean next move is no longer another subtraction. It is one compact organization add-back on the now-frozen `pass42/pass45` scaffold.

## 3) Why not a raw count or episode-index family first?
Because the literature and repo now line up against that move.

- Lavigne 2001 supports burst density within episodes, not raw episode totals by themselves.
- Wieckiewicz 2025 is an explicit warning against over-reading the episode index.
- In the earlier pass42 same-table sweep, the subset containing `evt_episode_count_30s, evt_active_fraction, evt_burst_duration_median_s` reached the same headline but a weaker margin (`+0.324`) and a higher `n11` (`0.494`) than the kept trio (`+0.339`, `n11` `0.486`).

So the right move is not to reopen a crude episode-count family first. It is to add the more specific organization term that stays closest to RMMA burst clustering.

## 4) Pass46 success and failure signatures beyond headline counts
The headline counts may stay unchanged again, so pass46 needs a stricter paired-surface read.

### Primary success signature
A real pass46 success should show all of the following on repaired `A3-only` relative to frozen `pass45`:
1. `brux2` rises materially from `0.178`.
2. `brux1` stays safely rescued; it should not materially give back the `0.641` pass45 gain.
3. highest control stays flat or lower than `0.345`; no control crosses `0.5`.
4. best-bruxism-minus-highest-control margin improves beyond `+0.295`.

### Strong success signature
The strongest success would be:
- `brux2` clears the highest control on the repaired `A3-only` table, and
- the repaired `A3-only` margin at least matches or beats repaired `A1-only` pass42 (`+0.339`),
- while `brux1` remains above the same highest control.

That would still be tiny-N, but it would finally say the add-back improved the actual unresolved subject-surface bottleneck rather than only making the branch cosmetically different.

### Weak-but-informative success signature
Even if the 1/2 and 3/3 counts stay unchanged, the add-back is still informative if:
- `brux2` gets a clear targeted lift,
- `brux1` is preserved,
- controls do not reopen,
- and the paired margin improves.

That would count as evidence that episode-composition information is real but not yet threshold-strong enough on this scaffold.

### Failure signature
Treat pass46 as a failure if any of these dominate:
1. `brux2` stays nearly flat or improves only trivially while controls rise.
2. `brux1` regresses materially toward the control surface.
3. any control reopens above threshold or highest control rises above `0.345`.
4. the add-back acts like a raw density confound, shifting both bruxism and controls together without selectively improving the unresolved `brux2` gap.

### Interpretation if it fails cleanly
A clean failure would mean the repaired cross-family branch is probably near its small event-organization limit. The next move after that should not be to reopen raw count or episode-index families broadly; it should be to preserve the negative result and reconsider whether the remaining signal lives outside this compact event-organization lane.

## 5) One explicitly rejected alternative add-back
Rejected first alternative: `evt_episode_count_30s`.

Why reject it first:
- it is too close to the literature-criticized episode-index shortcut
- it is biologically coarser than burst-density-within-episode
- the earlier pass42 sweep already gave it weaker repo-contact support than the kept trio and weaker support than the best `evt_bursts_per_episode_mean`-containing candidates

So if only one event feature comes back first, it should be `evt_bursts_per_episode_mean`, not `evt_episode_count_30s`.

## Bottom line
`evt_bursts_per_episode_mean` is now the right next one-feature add-back on the frozen `pass42/pass45` scaffold. It is the smallest biologically coherent term that captures the missing episode-composition axis, it matches the strongest RMMA source directly, and it avoids the newer literature's explicit warning against over-reading a crude episode index. Pass46 should therefore be judged mainly by whether it gives a targeted `brux2` lift while preserving `brux1` and the repaired control surface, not by headline counts alone.

## Exact files updated by this review
- `projects/bruxism-cap/reports/pass46-bursts-per-episode-add-back-science-review-2026-05-05.md`
- `wiki/queries/bruxism-cap-pass46-bursts-per-episode-add-back-review-2026-05-05.md`
- `wiki/concepts/bruxism-cap.md`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/raw/articles/rmma-during-sleep-humans-2001.md`
