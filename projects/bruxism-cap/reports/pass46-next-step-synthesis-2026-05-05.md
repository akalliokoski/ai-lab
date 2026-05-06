# Post-pass46 next-step synthesis — choose exactly one new bounded experiment outside the failed one-feature density add-back lane

Date: 2026-05-05
Status: synthesis completed after inspecting the preserved pass44/pass45/pass46 verdict and asymmetry artifacts plus the current `wiki/concepts/bruxism-cap.md` state.

## Scope held fixed
- keep the CAP five-subject benchmark frame fixed: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep `EMG1-EMG2` as the primary channel
- keep grouped `LOSO`, subject-level primacy, threshold `0.5`, and tiny-`N` caution fixed
- no dataset switch, no deep model branch, no privacy/LLM/RL activation, no scaffold rewrite, and no broad feature explosion
- keep `pass45` as the repaired `A3-only` anchor unless one later bounded run actually beats it on the paired repaired-`A3-only` surface

## 1) Current bottleneck after pass46
The bottleneck is no longer whether one extra event-organization feature can move `brux2` at all. `pass46` answered that narrowly: `evt_bursts_per_episode_mean` is biologically coherent and does give a believable tiny `brux2` lift on repaired `A3-only` (`0.178 -> 0.196`), but that lift is not selective enough to improve the actual benchmark bottleneck.

The active bottleneck after `pass46` is still this exact repaired-`A3-only` subject split:
- `brux1` remains the rescued subject on the repaired no-shape `A3-only` surface (`0.641` on `pass45`, `0.639` on `pass46`)
- `brux2` remains below the highest control (`0.196 < 0.347` on `pass46`)
- the strict headline stays fixed at `0.750 / 0.500 / 1.000`
- the paired repaired-`A3-only` best-bruxism-minus-highest-control margin slips slightly versus the `pass45` anchor (`+0.295 -> +0.292`)

So the branch is still count-matched but subject-unstable, and the unresolved miss is still broad under-support for `brux2` on the repaired `A3-only` table rather than absence of any event signal whatsoever.

## 2) Which candidate next moves still survive repo contact
Only a small set of moves still survives both the earlier repo contact and the new negative `pass46` verdict:

### A. Keep `pass45` as the repaired `A3-only` anchor
This survives cleanly because `pass46` did not beat it on headline counts, paired repaired-`A3-only` margin, or the cross-family `brux2` separation criterion.

### B. Keep working inside the compact event-organization lane, but not inside the exact `evt_bursts_per_episode_mean` add-back lane
Repo contact still says the event family is not dead:
- `pass42` and `pass44` validated the base trio as a real cross-family organization block
- `pass46` showed that one extra organization term can move `brux2` directionally without reopening thresholded controls

But `pass46` also says that simply stacking one more density-style feature on top of the frozen `pass45` trio is not enough by itself.

### C. A fixed-width event-trio swap using `evt_phasic_like_episode_fraction`
This still survives repo contact better than the remaining alternatives.
Why it survives:
- `evt_interburst_gap_median_s` was the weakest retained member in the pass41 feature-ranking audit: it dragged `brux1` and reopened all three controls there
- `evt_phasic_like_episode_fraction` was not safe enough to keep earlier as the first same-table A1 choice, but it remained the main "interesting near-miss" because it stayed positive on `brux1` and sat inside higher-margin candidate trios
- the pass42 sweep preserved two nearby candidates that paired `evt_phasic_like_episode_fraction` with safer backbone features while keeping the same honest headline and strong margins (`+0.347` and `+0.344`)
- unlike `evt_burst_count_30s`, this tests a distinct episode-composition axis rather than another near-neighbor of the failed density/count add-back idea

### D. Keep the paired subject-surface audit as the mandatory readout
This survives even more strongly after `pass46`, because the headline stayed frozen again while the paired repaired-`A3-only` margin exposed the real negative result.

## 3) Which moves are explicitly rejected now
### Rejected now: promoting `pass46` over `pass45`
`pass46` is a preserved negative result, not the new repaired `A3-only` anchor.

### Rejected now: another immediate one-feature density/count add-back on top of `pass45`
This includes treating `evt_burst_count_30s` as the next promoted move.
Reason:
- it is too close to the just-failed lane conceptually
- in the pass41 follow-up ranking, `evt_burst_count_30s` was slightly worse everywhere than `evt_bursts_per_episode_mean`
- it is more exposed to simple density/opportunity confounding than a cleaner episode-structure swap

### Rejected now: `evt_episode_count_30s`
This remains explicitly rejected because both the literature lane and earlier repo contact treat it as the coarsest and weakest option.

### Rejected now: reopening the full seven-feature event block or broad feature search
Reason:
- the current evidence state does not justify a wider search
- the user constraint is to avoid broad feature explosion
- the current branch is already localized enough to test one narrower replacement hypothesis

### Rejected now: another scaffold rewrite, model-family pivot, channel pivot, dataset switch, privacy branch, or LLM/RL branch
Reason:
- pass44 already resolved the main scaffold mismatch
- pass46 is still an unresolved repaired-surface miss, not a reason to leave the bounded benchmark loop

## 4) Exactly one chosen next experiment outside the failed lane
Chosen experiment: run one frozen-`pass45` repaired-`A3-only` event-trio swap that drops only `evt_interburst_gap_median_s` and adds only `evt_phasic_like_episode_fraction`.

Exact definition:
1. Reuse the frozen `pass45` repaired `A3-only` no-shape table and LOSO contract.
2. Keep the subject set, selected rows, threshold, channel, model family, base exclusions, and compact shape-drop exclusions fixed.
3. Keep `evt_active_fraction` fixed.
4. Keep `evt_burst_duration_median_s` fixed.
5. Remove only `evt_interburst_gap_median_s`.
6. Add only `evt_phasic_like_episode_fraction`.
7. Compare directly against the unchanged `pass45` anchor, not against train loss or headline counts alone.

Why this is the one chosen experiment:
- it is outside the exact failed `evt_bursts_per_episode_mean` add-back lane
- it keeps the event block width fixed at three features instead of broadening to four or seven
- it directly tests whether the weakest retained trio member (`evt_interburst_gap_median_s`) is the wrong A3-side organization descriptor for the unresolved `brux2` miss
- it preserves the safer backbone terms that repeatedly survived repo contact: `evt_active_fraction` and `evt_burst_duration_median_s`
- it uses the one surviving distinct event-organization idea that still has some positive repo contact without collapsing back into crude count/density proxies

Success criterion:
- `brux2` rises materially above the `pass45` value (`0.178`), ideally enough to close more of the gap to the highest control
- `brux1` stays near the `pass45` rescue and does not fall back below the control surface
- no control crosses threshold
- the paired repaired-`A3-only` best-bruxism-minus-highest-control margin improves beyond `+0.295`

Failure criterion:
- `brux2` stays nearly flat or improves only cosmetically while the highest control rises
- `brux1` materially regresses
- the paired repaired-`A3-only` margin stays flat or worsens again

## 5) One exact measurement/reporting carry-forward to keep
Carry forward exactly this reporting rule: every new matched run must include a paired subject-surface audit against the frozen anchor with copied-through subject-level exact CI blocks and subject-level Brier summaries.

Why keep exactly this:
- `pass45` and `pass46` proved that headline counts alone cannot distinguish meaningful repaired-surface changes from negative side-variants
- the paired margin, per-subject score deltas, prediction flips, exact CI block, and subject-level Brier are the smallest honest reporting surface that still exposes the real tiny-`N` decision

## 6) Exact files likely to edit next
Most likely experiment files:
1. `projects/bruxism-cap/src/run_pass47_repaired_a3_event_trio_swap_phasic_fraction.py`
2. `projects/bruxism-cap/reports/loso-cv-pass47-emg-a3-pct10-90-record-relative-eventsubset-no-shape-phasic-swap.json`
3. `projects/bruxism-cap/reports/pass47-repaired-a3-event-trio-swap-phasic-fraction.json`
4. `projects/bruxism-cap/reports/pass47-repaired-a3-event-trio-swap-phasic-fraction.md`
5. `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.json`
6. `projects/bruxism-cap/reports/pass47-vs-pass45-paired-subject-surface-audit.md`

Most likely reference files to reuse while implementing:
7. `projects/bruxism-cap/src/run_pass45_repaired_a3_shape_block_ablation.py`
8. `projects/bruxism-cap/src/run_pass46_repaired_cross_family_evt_bursts_per_episode_addback.py`
9. `projects/bruxism-cap/src/run_pass42_same_table_event_subset_ablation.py`
10. `projects/bruxism-cap/src/compare_subject_score_surfaces.py`

## Bottom line
After the negative `pass46` verdict, the repo should not keep stacking one-feature density/count add-backs. The surviving bounded move is one fixed-width event-trio swap on the frozen `pass45` repaired-`A3-only` surface: keep `evt_active_fraction` and `evt_burst_duration_median_s`, replace `evt_interburst_gap_median_s` with `evt_phasic_like_episode_fraction`, and judge it with the same paired subject-surface audit contract that exposed `pass46` as a negative side variant.