---
name: maintain-project-continuity
description: Project continuity for long-running projects across Codex and DeepSeek Harness (dsh). On an ordinary start, read only the current handoff and expand to older records or original sources only when the task actually needs them.
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
4. If something important is missing or contradictory, follow the handoff's references to the relevant timeline entry, then to the corresponding original conversation or runtime evidence.
5. Read the complete timeline or full source history only for first-time reconstruction, an explicit history audit, or a conflict that targeted lookup cannot resolve.

A manifest state is descriptive history. It never turns an ordinary start into a cold-start exam, forces a fixed checklist answer, or requires every manifest record to be loaded.

## Source discipline

- Original conversations and actual files, commits, pages, logs, or runtime results prove what happened.
- Do not use global memory, unrelated old tasks, or internet material as substitute project evidence.
- The timeline is a light chronological notebook. A normal entry is one or two lines: when something materially changed, what changed, and where to find the direct source. Include the reason only when it matters.
- The handoff is a short bookmark: current position, current boundary, and next authorized work. It may mention a pending decision when one is active, but it does not retell project history.
- Keep user decisions, assistant suggestions, implementation choices, external facts, verification results, and pending questions separate.
- Preserve earlier decisions and reasons. When they change, append a short new entry and source instead of rewriting history; point to the old entry only when the change would otherwise be unclear.
- Missing or unreadable evidence stays marked as a gap. Do not turn a summary into substitute evidence.

## Automatic write-back

- On a genuine project closure, or after material progress that changes the continuation point, append one short timeline note linked to the current conversation, file, commit, or runtime evidence, then refresh the handoff.
- Write naturally rather than filling a report template. Keep only the details another person or AI needs to locate the source and continue safely.
- Replace stale handoff details instead of accumulating history there.
- If nothing material changed, do not rewrite the records.
- The user does not need to request or supervise this bookkeeping.

## Reconstruction and audits

If a project has no usable handoff or timeline, reconstruct them from available sources as a setup or repair task. Do the work without turning the method into a design questionnaire for the user; ask only about genuine source gaps or ambiguous decisions.

Full-history reconstruction, source-fidelity audits, isolated cold-start exercises, and multi-round drift studies are special verification work. Run them only when the user requests that work or when targeted lookup proves the records are broadly unreliable. They are not the daily startup path.

## Tool boundary

Installation and validation scripts may check structure: readable files, unique managed blocks and paths, valid references, and repository state. They cannot decide whether memory is faithful, a user decision is correctly understood, a business task is complete, or the user's real path works. Report those checks as structure checks only.

## Boundaries

- Project records remain inside their own project. Original conversations may remain in Codex storage and be referenced directly.
- Do not edit another project's code, data, business rules, or runtime without authorization for that project.
- Do not delete old history merely to reduce startup context; stop loading it by default.
