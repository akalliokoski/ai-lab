---
title: Bruxism CAP patched EMG vs matched C4 anchor comparison (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: comparison
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - ../projects/bruxism-cap/reports/pass35-patched-emg-vs-matched-c4-anchor-comparison.md
  - queries/bruxism-cap-emg-a1-record-relative-audit-2026-05-05.md
  - queries/bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05.md
  - queries/bruxism-cap-c4-record-relative-comparator-2026-05-05.md
  - queries/bruxism-cap-c4-a1-percentile-band-vs-emg-2026-05-05.md
---

# Question
After the patched EMG runs and the matched `C4-P4` comparator rebuild, what is actually a channel effect, what is still a scaffold effect, and which result should guide the next bounded step?

# Short answer
`C4-P4` still wins on the narrow honest subject-level criterion, but only weakly after the matched record-relative rebuild, and both channels still remain bottlenecked by the repaired `A1-only` scaffold.

The strongest clean comparator is still pre-transform `pass29 C4-P4` (`0.750` subject balanced accuracy, `0.500` sensitivity, `1.000` specificity). The latest transformed `C4-P4` rerun drops to `0.583 / 0.500 / 0.667`, which shows that the pass34 normalization gain is not a channel-agnostic scaffold fix. A later honest-anchor verdict also narrows the EMG interpretation: pass35 shape repairs the named EMG score gaps more symmetrically than pass34, but it does not materially beat pass34 at the subject level and still does not catch the stronger matched `C4-P4` anchor. [[bruxism-cap]] [[bruxism-cap-emg-a1-shape-feature-expansion-2026-05-05]] [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]

# Comparison table
## Honest subject-level summaries
- `pass34` EMG record-relative: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- `pass35` EMG shape: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- `pass35` matched `C4-P4` record-relative: balanced accuracy `0.583`, sensitivity `0.500`, specificity `0.667`
- `pass29` matched `C4-P4` baseline anchor: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

## Gap-focused score checks
- `pass34` EMG record-relative:
  - `brux2 - n3`: `+0.041`
  - `n3 - brux1`: `+0.259`
- `pass35` EMG shape:
  - `brux2 - n3`: `+0.174`
  - `n3 - brux1`: `+0.009`
- `pass35` matched `C4-P4` record-relative:
  - `brux2 - n3`: `-0.338`
  - `n3 - brux1`: `-0.069`

# What is really a channel effect
`C4-P4` remains the only channel that actually produces a held-out positive bruxism subject on this repaired scaffold. Even after its regression under the matched transform, it still has subject sensitivity `0.500`, while both EMG mixed results remain at `0.000`.

That means the claim “channel still matters” survives this comparison. The repo should not rewrite the benchmark as if EMG has already caught up to the comparison channel.^[../projects/bruxism-cap/reports/pass35-patched-emg-vs-matched-c4-anchor-comparison.md]

# What is still a scaffold effect
The latest comparison is even stronger evidence that the benchmark is still scaffold-limited rather than cleanly solved by channel selection:
- the original matched percentile-band comparison already left `brux1` below `n3` under both channels
- pass34 fixes the `brux2` reversal but leaves `brux1` essentially untouched
- pass35 shape improves both named EMG gaps but still leaves both bruxism subjects below threshold
- matched transformed `C4-P4` flips the recoverable subject from `brux2` to `brux1` and turns `n3` into a false positive

So each representation tweak is still trading one failure surface against another instead of producing a robust two-bruxism-subject solution. That is the main scaffold bottleneck signal, not just a model-choice quirk. [[bruxism-cap-c4-record-relative-comparator-2026-05-05]] [[bruxism-cap-emg-a1-record-relative-audit-2026-05-05]]

# Anchor decision
## EMG-first anchor
Do not declare a single new EMG mixed-result winner yet.

Why:
- pass34 and pass35 tie on the subject-level headline that matters (`0.500` balanced accuracy, `0.000` sensitivity, `1.000` specificity)
- pass35 is better at symmetric repair of the two named EMG gaps
- pass34 is better at preserving the strongest `brux2` lift on the repaired scaffold
- the honest-anchor verdict shows that promoting pass35 alone overstates the result, because the decision-layer outcome did not improve and the stronger `C4-P4` comparator still remains ahead overall

So pass34 should be preserved as the normalization clue, pass35 should be preserved as the shape-family clue, and the next bounded move should test whether the two gains compose honestly rather than forcing an anchor choice prematurely. [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]

## Comparison-channel anchor
Keep `pass29 C4-P4` as the comparison-channel anchor. Do not promote transformed `pass35 C4-P4`, because that run is primarily evidence against over-generalizing the record-relative transform rather than evidence of a better benchmark state.

# Exact next bounded step
Stay EMG-first and stay on the repaired percentile-band `A1-only` scaffold. Start from the pass34 record-relative scaffold, add the same four compact shape features used in pass35, and keep the selector, LOSO split, model family, and exclusion contract fixed.

That is now the tightest next question left by this comparison and the later honest-anchor verdict: can the pass34 `brux2` improvement and the pass35 symmetric gap repair compose into a real subject-sensitivity gain without reopening channel or extraction drift? [[bruxism-cap-pass35-shape-vs-honest-anchors-verdict-2026-05-05]]
