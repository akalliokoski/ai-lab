# Pass 27 — strict shared-time-position feasibility audit for `EMG1-EMG2` exclusive `A1-only`

Date: 2026-05-05
Status: bounded EMG-first extraction-validity audit completed; rebuilding the pass25/pass26-style strict shared-time-position scaffold on `EMG1-EMG2` exclusive `SLEEP-S2 + MCAP-A1-only` is technically reproducible but collapses to only `2` windows per subject, so I did **not** trust a new LOSO rerun on that surface

## Why this pass exists

Pass26 preserved the EMG-first framing and pointed to one clean follow-up:
- keep the stricter time-position discipline from pass25/pass26
- rebuild it on the stronger `A1-only` overlap family for `EMG1-EMG2`
- check whether the strict `A3-only` scaffold itself was the real problem

This pass makes exactly one primary increment:
- keep the same verified `5`-subject subset: `brux1`, `brux2`, `n3`, `n5`, `n11`
- keep `EMG1-EMG2` as the primary channel
- switch the overlap family to exclusive `SLEEP-S2 + MCAP-A1-only`
- keep the same simple shared-absolute-time-position matching rule from `select_time_position_matched_windows.py`
- stop at extraction-validity audit if the resulting scaffold becomes too small to support a meaningful rerun

## Artifacts
- Full uncapped feature table: `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_full_envelope.csv`
- Strict shared-interval subset: `projects/bruxism-cap/data/window_features_pass27_emg_s2_mcap_a1_only_timepos2_envelope.csv`
- Matching summary JSON: `projects/bruxism-cap/reports/time-position-match-pass27-emg-a1.json`
- Selection script reused unchanged: `projects/bruxism-cap/src/select_time_position_matched_windows.py`
- Matched but non-time-position baseline for comparison: `projects/bruxism-cap/reports/pass13-emg-vs-c4-a1-only-matched14.md`

## Command path verified

```bash
source /home/hermes/work/ai-lab/.venv/bin/activate
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/prepare_windows.py --help
python /home/hermes/work/ai-lab/projects/bruxism-cap/src/select_time_position_matched_windows.py --help
```

Then I rebuilt the uncapped `EMG1-EMG2` exclusive `A1-only` pool for the verified `5`-subject subset and ran the same strict shared-time-position selector used in pass25/pass26.

## Extraction summary

### Full exclusive `A1-only` pool before strict time matching
- `brux1`: `27` windows
- `brux2`: `29`
- `n3`: `29`
- `n5`: `134`
- `n11`: `14`
- total rows: `233`

This confirms that the overlap family itself is not missing locally. The bounded problem appears only after the stricter time-position rule is enforced.

### Strict shared absolute interval across all five subjects
- shared `start_s` interval: `7650.0` to `12650.0`

Candidate rows that survive inside that interval:
- `brux1`: `16 / 27`
- `brux2`: `3 / 29`
- `n3`: `2 / 29`
- `n5`: `26 / 134`
- `n11`: `2 / 14`

So the largest valid strict shared-interval cap is only `2` windows per subject.

## What the selected strict scaffold looks like

The resulting strict subset contains only `10` rows total:
- `brux1`: starts at `8150.0`, `12650.0`
- `brux2`: `7650.0`, `12390.0`
- `n3`: `11730.0`, `12300.0`
- `n5`: `7890.0`, `12540.0`
- `n11`: `10530.0`, `11070.0`

Selected mean `start_s` values still differ somewhat by subject:
- `brux1`: `10400.0`
- `brux2`: `10020.0`
- `n3`: `12015.0`
- `n5`: `10215.0`
- `n11`: `10800.0`

So even after forcing the common interval, the remaining `A1-only` support is both tiny and still not perfectly aligned in time-position.

## Decision: no new LOSO rerun on this strict scaffold

I intentionally did **not** launch a new random/LOSO training pass on the `timepos2` subset.

Reason:
1. the strict scaffold preserves only `2` windows per subject (`10` total rows)
2. that is materially smaller than pass25/pass26 (`10` windows per subject) and far smaller than the earlier matched `A1-only` benchmark (`14` windows per subject)
3. any new score on this surface would be dominated by extraction sparsity rather than by a useful channel/family lesson

This is therefore a preserved negative extraction-validity result, not a failed execution.

## Interpretation

1. Pass26 was right to keep the EMG-first frame: the next issue was worth checking on `A1-only`, not by reverting to `C4-P4`.
2. But the strict pass25/pass26-style global shared-time-interval rule is **too brittle for `A1-only`** on the current verified subset.
3. The earlier pass12/pass13 matched `A1-only` results depended on count matching without this stricter global interval. Under the stricter timing discipline, `A1-only` coverage collapses before modeling even begins.
4. So the repo should **not** read pass12's stronger `A1-only` result as proof that strict time-position-matched `A1-only` is the immediate next honest benchmark. On the current subset, the first blocker is extraction feasibility.
5. This also means pass25/pass26 did more than expose an `A3-only` issue; they exposed a limitation of the current simple shared-interval matching rule itself.

## Best next bounded step

Keep the EMG-first framing and preserve this pass27 result as a first-class negative validity note.

The cleanest next experiment is:
- keep `EMG1-EMG2` and exclusive `A1-only`
- replace the current all-subject global shared-interval rule with a **softer timing-control scaffold** that still audits time position but preserves more than `2` windows per subject
- the smallest repo-grounded way to do that is to extend `projects/bruxism-cap/src/select_time_position_matched_windows.py` to support rank-based or percentile-band matching instead of only one hard shared interval

That would preserve the timing question without collapsing the benchmark into a `10`-row artifact.
