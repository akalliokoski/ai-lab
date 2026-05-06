# CAP control-side download verification — local `n1`/`n2` check for bounded control expansion

Date: 2026-05-06
Status: completed local verification of the two next admissible CAP healthy controls.

## Question
After the bounded control-side expansion audit admitted `n1` and `n2` in principle, are the canonical `n1`/`n2` EDF and sidecar files now present locally and compatible with the repo's current dual-channel + stage/event extraction contract?

## Short answer
Yes.

`n1.edf`, `n1.txt`, `n2.edf`, and `n2.txt` are present under `projects/bruxism-cap/data/raw/capslpdb/` and their local byte counts match the canonical PhysioNet objects exactly.

Local EDF inspection confirms that both subjects expose `EMG1-EMG2` and `C4-P4`.

Local sidecar parsing under the current extraction contract also confirms usable in-range `SLEEP-S2`, exclusive `MCAP-A1` overlap, and exclusive `MCAP-A3` overlap rows for both subjects.

## Verification method
1. Checked the repo raw-data layout for the four target files.
2. Compared local byte counts against canonical PhysioNet `Content-Length` metadata for each object.
3. Opened each EDF locally with MNE and verified required channel names and EDF duration.
4. Parsed each RemLogic `.txt` locally with the repo's current `prepare_windows.py` parser.
5. Recomputed the in-range row counts under the current extraction contract:
   - `SLEEP-S2`: event is `SLEEP-S2`, duration at least `30s`, start non-negative, and `start_s + 30 <= EDF duration`
   - `A1-only`: qualifying `SLEEP-S2` row overlaps `MCAP-A1` and does not overlap `MCAP-A2` or `MCAP-A3`
   - `A3-only`: qualifying `SLEEP-S2` row overlaps `MCAP-A3` and does not overlap `MCAP-A1` or `MCAP-A2`

## Exact verification table
| subject | edf_local_bytes | edf_remote_bytes | edf_match | txt_local_bytes | txt_remote_bytes | txt_match | duration_min | EMG1-EMG2 | C4-P4 | S2 in range | A1-only in range | A3-only in range |
|---|---:|---:|---|---:|---:|---|---:|---|---|---:|---:|---:|
| n1 | 496456432 | 496456432 | yes | 84246 | 84246 | yes | 577.0 | yes | yes | 508 | 139 | 56 |
| n2 | 372825496 | 372825496 | yes | 45163 | 45163 | yes | 735.0 | yes | yes | 367 | 94 | 49 |

## Local channel notes
### n1
- Required channels present: `EMG1-EMG2`, `C4-P4`
- EDF duration: `34620` seconds (`577.0` minutes)
- Additional channel context: `ROC-LOC`, `LOC-ROC`, `F2-F4`, `F4-C4`, `C4-P4`, `P4-O2`, `F1-F3`, `F3-C3`, `C3-P3`, `P3-O1`, `C4-A1`, `EMG1-EMG2`, `ECG1-ECG2`, `TERMISTORE`, `TORACE`, `ADDOME`, `Dx1-DX2`, `SX1-SX2`, `Posizione`, `HR`, `SpO2`

### n2
- Required channels present: `EMG1-EMG2`, `C4-P4`
- EDF duration: `44100` seconds (`735.0` minutes)
- Additional channel context: `Fp2-F4`, `F4-C4`, `C4-P4`, `P4-O2`, `C4-A1`, `ROC-LOC`, `EMG1-EMG2`, `ECG1-ECG2`, `DX1-DX2`, `SX1-SX2`, `SAO2`, `HR`, `PLETH`, `STAT`, `MIC`

## Sidecar notes
Raw sidecar event counts are larger than the extraction-contract counts because the current benchmark does not keep every CAP-event row directly; it filters to in-range `30s` `SLEEP-S2` windows and then applies exclusive overlap rules.

For context, the raw sidecar event totals are:
- `n1`: `SLEEP-S2=508`, `MCAP-A1=363`, `MCAP-A3=80`
- `n2`: `SLEEP-S2=367`, `MCAP-A1=186`, `MCAP-A3=94`

The contract-level counts above match the current manifest proposal exactly, so the admissible-set understanding does not change.

## Manifest consequence
No update is needed to `projects/bruxism-cap/data/subject_manifest.example.csv`.

The current example manifest already records the locally verified admissible-set counts correctly:
- `n1`: `S2=508`, `A1-only=139`, `A3-only=56`
- `n2`: `S2=367`, `A1-only=94`, `A3-only=49`

## Caveats
1. This task verifies local presence and compatibility only; it does not start the bounded control-expanded benchmark rerun.
2. `n10` remains `refresh_needed` and should stay out of stage-aware rebuilds until its EDF is refreshed to the canonical `474168064` bytes.
3. The benchmark remains tiny and positive-capped: the positive class is still only `brux1` and `brux2`.

## Handoff answer
Yes: after this verification step, the repo is ready for the first bounded control-expanded benchmark rerun on the fixed positive set, assuming the next card uses exactly the verified subject contract:
- positives: `brux1`, `brux2`
- verified existing controls: `n3`, `n5`, `n11`
- newly verified additions: `n1`, `n2`
- excluded for now: `n10` and the remaining non-dual-channel `n*` subjects