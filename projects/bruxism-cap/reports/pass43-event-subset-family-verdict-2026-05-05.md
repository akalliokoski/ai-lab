# Pass43 fixed event-subset family verdict

Date: 2026-05-05

Scope: decide what the board learned after the pass43 transfer audit by combining the verified pass42 three-feature event subset result, the bounded literature/audit read on the subset, and the pre-registered verdict rubric.

## Inputs compared
- pass36 repaired `A1-only` EMG scaffold: first honest EMG surface that recovered subject-level sensitivity on the repaired percentile-band / time-aware table, but only through `brux2`
- pass42 repaired `A1-only` event-subset result: same pass36 scaffold plus exactly `evt_active_fraction`, `evt_burst_duration_median_s`, and `evt_interburst_gap_median_s`
- pass14 old matched14 `A3-only` EMG baseline: closest pre-existing `A3-only` matched surface before the new transfer audit
- pass43 old matched14 `A3-only` transfer check: pass14 table plus the exact same three event features, with no broader feature or model-family change
- pass29 `C4-P4` comparator context: stronger non-EMG honest anchor on its own matched `A1-only` percentile-band scaffold
- literature/audit note: the surviving event features look more like burst occupancy / width / clustering descriptors than pure `A1`-locked amplitude quirks, but family claims stay fragile because `A1` and `A3` also change row availability and sampling surfaces in this repo

## Pre-registered rubric read
The rubric made subject-level LOSO primary, required tiny-N counts and intervals to stay visible, and allowed four verdicts only: `A1-specific`, `A3-transferable`, `family-ambiguous`, or `scaffold-bound`.

## Core evidence

### pass42 repaired `A1-only` subset anchor
- balanced_accuracy: `0.750`
- sensitivity: `0.500` (`1/2`; exact 95% CI `0.013` to `0.987`; Wilson `0.095` to `0.905`)
- specificity: `1.000` (`3/3`; exact 95% CI `0.292` to `1.000`)
- best-bruxism-minus-highest-control margin: `+0.339`
- subject scores:
  - `brux1` `0.136`
  - `brux2` `0.825`
  - `n3` `0.155`
  - `n5` `0.199`
  - `n11` `0.486`

### pass14 old matched14 `A3-only` baseline
- balanced_accuracy: `0.500`
- sensitivity: `0.000` (`0/2`)
- specificity: `1.000` (`3/3`)
- best-bruxism-minus-highest-control margin: `-0.091`
- subject scores:
  - `brux1` `0.176`
  - `brux2` `0.074`
  - `n3` `0.267`
  - `n5` `0.266`
  - `n11` `0.095`

### pass43 old matched14 `A3-only` transfer check with the fixed subset
- balanced_accuracy: `0.500`
- sensitivity: `0.000` (`0/2`; exact 95% CI `0.000` to `0.842`; Wilson `0.000` to `0.658`)
- specificity: `1.000` (`3/3`; exact 95% CI `0.292` to `1.000`)
- best-bruxism-minus-highest-control margin: `-0.134`
- subject scores:
  - `brux1` `0.176`
  - `brux2` `0.130`
  - `n3` `0.208`
  - `n5` `0.128`
  - `n11` `0.310`

### What moved and what did not
- `brux1` basically held on the old `A3-only` surface: `0.176 -> 0.176` versus pass14, so the subset is not behaving like pure repaired-`A1` noise.
- `brux2` improved on `A3` versus pass14 (`0.074 -> 0.130`) but stayed far below the repaired pass42 `A1` anchor (`0.825`).
- `n3` and `n5` improved downward on `A3` versus pass14, which is directionally good.
- `n11` worsened sharply on `A3` versus pass14 (`0.095 -> 0.310`), although it stayed below threshold.
- The honest subject-level headline on `A3` did not change at all: sensitivity stayed `0/2`, balanced accuracy stayed `0.500`, and the highest control still outranked the best bruxism subject.

## Final verdict
Verdict: `scaffold-bound`.

Reason:
1. The result is not cleanly `A1-specific`, because the exact same three features do carry some directional signal onto the old matched `A3-only` surface: `brux1` holds, `brux2` lifts a bit, and two controls move down.
2. The result is not `A3-transferable`, because the honest subject-level endpoint remains unchanged on `A3`: sensitivity is still `0/2`, balanced accuracy is still `0.500`, and the best control still outranks `brux1`.
3. `family-ambiguous` is too weak as the main label because the dominant visible confound is scaffold mismatch, not a symmetric split between family stories. The comparison is still repaired `A1` (`50` rows, percentile-band/time-aware surface) versus old matched14 `A3` (`70` rows, older surface), and the literature read already predicted that these event descriptors should be less family-locked than amplitude-family effects.
4. So the most honest board read is that the verified subset currently looks portable in direction but not yet portable as an honest benchmark win; the observed gain is still bound to the repaired scaffold it was discovered on.

## Does this become the new active EMG benchmark surface?
Yes, but only in the narrow repaired-EMG sense.

- Promote pass42 as the active EMG benchmark surface inside the EMG branch: repaired `A1-only` scaffold plus the fixed three-feature event subset.
- Do not promote it as a family-general EMG benchmark yet.
- Do not replace the broader honest comparator context with it: pass29 `C4-P4` still matters as the stronger non-EMG anchor because it also reached `0.750 / 0.500 / 1.000`, and its `brux1` score (`0.405`) is still much healthier than pass42 `brux1` (`0.136`).

So the board should treat pass42 as the current active EMG working surface, not as a settled cross-family or project-wide winner.

## Exact comparison against pass42 / pass36 / pass14 / pass29

### versus pass36
- pass36 and pass42 share the same repaired `A1-only` scaffold and the same subject-level headline (`0.750 / 0.500 / 1.000`).
- pass42 is the cleaner local EMG state because it keeps the pass36 rescue while improving the target subject (`brux1` `0.112 -> 0.136`) and keeping `n11` below threshold (`0.489 -> 0.486`) after the broader pass41 event bundle had reopened that control.
- This means the event-subset branch added real local value on the repaired surface, even though it did not solve threshold crossing for `brux1`.

### versus pass42
- pass43 did not reproduce the pass42 honest gain on `A3`.
- The main failure is not total subject-score collapse; it is that the repaired pass42 gain stayed threshold-irrelevant on the old `A3` surface.
- `brux1` held (`0.136` on repaired `A1` vs `0.176` on old `A3`), but the repaired pass42 branch depended heavily on `brux2` clearing threshold, and that did not transfer (`0.825` -> `0.130`).
- Therefore pass43 did not invalidate pass42; it limited pass42's interpretation.

### versus pass14
- pass14 had already shown that old matched14 `A3-only` was the less-bad EMG family on that older surface, but still an honest negative result.
- pass43 improved that old `A3` score ordering in a few places (`brux2` up, `n3` down, `n5` down), yet the same honest verdict persisted.
- So the fixed subset taught the board something useful about signal direction, but not enough to rewrite the old `A3` family verdict.

### versus pass29
- pass29 remains an important context anchor because it already achieved the same subject-level headline as pass36/pass42 (`0.750 / 0.500 / 1.000`) while producing a much stronger `brux1` score (`0.405`) on its own matched `C4-P4` comparison scaffold.
- The pass42/pass43 event-subset story therefore does not yet justify saying EMG has surpassed the stronger comparator context; it only says the EMG branch now has a cleaner active working surface worth continuing.

## What the literature lane changed in interpretation
The literature/audit lane matters because it blocks an overreaction in both directions.

- It argues against reading the three features as pure `A1`-locked artifacts, because burst occupancy, typical burst width, and inter-burst gap are plausible jaw-EMG organization descriptors that should transfer better than raw amplitude quirks.
- It also argues against overclaiming transfer from pass43, because CAP family labels are EEG microstructure labels and in this repo they also change which rows survive the filter, which subjects are balanced, and which time positions get sampled.
- Combined with pass43, that pushes the board toward a scaffold explanation: the subset likely contains some family-weak information, but the current `A3` surface is too mismatched to certify transfer honestly.

## Primary next bounded task
Primary branch only: rebuild the `A3-only` comparison table on the repaired percentile-band / time-aware `EMG1-EMG2` scaffold while keeping the exact same three event features fixed.

Why this wins:
- It directly tests the dominant remaining uncertainty: whether the failed transfer verdict is mostly old-surface mismatch or true family dependence.
- It preserves the subset identity, model family, and tiny-N interpretation contract.
- It does not open privacy, LLM/RL, or broader feature creep before the core benchmark question is answered.

## Backup task not promoted yet
Backup only, not promoted: run one matched within-record `A1`-vs-`A3` interaction audit on the already selected event windows using the fixed backbone plus the three event terms and three event-by-family interaction terms.

Why it stays backup:
- It is analytically useful only if the repaired `A3` rebuild still leaves the verdict unclear.
- It adds another inference layer before the cleaner scaffold question has been resolved.

## Gate status
- Privacy branch: not promoted.
- LLM/RL branch: not promoted.
- Model-family change: not promoted.
- Broader feature expansion: not promoted.

## Bottom line
The board did learn something real after pass43, but it is narrower than a family win. The verified three-feature event subset is probably not just repaired-`A1` noise, yet it still has not earned an honest cross-family transfer claim. The best current label is `scaffold-bound`: keep pass42 as the active EMG working surface, preserve tiny-N caution, and answer the repaired-`A3` scaffold question before promoting any broader branch.