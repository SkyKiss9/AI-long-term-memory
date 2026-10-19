---
name: maintain-project-continuity
description: Continue or close long-running projects in Codex, Claude Code and DeepSeek Harness. Use for project work, decisions, “继续”, “本对话收尾”, or “下个对话继续”; maintain source-linked notes and safely close out Git changes, not standalone Q&A.
---

# Maintain Project Continuity

Keep a project notebook, not a chain of summaries. Original sources establish facts; the timeline preserves origins, decisions and their reasons; the current handoff locates today's work; Git preserves the actual changes. The user works normally; the AI owns this bookkeeping.

## Ordinary start

1. Read the nearest project rules. Check the actual repository root, branch, staged, unstaged and untracked changes before editing; preserve pre-existing work. For changes or closeout, read [Git closeout](references/git-closeout.md).
2. Read the project's continuity manifest, then only its current handoff. Recover the goal, relevant effective decisions, current position and authorization boundary before acting. Do not recite project history to the user.
3. If a relevant fact is missing, stale or contradictory, follow the handoff to the specific timeline entry and its direct source. Before reopening a rejected route or reversing a decision, check its recorded reason. Do not infer current authority from a filename or modification time.
4. If competing manifests or handoffs are encountered, resolve the relevant conflict using project evidence and existing rules. Do not silently overwrite either entry or migrate the project. A descriptive manifest state is not an instruction to run an exam.

In Claude Code, the optional [SessionStart hook](references/claude-code.md) injects the manifest and handoff automatically; that injection counts as reading them. After compaction, treat the compaction summary as navigation, not evidence.

Full history is for first-time reconstruction, an explicit audit, or widespread conflicts that targeted lookup cannot resolve. Ordinary continuation must not load the entire timeline, source index or acceptance history. A previous summary is a navigation aid, not independent evidence for another summary.

## Entry and scope

- New project: create records inside that project using the existing installer and templates. Record why the project started, its intended outcome and constraints in the overview (or an existing equivalent); link it from the handoff. Do not require a new document for every conversation.
- Old project: keep usable local records. Repair or reactivate it from its own workspace and evidence; do not batch-migrate projects from elsewhere. Entry-point or preservation choices need a question only when genuinely ambiguous or scope-changing, not when already decided.
- Project facts come from that project's conversations, files, commits and observed results. Global memory may route lookup, but cannot substitute for project evidence. An unreadable source remains an explicit gap; try an available local archive, including compressed transcripts, before claiming it is lost.
- Keep user decisions, assistant suggestions, implementation choices and verification results distinct. Records do not authorize business changes, tests, deployment or work in another project. Follow the user's actual authorization, including a no-write or stop instruction.

## The notebook

- For each substantive conversation or milestone, append a short dated entry, normally two or three sentences: why this work arose, what was decided/done and the actual result, and any remaining or stopped work. Attach a direct source locator (conversation and turn when available, or a specific artifact). Separate unrelated important decisions rather than compressing away their boundaries.
- Preserve important decisions **and their known reasons**. If the reason was not stated, do not invent one. A decision, rejection, cancellation or user acceptance is material even if no code changed. Distinguish user-reported acceptance from AI-run verification.
- Later changes append a correction or superseding decision and its reason, pointing to the earlier entry when needed. Never rewrite the old history to make the project appear to have always followed the latest plan. Correct a handoff's stale state without erasing the history.
- Small talk, repeated confirmations and already-recorded closeouts need no placeholder entries. Do not copy logs or full chat transcripts into the timeline. See [method and example](references/method.md) when composing or repairing records.

## Current handoff

Keep a brief current bookmark: goal and origin reference; relevant effective decisions and reasons (or precise links); latest deliverable and verification level; unresolved issues, stopped work and boundaries; next authorized action; any uncommitted work and its disposition. Omit irrelevant or empty sections.

Update it against this conversation and actual artifacts, not just the previous handoff. Replace stale details instead of stacking dated updates. Completed, cancelled and unverified are different states. No authorized next action means wait for a new request, not invent a follow-up. Keep enough context to choose safely; details and history stay behind references.

## Milestones and closeout

Record decisions, acceptance and material progress while working, rather than waiting until context is exhausted. The user does not need a special maintenance command.

On “本对话收尾”, “下个对话继续”, or an equivalent closeout:

1. Stop expanding business work. Review the **whole current conversation** for material information not yet recorded; the final sentence alone is not the test for “nothing changed”.
2. Append only missing notebook entries and refresh the handoff from direct sources. Closing a conversation does not cancel unfinished work unless the user says so; cancellation does not mean it was fixed. Do not start extra tests or repairs just to close.
3. Finish the scoped Git closeout below. Reread saved records and inspect the actual commit and remaining changes before claiming they were saved or committed.
4. Give a short truthful receipt: what is recorded, whether this round's changes are committed, and any specific exception. Do not expose commands, paths or a technical checklist unless asked.

If everything was already recorded and committed, do not write duplicate entries or empty commits. If writing is forbidden, interrupted or failed, do not claim closeout succeeded; on authorized resumption inspect the last saved state and recover missing facts from the source. Explicit “stop all operations” takes precedence over bookkeeping.

## Git closeout

Use [Git closeout](references/git-closeout.md) before editing and at closeout. Commit this round's attributable, authorized changes after the permitted checks; preserve unrelated staged and unstaged work. A safely labelled unverified checkpoint is not a completed feature. If a commit is prohibited or unsafe, preserve the work and record the exact remainder, reason and disposition instead of silently carrying it forward.

The aim is **no unexplained leftovers from this round**, not a forcibly clean workspace. Never blanket-stage, reset, clean, stash other work, bypass hooks, change signing/identity policy, or push just to make closeout pass. Sensitive data and transient outputs are not commit candidates. A local commit is neither a remote backup nor proof of business completion.

## Verification and communication

Installation and validation tools check structure only. They cannot establish source fidelity, memory accuracy, successful Git attribution or user experience. When behavioral testing is authorized, test source-linked decisions, fresh continuation, corrections, repetition/interruption and mixed Git ownership in isolated fixtures. Do not turn ordinary starts into these tests.

Keep continuity work in the background. Follow global communication preferences; answer the user's actual request directly and do not ask them to administer records, choose context budgets, repeat settled decisions or organize memory tests. Do not remove old history to reduce context use; stop loading it by default.
