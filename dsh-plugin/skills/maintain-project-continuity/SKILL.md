---
name: maintain-project-continuity
description: Project continuity for long-running Codex and DeepSeek Harness (dsh) work. Use when resuming a project in a fresh conversation, recovering after context loss, recording material progress or decisions for later continuation, or repairing/auditing continuity records.
---

# Maintain Project Continuity

The user should be able to continue a project by speaking normally. The AI owns the bookkeeping, source lookup, and write-back.

## Default user experience

- Do not ask the user to choose a storage model, file count, context budget, validation sequence, or maintenance workflow.
- Do not ask the user to reconfirm a decision that was already stated clearly.
- Ask only when the user's meaning is materially ambiguous or a proposed action would reverse or expand an existing decision.
- Do not begin an ordinary conversation with a project-history recital. Recover enough context internally, then work on the user's actual request.

## Ordinary start

1. Read the nearest project rules and check the repository state.
2. Read the project continuity manifest, then read only the current handoff named by it.
3. If the handoff is sufficient, start the requested work.
4. If something important is missing or contradictory, follow the handoff's `Basis` timeline IDs to the matching timeline entries, then follow their source locators to the corresponding original conversation or runtime evidence.
5. Access broader history only for first-time reconstruction, an explicit history audit, or a conflict that targeted lookup cannot resolve. For long histories, process sources in bounded batches; never load the entire history into one model context merely because a full reconstruction is required.

A manifest state is descriptive history. It never turns an ordinary start into a cold-start exam, forces a fixed checklist answer, or requires every manifest record to be loaded.

## Source discipline

- Original conversations and actual files, commits, pages, logs, or runtime results prove what happened.
- Do not use global memory, unrelated old tasks, or internet material as substitute project evidence.
- The timeline is a light chronological notebook. Each material event has a stable ID such as `T-20260820-001`, a date, what changed, and a direct source locator that another agent can use to find the evidence. Include the reason only when it matters.
- The handoff is a short bookmark: revision, current position, current boundary, next authorized work, and `Basis` timeline IDs. It may mention a pending decision when one is active, but it does not retell project history.
- Keep user decisions, assistant suggestions, implementation choices, external facts, verification results, and pending questions separate.
- Preserve earlier decisions and reasons. When they change, append a short new timeline entry and source instead of rewriting history; point to the old entry only when the change would otherwise be unclear.
- Missing or unreadable evidence stays marked as a gap. Do not turn a summary into substitute evidence.

## Automatic write-back

- On a genuine project closure, or after material progress that changes the continuation point, append one short timeline event linked to the current conversation, file, commit, page, log, or runtime evidence, then refresh the handoff.
- Before write-back, reread the current handoff and the tail of the timeline. If another agent or session changed them since this task started, merge the newer state instead of overwriting it.
- Only the coordinating/main agent writes shared continuity records. Subagents return findings and evidence to the coordinator rather than editing the handoff or timeline directly.
- Increment the handoff `Revision` on every material handoff refresh.
- Write naturally rather than filling a report template. Keep only the details another person or AI needs to locate the source and continue safely.
- Replace stale handoff details instead of accumulating history there.
- Update the overview only when a stable project truth changes: real goal, scope/boundary, a confirmed durable decision, a superseded route, evidence boundary, or acceptance standard.
- If nothing material changed, do not rewrite the records.
- The user does not need to request or supervise this bookkeeping.

## Reconstruction and audits

If a project has no usable handoff or timeline, reconstruct them from available sources as a setup or repair task. Do the work without turning the method into a design questionnaire for the user; ask only about genuine source gaps or ambiguous decisions.

Full-history reconstruction, source-fidelity audits, isolated cold-start exercises, and multi-round drift studies are special verification work. Run them only when the user requests that work or when targeted lookup proves the records are broadly unreliable. They are not the daily startup path.

## Tool boundary

Installation and validation scripts may check structure: readable files, unique managed blocks and paths, valid references, record shape, and repository state. They cannot decide whether memory is faithful, a user decision is correctly understood, a business task is complete, or the user's real path works. Report those checks as structure checks only.

A project can be structurally registered without being ready for ordinary continuation. `registered` means the rules/manifest exist; it does not mean a usable handoff and timeline already exist.

## Boundaries

- Project records remain inside their own project. Original conversations may remain in Codex or dsh storage and be referenced directly.
- Do not edit another project's code, data, business rules, runtime, or continuity records without authorization for that project.
- Do not delete old history merely to reduce startup context; stop loading it by default.
