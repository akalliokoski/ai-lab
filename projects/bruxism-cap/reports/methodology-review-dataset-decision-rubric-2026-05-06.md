# Methodology review — dataset decision rubric for `bruxism-cap` beyond CAP

Date: 2026-05-06
Status: completed methodology review memo.

## Question
How should this repo decide whether `bruxism-cap` should stay a tiny CAP pilot, expand within CAP, or pivot to a new dataset branch, given the current benchmark state after repaired `pass42` / `pass45` / `pass46`?

## Short answer
Use a science-first weighted rubric that treats label validity and tiny-`N` honesty as harder constraints than raw dataset size or model ambition.

Right now the repo should default to staying inside CAP unless a candidate next dataset clearly improves label validity and jaw-muscle relevance without making subject-level evaluation less honest or reproducibility materially worse.

## Project-state anchor
The current repo state is not “CAP has failed.” It is:
- CAP remains the only clearly open, already-ingested dataset with a reproducible audit trail in the repo.
- `EMG1-EMG2` is the right primary signal family for translational alignment, but the benchmark is still tiny and subject-unstable.
- The strongest honest surfaces still stop at subject-level sensitivity `0.500`, with repaired `pass42`, `pass45`, and `pass46` all sharing the same tiny-`N` headline while differing mainly on paired subject-score surfaces.
- The main methodological lesson so far is that scaffold fairness, label validity, and paired subject-level reading matter more than raw feature novelty.

So the decision is not “which dataset is biggest?” It is “which next dataset choice most improves scientific validity per unit complexity without letting the benchmark become less honest?”

## Weighted dataset-decision rubric
Score each candidate branch on a 0-5 scale per criterion, then multiply by the weight. Maximum total = 100.

### 1. Positive-label validity — weight 25
Question: how trustworthy are the positive bruxism labels as actual bruxism-related events rather than weak proxies?

High score:
- labels are anchored to PSG-grade or otherwise well-validated scoring
- event definitions are explicit and auditable
- label provenance is available per record / per event

Low score:
- labels are simulated, heuristic, EMG-only without a strong validity anchor, or poorly documented

Why this is first:
A bigger dataset with weaker positives would make the repo look busier while making the actual benchmark less scientific.

### 2. Jaw-muscle relevance — weight 20
Question: how directly does the dataset measure the physiology the project actually cares about?

High score:
- direct jaw-muscle EMG or very close validated jaw-activity sensing
- enough signal detail to support burst / episode organization features

Low score:
- indirect EEG-only or non-jaw proxies unless they are clearly the best available validity anchor

Why this matters now:
The repo has already learned that translational alignment improves when the benchmark is EMG-first, not EEG-first.

### 3. Subject-level evaluation honesty — weight 20
Question: can the candidate support leakage-aware subject-level evaluation that stays honest under tiny or moderate `N`?

High score:
- enough distinct subjects for grouped LOSO or similarly strict subject-held-out evaluation
- clear subject IDs and no forced leakage-prone splitting
- enough per-subject support to report exact uncertainty rather than hide it

Low score:
- no reliable subject identities
- only pooled segments with no subject-aware split
- apparent scale that still collapses to very few real positive subjects

Why this matters now:
This repo’s core methodological advance is not a feature family; it is refusing to trust random-window wins.

### 4. Ecological validity — weight 12
Question: does the dataset move the repo toward real wearable / home / multi-night bruxism monitoring rather than only one-night lab convenience?

High score:
- home or wearable collection
- multi-night structure
- realistic natural behavior rather than simulation

Low score:
- short lab-only snapshots with weak relation to real use

Why the weight is not higher yet:
This matters scientifically, but the repo should not sacrifice benchmark honesty and openness just to sound more translational.

### 5. Openness and reproducibility — weight 10
Question: can another person actually download, inspect, rerun, and audit the dataset branch?

High score:
- openly downloadable
- stable licensing / access
- enough metadata and documentation for reproduction

Low score:
- on-request data, proprietary devices, unclear access, or private cohorts

Why this still matters a lot:
A non-open branch may be scientifically attractive, but it weakens the repo’s role as a public benchmark scaffold.

### 6. Portability toward future wearable work — weight 8
Question: if the repo later moves to private wearable jaw EMG, does work on this dataset still transfer?

High score:
- same signal family or same event logic likely reusable later
- feature / audit logic stays relevant to future off-lab sensing

Low score:
- highly dataset-specific artifacts with little value for a wearable transition

### 7. Implementation tractability — weight 5
Question: can the branch be brought up cleanly without derailing the project into infra churn?

High score:
- data are accessible now
- channel mapping and labels are clear
- bounded extraction / evaluation work

Low score:
- heavy acquisition friction, ambiguous formats, or major pipeline rewrite needed before any honest benchmark exists

Why this is last:
Tractability matters, but this repo should not let convenience outrank scientific validity.

## Outcome thresholds
Apply both weighted score thresholds and hard guards.

### Outcome A — stay-on-CAP pilot
Choose this if any of the following is true:
- no candidate new dataset scores at least 70/100, or
- no candidate clearly beats CAP on positive-label validity, or
- the candidate improves ecology but loses openness or subject-level honesty, or
- the candidate requires speculative data access rather than a runnable benchmark now

Interpretation:
- keep CAP as the bounded public benchmark
- continue narrow within-CAP experiments
- treat future wearable work as a planned later branch, not an immediate dataset move

This is the default current outcome.

### Outcome B — expand-within-CAP
Choose this if:
- CAP itself still scores acceptably on honesty and openness,
- no outside dataset clearly beats it on the weighted rubric,
- and there remains one scientifically meaningful within-CAP move that improves validity without broadening scope

Practical meaning here:
- keep the dataset fixed
- allow stricter or better-matched CAP subset/scaffold work
- allow channel-family or event-definition refinement inside the same audited corpus
- do not market that as a new dataset branch

Current repo state fits here most strongly.

### Outcome C — pivot-to-new-dataset
Require all of these:
1. candidate weighted score at least 80/100
2. candidate beats CAP by at least 12 points overall
3. candidate scores at least 4/5 on positive-label validity
4. candidate scores at least 4/5 on jaw-muscle relevance
5. candidate does not score worse than CAP on subject-level evaluation honesty
6. access is real enough to reproduce now, not just literature aspiration

Interpretation:
Only pivot when the new branch is not merely newer or larger, but plainly more scientifically grounded for this exact benchmark mission.

## What matters most right now vs later
### Matters most right now
1. Positive-label validity
2. Subject-level evaluation honesty
3. Jaw-muscle relevance
4. Openness / reproducibility

Reason:
The repo is still proving that it can produce an honest benchmark at all. At this maturity stage, a dataset that weakens validity or obscures tiny-`N` uncertainty would be a regression even if it looks more modern.

### Matters more later
1. Ecological validity
2. Portability to future wearable / privacy-preserving work
3. Larger-scale implementation tractability for multi-night or intervention-aware branches

Reason:
Those become more important after the repo has either stabilized a good-enough CAP benchmark or identified a clearly superior open corpus. They should shape the next branch, but not prematurely override the current benchmark contract.

## Seductive but weak criteria that should NOT drive the decision
Do not pivot mainly because of:
- bigger raw `N` when the positive labels are weaker or less auditable
- more windows / more rows when the number of real positive subjects stays tiny
- availability of deep models or GPU-heavy methods
- literature trendiness alone (“wearable”, “AI”, “closed-loop”, “intervention-aware”) without open data and honest evaluation support
- channel novelty without clearer bruxism-label validity
- apparent window-level accuracy that cannot survive subject-held-out evaluation
- proprietary-device prestige or polished paper narratives without reproducible corpus access

In this repo, those are exactly the kinds of criteria that could create fake progress.

## Current recommendation
Recommendation: do not open a new dataset branch yet.

The project should currently be read as “expand within CAP while preserving the benchmark’s honesty contract,” not as “stay forever on CAP” and not as “pivot now.”

Why:
- CAP is still the only clearly open runnable corpus in the repo.
- The translational literature strengthens the EMG-first framing but still does not supply a clearly better open benchmark.
- The active bottleneck is still benchmark maturity inside the repaired CAP scaffold, not dataset exhaustion.
- The repo is still learning from paired subject-level surfaces inside a tiny but auditable frame.

## One evidence demand before opening a new dataset branch
Before opening any new dataset branch, require a one-page evidence pack proving all four of these:
1. exact access path and license are real now
2. positive-label provenance is materially stronger than CAP’s proxy surface
3. jaw-muscle signal relevance is at least as direct as `EMG1-EMG2`
4. the dataset supports a subject-held-out evaluation contract at least as honest as the current grouped LOSO benchmark

If that pack cannot be assembled, the branch should stay in wiki/planning form rather than becoming an active benchmark branch.

## Exact files likely to touch next
If the repo stays on the current recommendation, the next likely files are:
1. `projects/bruxism-cap/src/run_pass47_repaired_a3_event_trio_swap_phasic_fraction.py`
2. `projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-pct10-90-record-relative-eventsubset-no-shape-phasic-swap.json`
3. `projects/bruxism-cap/reports/pass47-repaired-a3-event-trio-swap-phasic-fraction.json`
4. `projects/bruxism-cap/reports/pass47-repaired-a3-event-trio-swap-phasic-fraction.md`
5. `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.json`
6. `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.md`
7. `projects/bruxism-cap/reports/campaign-handoff-2026-05-05.md`
8. `wiki/queries/bruxism-cap-dataset-decision-rubric-2026-05-06.md`
9. `wiki/concepts/bruxism-cap.md`

If a later branch-spec task really finds a superior new dataset, then the likely touch set would shift toward:
10. `wiki/queries/<new-dataset-branch-spec>.md`
11. `projects/bruxism-cap/README.md`
12. a new dataset-specific pipeline script under `projects/bruxism-cap/src/`

## Bottom line
For this repo, the right dataset decision rule is not “switch when something looks more modern.” It is “switch only when a candidate dataset clearly improves label validity and jaw-muscle relevance without weakening tiny-`N` honesty or reproducibility.”

Under that rule, the current answer is: keep the project inside CAP, keep the framing EMG-first, and treat any future non-CAP branch as evidence-gated rather than aspiration-gated.
