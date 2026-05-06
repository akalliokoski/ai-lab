# Pass35 shape vs honest anchors verdict

Date: 2026-05-05

Scope: judge whether the new EMG pass (`loso-cv-pass35-emg-a1-pct10-90-shape.json`) materially improves the honest baseline without relying on random-window CV or train-loss proxies.

## Anchors compared
- EMG repaired scaffold baseline: pass28
- EMG raw-location ablation anchor: pass33
- EMG record-relative anchor: pass34
- Strong non-EMG honest comparator: pass29 (C4)

## Core comparison

### Subject-level metrics
- pass35 shape: balanced_accuracy 0.50, sensitivity 0.00, specificity 1.00
- pass34: balanced_accuracy 0.50, sensitivity 0.00, specificity 1.00
- pass33 EMG: balanced_accuracy 0.33, sensitivity 0.00, specificity 0.67
- pass28 EMG: balanced_accuracy 0.33, sensitivity 0.00, specificity 0.67
- pass29 C4: balanced_accuracy 0.75, sensitivity 0.50, specificity 1.00

### Score-ordering / gap checks
- pass35 shape closes `brux2 - n3` from -0.494 (pass28) and -0.492 (pass33) to +0.174.
- pass35 shape nearly closes `n3 - brux1` from +0.260 (pass28) / +0.497 (pass33) / +0.259 (pass34) to +0.009.
- pass35 shape still does not clear the threshold on either brux subject:
  - brux1 mean_score 0.216
  - brux2 mean_score 0.399
- pass35 shape ranking is still interleaved with controls:
  - brux2 0.399
  - n5 0.387
  - n3 0.225
  - brux1 0.216
  - n11 0.188
- So controls still outrank at least one bruxism subject, and one control (`n5`) sits almost on top of the strongest brux subject.

## Interpretation
The new shape-feature pass is a real ordering improvement over the older EMG anchors (pass28/pass33): the worst control-vs-brux inversions shrink dramatically and the best brux subject now outranks the strongest problematic control (`n3`).

But it does not materially beat the current honest EMG anchor, because pass34 already achieved the same subject-level outcome (balanced_accuracy 0.50, sensitivity 0.00, specificity 1.00), and pass35 shape still leaves both brux subjects below the 0.5 subject threshold. It also remains clearly behind the stronger honest comparator pass29, which still has the only positive subject-level sensitivity (0.50).

## Current bottleneck after the run
The bottleneck is no longer gross score inversion between `brux2` and `n3`; it is threshold-crossing subject sensitivity. The representation change improved ranking geometry, but not enough to lift either brux subject above the decision threshold, especially `brux1`, while at least one control remains interleaved with the brux scores.

## Verdict
Ambiguous.

Reason: positive directional change in subject ordering versus older EMG anchors, but no subject-level sensitivity gain versus pass34 and no material beat of the honest comparator set overall.

## Best next bounded step
Run one bounded apples-to-apples audit that combines the two best EMG ideas instead of stacking unrelated changes: apply the same four compact shape features on top of the pass34 record-relative scaffold, then compare only pass34 vs `record-relative + shape` on the same five-subject LOSO split and the same subject-score gap checks.
