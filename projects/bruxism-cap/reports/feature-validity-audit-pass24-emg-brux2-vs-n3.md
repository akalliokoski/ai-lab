# Pass 24 — EMG `brux2` collapse versus `n3` control audit on the retained pass19 working point

Date: 2026-05-05
Status: bounded EMG-first validity audit completed; the strongest current EMG recipe still fails mainly because `brux2` collapses while `n3` becomes the dominant control, and the largest surviving gap is now concentrated in control-favoring crossing/irregularity features rather than in a generic threshold problem

## Why this audit exists

Pass23 made the benchmark gap sharper but did not yet explain the main EMG failure surface:
- under the honest `C4-P4 A1-only` anchor, `brux2` is the strongest subject
- under the current pass19 `EMG1-EMG2 A3-only` working point, `brux2` collapses and `n3` becomes the highest-score control

This pass makes exactly one bounded increment:
- keep the stronger pass19 matched `EMG1-EMG2` `A3-only` scaffold fixed
- keep the same selection-aware exclusions fixed (`^bp_`, `^rel_bp_`, `^ratio_`)
- keep the same model family fixed (`logreg`)
- audit the `brux2` versus `n3` score flip directly instead of launching another extraction rewrite

## Artifacts
- Audit script: `projects/bruxism-cap/src/audit_emg_brux2_n3_gap.py`
- Audit JSON: `projects/bruxism-cap/reports/feature-validity-audit-pass24-emg-brux2-vs-n3.json`
- Feature CSV: `projects/bruxism-cap/data/window_features_pass18_emg_s2_mcap_a3_only_matched14_envelope.csv`
- EMG context report: `projects/bruxism-cap/reports/loso-cv-pass19-emg-a3-envelope-selected-matched14.json`
- Anchor report: `projects/bruxism-cap/reports/loso-cv-pass12-s2-mcap-a1-only-matched14.json`

## Reproduced pass19 score ordering
- `n3` (`control`): mean LOSO score `0.280`
- `n5` (`control`): mean LOSO score `0.222`
- `brux1` (`bruxism`): mean LOSO score `0.151`
- `n11` (`control`): mean LOSO score `0.147`
- `brux2` (`bruxism`): mean LOSO score `0.088`

This keeps the same honest failure in view: subject-level sensitivity remains `0.000`, with `n3` and `n5` still above both bruxism subjects.

## Cross-channel benchmark contrast for the same two key subjects
- EMG pass19 `brux2 - n3` mean-score gap: `-0.193` (`0.088 - 0.280`).
- Honest anchor pass12 `brux2 - n3` mean-score gap: `+0.551` (`0.795 - 0.245`).
- So the same subject pair flips by `-0.743` between the current EMG surface and the honest comparison anchor.
- This localizes the remaining EMG problem more tightly than “EMG is just weaker overall”: the decisive regression is one bruxism subject (`brux2`) falling below one control (`n3`).

## Focused subject summaries

### `brux2` (bruxism)
- mean LOSO score: `0.088`
- windows: `14` | start_s mean `4377.9` | median `4515.0` | min `2520.0` | max `7080.0`
- focused feature summaries:
  - `zero_crossing_rate`: raw mean `0.416916`, raw p95 `0.446881`, mean z-score `+2.722`, mean contribution `-2.328`
  - `sample_entropy`: raw mean `1.852369`, raw p95 `2.245432`, mean z-score `+0.648`, mean contribution `+0.102`
  - `burst_fraction`: raw mean `0.119903`, raw p95 `0.156582`, mean z-score `+0.440`, mean contribution `-0.015`
  - `burst_rate_hz`: raw mean `22.419048`, raw p95 `31.846667`, mean z-score `-0.029`, mean contribution `+0.020`
  - `line_length`: raw mean `0.018715`, raw p95 `0.044149`, mean z-score `-0.693`, mean contribution `+0.887`
  - `mean`: raw mean `-0.000000`, raw p95 `0.000000`, mean z-score `-0.366`, mean contribution `-0.111`
  - `rectified_mean`: raw mean `0.000002`, raw p95 `0.000004`, mean z-score `-0.628`, mean contribution `+0.009`
  - `envelope_mean`: raw mean `0.000002`, raw p95 `0.000004`, mean z-score `-0.628`, mean contribution `+0.009`
  - `rectified_std`: raw mean `0.000003`, raw p95 `0.000008`, mean z-score `-0.579`, mean contribution `-0.162`
  - `envelope_std`: raw mean `0.000001`, raw p95 `0.000006`, mean z-score `-0.557`, mean contribution `-0.173`
  - `p95_abs`: raw mean `0.000006`, raw p95 `0.000016`, mean z-score `-0.548`, mean contribution `-0.013`

### `n3` (control)
- mean LOSO score: `0.280`
- windows: `14` | start_s mean `8327.1` | median `7665.0` | min `3210.0` | max `16170.0`
- focused feature summaries:
  - `zero_crossing_rate`: raw mean `0.221992`, raw p95 `0.242242`, mean z-score `-0.173`, mean contribution `-0.264`
  - `sample_entropy`: raw mean `1.857558`, raw p95 `2.282722`, mean z-score `+0.662`, mean contribution `+0.213`
  - `burst_fraction`: raw mean `0.137626`, raw p95 `0.163141`, mean z-score `+0.953`, mean contribution `+0.399`
  - `burst_rate_hz`: raw mean `34.616667`, raw p95 `42.646667`, mean z-score `+1.163`, mean contribution `-1.037`
  - `line_length`: raw mean `0.027194`, raw p95 `0.075275`, mean z-score `-0.350`, mean contribution `+0.621`
  - `mean`: raw mean `0.000000`, raw p95 `0.000000`, mean z-score `-0.358`, mean contribution `-0.166`
  - `rectified_mean`: raw mean `0.000002`, raw p95 `0.000006`, mean z-score `-0.556`, mean contribution `-0.117`
  - `envelope_mean`: raw mean `0.000002`, raw p95 `0.000006`, mean z-score `-0.556`, mean contribution `-0.117`
  - `rectified_std`: raw mean `0.000003`, raw p95 `0.000011`, mean z-score `-0.540`, mean contribution `-0.268`
  - `envelope_std`: raw mean `0.000002`, raw p95 `0.000007`, mean z-score `-0.536`, mean contribution `-0.277`
  - `p95_abs`: raw mean `0.000008`, raw p95 `0.000027`, mean z-score `-0.399`, mean contribution `-0.053`

### `brux1` (bruxism)
- mean LOSO score: `0.151`
- windows: `14` | start_s mean `4067.9` | median `3305.0` | min `2180.0` | max `8180.0`
- focused feature summaries:
  - `zero_crossing_rate`: raw mean `0.079893`, raw p95 `0.225607`, mean z-score `-2.464`, mean contribution `-3.635`
  - `sample_entropy`: raw mean `0.700437`, raw p95 `2.122766`, mean z-score `-1.392`, mean contribution `-0.037`
  - `burst_fraction`: raw mean `0.062119`, raw p95 `0.148841`, mean z-score `-1.370`, mean contribution `-0.059`
  - `burst_rate_hz`: raw mean `8.483333`, raw p95 `34.173333`, mean z-score `-1.629`, mean contribution `+0.679`
  - `line_length`: raw mean `0.025542`, raw p95 `0.043275`, mean z-score `-0.367`, mean contribution `+0.090`
  - `mean`: raw mean `0.000004`, raw p95 `0.000009`, mean z-score `+554.107`, mean contribution `-827.298`
  - `rectified_mean`: raw mean `0.000013`, raw p95 `0.000024`, mean z-score `+4.454`, mean contribution `-0.750`
  - `envelope_mean`: raw mean `0.000013`, raw p95 `0.000024`, mean z-score `+4.454`, mean contribution `-0.748`
  - `rectified_std`: raw mean `0.000040`, raw p95 `0.000064`, mean z-score `+7.206`, mean contribution `-0.217`
  - `envelope_std`: raw mean `0.000030`, raw p95 `0.000050`, mean z-score `+7.485`, mean contribution `+0.072`
  - `p95_abs`: raw mean `0.000036`, raw p95 `0.000089`, mean z-score `+2.638`, mean contribution `-0.291`

## Pairwise focused deltas

### `n3` minus `brux2` (score gap `+0.193`)
- focused features pushing toward `n3`:
  - `zero_crossing_rate` contribution delta `+2.064` | z-mean delta `-2.896` | raw-mean delta `-0.194925`
  - `burst_fraction` contribution delta `+0.414` | z-mean delta `+0.513` | raw-mean delta `+0.017722`
  - `sample_entropy` contribution delta `+0.110` | z-mean delta `+0.015` | raw-mean delta `+0.005189`
- focused features pushing back toward `brux2`:
  - `burst_rate_hz` contribution delta `-1.057` | z-mean delta `+1.193` | raw-mean delta `+12.197619`
  - `line_length` contribution delta `-0.265` | z-mean delta `+0.343` | raw-mean delta `+0.008480`
  - `rectified_mean` contribution delta `-0.126` | z-mean delta `+0.072` | raw-mean delta `+0.000000`
  - `envelope_mean` contribution delta `-0.126` | z-mean delta `+0.072` | raw-mean delta `+0.000000`
  - `rectified_std` contribution delta `-0.106` | z-mean delta `+0.039` | raw-mean delta `+0.000001`

### `n3` minus `brux1` (score gap `+0.129`)
- focused features pushing toward `n3`:
  - `mean` contribution delta `+827.132` | z-mean delta `-554.466` | raw-mean delta `-0.000004`
  - `zero_crossing_rate` contribution delta `+3.370` | z-mean delta `+2.291` | raw-mean delta `+0.142099`
  - `rectified_mean` contribution delta `+0.634` | z-mean delta `-5.010` | raw-mean delta `-0.000011`
  - `envelope_mean` contribution delta `+0.632` | z-mean delta `-5.010` | raw-mean delta `-0.000011`
  - `line_length` contribution delta `+0.531` | z-mean delta `+0.018` | raw-mean delta `+0.001652`
- focused features pushing back toward `brux1`:
  - `burst_rate_hz` contribution delta `-1.716` | z-mean delta `+2.792` | raw-mean delta `+26.133333`
  - `envelope_std` contribution delta `-0.349` | z-mean delta `-8.021` | raw-mean delta `-0.000028`
  - `rectified_std` contribution delta `-0.050` | z-mean delta `-7.746` | raw-mean delta `-0.000036`

### `brux2` minus `brux1` (score gap `-0.064`)
- focused features pushing toward `brux2`:
  - `mean` contribution delta `+827.187` | z-mean delta `-554.474` | raw-mean delta `-0.000004`
  - `zero_crossing_rate` contribution delta `+1.307` | z-mean delta `+5.187` | raw-mean delta `+0.337024`
  - `line_length` contribution delta `+0.796` | z-mean delta `-0.326` | raw-mean delta `-0.006827`
  - `rectified_mean` contribution delta `+0.759` | z-mean delta `-5.082` | raw-mean delta `-0.000011`
  - `envelope_mean` contribution delta `+0.757` | z-mean delta `-5.082` | raw-mean delta `-0.000011`
- focused features pushing back toward `brux1`:
  - `burst_rate_hz` contribution delta `-0.659` | z-mean delta `+1.599` | raw-mean delta `+13.935714`
  - `envelope_std` contribution delta `-0.245` | z-mean delta `-8.042` | raw-mean delta `-0.000028`

## Interpretation

1. The current EMG failure is concentrated, not diffuse: the strongest honest gap from the anchor is the `brux2` versus `n3` reversal, not a uniform regression across all subjects.
2. Within the fixed pass19 feature set, the largest surviving control-favoring signal in `n3` versus `brux2` is `zero_crossing_rate`, with smaller support from `burst_fraction` and `sample_entropy`.
3. `burst_rate_hz` still pushes the other way and favors `brux2`, so the EMG recipe is not devoid of bruxism-aligned signal; it is being outweighed by a small competing control-favoring family.
4. The matched-14 scaffold is count-matched but not time-position-matched: `n3` windows sit materially later in the night than `brux2` on average, so a future extraction audit should treat time-position matching as a real validity question rather than assuming the current cap already equalizes it.
5. This is therefore another negative-but-useful validity result, not a new baseline win.

## Best next bounded step

Keep pass19 as the EMG-first working point and do one compact extraction-validity follow-up next:
- either rebuild the same `EMG1-EMG2 A3-only` scaffold with a simple time-position matching rule across subjects before any new feature change,
- or audit whether the current `zero_crossing_rate` / `sample_entropy` surface is acting as a residual artifact proxy for `n3` versus `brux2` under EMG.

The safer next experiment is the first one because it tests a concrete validity hole without changing model family or broadening feature scope.
