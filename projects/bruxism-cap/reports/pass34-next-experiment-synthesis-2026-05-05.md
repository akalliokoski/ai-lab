# Pass 34 synthesis — one smallest paper-backed next experiment for the repaired `A1-only` EMG scaffold

Date: 2026-05-05
Status: synthesis completed; choose exactly one bounded representation-first experiment next and keep the repaired `A1-only` percentile-band anchor fixed.

## Current bottleneck after synthesis

The repaired `SLEEP-S2 + MCAP-A1-only` percentile-band scaffold is no longer blocked by extraction validity, threshold choice, or another obvious deletion candidate. The stable failure surface is now representation on the fixed LOSO benchmark:

- `pass28` recovered a reproducible `EMG1-EMG2` `A1-only` scaffold but still left both bruxism subjects below all controls.
- `pass29` and `pass30` showed the scaffold is timing-matched and that `C4-P4` can recover `brux2` on the same rows, so the remaining issue is narrower than row selection alone.
- `pass31` showed the recurrent `n3`-favoring family is real but not narrow enough to explain the whole gap.
- `pass32` and `pass33` showed further deletion is the wrong lever: broad ablation destroys useful signal, and even the smaller `mean/min/max` ablation collapses `brux1` while leaving `n3` high.
- The current honest bottleneck is therefore: on the repaired anchor, `EMG1-EMG2` still represents `brux1` too weakly relative to `n3`, and raw amplitude/location terms appear partly useful but too fragile across held-out subjects.

Working synthesis: this is now a record-relative representation problem, not a “remove more features” problem.

## Which paper-backed ideas survived contact with repo constraints

### 1. Survived and chosen: within-record robust feature-space normalization on the retained EMG morphology-envelope family
Why it survived:
- Best match to the repo bottleneck from `pass33`: preserve whatever weakly useful absolute information remains, but express it relative to each subject record instead of asking raw cross-subject levels to transfer directly.
- Best match to the literature actually inspected: Burden 2010, CEDE 2020, and Yang/Winter 1984 all support task/record-relative normalization when the goal is cross-subject comparability rather than raw absolute amplitude.
- It preserves comparability to the repaired anchor because the selected rows, labels, subject set, and `logreg` LOSO surface stay fixed.
- It avoids repeating the negative `pass22` mistake, because the transform happens after feature extraction at the feature-table level rather than by normalizing every waveform first.

Exact surviving transform shape:
- Start from the existing pass28 `EMG1-EMG2` feature CSV.
- Keep the current retained morphology-envelope family fixed.
- For a bounded subset of retained features, derive a within-record robust relative version using per-subject median and MAD across that subject’s kept windows.
- First-pass feature family: `mean`, `max`, `ptp`, `line_length`, `zero_crossing_rate`, `rectified_std`, `envelope_std`, `envelope_cv`, and optionally `rectified_mean`, `envelope_mean`, `p95_abs` if the implementation stays clean.
- First-pass formula: `(x - median_subject_feature) / max(MAD_subject_feature, eps)`.

### 2. Survived as backup only: shape-focused compact morphology expansion
Why it survived:
- The literature scan found plausible support for skewness, kurtosis, temporal-moment, and Hjorth mobility/complexity style descriptors.
- It addresses the possibility that `n3 > brux1` is partly a waveform-organization problem rather than only an amplitude comparability problem.

Why it is backup and not primary:
- It adds a new feature family instead of first testing whether the current retained family simply needs a better cross-subject representation.
- It is a larger branch away from the repaired anchor than a post-extraction record-relative transform.

## Which ideas were rejected and why

### Rejected for the next pass: another deletion-first ablation
Reason:
- Repo evidence already says no. `pass32` and `pass33` preserved deletion-first negatives, and `pass33` in particular showed that removing raw-location terms mostly destroys `brux1` rather than lowering `n3`.

### Rejected for the next pass: broad per-window waveform normalization
Reason:
- `pass22` already gave a closely related negative signal (`median_mad` before feature extraction). Repeating a broad signal-first rewrite would be lower value than a feature-space record-relative audit.

### Rejected for the next pass: whitening before feature extraction
Reason:
- Paper-backed and interesting, but too broad for the smallest next increment. Whitening would perturb nearly every feature at once and make interpretation harder than the direct representation test now needed.

### Rejected for the next pass: raw + relative + log-compressed multi-branch expansion
Reason:
- Literature support exists, but it is not the smallest single increment. Adding companion raw/relative/log branches in one pass risks turning the next run into a mini feature-program instead of a clean test of the current bottleneck.

### Rejected for the next pass: AR / cepstral / TD-PSD-style stable descriptor replacement
Reason:
- Supported by prosthesis-control literature, but too large a feature-family rewrite for the immediate next step.

### Rejected for the next pass: multi-muscle invariant features, dataset switch, or deep-learning rewrite
Reason:
- These ideas do not fit the current single-derived-channel, tiny-subject, repaired-anchor benchmark and would blur the interpretation target.

## One chosen experiment

Run exactly one matched representation audit on the repaired pass28 scaffold:

1. Keep the selected rows fixed.
2. Keep the subject set, labels, cap, and `logreg` LOSO surface fixed.
3. Keep the retained EMG morphology-envelope family fixed.
4. Build one alternate feature table where only the chosen retained family is transformed into within-record robust relative form using per-subject median/MAD.
5. Rerun `EMG1-EMG2` only and compare against the existing pass28 anchor on:
   - `brux1`, `brux2`, `n3`, `n5`, `n11` subject mean scores
   - `n3 - brux1` gap
   - best-bruxism-minus-highest-control margin
   - subject-level sensitivity / balanced accuracy

Chosen experiment name:
- `record-relative robust feature-space normalization audit on repaired A1-only EMG`

Why this is the primary increment:
- It is the smallest experiment that still directly tests the synthesis claim.
- It is more faithful to the literature than another blind deletion.
- It preserves the repaired A1 percentile-band anchor cleanly enough that any movement is interpretable.

## One backup experiment

If the chosen record-relative audit fails cleanly, run one compact shape-only expansion next:

- Add `skewness`, `kurtosis`, `hjorth_mobility`, and `hjorth_complexity` to the same repaired scaffold.
- Keep selector, subject set, labels, cap, and model family fixed again.
- Treat this as a shape-focused fallback, not as a joint pass with the record-relative transform.

Why this is the backup:
- It is still bounded and literature-backed.
- It is the next best way to test whether the remaining failure is waveform organization rather than raw level.

## Exact files to edit next

Primary implementation path should stay as post-extraction auditing, so the cleanest next edits are:

1. `projects/bruxism-cap/src/run_pass34_record_relative_emg_audit.py`
   - new runner cloned from the pass33 pattern
   - load the existing pass28 EMG CSV
   - derive the within-record robust transformed columns or transformed alternate table
   - call `train_baseline.py` on the transformed table
   - emit pass34 JSON and markdown summaries focused on `brux1`, `n3`, and best-bruxism-minus-highest-control

2. `projects/bruxism-cap/src/audit_percentile_band_channel_gap.py`
   - optional small helper reuse only if needed for consistent pairwise gap reporting on the transformed table
   - keep changes minimal; this should stay an audit utility, not a new feature pipeline rewrite

3. `projects/bruxism-cap/src/train_baseline.py`
   - touch only if the new transformed columns need explicit include/exclude handling or clearer feature-selection reporting
   - otherwise leave unchanged

Files that should probably stay untouched for the primary pass:
- `projects/bruxism-cap/src/prepare_windows.py`
- `projects/bruxism-cap/src/features.py`

Reason to avoid touching them first:
- The chosen experiment is strongest if it stays a post-extraction feature-table audit. That preserves direct comparability to the repaired anchor and avoids confounding extraction changes with representation changes.

## Bottom line

Choose one next increment only: a post-extraction within-record robust normalization audit on the retained `EMG1-EMG2` morphology-envelope family from the repaired `A1-only` percentile-band scaffold. Do not spend the next pass on more deletion, another waveform-normalization rewrite, or a broader feature-family replacement until this smaller paper-backed representation test has been run.