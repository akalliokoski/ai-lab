# Literature scan — tiny-subject benchmark methodology upgrade for `bruxism-cap`

Date: 2026-05-05
Status: completed; source-verified methodology scan mapped onto the current repaired five-subject `bruxism-cap` benchmark contract.

## Why this memo exists

The repo now has a sharper honest benchmark surface after `pass36` through `pass40`, but the current reporting contract is still lighter than the literature would support. The goal here is not to broaden into nested CV, deep models, or clinical-grade validation. The goal is to identify the smallest paper-backed benchmark/reporting upgrade that makes the current tiny-subject CAP scaffold more honest without making it heavy.

Current repo anchor for this memo:
- benchmark shape: tiny repeated-window biosignal classification with subject grouping
- primary honest split: LOSO
- current honest subject surface on the repaired scaffold: often `2` bruxism subjects and `3` controls
- key failure mode: subject-level transfer remains fragile even when the window-level picture looks decent

## Verified citations with relevance notes

### 1. Roberts DR, Bahn V, Ciuti S, Boyce MS, et al. 2017.
`Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure.` Ecography. DOI: `10.1111/ecog.02881`

Relevance here:
- explicitly argues that cross-validation should respect grouped / hierarchical dependence instead of splitting dependent observations as if they were IID
- maps directly onto this repo's repeated windows nested within subject structure
- supports keeping LOSO / grouped validation as the headline benchmark rather than random-window CV

Why it matters for `bruxism-cap`:
- window-level random CV is useful only as a leakage reference surface
- headline claims should stay on subject-grouped validation

### 2. Varoquaux G. 2018.
`Cross-validation failure: Small sample sizes lead to large error bars.` NeuroImage. DOI: `10.1016/j.neuroimage.2017.06.061`

Relevance here:
- shows that small-sample cross-validation estimates inherently have large uncertainty
- warns that fold-to-fold standard errors underestimate real uncertainty
- especially relevant to inter-subject prediction settings where sample size is tiny and between-subject heterogeneity matters

Why it matters for `bruxism-cap`:
- a subject-level result from `5` people should never be read as precise just because the split is honest
- the repo should report uncertainty explicitly rather than only point estimates

### 3. Chaibub Neto E, Pratap A, Perumal TM, Tummalacherla M, Snyder P, Bot BM, Trister AD, Friend SH, Mangravite L, Omberg L. 2019.
`Detecting the impact of subject characteristics on machine learning-based diagnostic applications.` npj Digital Medicine. DOI: `10.1038/s41746-019-0178-x`

Relevance here:
- directly studies repeated-measures digital-health settings
- shows that record-wise splitting can massively underestimate prediction error because models learn subject identity as well as disease signal
- explicitly contrasts record-wise versus subject-wise splitting

Why it matters for `bruxism-cap`:
- supports the repo's anti-leakage framing strongly
- supports treating subject-level rather than window-level generalization as the honest interpretation surface
- reinforces that repeated windows from the same subject must never be allowed to leak across train/test in headline evaluation

### 4. Stevens LM, Mortazavi BJ, Deo RC, Curtis L, Kao DP. 2020.
`Recommendations for Reporting Machine Learning Analyses in Clinical Research.` Circulation: Cardiovascular Quality and Outcomes. DOI: `10.1161/CIRCOUTCOMES.120.006556`

Relevance here:
- reporting-focused guidance for clinical ML analyses
- supports explicit reporting of validation design and enough detail for readers to judge credibility
- useful here not as a demand for full clinical deployment reporting, but as support for making the benchmark contract explicit and repeatable

Why it matters for `bruxism-cap`:
- the repo should make its evaluation contract very explicit: grouping unit, primary threshold, exploratory threshold analyses, and subject-level endpoint
- the next reporting upgrade should live in the saved JSON/report artifacts, not only in prose after the fact

### 5. Binuya MAE, Engelhardt EG, Schats W, Schmidt MK, Steyerberg EW. 2022.
`Methodological guidance for the evaluation and updating of clinical prediction models: a systematic review.` BMC Medical Research Methodology. DOI: `10.1186/s12874-022-01801-8`

Relevance here:
- synthesizes guidance that validation should assess discrimination and calibration
- notes that clinically meaningful thresholding / decision use should be treated explicitly rather than hidden behind simplistic accuracy-style summaries
- provides the strongest lightweight support in this scan for calibration / threshold discipline

Why it matters for `bruxism-cap`:
- this repo should keep discrimination metrics, but also preserve calibration-aware subject-score reporting
- threshold choice should be pre-declared for the primary result; any threshold sweep should be exploratory and clearly labeled as such

### 6. Brown LD, Cai TT, DasGupta A. 2001.
`Interval Estimation for a Binomial Proportion.` Statistical Science. DOI: `10.1214/ss/1009213286`

Relevance here:
- classic methodological source showing that naive Wald intervals behave badly, especially in small samples
- supports using exact or otherwise better small-sample binomial intervals instead of asymptotic shortcuts

Why it matters for `bruxism-cap`:
- current subject-level sensitivity / specificity estimates are often based on `2` positives and `3` negatives
- that is exactly the regime where exact binomial intervals are more honest than asymptotic confidence intervals or no intervals at all

## What these sources motivate for this repo

### A. Keep grouped / LOSO evaluation as the primary benchmark contract

Recommended contract:
- keep random-window CV only as a leakage-reference surface
- keep LOSO as the primary headline evaluation
- keep the grouping unit explicit everywhere: subject

Repo effect:
- this is already mostly true in spirit
- the contract should become more explicit in README and saved reports

### B. Promote subject-level aggregation to the primary honest endpoint

Recommended contract:
- keep subject-level aggregation in every LOSO report
- present subject-level metrics before window-level metrics in benchmark conclusions
- always include the raw subject counts behind sensitivity / specificity

Repo effect:
- this is already partly implemented in `train_baseline.py`
- the reporting emphasis should shift from “window-level plus subject appendix” toward “subject-level primary, window-level secondary”

### C. Add exact 95% binomial confidence intervals for subject-level sensitivity and specificity

Recommended contract:
- for each LOSO subject-level summary, report:
  - `tp/fn` for bruxism subjects
  - `tn/fp` for controls
  - exact 95% binomial CI for sensitivity and specificity
- do this at the subject level, not only at the window level

Why this is especially justified here:
- current honest subject-level denominators are tiny
- for a representative `1/2` subject sensitivity result, the exact 95% binomial interval is about `[0.013, 0.987]`
- for a representative `3/3` subject specificity result, the exact 95% binomial interval is about `[0.292, 1.000]`
- those widths are ugly, but they are the honest message of the current benchmark size

Repo effect:
- this is the smallest high-value honesty upgrade because it changes reporting, not training or data selection

### D. Keep threshold discipline simple and explicit

Recommended contract:
- keep one pre-declared primary subject threshold for the headline result
- keep the current mean-score subject aggregation rule for the primary result
- if threshold sweeps are shown, mark them exploratory and never pick the “best” threshold from the same tiny subject set as if it were a validated operating point

Repo effect:
- pass15 already points in this direction by showing that threshold tuning on the same tiny set does not rescue the benchmark honestly
- the benchmark contract should preserve that lesson rather than reopening free threshold optimization

### E. Add calibration-lite reporting, not heavy calibration machinery

Recommended contract:
- preserve per-subject mean scores in saved reports
- add a simple subject-level Brier score for probabilistic readout if easy
- defer full calibration curves / smoother fits until there are materially more subjects

Repo effect:
- this keeps calibration visible without pretending the repo has enough data for stable post-hoc calibration analysis

## What is overkill for this repo right now

These changes are not justified yet for the current tiny CAP benchmark:

1. Nested cross-validation for threshold tuning or model selection
- too expensive in degrees of freedom for `5` subjects
- would create procedural complexity without solving the tiny-N uncertainty problem

2. Learned calibration layers such as Platt scaling or isotonic regression
- too data-hungry for the current subject counts
- high risk of turning noise into pseudo-calibration

3. Rich calibration curves as a primary headline artifact
- with this few subjects, the curve is more likely to look precise than to be precise
- subject-score tables are currently a better lightweight surface

4. External-validation style claims
- the current repo is still a bounded internal benchmark and negative-result learning surface
- the literature supports caution here, not escalation

5. Deep uncertainty machinery, ensembles, or Bayesian model rewrites
- not the smallest next benchmarking upgrade
- would blur whether the project improved reporting honesty versus changed the model family

## One smallest benchmarking improvement to implement next

Add exact 95% Clopper-Pearson confidence intervals plus raw subject counts to the existing LOSO `subject_aggregation.summary` output in `train_baseline.py`, and make those subject-level interval-bearing metrics the first benchmark lines shown in future reports.

Why this is the best next step:
- it is directly supported by the tiny-sample and binomial-interval literature above
- it preserves the current scaffold, models, and subject split
- it makes the current benchmark more honest without inventing new model capacity
- it complements the repo's existing subject-level aggregation instead of replacing it

## Exact benchmark/reporting changes I would make here

Minimal contract change set:
1. README: state that the primary benchmark surface is LOSO subject-level performance, with random-window CV retained only as a leakage reference.
2. `train_baseline.py`: add exact 95% CI fields for subject-level sensitivity and specificity, plus explicit subject counts.
3. Future benchmark reports: show subject-level counts and exact CIs before window-level summaries.
4. Preserve one fixed primary subject threshold (`0.5`) and label any threshold sweep as exploratory only.
5. Optionally add subject-level Brier score if it is one small patch; do not block the CI patch on this.

## Exact repo files likely to change

Most likely direct code/docs touch points:
- `projects/bruxism-cap/src/train_baseline.py`
- `projects/bruxism-cap/README.md`
- `projects/bruxism-cap/reports/first-baseline.md`
- `wiki/concepts/bruxism-cap.md`

Possible optional helper / downstream touch points:
- `projects/bruxism-cap/src/eval.py` if comparison output should surface CI-aware subject summaries
- a small new helper such as `projects/bruxism-cap/src/stats_utils.py` if exact binomial intervals should be factored out cleanly

## Bottom line

The literature does not justify broadening this repo into nested CV, learned calibration, or heavier model work yet. It does justify hardening the benchmark contract in one narrow way: keep subject-grouped LOSO and subject-level aggregation as the primary endpoint, then add exact small-sample uncertainty reporting at that subject level so the current `5`-subject CAP benchmark cannot be overread.
