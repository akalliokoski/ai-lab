# Privacy next-step decision after the threat-model memo for `bruxism-cap`

Date: 2026-05-05
Status: bounded branch-decision memo completed.

## Verdict

Keep the privacy branch memo-first for one more step.

Do not advance to a privacy prototype yet. The smallest correct next move is to turn the threat-model memo into one concrete export-boundary design artifact:
- `privacy: design a minimized off-device export schema for future wearable bruxism-cap experiments`

That should be the single next privacy task on the board.

## Why the branch should not jump to a prototype yet

The current repo state is still too benchmark-shaped for a prototype-first privacy move:
- the project is still a tiny public CAP benchmark, not a wearable data pipeline
- pass29 remains the honest comparison anchor
- pass36 only just established that the best current EMG representation clues compose partially on the repaired scaffold
- the threat-model memo was explicit that raw wearable waveform, exact timing structure, dense per-window rows, and personalized calibration should stay local by default
- there is still no real wearable ingestion path, no private user data boundary, and no approved reduced export contract

Because of that, a prototype now would be underspecified. Even a toy DP or federated mockup would force premature choices about what leaves device, at what granularity, and with which identifiers. The next mistake to avoid is importing the current CAP artifact style into a future private-data branch before the export surface is defined.

## Best single next privacy task

Recommended task:
- `privacy: design a minimized off-device export schema for future wearable bruxism-cap experiments`

Expected output:
1. one allowlist of fields permitted to leave device at nightly, weekly, and cohort level
2. one denylist of fields that must remain local
3. one rationale table mapping each allow/deny decision back to the leakage surfaces in the threat-model memo
4. one explicit note on how this differs from the current CAP benchmark artifact flow

## Why this wins over the other roadmap options

### It beats a prototype on sequencing
A schema memo is the prerequisite for any later prototype. Without it, a prototype would mostly test an arbitrary data-sharing shape rather than a privacy design decision grounded in the repo.

### It beats a PySyft/OpenMined feasibility memo on repo-coupling
Tool feasibility is still secondary to data-boundary design. The repo does not yet need a stack decision; it first needs a statement of what data a stack would be allowed to handle.

### It beats a CAP-to-wearable architecture sketch on boundedness
The architecture sketch is useful, but broader. The export schema is smaller, directly implied by the threat-model memo, and more actionable for the next eventual prototype.

### It beats regulatory/DPIA prep on immediate leverage
A DPIA-style memo is important later, but the current branch is still pre-product and repo-constrained. The minimized export contract creates sharper technical substance for any later compliance note.

## Exact files or wiki pages to touch next

Primary repo file to create next:
- `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/privacy-minimized-off-device-export-schema-2026-05-05.md`

Existing files/pages that the next task should read and update against:
- `/home/hermes/work/ai-lab/projects/bruxism-cap/reports/privacy-threat-model-cap-to-wearable-transition-2026-05-05.md`
- `/home/hermes/work/ai-lab/wiki/queries/bruxism-cap-privacy-pets-roadmap-2026-05-05.md`
- `/home/hermes/work/ai-lab/wiki/concepts/bruxism-cap.md`

If the wiki is updated after that next task completes, the most natural preservation target is:
- `/home/hermes/work/ai-lab/wiki/queries/bruxism-cap-minimized-export-schema-2026-05-05.md`

## Bottom line

The privacy branch is active enough to move past a pure threat-model statement, but not yet mature enough for a prototype-first move. The clean smallest next step is one more memo-level design artifact: define the minimized off-device export schema, lock the first privacy boundary, and only then consider a toy local privacy-preserving prototype on CAP-derived summaries.