# Pass 44 follow-up — repaired cross-family asymmetry audit on the fixed 3-feature event subset

Date: 2026-05-05
Status: read-only audit completed. This note explains the main asymmetry left after pass44 while keeping the repaired `EMG1-EMG2` event-subset scaffold fixed.

## Current bottleneck
The bottleneck is no longer whether the retained 3-feature event subset transfers from repaired `A1-only` to repaired `A3-only`. Pass44 resolved that. The remaining bottleneck is a within-family subject split on the repaired `A3-only` surface: the same fixed scaffold that rescues `brux1` to `0.532` simultaneously leaves `brux2` collapsed at `0.123`, so the benchmark still gets only one of the two bruxism subjects above threshold even though balanced accuracy stays at `0.750`.

## Exact asymmetry after pass44
Subject-level scores on the repaired surfaces:
- pass42 repaired `A1-only`: `brux1 0.136`, `brux2 0.825`, `n3 0.155`, `n5 0.199`, `n11 0.486`
- pass44 repaired `A3-only`: `brux1 0.532`, `brux2 0.123`, `n3 0.034`, `n5 0.365`, `n11 0.395`

So pass44 does not produce a generic cross-family failure. It reallocates the one positive bruxism verdict from `brux2` to `brux1` while preserving the same headline subject-level result (`0.750` balanced accuracy, `0.500` sensitivity, `1.000` specificity).

## Why `brux1` is rescued on repaired A3 while `brux2` collapses there
The dominant difference is not the retained event block by itself. It is the repaired `A3-only` amplitude / dispersion surface.

Evidence from the pass44 subject audits:
- `brux1` block means: amp/disp `+14.070`, shape `-1.404`, event `+0.058`, other `+1.219`
- `brux2` block means: amp/disp `-0.048`, shape `-0.735`, event `+0.117`, other `+0.060`
- `brux1 - brux2` block delta: amp/disp `+14.118`, shape `-0.670`, event `-0.059`, other `+1.159`

That means the rescue is overwhelmingly carried by amplitude / dispersion, not by a large event-only advantage.

Time-rank evidence sharpens that further:
- `brux1` early ranks `1-3` are effectively saturated at score `1.000` with amp/disp mean `+40.076`
- `brux1` mid ranks `4-7` still average `0.412`
- `brux1` late ranks `8-10` fall back to `0.225`
- `brux2` stays low across all three rank groups: early `0.124`, mid `0.132`, late `0.108`

So `brux1` is rescued because the repaired `A3-only` selector exposes a concentrated early high-amplitude/high-dispersion pocket that the current logistic surface scores very strongly. `brux2` does not show a comparable pocket on the repaired `A3-only` subset; its scores stay uniformly low across early, mid, and late ranks rather than failing through one catastrophic local patch.

## Which retained feature families look most responsible
### 1. Primary driver: retained amplitude / dispersion block
This is the main asymmetry carrier.
- `brux1` changes from pass42 amp/disp `-49.074` to pass44 amp/disp `+14.070` (`+63.144`)
- `brux2` changes only from `-0.713` to `-0.048` (`+0.665`)
- `n3` becomes much safer on pass44 because its amp/disp block drops from `+0.189` to `-9.104`

So the repaired `A3-only` scaffold did two things at once: it rescued `brux1` through amp/disp and pushed the old `n3` concern downward. That is why pass44 can match pass42's headline metrics even though the positive subject flips.

Within that block, the single largest contribution-gap term between `brux1` and `brux2` is `mean`:
- `mean` contribution: `brux1 +16.163` vs `brux2 -0.052` (delta `+16.215`)

Other notable contribution deltas are much smaller by comparison:
- `burst_rate_hz`: delta `+1.263`
- `evt_burst_duration_median_s`: delta `+0.231`
- `envelope_cv`: delta `+0.073`

This makes the residual asymmetry look far more amplitude-centered than event-centered.

### 2. Secondary driver: compact shape block hurts `brux2` more after the family swap
The shape block is not the main rescue signal, but it does participate in the split.
- `brux2` shape mean falls from pass42 `+2.313` to pass44 `-0.735` (`-3.047`)
- `brux1` shape mean falls from `+0.110` to `-1.404` (`-1.514`)

So both bruxism subjects lose shape support on repaired `A3-only`, but `brux2` loses much more relative to its pass42 anchor. That makes shape a plausible bounded ablation target on the fixed pass44 table.

### 3. Retained event subset is real but not the main remaining blocker
The fixed event subset still matters diagnostically, but it is too small to explain the pass44 subject split by itself.
- `brux1` vs `brux2` event block delta is only `-0.059`
- pairwise pass44 audits against controls show event contributions helping `brux1` versus `n11` and `n5` in some directions, but the largest cross-subject separation still lives in amp/disp

So the repaired cross-family asymmetry after pass44 should be read as scaffold-plus-representation interaction, not as an event-subset failure.

## Safest next bounded experiment
Keep the repaired pass44 `A3-only` table fixed and run one same-table shape-only ablation on that exact table.

Why this is the safest next move:
- it isolates the second-strongest plausible driver of the `brux1`/`brux2` split without reopening selector, channel, family, or model questions
- it tests whether `brux2` is being suppressed by the compact shape block after the family swap while preserving the amp/disp rescue that currently helps `brux1`
- it is narrower and safer than editing the record-relative transform again, because pass44's strongest positive change is currently the amp/disp rescue itself

Recommended bounded test:
- keep rows, train-time exclusions, and the retained 3 event features fixed
- exclude only the compact shape family (`skewness`, `kurtosis`, `hjorth_mobility`, `hjorth_complexity`) from the pass44 table
- compare subject scores against the unchanged pass44 anchor

Success criterion:
- `brux2` rises materially from `0.123` without knocking `brux1` back below threshold and without pushing `n5` or `n11` above threshold

## Explicitly rejected broader move
Rejected move: another scaffold rewrite or model-family pivot.

Why rejected:
- pass44 already answered the scaffold-transfer question cleanly: the pass43 failure was mainly old-surface mismatch, not proof that the subset was `A1`-locked
- the current asymmetry is now localized inside the repaired surface, so another selector rewrite, broader feature search, or model-family change would blur the diagnosis instead of testing it
- the user constraint for this branch is to keep the scaffold fixed and avoid broad search

## Exact files likely to change next
Experiment-facing files most likely to change next:
- `projects/bruxism-cap/src/run_pass45_repaired_a3_shape_block_ablation.py`
- `projects/bruxism-cap/reports/loso-cv-pass45-emg-a3-pct10-90-record-relative-eventsubset-no-shape.json`
- `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.md`
- `projects/bruxism-cap/reports/pass45-repaired-a3-shape-block-ablation.json`

Documentation files likely to change next:
- `wiki/queries/bruxism-cap-pass45-repaired-a3-shape-block-ablation-2026-05-05.md`
- `wiki/concepts/bruxism-cap.md`
- `wiki/index.md`
- `wiki/log.md`
