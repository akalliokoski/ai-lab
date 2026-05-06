# Pass41 event-feature follow-up subset selection

Date: 2026-05-05
Status: completed same-table feature-subset audit on the existing pass41 event table; no retraining run executed in this task.

## Scope lock
- Same repaired five-subject CAP scaffold only.
- Same pass41 event table only.
- No new features, no channel pivot, no dataset slice change, no benchmark rewrite.
- Ranking is based on pass41 mean contribution audit values already preserved in the pass41 artifacts.

## Exact ranking of the 7 evt_* features
Ranking rule: prefer features that keep or lift brux1 while minimizing control-minus-brux1 reopening, with n11 treated as the primary control-risk tie-breaker because n11 is the actual pass41 failure.

1. `evt_active_fraction` | brux1 +0.066 | n11-brux1 -0.420 | n5-brux1 -0.567 | n3-brux1 +0.312 | control-damage-sum 0.312
   - Best keep feature: positive on brux1 (+0.066) and the only feature that is net-protective against n11 (-0.420) while also strongly helping against n5 (-0.567).
2. `evt_burst_duration_median_s` | brux1 +0.153 | n11-brux1 +0.100 | n5-brux1 -0.945 | n3-brux1 -0.369 | control-damage-sum 0.100
   - Strongest target-useful term after active fraction: positive on brux1 (+0.153) and very protective against n5 (-0.945), with only a modest n11 reopening cost (+0.100).
3. `evt_bursts_per_episode_mean` | brux1 -0.015 | n11-brux1 +0.040 | n5-brux1 +0.017 | n3-brux1 +0.019 | control-damage-sum 0.076
   - Best low-damage third filler: tiny brux1 drag (-0.015) but the smallest positive control damage footprint among the remaining candidates (n11 +0.040, n5 +0.017, n3 +0.019).
4. `evt_burst_count_30s` | brux1 -0.030 | n11-brux1 +0.045 | n5-brux1 +0.026 | n3-brux1 +0.047 | control-damage-sum 0.118
   - Similar to bursts-per-episode but slightly worse everywhere: brux1 drag (-0.030) and slightly larger control reopening (n11 +0.045, n5 +0.026, n3 +0.047).
5. `evt_phasic_like_episode_fraction` | brux1 +0.013 | n11-brux1 +0.144 | n5-brux1 -0.046 | n3-brux1 -0.252 | control-damage-sum 0.144
   - Mixed signal: small brux1 help (+0.013) and helpful against n5 (-0.046), but too much n11 reopening (+0.144) to include ahead of the safer count fillers.
6. `evt_interburst_gap_median_s` | brux1 -0.064 | n11-brux1 +0.053 | n5-brux1 +0.093 | n3-brux1 +0.197 | control-damage-sum 0.343
   - Net harmful: brux1 drag (-0.064) plus positive reopening on all three controls, especially n3 (+0.197).
7. `evt_episode_count_30s` | brux1 -0.195 | n11-brux1 +0.185 | n5-brux1 +0.141 | n3-brux1 +0.146 | control-damage-sum 0.471
   - Worst feature to keep: largest brux1 drag (-0.195) and the largest combined control damage, especially n11 (+0.185) and n5 (+0.141).

## Recommended 3-feature subset
- `evt_bursts_per_episode_mean`, `evt_active_fraction`, `evt_burst_duration_median_s`
- Net event contribution sum on brux1: +0.204
- Control-minus-brux1 gaps: n11 -0.280, n5 -1.495, n3 -0.038
- Combined positive control damage: 0.000
- Why this subset: active_fraction and burst_duration_median_s carry almost all of the target lift; bursts_per_episode_mean is the safest third term to leave in because it adds only tiny control reopening and preserves a positive brux1 net. This combination is the strongest zero-positive-damage 3-feature option on the pass41 same-table heuristic.

## Explicitly rejected 3-feature subset
- `evt_burst_count_30s`, `evt_episode_count_30s`, `evt_interburst_gap_median_s`
- Net event contribution sum on brux1: -0.289
- Control-minus-brux1 gaps: n11 +0.283, n5 +0.259, n3 +0.389
- Combined positive control damage: 0.932
- Why rejected: this is the worst count-style trio. All three features drag brux1 while reopening every control, and it produces the largest combined control damage of any 3-feature subset on the audit table.

## Important near-miss subset not chosen
- `evt_active_fraction`, `evt_burst_duration_median_s`, `evt_phasic_like_episode_fraction`
- Net event contribution sum on brux1: +0.232
- Control-minus-brux1 gaps: n11 -0.176, n5 -1.558, n3 -0.309
- Why not chosen: it is appealing because all three terms are positive on brux1, but phasic_like_episode_fraction is exactly the kind of term that reopens n11 more than the safer count filler does. The recommended subset sacrifices only 0.028 of brux1 event contribution to gain materially safer n11 behavior.

## Exact repo files/artifacts to use for the follow-up run
- input_table: `projects/bruxism-cap/data/window_features_pass41_emg_s2_mcap_a1_only_pct10_90_timepos10_record_relative_shape_eventblock.csv`
- selection_reference: `projects/bruxism-cap/src/run_pass41_event_conditioned_feature_block_audit.py`
- feature_semantics: `projects/bruxism-cap/src/features.py`
- training_entrypoint: `projects/bruxism-cap/src/train_baseline.py`
- current_loso_report_anchor: `projects/bruxism-cap/reports/loso-cv-pass41-emg-a1-pct10-90-record-relative-shape-eventblock.json`
- current_audit_anchor_md: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.md`
- current_audit_anchor_json: `projects/bruxism-cap/reports/pass41-event-conditioned-feature-block-audit.json`

## Follow-up run instruction
- Start from the pass41 CSV, keep the train-time exclusions unchanged, and run one LOSO logreg ablation that keeps pass36 plus only the recommended three event columns.
- Use `run_pass41_event_conditioned_feature_block_audit.py` as the naming/feature reference and `train_baseline.py` as the execution entrypoint for the same-table subset run.

## Artifacts
- JSON summary: `projects/bruxism-cap/reports/pass41-event-feature-subset-followup-selection.json`
- Markdown summary: `projects/bruxism-cap/reports/pass41-event-feature-subset-followup-selection.md`
