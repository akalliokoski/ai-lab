# Pass 11 — rule-survival audit across stage-aware overlap filters

Date: 2026-05-04
Status: bounded validity audit; no model change, no new rerun

## Why this audit exists

Pass10 showed that exclusive `S2 + A3-only` windows were cleaner but still not transferable.
The next bounded validity question was whether the successive overlap rules are shrinking the usable window pools symmetrically across subjects and labels, or whether they are silently changing event availability in a way that makes run-to-run comparisons harder to trust.

## Audited rules

- `pass4_s2` — in-range `SLEEP-S2` windows only
- `pass7_s2_mcap_any` — `SLEEP-S2` windows overlapping any of `MCAP-A1`, `MCAP-A2`, or `MCAP-A3`
- `pass9_s2_mcap_a3` — `SLEEP-S2` windows overlapping `MCAP-A3`
- `pass10_s2_mcap_a3_only` — `SLEEP-S2` windows overlapping `MCAP-A3` while excluding simultaneous `MCAP-A1` or `MCAP-A2`

## Subject-level survival summary

| subject | label | eligible pass4 S2 | eligible pass7 any-MCAP | pass7 vs pass4 | eligible pass9 A3 | pass9 vs pass4 | eligible pass10 A3-only | pass10 vs pass4 | pass10 kept rows |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| brux1 | bruxism | 144 | 77 | 53.5% | 34 | 23.6% | 31 | 21.5% | 20 |
| brux2 | bruxism | 298 | 181 | 60.7% | 127 | 42.6% | 111 | 37.2% | 20 |
| n11 | control | 266 | 96 | 36.1% | 49 | 18.4% | 42 | 15.8% | 20 |
| n3 | control | 347 | 166 | 47.8% | 81 | 23.3% | 76 | 21.9% | 20 |
| n5 | control | 413 | 194 | 47.0% | 47 | 11.4% | 38 | 9.2% | 20 |

## Label-level survival summary

| label | eligible pass4 S2 | eligible pass7 any-MCAP | pass7 vs pass4 | eligible pass9 A3 | pass9 vs pass4 | eligible pass10 A3-only | pass10 vs pass4 | pass10 kept rows |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bruxism | 442 | 258 | 58.4% | 161 | 36.4% | 142 | 32.1% | 40 |
| control | 1026 | 456 | 44.4% | 177 | 17.3% | 156 | 15.2% | 60 |

## Evidence-backed takeaways

1. The successive overlap filters shrink the available window pools **very unevenly** across subjects.
2. `brux2` keeps a much larger exclusive-`A3` pool than the other subjects, while `n5` drops sharply once the rule moves from `any MCAP` to `A3` and then `A3-only`.
3. The bruxism label pool stays relatively rich under `A3`-based rules, but the control pool thins much faster.
4. That means pass7/pass9/pass10 are not only changing event semantics; they are also changing the effective per-subject and per-label sampling surface.
5. This strengthens the current interpretation of pass9/pass10 as useful negative results: lower random-window optimism did not translate into better transfer, and the stricter rules also made the candidate control-window pool less balanced.

## Best next bounded step

Stay on validity work. The cleanest next increment is to compare one alternate exclusive family such as `S2 + A1-only` against `S2 + A3-only` on the same verified subject set, while preserving this survival audit so later comparisons can separate physiological signal from changing event availability.
