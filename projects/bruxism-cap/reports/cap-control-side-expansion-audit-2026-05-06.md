# CAP control-side expansion audit — bounded `n*` additions for `bruxism-cap`

Date: 2026-05-06
Status: control-side audit completed; this memo checks which healthy `n*` CAP subjects are compatible with the repo's current bounded dual-channel control-expansion contract.

## Question
Which bounded CAP healthy controls can be added honestly to the current `bruxism-cap` branch if the positive class stays fixed at `brux1` and `brux2`?

## Short answer
Admit only `n1` and `n2` as the next control additions under the current contract.

Keep `n3`, `n5`, and `n11` as the already verified local control core.

Treat `n10` as conditional / not currently admissible because the local file is truncated relative to the canonical PhysioNet copy.

Exclude `n4`, `n6`, `n7`, `n8`, `n9`, `n12`, `n13`, `n14`, `n15`, and `n16` from this branch because they do not satisfy the current dual-channel compatibility rule (`EMG1-EMG2` plus `C4-P4`).

## Current expansion contract
This branch is intentionally narrow.

A new control is admissible only if it passes all of these checks:
1. positive class remains fixed at `brux1` and `brux2`
2. the control exposes both `EMG1-EMG2` and `C4-P4`
3. `SLEEP-S2` stage rows are usable and in-range relative to the EDF duration actually available to the repo
4. the sidecar also exposes usable `MCAP-A1` and `MCAP-A3` overlap rows so the current event-conditioned branch can be rebuilt without inventing a new annotation contract
5. the result is reported as a control-side specificity stress test, not as a larger bruxism dataset

## Evidence used
### 1. Remote canonical audit
A lightweight remote PhysioNet audit was run across `n1`-`n16` using EDF header parsing, file-size checks, and RemLogic sidecar parsing.

That audit established:
- both `EMG1-EMG2` and `C4-P4` are present only in `n1`, `n2`, `n3`, `n5`, `n10`, and `n11`
- `n4`, `n8`, and `n16` expose `C4-P4` but not `EMG1-EMG2`
- `n6`, `n7`, `n9`, `n12`, `n13`, `n14`, and `n15` expose neither required channel pair
- all audited controls have in-range `SLEEP-S2` rows except `n16`, which has `2` out-of-range `S2` rows
- `n13` and `n14` use EDF header `n_records=-1`, but their durations are still recoverable from total file size and samples per record

### 2. Local repo cross-check
Local MNE inspection of the currently downloaded control subset confirms:
- `n3`, `n5`, and `n11` are full-length and dual-channel compatible
- local `n10.edf` is only about `63.05` minutes long despite the canonical PhysioNet file indicating about `490` minutes

Exact local size mismatch:
- local `projects/bruxism-cap/data/raw/capslpdb/n10.edf`: `61,030,035` bytes
- canonical remote `n10.edf`: `474,168,064` bytes

So the repo should treat the current local `n10` as truncated until refreshed and re-audited.

## Decision table
| subject | duration_min | EMG1-EMG2 | C4-P4 | S2 in range | A1-only in range | A3-only in range | decision | reason |
|---|---:|---|---|---:|---:|---:|---|---|
| n1 | 577.0 | yes | yes | 508 | 139 | 56 | admit | dual-channel compatible and annotation-compatible; next clean control addition |
| n2 | 735.0 | yes | yes | 367 | 94 | 49 | admit | dual-channel compatible and annotation-compatible; next clean control addition |
| n3 | 551.02 | yes | yes | 347 | 29 | 76 | keep | already verified local control |
| n4 | 595.67 | no | yes | 401 | 81 | 29 | exclude | lacks `EMG1-EMG2` |
| n5 | 524.02 | yes | yes | 413 | 134 | 38 | keep | already verified local control |
| n6 | 527.08 | no | no | 489 | 89 | 76 | exclude | lacks both required channels |
| n7 | 492.33 | no | no | 404 | 101 | 21 | exclude | lacks both required channels |
| n8 | 500.67 | no | yes | 402 | 61 | 101 | exclude | lacks `EMG1-EMG2` |
| n9 | 532.35 | no | no | 472 | 60 | 38 | exclude | lacks both required channels |
| n10 | 490.0 remote / 63.05 local | yes | yes | 261 remote | 15 remote | 58 remote | conditional | canonical record looks admissible, but the current local EDF is truncated and must be refreshed before inclusion |
| n11 | 527.0 | yes | yes | 266 | 14 | 42 | keep | already verified local control |
| n12 | 495.0 | no | no | 423 | 30 | 37 | exclude | lacks both required channels |
| n13 | 490.45 | no | no | 421 | 102 | 40 | exclude | lacks both required channels; `n_records=-1` is not the blocker |
| n14 | 492.52 | no | no | 354 | 47 | 32 | exclude | lacks both required channels; `n_records=-1` is not the blocker |
| n15 | 494.17 | no | no | 504 | 46 | 72 | exclude | lacks both required channels |
| n16 | 513.33 | no | yes | 452 of 454 | 79 | 54 | exclude | lacks `EMG1-EMG2`; the `2` out-of-range `S2` rows are secondary |

## Admissible bounded control set
Under the current repo contract, the bounded control-side branch should be read as:
- fixed positives: `brux1`, `brux2`
- verified current controls: `n3`, `n5`, `n11`
- next admissible additions: `n1`, `n2`
- conditional / refresh-needed candidate: `n10`
- excluded from this dual-channel branch: `n4`, `n6`, `n7`, `n8`, `n9`, `n12`, `n13`, `n14`, `n15`, `n16`

## Why `n10` is not promoted now
`n10` is the only dual-channel candidate whose canonical remote metadata looks acceptable but whose local working copy breaks the repo's extraction contract.

The key issue is not a subtle event mismatch. It is a concrete file mismatch:
- remote canonical header path implies `29400` one-second records (`490.0` minutes)
- current local MNE read shows only `63.05` minutes
- current local file size is far smaller than the canonical remote object

So the right repo status is `refresh_needed`, not `admit` and not permanent `exclude`.

## Exact operational recommendation
1. Keep the positive class fixed at `brux1` and `brux2`.
2. Preserve `n3`, `n5`, and `n11` as the current local control core.
3. Download `n1.edf`, `n1.txt`, `n2.edf`, and `n2.txt` next if the branch needs more controls.
4. Update the example manifest and README language so the bounded control-expansion contract is explicit.
5. Do not include `n10` in any stage-aware rebuild until the local file is refreshed and verified against the canonical size.

## Smallest safe next download step
If the repo wants the next two additions now, fetch:
- `n1.edf`
- `n1.txt`
- `n2.edf`
- `n2.txt`

If the repo wants to re-open `n10`, first replace the local EDF and verify that the refreshed file matches the canonical object size (`474,168,064` bytes) before any new window extraction.

## Bottom line
The bounded CAP control-side expansion is real, but smaller than the full `n*` pool. Under the current dual-channel and annotation-aware contract, `n1` and `n2` are the only clean new additions, `n10` is refresh-needed, and the remaining `n*` controls are outside this branch because they are not dual-channel compatible.