---
title: Bruxism CAP C4 percentile-band `A1-only` vs EMG (2026-05-05)
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [research, dataset, evaluation, experiment, notes]
sources:
  - concepts/bruxism-cap.md
  - ../projects/bruxism-cap/reports/pass28-emg-a1-percentile-band-rerun.md
  - ../projects/bruxism-cap/reports/pass29-c4-a1-percentile-band-vs-emg.md
---

# Question
On the new percentile-band `A1-only` timing-controlled scaffold, does the comparison channel `C4-P4` still outperform primary-channel `EMG1-EMG2`, and if so, does that overturn the EMG-first project framing?

# Short answer
Yes, `C4-P4` is stronger on this exact matched scaffold, but no, that does not by itself justify reverting the whole project back to EEG-first.

Pass29 answers the pass28 follow-up cleanly: on the same verified `5`-subject subset, the same exclusive `SLEEP-S2 + MCAP-A1-only` rule, the same percentile-band timing control (`0.10` to `0.90`), the same `10` windows per subject, and the same train-time exclusions, `C4-P4` improves the honest LOSO surface relative to `EMG1-EMG2`.

# What stayed fixed
- subjects: `brux1`, `brux2`, `n3`, `n5`, `n11`
- event rule: exclusive `SLEEP-S2 + MCAP-A1-only`
- timing selector: percentile-band `0.10` to `0.90`
- cap: `10` windows per subject
- train-time exclusions: `^bp_`, `^rel_bp_`, `^ratio_`
- matched rows: `50`

The matched timing summary is identical between pass28 and pass29, so this is a real channel comparison rather than a hidden sampling change.

# Matched result

## Honest LOSO window-level best model
- `EMG1-EMG2` pass28: balanced accuracy `0.600`, sensitivity `0.000`, specificity `0.600`
- `C4-P4` pass29: balanced accuracy `0.760`, sensitivity `0.260`, specificity `0.500`

## Honest LOSO subject-level best model
- `EMG1-EMG2` pass28: balanced accuracy `0.500`, sensitivity `0.000`, specificity `1.000`
- `C4-P4` pass29: balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

So the comparison channel clearly wins on the honest surface for this scaffold.

# What changed in subject ordering
Under pass28 EMG, all controls outranked both bruxism subjects:
- `n3` `0.422`
- `n11` `0.319`
- `n5` `0.264`
- `brux1` `0.222`
- `brux2` `0.209`

Under pass29 `C4-P4`, the ordering becomes much less hostile:
- `brux2` `0.959`
- `n3` `0.417`
- `brux1` `0.405`
- `n5` `0.212`
- `n11` `0.188`

This matters because the new gap is no longer “EMG collapses both bruxism subjects.” It is now narrower:
- `C4-P4` strongly recovers `brux2`
- `C4-P4` also lifts `brux1`, but not quite enough to clear `n3`
- the remaining failure surface is therefore mainly `brux1` versus `n3`

# Does this beat the current best honest baseline?
Not clearly.

Pass29 ties the older pass12 `C4-P4 A1-only` subject-level honest verdict rather than beating it:
- pass12 subject-level balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`
- pass29 subject-level balanced accuracy `0.750`, sensitivity `0.500`, specificity `1.000`

So pass29 should be read as:
- a benchmark-clarity win over pass28 EMG on the same timing-controlled scaffold
- a measurement-hardening result that preserves the percentile-band selector as useful infrastructure
- not yet a new overall project-best detector

# Project-shape implication
This does **not** overturn the EMG-first framing by itself.

Why not:
1. The project objective is still an EMG-first, leakage-aware, reproducible CAP benchmark, not a claim that EMG must already be the strongest channel on every bounded scaffold.
2. The comparison result is useful exactly because it sharpens the next EMG-first question: why does `brux1` stay below `n3`, and why does `brux2` recover under `C4-P4` but not under `EMG1-EMG2`, when the scaffold is otherwise identical?
3. A matched comparison channel that currently wins is evidence to explain, not a reason to erase the EMG-first research direction.

# Recommended next bounded step
Do one compact cross-channel validity audit on the same pass28/pass29 percentile-band `A1-only` rows:
- compare feature and score behavior for `EMG1-EMG2` versus `C4-P4`
- focus specifically on `brux1` versus `n3`
- keep the scaffold fixed before trying any new model family or broader extraction rewrite

That preserves the EMG-first mission while using pass29 as the clearest available comparison anchor. [[bruxism-cap]] [[bruxism-cap-emg-a1-percentile-band-rerun-2026-05-05]] [[bruxism-cap-c4-vs-emg-timepos-a3-2026-05-05]]
