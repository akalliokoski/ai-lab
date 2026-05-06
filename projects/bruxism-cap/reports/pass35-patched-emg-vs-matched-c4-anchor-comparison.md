# Pass 35/34 synthesis — patched EMG vs matched C4 on the repaired `A1-only` scaffold

Date: 2026-05-05
Status: comparison/synthesis completed; compared the two mixed EMG repair paths against the matched `C4-P4` comparator to separate channel effects from scaffold effects before choosing the next anchor.

## Runs compared
- `pass34` `EMG1-EMG2` record-relative audit on the repaired percentile-band `A1-only` scaffold
- `pass35` `EMG1-EMG2` compact shape-feature expansion on the same scaffold
- `pass29` `C4-P4` matched percentile-band baseline comparator
- `pass35` `C4-P4` record-relative comparator rebuild on the same scaffold

## Honest subject-level verdict
`C4-P4` still wins on the narrow subject-level benchmark, but only weakly and not cleanly after the matched transform test.

- best EMG mixed results:
  - `pass34` subject balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
  - `pass35` shape subject balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- matched transformed `C4-P4`:
  - `pass35` subject balanced accuracy `0.583`, sensitivity `0.500`, specificity `0.667`
- clean matched comparison-channel anchor still remains the pre-transform `pass29 C4-P4` result:
  - subject balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

So the channel story is now: `C4-P4` still beats EMG on honest subject-level detection, but the matched record-relative comparator shows that this is not because the repaired scaffold was universally fixed. The transform helps EMG more than it helps `C4-P4`, yet neither transformed branch resolves the benchmark cleanly.

## What the comparison says about channel effects vs scaffold effects
### Channel effect that survives
`C4-P4` remains the only channel that actually produces a positive held-out bruxism subject on this scaffold. Even after the transform regression, it still has subject sensitivity `0.500` while both EMG mixed results stay at `0.000`.

### Scaffold bottleneck that survives
Both channels are still bottlenecked by the same repaired `A1-only` benchmark rather than only by feature family choice:
- EMG still cannot push either `brux1` or `brux2` above the `0.5` subject threshold.
- `C4-P4` can no longer keep both the `brux2` separator and clean controls once the matched transform is applied.
- The original matched audit already showed the shared bottleneck: `brux1` versus `n3` stayed unresolved under both channels on the same selected rows.

This means the repo should not read the latest evidence as either:
- “EMG is now fixed”, or
- “C4 is universally better regardless of representation.”

Instead, the scaffold is still fragile enough that each representation tweak repairs one failure surface while exposing another.

## EMG anchor decision
For the next EMG-first representation step, promote `pass35` shape to the new mixed-result EMG anchor.

Why `pass35` shape beats `pass34` record-relative as the working anchor:
- same honest subject-level headline (`0.500` balanced accuracy, `0.000` sensitivity, `1.000` specificity)
- better symmetric gap repair:
  - `pass34`: `brux2 - n3 = +0.041`, `n3 - brux1 = +0.259`
  - `pass35` shape: `brux2 - n3 = +0.174`, `n3 - brux1 = +0.009`
- keeps all controls below threshold, unlike transformed `C4-P4`
- does not depend on a transform that the matched comparator just showed to be non-portable across channels

So `pass34` should be preserved as an important clue about EMG-specific normalization, but `pass35` shape is the stronger anchor for the next bounded EMG-only increment because it improves both named score gaps at once on the unchanged scaffold.

## Comparator-anchor decision
Do not replace the comparison-channel anchor with transformed `pass35 C4-P4`.
Keep `pass29 C4-P4` as the clean comparison anchor, and keep `pass35 C4-P4` only as evidence that the record-relative transform is not a channel-agnostic scaffold upgrade.

## Exact next bounded step
Run one EMG-only follow-up from the new `pass35` shape anchor:
- keep the repaired percentile-band `A1-only` scaffold fixed
- keep `logreg` LOSO and the same train-time exclusions fixed
- keep the compact shape family already added
- add exactly one small within-record normalization layer to the shape-sensitive EMG features only, then compare against `pass35` shape

The key discipline is not to reopen channel choice or extraction yet. The bounded question should be: can the EMG shape anchor recover the remaining `brux1` deficit without losing the cleaner control ordering that `pass35` shape achieved?
