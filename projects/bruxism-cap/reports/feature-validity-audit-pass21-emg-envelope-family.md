# Pass 21 — EMG envelope-family audit on the retained pass19 working point

Date: 2026-05-04
Status: bounded EMG-first validity audit completed; the retained amplitude / envelope family does change the score surface, but it still does not create a clean `brux1`-over-control separation on the current matched scaffold

## Why this audit exists

Pass20 showed that naive raw-`mean` removal is the wrong next move: it leaves `n3` and `n5` essentially unchanged while collapsing `brux1`.

This pass makes exactly one bounded increment:
- keep the stronger pass19 matched `EMG1-EMG2` `A3-only` scaffold fixed
- keep the same selection-aware exclusions fixed (`^bp_`, `^rel_bp_`, `^ratio_`)
- keep the same model family fixed (`logreg`)
- audit the retained amplitude / envelope family directly instead of doing another deletion-only rerun

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_emg_envelope_family.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass21-emg-envelope-family.json`
- Feature CSV: `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`
- Context report: `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`

## Reproduced score ordering
- `n3` (`control`): mean LOSO score `0.280`
- `n5` (`control`): mean LOSO score `0.222`
- `brux1` (`bruxism`): mean LOSO score `0.151`
- `n11` (`control`): mean LOSO score `0.147`
- `brux2` (`bruxism`): mean LOSO score `0.088`

This keeps the same pass19 bottleneck in view: `n3` and `n5` still outrank `brux1`, and subject-level sensitivity remains `0.000`.

## Focused per-subject feature summaries

### `n3` (control)
- mean LOSO score: `0.280`
- focused feature summaries:
- `sample_entropy`: raw mean `1.857558`, raw p95 `2.282722`, mean z-score `+0.662`, mean contribution `+0.213`
- `rectified_mean`: raw mean `0.000002`, raw p95 `0.000006`, mean z-score `-0.556`, mean contribution `-0.117`
- `rectified_std`: raw mean `0.000003`, raw p95 `0.000011`, mean z-score `-0.540`, mean contribution `-0.268`
- `envelope_mean`: raw mean `0.000002`, raw p95 `0.000006`, mean z-score `-0.556`, mean contribution `-0.117`
- `envelope_std`: raw mean `0.000002`, raw p95 `0.000007`, mean z-score `-0.536`, mean contribution `-0.277`
- `envelope_cv`: raw mean `0.383916`, raw p95 `1.268195`, mean z-score `-0.736`, mean contribution `+0.085`
- `burst_fraction`: raw mean `0.137626`, raw p95 `0.163141`, mean z-score `+0.953`, mean contribution `+0.399`
- `burst_rate_hz`: raw mean `34.616667`, raw p95 `42.646667`, mean z-score `+1.163`, mean contribution `-1.037`
- `p95_abs`: raw mean `0.000008`, raw p95 `0.000027`, mean z-score `-0.399`, mean contribution `-0.053`

### `n5` (control)
- mean LOSO score: `0.222`
- focused feature summaries:
- `sample_entropy`: raw mean `1.583710`, raw p95 `2.210118`, mean z-score `+0.225`, mean contribution `+0.098`
- `rectified_mean`: raw mean `0.000003`, raw p95 `0.000006`, mean z-score `-0.357`, mean contribution `-0.065`
- `rectified_std`: raw mean `0.000005`, raw p95 `0.000014`, mean z-score `-0.419`, mean contribution `-0.186`
- `envelope_mean`: raw mean `0.000003`, raw p95 `0.000006`, mean z-score `-0.356`, mean contribution `-0.066`
- `envelope_std`: raw mean `0.000003`, raw p95 `0.000009`, mean z-score `-0.436`, mean contribution `-0.194`
- `envelope_cv`: raw mean `0.669091`, raw p95 `1.577188`, mean z-score `-0.334`, mean contribution `+0.144`
- `burst_fraction`: raw mean `0.107287`, raw p95 `0.161816`, mean z-score `+0.091`, mean contribution `+0.014`
- `burst_rate_hz`: raw mean `26.659524`, raw p95 `43.033333`, mean z-score `+0.356`, mean contribution `-0.409`
- `p95_abs`: raw mean `0.000010`, raw p95 `0.000023`, mean z-score `-0.287`, mean contribution `+0.004`

### `brux1` (bruxism)
- mean LOSO score: `0.151`
- focused feature summaries:
- `sample_entropy`: raw mean `0.700437`, raw p95 `2.122766`, mean z-score `-1.392`, mean contribution `-0.037`
- `rectified_mean`: raw mean `0.000013`, raw p95 `0.000024`, mean z-score `+4.454`, mean contribution `-0.750`
- `rectified_std`: raw mean `0.000040`, raw p95 `0.000064`, mean z-score `+7.206`, mean contribution `-0.217`
- `envelope_mean`: raw mean `0.000013`, raw p95 `0.000024`, mean z-score `+4.454`, mean contribution `-0.748`
- `envelope_std`: raw mean `0.000030`, raw p95 `0.000050`, mean z-score `+7.485`, mean contribution `+0.072`
- `envelope_cv`: raw mean `1.892069`, raw p95 `3.117991`, mean z-score `+1.882`, mean contribution `+0.121`
- `burst_fraction`: raw mean `0.062119`, raw p95 `0.148841`, mean z-score `-1.370`, mean contribution `-0.059`
- `burst_rate_hz`: raw mean `8.483333`, raw p95 `34.173333`, mean z-score `-1.629`, mean contribution `+0.679`
- `p95_abs`: raw mean `0.000036`, raw p95 `0.000089`, mean z-score `+2.638`, mean contribution `-0.291`

### `n11` (control)
- mean LOSO score: `0.147`
- focused feature summaries:
- `sample_entropy`: raw mean `1.199039`, raw p95 `2.176256`, mean z-score `-0.382`, mean contribution `-0.087`
- `rectified_mean`: raw mean `0.000005`, raw p95 `0.000008`, mean z-score `-0.012`, mean contribution `-0.003`
- `rectified_std`: raw mean `0.000008`, raw p95 `0.000013`, mean z-score `-0.217`, mean contribution `-0.095`
- `envelope_mean`: raw mean `0.000005`, raw p95 `0.000008`, mean z-score `-0.013`, mean contribution `-0.003`
- `envelope_std`: raw mean `0.000005`, raw p95 `0.000010`, mean z-score `-0.229`, mean contribution `-0.114`
- `envelope_cv`: raw mean `1.117459`, raw p95 `2.690100`, mean z-score `+0.279`, mean contribution `+0.057`
- `burst_fraction`: raw mean `0.093029`, raw p95 `0.137129`, mean z-score `-0.290`, mean contribution `-0.112`
- `burst_rate_hz`: raw mean `21.604762`, raw p95 `36.471667`, mean z-score `-0.100`, mean contribution `+0.104`
- `p95_abs`: raw mean `0.000017`, raw p95 `0.000028`, mean z-score `+0.098`, mean contribution `+0.016`

### `brux2` (bruxism)
- mean LOSO score: `0.088`
- focused feature summaries:
- `sample_entropy`: raw mean `1.852369`, raw p95 `2.245432`, mean z-score `+0.648`, mean contribution `+0.102`
- `rectified_mean`: raw mean `0.000002`, raw p95 `0.000004`, mean z-score `-0.628`, mean contribution `+0.009`
- `rectified_std`: raw mean `0.000003`, raw p95 `0.000008`, mean z-score `-0.579`, mean contribution `-0.162`
- `envelope_mean`: raw mean `0.000002`, raw p95 `0.000004`, mean z-score `-0.628`, mean contribution `+0.009`
- `envelope_std`: raw mean `0.000001`, raw p95 `0.000006`, mean z-score `-0.557`, mean contribution `-0.173`
- `envelope_cv`: raw mean `0.530336`, raw p95 `1.468421`, mean z-score `-0.530`, mean contribution `+0.041`
- `burst_fraction`: raw mean `0.119903`, raw p95 `0.156582`, mean z-score `+0.440`, mean contribution `-0.015`
- `burst_rate_hz`: raw mean `22.419048`, raw p95 `31.846667`, mean z-score `-0.029`, mean contribution `+0.020`
- `p95_abs`: raw mean `0.000006`, raw p95 `0.000016`, mean z-score `-0.548`, mean contribution `-0.013`

## Pairwise focused deltas versus `brux1`

### `n3` minus `brux1` (score gap `+0.129`)
- focused features pushing toward `n3`:
  - `rectified_mean` contribution delta `+0.634` | z-mean delta `-5.010` | raw-mean delta `-0.000011`
  - `envelope_mean` contribution delta `+0.632` | z-mean delta `-5.010` | raw-mean delta `-0.000011`
  - `burst_fraction` contribution delta `+0.457` | z-mean delta `+2.323` | raw-mean delta `+0.075507`
  - `sample_entropy` contribution delta `+0.250` | z-mean delta `+2.054` | raw-mean delta `+1.157121`
  - `p95_abs` contribution delta `+0.238` | z-mean delta `-3.037` | raw-mean delta `-0.000028`
- focused features pushing back toward `brux1`:
  - `burst_rate_hz` contribution delta `-1.716` | z-mean delta `+2.792` | raw-mean delta `+26.133333`
  - `envelope_std` contribution delta `-0.349` | z-mean delta `-8.021` | raw-mean delta `-0.000028`
  - `rectified_std` contribution delta `-0.050` | z-mean delta `-7.746` | raw-mean delta `-0.000036`
  - `envelope_cv` contribution delta `-0.036` | z-mean delta `-2.618` | raw-mean delta `-1.508153`

### `n5` minus `brux1` (score gap `+0.070`)
- focused features pushing toward `n5`:
  - `rectified_mean` contribution delta `+0.685` | z-mean delta `-4.811` | raw-mean delta `-0.000010`
  - `envelope_mean` contribution delta `+0.683` | z-mean delta `-4.810` | raw-mean delta `-0.000010`
  - `p95_abs` contribution delta `+0.296` | z-mean delta `-2.925` | raw-mean delta `-0.000026`
  - `sample_entropy` contribution delta `+0.135` | z-mean delta `+1.616` | raw-mean delta `+0.883273`
  - `burst_fraction` contribution delta `+0.072` | z-mean delta `+1.462` | raw-mean delta `+0.045168`
- focused features pushing back toward `brux1`:
  - `burst_rate_hz` contribution delta `-1.088` | z-mean delta `+1.985` | raw-mean delta `+18.176190`
  - `envelope_std` contribution delta `-0.266` | z-mean delta `-7.920` | raw-mean delta `-0.000027`

### `brux2` minus `brux1` (score gap `-0.064`)
- focused features pushing toward `brux2`:
  - `rectified_mean` contribution delta `+0.759` | z-mean delta `-5.082` | raw-mean delta `-0.000011`
  - `envelope_mean` contribution delta `+0.757` | z-mean delta `-5.082` | raw-mean delta `-0.000011`
  - `p95_abs` contribution delta `+0.278` | z-mean delta `-3.186` | raw-mean delta `-0.000030`
  - `sample_entropy` contribution delta `+0.140` | z-mean delta `+2.039` | raw-mean delta `+1.151932`
  - `rectified_std` contribution delta `+0.056` | z-mean delta `-7.785` | raw-mean delta `-0.000037`
- focused features pushing back toward `brux1`:
  - `burst_rate_hz` contribution delta `-0.659` | z-mean delta `+1.599` | raw-mean delta `+13.935714`
  - `envelope_std` contribution delta `-0.245` | z-mean delta `-8.042` | raw-mean delta `-0.000028`
  - `envelope_cv` contribution delta `-0.080` | z-mean delta `-2.412` | raw-mean delta `-1.361732`

### `n11` minus `brux1` (score gap `-0.005`)
- focused features pushing toward `n11`:
  - `rectified_mean` contribution delta `+0.748` | z-mean delta `-4.467` | raw-mean delta `-0.000008`
  - `envelope_mean` contribution delta `+0.746` | z-mean delta `-4.466` | raw-mean delta `-0.000008`
  - `p95_abs` contribution delta `+0.308` | z-mean delta `-2.540` | raw-mean delta `-0.000019`
  - `rectified_std` contribution delta `+0.123` | z-mean delta `-7.423` | raw-mean delta `-0.000031`
- focused features pushing back toward `brux1`:
  - `burst_rate_hz` contribution delta `-0.575` | z-mean delta `+1.528` | raw-mean delta `+13.121429`
  - `envelope_std` contribution delta `-0.185` | z-mean delta `-7.714` | raw-mean delta `-0.000024`
  - `envelope_cv` contribution delta `-0.063` | z-mean delta `-1.603` | raw-mean delta `-0.774610`
  - `burst_fraction` contribution delta `-0.053` | z-mean delta `+1.080` | raw-mean delta `+0.030911`
  - `sample_entropy` contribution delta `-0.050` | z-mean delta `+1.009` | raw-mean delta `+0.498602`

## Interpretation

1. The retained EMG-oriented family is not useless: several envelope / burst features move materially across subjects and do reshape contributions.
2. But the family is not consistently bruxism-aligned on this tiny matched subset. Some retained features still favor controls (`n3` and/or `n5`) more than `brux1`, while others help `brux1` without being large enough to rescue the final ranking.
3. This supports keeping pass19 as the working point but treating the remaining problem as feature-behavior auditing, not threshold tuning and not more blind single-feature deletion.
4. This is another validity note, not a new honest baseline.

## Best next bounded step

Keep the pass19 scaffold fixed again and do one matched comparison next:
- compare the current pass19 selection-aware EMG recipe against the honest pass12 `C4-P4 A1-only` anchor in one shared subject-score table, or
- if staying within EMG only, test one normalization-aware extraction change that preserves the envelope family (for example robust per-window centering / scaling recorded in the feature pipeline) rather than dropping more retained features.

The safer next experiment is the first one if the goal is benchmark clarity; the safer EMG-only experiment is the second one if the goal is still to explain why `brux1` stays below `n3` and `n5`.
