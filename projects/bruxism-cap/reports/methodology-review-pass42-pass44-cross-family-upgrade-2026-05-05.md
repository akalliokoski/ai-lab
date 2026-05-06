# Methodology review — pass42/pass44 cross-family evaluation upgrade

Date: 2026-05-05
Status: completed; source-verified methodology review grounded in the current repaired `pass42`/`pass44` cross-family surface.

## Repo evidence inspected first
- `wiki/concepts/bruxism-cap.md`
- `wiki/queries/bruxism-cap-tiny-subject-benchmarking-upgrade-2026-05-05.md`
- `projects/bruxism-cap/reports/pass42-same-table-event-subset-ablation.md`
- `projects/bruxism-cap/reports/pass44-repaired-a3-event-subset-rebuild.md`
- `projects/bruxism-cap/src/train_baseline.py`
- new paired audit artifact generated during this review: `projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.{json,md}`

## Current repo-grounded problem
The repaired `A1-only` and repaired `A3-only` event-subset runs now land on the same subject-level headline:
- `pass42`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- `pass44`: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

But they do not rescue the same bruxism subject:
- `pass42` calls `brux2` positive and misses `brux1`
- `pass44` calls `brux1` positive and misses `brux2`

So the current question is no longer just “how uncertain is `1/2` and `3/3`?” The sharper question is whether the benchmark preserves the same subject-level disease surface across matched family rebuilds.

## Verified external sources

1. Roberts DR, Bahn V, Ciuti S, Boyce MS, et al. 2017. Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. Ecography. DOI `10.1111/ecog.02881`.
   - Verified via search result metadata and abstract/summary pages.
   - Relevant claim: when dependence or hierarchy exists, cross-validation should respect those blocks rather than treating observations as IID.
   - Why it matters here: repeated windows are nested within subject, so subject-grouped `LOSO` remains the right primary split.

2. Varoquaux G. 2018. Cross-validation failure: small sample sizes lead to large error bars. NeuroImage. DOI `10.1016/j.neuroimage.2017.06.061`.
   - Verified from the HAL/arXiv-accessible abstract text.
   - Relevant claim: small-sample CV estimates have large uncertainty, and fold-to-fold standard errors understate that uncertainty.
   - Why it matters here: `N=5` subject-level point estimates must not be read as precise.

3. Chaibub Neto E, Pratap A, Perumal TM, et al. 2019. Detecting the impact of subject characteristics on machine learning-based diagnostic applications. npj Digital Medicine. DOI `10.1038/s41746-019-0178-x`.
   - Verified from Nature/PubMed pages.
   - Relevant claim: record-wise splitting with repeated measures can massively underestimate error because models learn subject identity; subject-wise splitting should be used.
   - Why it matters here: random-window CV should remain a leakage reference only, not the headline surface.

4. Brown LD, Cai TT, DasGupta A. 2001. Interval Estimation for a Binomial Proportion. Statistical Science. DOI `10.1214/ss/1009213286`.
   - Verified from Project Euclid/JSTOR metadata and abstract snippets.
   - Relevant claim: Wald-style asymptotic intervals behave badly in small samples; exact/Wilson-style intervals are safer.
   - Why it matters here: subject sensitivity `1/2` and specificity `3/3` need small-sample intervals, not naked point estimates.

5. Binuya MAE, Engelhardt EG, Schats W, Schmidt MK, Steyerberg EW. 2022. Methodological guidance for the evaluation and updating of clinical prediction models: a systematic review. BMC Medical Research Methodology. DOI `10.1186/s12874-022-01801-8`.
   - Verified from PMC/search metadata.
   - Relevant claim: model evaluation should consider discrimination and calibration explicitly, and threshold/decision use should be made explicit rather than implied.
   - Why it matters here: the repo should preserve subject-level probabilistic summaries and keep the headline threshold fixed and explicit.

6. Clinical prediction model evaluation guidance summarized in JAMA Users’ Guides / related review literature on discrimination vs calibration.
   - Verified via search metadata pointing to JAMA and review summaries.
   - Relevant claim: discrimination alone is insufficient; calibration-aware summaries matter, but the tooling should match the sample size.
   - Why it matters here: subject-level Brier score is justified as a lightweight add-on, while full calibration curves are not.

## What is justified at `N=5`
1. Keep subject-grouped `LOSO` primary.
2. Keep subject-level aggregation primary and window-level metrics secondary.
3. Preserve raw denominators behind subject sensitivity/specificity.
4. Preserve exact small-sample binomial intervals for subject sensitivity/specificity.
5. Preserve one fixed primary subject threshold (`0.5`) and mark threshold sweeps exploratory only.
6. Add paired matched-surface comparisons when two runs have the same subjects and the same per-subject window counts.
7. Keep one lightweight probabilistic summary such as subject-level Brier score.

## What is overkill at `N=5`
- nested CV
- threshold optimization presented as validated
- Platt / isotonic calibration
- full calibration curves as headline artifacts
- formal superiority claims from tiny paired family comparisons
- broader model-family leaderboards that create benchmarking theater instead of resolving subject-level instability

## Do exact binomial CIs remain the best next reporting change?
Not anymore as the first incremental upgrade.

They remain necessary, and the repo was right to add them in `train_baseline.py`. But for the current `pass42` versus `pass44` repaired cross-family question, exact CIs are now insufficient because they are numerically identical across the two runs:
- sensitivity: `1/2` in both runs
- specificity: `3/3` in both runs
- exact `95%` sensitivity CI: `[0.013, 0.987]` in both runs
- exact `95%` specificity CI: `[0.292, 1.000]` in both runs

Those intervals honestly communicate uncertainty, but they do not answer the sharper scientific question created by the repaired scaffold: the benchmark now swaps which bruxism subject is recovered while keeping the same top-line subject metrics.

So the stronger next audit should come first: a paired subject-surface comparison on matched repaired family runs.

## Why a paired-surface audit is the right next increment
The new paired artifact shows exactly what the identical headline metrics hide:
- `brux1`: `0.136 -> 0.532` (`pass42 -> pass44`, `+0.396`)
- `brux2`: `0.825 -> 0.123` (`-0.702`)
- controls stay below threshold in both runs, but the highest control and margin change materially
- best-bruxism-minus-highest-control margin shrinks from `+0.339` on `pass42` to `+0.138` on `pass44`

So the repaired cross-family story is not “A1 and A3 are equivalent.” It is “the repaired scaffold restores the same coarse subject-level count result, but the rescued bruxism subject is not stable across families.”

That is a more informative honesty upgrade than adding yet another scalar summary.

## One smallest repo-compatible measurement upgrade
Generate and preserve a paired matched-surface audit whenever two candidate runs share:
- the same subjects
- the same per-subject window counts
- the same evaluation contract

For the current branch, that means preserving `pass42` vs `pass44` with:
- per-subject mean positive probability deltas
- subject prediction flips
- best-bruxism-minus-highest-control margin change
- the existing subject-level CI/Brier block copied through from each underlying LOSO report

This is small because it uses existing saved LOSO reports and the existing `compare_subject_score_surfaces.py` helper. No retraining, no new model family, and no new data extraction are required.

## Exact files likely to touch next
Already touched in this review:
- `projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.json`
- `projects/bruxism-cap/reports/pass44-vs-pass42-paired-subject-surface-audit.md`
- `projects/bruxism-cap/reports/methodology-review-pass42-pass44-cross-family-upgrade-2026-05-05.md`

Most likely durable next code/docs touch points if this becomes standard policy:
- `projects/bruxism-cap/src/compare_subject_score_surfaces.py` if a tiny enhancement is wanted for explicit prediction-flip / margin summaries
- `projects/bruxism-cap/src/eval.py` if single-line compare output should surface paired-surface hints
- `wiki/queries/bruxism-cap-pass42-pass44-cross-family-methodology-review-2026-05-05.md`
- `wiki/concepts/bruxism-cap.md`

## Bottom line
For this repo at `N=5`, the justified contract is still simple: grouped `LOSO`, subject-level primacy, raw denominators, exact small-sample intervals, fixed threshold discipline, and lightweight probability summaries.

But after `pass42` and `pass44`, the next honesty gain is no longer another interval field. The best next reporting/measurement upgrade is a paired repaired-surface audit that makes cross-family subject instability visible even when the top-line subject metrics are identical.
