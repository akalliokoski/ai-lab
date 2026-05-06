# Pass45 next-step synthesis after pass44 cross-family repair

Date: 2026-05-05
Status: synthesis completed; choose exactly one primary bounded experiment plus one bounded measurement/reporting upgrade after the fresh literature, methodology, and repo-grounded asymmetry lanes were combined.

## Scope held fixed
- Keep the CAP five-subject benchmark frame fixed: `brux1`, `brux2`, `n3`, `n5`, `n11`.
- Keep `EMG1-EMG2` as the primary channel.
- Keep the repaired cross-family scaffold fixed: repaired `A1-only` pass42 and repaired `A3-only` pass44 remain the current matched-family anchor pair.
- Keep grouped `LOSO`, subject-level primacy, threshold `0.5`, and the existing exact CI / Brier reporting contract.
- Do not promote privacy or LLM/RL branches unless the current repaired benchmark evidence clearly forces it.

## 1) Current bottleneck after synthesis
The bottleneck is no longer whether the fixed 3-feature event subset transfers across families. Pass44 already answered that: once the `A3-only` table is rebuilt on the repaired percentile-band / time-aware scaffold, the cross-family headline returns to the same honest subject-level result as repaired pass42.

The sharper bottleneck is now subject instability inside the repaired cross-family surface:
- repaired `A1-only` pass42 rescues `brux2` (`0.825`) but misses `brux1` (`0.136`)
- repaired `A3-only` pass44 rescues `brux1` (`0.532`) but leaves `brux2` collapsed (`0.123`)
- both runs still report the same top-line subject counts: sensitivity `1/2`, specificity `3/3`, balanced accuracy `0.750`

So the current branch should be read as count-matched but subject-unstable. The remaining scientific blocker is not generic transfer failure; it is broad under-support for `brux2` on the repaired `A3-only` table while `brux1` is rescued through an amplitude / dispersion pocket. The event trio now looks validated as a base organization block, but it does not look like the main driver of the remaining pass44 split.

## 2) Which literature ideas survived repo contact
### A. Survived strongly: keep the 3-feature event trio as the validated base block
The literature lane and the repo now agree that these three terms should stay fixed as the current base burst-organization block:
- `evt_active_fraction`
- `evt_burst_duration_median_s`
- `evt_interburst_gap_median_s`

Why this survived:
- pass42 and pass44 both preserve the same honest repaired cross-family headline on this trio
- the literature supports occupancy, burst duration, and gap structure as compact jaw-EMG organization descriptors
- repo contact shows the trio is no longer the active uncertainty; the active uncertainty is what still suppresses `brux2` on repaired `A3-only`

### B. Survived as the primary next experiment: same-table repaired-A3 shape-only ablation
The asymmetry audit says the dominant residual split is amplitude / dispersion, but the smallest intervention that still directly tests a plausible suppressor on `brux2` is the compact shape block.

Why this survived contact:
- it is bounded to the exact repaired pass44 table
- it does not reopen selector, family, channel, model, or event-subset questions
- repo evidence says `brux2` loses more shape support than `brux1` after the repaired family swap, making shape the cleanest removable secondary drag
- compared with a new add-back, it is the smaller test against the already validated pass44 anchor

### C. Survived as the bounded measurement/reporting upgrade: standard paired subject-surface audit
The methodology lane survives repo contact cleanly.

Why this survived:
- repaired pass42 and pass44 already prove that exact binomial CIs remain necessary but no longer differentiate the current question because the counts are identical across both runs
- the paired audit directly exposes what the headline metrics hide: repaired `A1-only` and repaired `A3-only` recover different bruxism subjects and produce different best-bruxism-minus-highest-control margins
- this upgrade is small, reproducible, and reuses existing report artifacts rather than requiring new modeling machinery

## 3) Which ideas were rejected and why
### Rejected as the primary next move: one-feature cluster-density add-back (`evt_bursts_per_episode_mean`)
Reason:
- the literature support is real, but repo contact weakens it as the immediate next move
- on pass44, the `brux1` vs `brux2` event-block delta is only `-0.059`, while the residual split is much larger in amplitude / dispersion and still meaningfully shaped by the compact shape block
- the add-back introduces new signal before testing the smaller hypothesis that an existing retained family is suppressing `brux2`

This idea remains alive as a backup branch, but not as the first promoted experiment.

### Rejected for now: raw event-count or episode-index reopenings
Reason:
- the literature explicitly warns against over-reading coarse episode counts
- repo contact says the current unresolved miss is not best explained by reopening broad count-style event features first
- this would be a noisier move than either the chosen shape ablation or the backup cluster-density add-back

### Rejected for now: another scaffold rewrite or model-family pivot
Reason:
- pass44 already resolved the main scaffold-mismatch ambiguity left by pass43
- the current uncertainty is now localized enough to test inside the repaired table
- another selector rewrite, broader feature search, or model-family branch would blur diagnosis instead of narrowing it

### Rejected for now: privacy and LLM/RL branch promotion
Reason:
- the repaired benchmark is still not handoff-grade because subject-level sensitivity remains `0.500`
- the new evidence sharpened benchmark diagnosis, but did not create a durable benchmark win that forces branch expansion

## 4) One chosen experiment
Chosen experiment: run one repaired-`A3-only` same-table shape-only ablation against the frozen pass44 anchor.

Exact definition:
1. Keep the repaired pass44 selected rows fixed.
2. Keep train-time exclusions, subject set, labels, threshold, and `logreg` LOSO contract fixed.
3. Keep the validated 3-feature event trio fixed.
4. Drop only the compact shape family:
   - `skewness`
   - `kurtosis`
   - `hjorth_mobility`
   - `hjorth_complexity`
5. Compare directly against the unchanged pass44 anchor on:
   - `brux1`, `brux2`, `n3`, `n5`, `n11` mean subject scores
   - subject prediction flips
   - best-bruxism-minus-highest-control margin
   - subject-level balanced accuracy / sensitivity / specificity

Why this is the one primary experiment:
- it is the smallest repo-grounded test of whether `brux2` is being held down by a removable secondary family inside the already repaired table
- it preserves the literature-validated event base while not pretending the event block is the main diagnosed bottleneck
- it avoids reopening the stronger amplitude / dispersion carrier directly before testing the cleaner secondary hypothesis

Success criterion:
- `brux2` rises materially from `0.123`, ideally above threshold
- `brux1` stays above threshold or at least does not lose the pass44 rescue materially
- no control crosses threshold

## 5) One chosen measurement/reporting upgrade
Chosen upgrade: standardize a paired subject-surface audit as the default companion artifact whenever two runs share the same subjects, same per-subject window counts, and same evaluation contract.

Immediate next use:
- compare the chosen pass45 shape-ablation run directly against the frozen pass44 anchor

Minimum paired artifact contents:
- per-subject mean positive probability deltas
- subject prediction flips
- best-bruxism-minus-highest-control margin change
- copied-through subject-level denominator counts, exact CI block, and Brier summaries from the underlying LOSO reports

Why this is the right single upgrade:
- it makes the key honesty issue visible on this branch: who is rescued, who collapses, and whether the margin really improves
- it stays lightweight and compatible with the current tiny-`N` benchmark
- it is more decision-relevant than adding heavier calibration or threshold machinery right now

## 6) One backup branch explicitly not promoted yet
Backup branch: run one repaired cross-family add-back audit with exactly four event features by adding only `evt_bursts_per_episode_mean` on top of the frozen pass42/pass44 trio.

Why it is not promoted yet:
- it is literature-backed, but the current repo-grounded asymmetry is not primarily event-separated
- shape-only ablation is the smaller diagnosis-preserving move on the frozen pass44 table
- if shape-only ablation fails cleanly, the one-feature cluster-density add-back remains the best next literature-backed branch without reopening the full pass41 event block

## 7) Exact files to edit next
### Primary experiment path
1. `projects/bruxism-cap/src/run_pass45_repaired_a3_shape_block_ablation.py`
2. `projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json`
3. `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.json`
4. `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md`

### Measurement/reporting upgrade path
5. `projects/bruxism-cap/src/compare_subject_score_surfaces.py`
6. `projects/bruxism-cap/src/eval.py`
7. `projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.json`
8. `projects/bruxism-cap/reports/pass45-vs-pass44-paired-subject-surface-audit.md`

### Documentation / preservation path
9. `projects/bruxism-cap/reports/pass45-next-step-synthesis-2026-05-05.md`
10. `wiki/queries/bruxism-cap-pass45-next-step-synthesis-2026-05-05.md`
11. `wiki/concepts/bruxism-cap.md`
12. `wiki/index.md`
13. `wiki/log.md`

## Bottom line
Choose one primary experiment only: a repaired-`A3-only` same-table shape-only ablation on top of the frozen pass44 anchor. Pair it with one bounded reporting upgrade only: standard paired subject-surface audits for matched runs. Keep the cluster-density add-back alive as the backup branch, but do not promote it ahead of the smaller repo-grounded shape test, and keep privacy plus LLM/RL branches gated.