# Pass41 next-branch synthesis after fresh literature refresh

Date: 2026-05-05
Status: decision memo; chooses exactly one primary bounded increment after pass40 plus the two fresh literature tasks.

## Scope held fixed
- Keep the CAP five-subject `SLEEP-S2 + MCAP-A1-only` benchmark frame fixed: `brux1`, `brux2`, `n3`, `n5`, `n11`.
- Keep `EMG1-EMG2` as the primary channel.
- Preserve comparability to pass36/pass40: same selected rows, same train-time exclusions, same model family, same LOSO subject-level readout, same threshold discipline.
- Do not reopen the exhausted pass37-pass40 `envelope_cv` floor family.

## Current repo-state read before choosing
1. Pass36 remains the best current composed representation on the fixed scaffold: subject-level balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`, with `brux2` rescued but `brux1` still below threshold.
2. The pass36 fold audit localizes the unresolved miss to the record-relative amplitude/dispersion block, with the earliest three `brux1` windows collapsing catastrophically while the added shape block is neutral-to-helpful rather than harmful.
3. Pass37 through pass40 tested the narrow floor/cap stabilization family repeatedly and closed it as a negative-result loop: the early `brux1` trio softens directionally, but `brux1` never becomes threshold-relevant and pass40 returns to `0.112`, effectively flat versus pass36.
4. The current feature code already contains the right low-level substrate for an event-conditioned step: `src/features.py` already computes centered rectified amplitude, a `0.2 s` moving-average envelope, and simple burst summaries (`burst_fraction`, `burst_rate_hz`), so a bounded event block is an extension of the existing EMG path rather than a representation reset.
5. The benchmark-upgrade literature is valid and useful, but in current repo state it is secondary to the core detection bottleneck: `README.md` already states LOSO subject-level priority and exact subject-level CIs as desired contract language, while `src/train_baseline.py` still lacks actual subject-level CI fields. That gap matters for honesty, but it does not address why `brux1` is still missed.

## 1) Current bottleneck statement after pass40 and the literature refresh
The bottleneck is no longer benchmark ambiguity; it is unresolved representation transfer for `brux1` inside the fixed pass36 scaffold. More specifically: the benchmark contract is already directionally settled around grouped LOSO subject-level evaluation, but the feature representation still collapses the earliest `brux1` windows under the record-relative amplitude/dispersion surface. Pass37-pass40 show that another same-family stabilization tweak is unlikely to rescue that failure. The next increment therefore has to add new within-window structure that is still comparable to pass36, rather than spend the next bounded step only improving reporting.

## 2) Should pass41 be an event-conditioned EMG feature pass, a benchmark-instrumentation pass, or a tightly coupled pair?
It should be a tightly coupled pair with one clear primary:
- Primary: event-conditioned EMG feature pass.
- Secondary / backup: benchmark instrumentation patch.

Why this pairing is right:
- The literature refresh on RMMA / jaw EMG directly supports moving from coarse window summaries toward a compact burst/episode-conditioned block, while explicitly warning against collapsing everything into a single episode index.
- The benchmark-methodology refresh supports exact subject-level confidence intervals and raw counts, but that work mainly sharpens interpretation of the same current miss; it does not create a new chance for `brux1` recovery.
- Because the benchmark frame is already largely fixed conceptually, the more decision-relevant next experiment is the smallest new representation question outside the exhausted floor family.

## 3) One chosen primary branch
Chosen primary branch: implement `pass36 + compact event-conditioned jaw-EMG block` as pass41.

Exact branch definition:
- Start from the current pass36 table and leave the existing retained features in place.
- Append exactly the seven literature-backed event features proposed in `reports/pass41-event-conditioned-feature-block-literature-memo-2026-05-05.md`:
  - `evt_burst_count_30s`
  - `evt_episode_count_30s`
  - `evt_bursts_per_episode_mean`
  - `evt_active_fraction`
  - `evt_burst_duration_median_s`
  - `evt_interburst_gap_median_s`
  - `evt_phasic_like_episode_fraction`
- Use the bounded burst/episode logic from the literature memo so the pass remains hand-auditable and comparable.
- First comparison should be only `pass36` vs `pass36 + 7 event features` on the unchanged LOSO audit surface.

Why this wins over instrumentation-first:
- It attacks the actual unresolved scientific bottleneck.
- It stays bounded and auditable.
- It preserves the existing CAP/EMG benchmark contract instead of changing multiple layers at once.
- It exploits code that already exists in `features.py` for rectification, smoothing, and simple burst logic, minimizing scaffolding cost.

## 4) One backup branch
Backup branch: benchmark-instrumentation patch for exact subject-level counts and 95% Clopper-Pearson confidence intervals in `src/train_baseline.py`, with future reports surfacing those interval-bearing subject metrics first.

Why it is backup rather than primary:
- It improves honesty and should happen soon.
- But it does not change the answer to the current branch question: the benchmark is already honest enough to show that `brux1` is the remaining blocker.
- If taken first, it risks spending the next bounded increment on clearer reporting of a failure mode that is already well localized instead of testing the next plausible representation hypothesis.

## 5) Exact files and artifacts to touch next
### Primary branch files to touch next
1. `projects/bruxism-cap/src/features.py`
   - add a reusable event-detection helper built on the existing rectified/envelope pipeline
   - emit the 7 new `evt_*` features
2. `projects/bruxism-cap/src/prepare_windows.py`
   - touch only if needed to ensure regenerated feature CSVs preserve the new event columns cleanly in the existing extraction path
3. `projects/bruxism-cap/src/run_pass41_event_conditioned_feature_block_audit.py`
   - new bounded runner comparing pass36 against pass36-plus-event-block on the unchanged scaffold
4. `projects/bruxism-cap/src/audit_pass36_brux1_vs_n5_n11.py`
   - reuse or lightly extend for fold-local interpretation of whether the new block specifically softens the early `brux1` trio without reopening `n3`, `n5`, or `n11`
5. `projects/bruxism-cap/src/train_baseline.py`
   - leave unchanged for the primary pass unless the new columns require explicit metadata-protection logic

### Primary branch artifacts to generate next
1. New feature table:
   - `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
2. New LOSO report:
   - `projects/bruxism-cap/reports/loso-cv-pass41-emg-a1-pct10-90-record-relative-shape-eventblock.json`
3. New pass summary JSON:
   - `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.json`
4. New pass summary memo:
   - `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md`

### Backup-branch files after that
- `projects/bruxism-cap/src/train_baseline.py`
- `projects/bruxism-cap/reports/first-baseline.md`
- `projects/bruxism-cap/README.md`
- optionally `projects/bruxism-cap/src/eval.py` if comparison output should surface subject-level CI-aware summaries

## Bottom line
Choose the event-conditioned EMG feature pass next. The literature refresh says the right new signal is burst/episode structure, the repo state says the floor-family loop is finished, and the current benchmark contract is already stable enough to reveal the real bottleneck. So pass41 should be one bounded `pass36 + 7 event features` experiment now, with the benchmark-instrumentation CI patch queued immediately behind it as the backup branch rather than promoted ahead of it.
