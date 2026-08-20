<!-- maintain-project-continuity:start -->
## Long-running project continuity

- On the first project-related message and on a natural request to continue, use `$maintain-project-continuity`.
- For an ordinary start, check the repository and manifest, then read only the current handoff. Do not load the complete overview, timeline, source index, or acceptance history, and do not give the user a recovery report unless asked.
- If the handoff is not enough, follow its `Basis` timeline IDs to the matching timeline entries and then follow those entries' source locators to original evidence. Access broader history only for first-time reconstruction, an explicit audit, or a conflict that targeted lookup cannot resolve; process long histories in bounded batches rather than loading them all into one context.
- Use the project's own original conversations, files, commits, pages, logs, or runtime results as evidence. Do not substitute global memory, unrelated old tasks, or internet material. Manifest states are descriptive only and never turn an ordinary start into an exam.
- The user speaks and decides normally; the AI owns source lookup, record maintenance, and write-back. Do not ask the user to administer the memory system or reconfirm an already clear decision.
- After material progress or a genuine closure, append one short timeline event with a stable ID, date, what changed, and a direct source locator; include the reason only when it matters. Refresh the handoff as a brief current bookmark and increment its `Revision` instead of accumulating history. If nothing material changed, do not rewrite records.
- Before write-back, reread the current handoff and timeline tail. If another session changed them, merge the newer state instead of overwriting it. Only the coordinating/main agent writes shared continuity records; subagents return evidence to the coordinator.
- Update the overview only when stable project truths change: goal, scope/boundary, durable confirmed decisions, superseded routes, evidence boundary, or acceptance standard.
- Keep user decisions, assistant suggestions, implementation choices, external facts, verification results, and pending questions distinct. Preserve old decisions and append later changes instead of rewriting history.
- Structure tools may report missing, duplicate, unreadable, malformed, or broken records. They do not prove source fidelity, memory quality, business completion, or user-path success. A `registered` project may still be not ready for ordinary continuation.
<!-- maintain-project-continuity:end -->
