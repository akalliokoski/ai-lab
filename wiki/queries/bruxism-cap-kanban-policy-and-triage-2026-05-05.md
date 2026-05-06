---
title: Bruxism CAP kanban policy and triage rule
created: 2026-05-05
updated: 2026-05-05
type: query
tags: [workflow, notes, research, experiment]
sources:
  - bruxism-cap-pass43-event-subset-family-verdict-2026-05-05.md
  - bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05.md
  - bruxism-cap-campaign-handoff-2026-05-05.md
---

# Bruxism CAP kanban policy and triage rule

Question: after the pass43 verdict and the board confusion around `Nudge Dispatcher`, what short written kanban policy should govern `bruxism-cap`, what should the `TRIAGE` lane text say, and which currently activated card should count as the next picked specification task? [[bruxism-cap]] [[bruxism-cap-pass43-event-subset-family-verdict-2026-05-05]] [[bruxism-cap-pass43-matched-a1-vs-a3-transfer-audit-2026-05-05]]

## Short written kanban policy
1. `ai-lab` is the default specifier for `TRIAGE` cards on `bruxism-cap`.
2. `TRIAGE` is for real branch ideas that matter, but are still underspecified or gated by an upstream result.
3. The dispatcher does not promote `TRIAGE`; a human or agent must explicitly move a card out of `TRIAGE` once one bounded next task is clear.
4. `TODO` means the task is already specified tightly enough to run once dependencies and priority allow.
5. `READY` means the task is executable now and may be claimed by the dispatcher.
6. `RUNNING` means one profile is actively working the task.
7. `ai-lab` owns repo-grounded specification and implementation on the active benchmark loop unless a card says otherwise.
8. `gemma` is the skeptic/reviewer/synthesizer lane, especially for verdicts, branch choice, and overclaim checks.
9. `aaltoni` is the literature/preservation lane, especially for source verification, wiki updates, and durable notes.
10. Future branches should stay wiki-first until there is exactly one bounded next task with explicit files, outputs, and an activation condition.

## Revised TRIAGE lane description
`TRIAGE`: real but still underspecified branch ideas. On `bruxism-cap`, `ai-lab` is the default specifier for this lane. A card stays here until one exact next task is clear: one primary output, one owner, exact files or artifacts to touch, and a concrete activation condition if it is still gated. The dispatcher ignores `TRIAGE`; moving a card out of this lane is an explicit human/agent decision, not an automatic promotion.

## Picked card
Picked active card: `t_98c3f05e` — `triage: specify the first post-pass43 branch if fixed-subset transfer stays ambiguous`.

Why this is the right picked card now:
- pass43 resolved the ambiguity enough to make the next branch concrete;
- the durable verdict is now `scaffold-bound`, so the highest-value uncertainty is scaffold mismatch rather than feature identity;
- this makes the next specification task narrower than a broad new feature search or future-branch pivot.

## Exact branch this card should now specify
The card should narrow to one primary next task:
- keep the verified 3-feature event subset fixed;
- rebuild only the `A3-only` comparison table on the repaired percentile-band / time-aware `EMG1-EMG2` scaffold;
- compare that repaired `A3-only` result directly against the repaired `A1-only` pass42 surface;
- keep model family, broader feature search, privacy work, and LLM/RL work out of scope.

In other words, the next active question is not "search for another clever subset" but "remove the old `A3-only` scaffold mismatch and see whether the pass42 event subset still looks scaffold-bound once the comparison surface is repaired." [[bruxism-cap-pass43-event-subset-family-verdict-2026-05-05]]

## What should stay gated
- Privacy branch: still gated.
- LLM/RL branch: still gated.
- Broad feature-family rewrite: still gated.
- Model-family change: still gated.

## Practical operator rule
If a card in `TRIAGE` cannot be rewritten as one sentence of the form "profile X should produce artifact Y by touching files Z under condition C," it should stay in `TRIAGE` or move back to the wiki rather than being nudged forward on the board.
