---
title: Bruxism CAP Control-Side Download Verification (2026-05-06)
created: 2026-05-06
updated: 2026-05-06
type: query
tags: [research, dataset, evaluation, workflow, notes]
sources:
  - queries/bruxism-cap-control-side-expansion-audit-2026-05-06.md
  - queries/bruxism-cap-next-data-strategy-2026-05-06.md
---

# Bruxism CAP Control-Side Download Verification

## Question
Are the two next admissible CAP healthy controls, `n1` and `n2`, now locally present in canonical form and actually compatible with the repo's current dual-channel and stage/event extraction contract? [[bruxism-cap]]

## Answer
Yes.

The repo already contains `n1.edf`, `n1.txt`, `n2.edf`, and `n2.txt` under `projects/bruxism-cap/data/raw/capslpdb/`, and each local object matches the canonical PhysioNet byte count exactly.

Local EDF inspection confirms that both subjects expose the required channel pair `EMG1-EMG2` and `C4-P4`. Local sidecar parsing under the current extraction contract also confirms usable in-range `SLEEP-S2`, exclusive `MCAP-A1`, and exclusive `MCAP-A3` rows for both subjects. [[bruxism-cap-control-side-expansion-audit-2026-05-06]]

## Exact local verification
| subject | edf bytes local=remote | txt bytes local=remote | duration_min | EMG1-EMG2 | C4-P4 | S2 in range | A1-only in range | A3-only in range |
|---|---|---|---:|---|---|---:|---:|---:|
| n1 | `496456432` | `84246` | `577.0` | yes | yes | `508` | `139` | `56` |
| n2 | `372825496` | `45163` | `735.0` | yes | yes | `367` | `94` | `49` |

## Contract used
The counts above follow the repo's current local extraction contract, not a looser sidecar presence check:
1. `SLEEP-S2` rows must be in-range for the locally available EDF duration.
2. `A1-only` means a kept `SLEEP-S2` window overlaps `MCAP-A1` and excludes simultaneous `MCAP-A2` / `MCAP-A3` overlap.
3. `A3-only` means a kept `SLEEP-S2` window overlaps `MCAP-A3` and excludes simultaneous `MCAP-A1` / `MCAP-A2` overlap.

That matters because raw sidecar event totals are larger than the contract-level kept counts, especially for `MCAP-A1` / `MCAP-A3`. [[bruxism-cap]]

## Repo consequence
The admissible-set understanding does not change, but it is now locally verified rather than only remotely audited:
- positives stay fixed at `brux1` and `brux2`
- verified controls stay `n3`, `n5`, and `n11`
- newly verified clean additions are `n1` and `n2`
- `n10` still stays `refresh_needed` until its EDF is replaced with the canonical full-length object

Because the local verification matches the existing manifest proposal exactly, `projects/bruxism-cap/data/subject_manifest.example.csv` does not need another edit. [[bruxism-cap-next-data-strategy-2026-05-06]] [[bruxism-cap]]

## Repo artifact
Detailed repo memo: `projects/bruxism-cap/reports/cap-control-side-download-verification-2026-05-06.md`

## Bottom line
`n1` and `n2` are now cleanly verified local additions for the bounded CAP control-side expansion, so the repo is ready for the first control-expanded rerun on the fixed positive set.