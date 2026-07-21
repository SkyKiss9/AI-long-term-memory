---
name: maintain-project-continuity
description: Use automatically on the first project-related turn, when a project continuity skill was registered but not fully activated, when the user starts or resumes project work, and when the user finishes or hands off a long-running project. Project activation means rebuilding source-backed project-local records, validating a fresh cold start, writing it back naturally, and proving a second fresh handoff; merely wiring the skill is not activation. The user does not need to name or select the skill.
---

# Maintain Project Continuity

Use this skill to keep a long-running project understandable across conversations. It is a reusable workflow, not a replacement for the project's own rules and not proof that a project's history has already been reconstructed.

## Storage model

- The skill is a globally discoverable workflow with one canonical implementation. Do not copy or fork the skill body into every project.
- Each project's authoritative overview, timeline, current handoff, source index, and acceptance state belong inside that project's own repository and are named by its `.codex/project-continuity.json` manifest.
- Original Codex conversations or archives remain source evidence. Project records point back to them and summarize the working history; they do not require every raw conversation to be copied into the project.
- A method repository may keep frozen pilot snapshots and acceptance evidence for another project, but those snapshots never become that project's living current handoff. Once a project has its own records, only that project maintains its current state.

## Scope gate

- On the first project-related turn of a conversation, restore continuity before answering even if the user only asks whether the project skill is installed or whether the assistant knows the project. A genuinely unrelated one-off question does not trigger project restoration.
- For any substantive task, first check the project rules, repository state, and the project continuity manifest at `.codex/project-continuity.json`.
- Treat the manifest state as a claim with five levels: `registered` means only the skill trigger and manifest are wired and the project is not activated; `bootstrapped` means sources and project-local continuity records were rebuilt but no fresh task has passed; `handoff-pending` means the first fresh task recovered the project and naturally wrote back, but the required second fresh handoff has not passed; `cold-start-validated` means that second fresh task received the write-back correctly and the project is activated for ordinary continuation; `live-validated` means a fresh task additionally completed authorized real work, wrote it back, and a second fresh task reran the critical path. Legacy `installed` means the same incomplete state as `registered` and must be migrated.
- Never upgrade a state from evidence that only proves a lower state.

## Activation contract

- Registering the global skill or writing a project trigger is only wiring. Never tell the user that the project skill is activated, ready, or directly usable while the manifest is `registered`, legacy `installed`, `bootstrapped`, or `handoff-pending`.
- When the user asks to install, activate, enable, or use this skill for a project, complete activation end to end in the same workstream unless a real source, permission, or environment blocker prevents it. Do not stop after creating the manifest.
- Activation must inventory every available original conversation, complete archive, project document, commit, and relevant runtime source; record coverage and gaps; build the project's own overview, append-only timeline, current handoff, and source index; make stale project entry points unambiguously historical or redirect them to the current authority; and commit a reproducible baseline.
- After the baseline, run a genuinely fresh task that does not name the skill and does not inherit the builder's hidden context. It must recover the goal, evolution, confirmed decisions and reasons, superseded or reopened routes, evidence gaps, current state, unauthorized work, and exact continuation point from the project records. Correct any error and repeat with another fresh task.
- After the first fresh task passes, a natural closure must write that result back and set `handoff-pending`. Then run a second genuinely fresh task with only a normal continuation request. It must receive the first task's write-back, identify itself as the required second handoff, and leave only independent evaluation plus final state write-back; asking for a third fresh task fails.
- The task that performs the first fresh recovery must never promote itself to `cold-start-validated`, even after a follow-up message such as `完成` or `交接`. That follow-up is only the first task's natural closure and may move the project to `handoff-pending`. A second-task promotion is valid only from a separate task/conversation with a new task boundary and its own source trace; if that boundary cannot be independently evidenced, downgrade the result to `handoff-pending` and record the false promotion as a failed test.
- Activation is complete only after both fresh-task results and repository closure are written into the project acceptance record, the manifest is `cold-start-validated` or `live-validated`, required changes are committed, and the worktree state is reported honestly.
- If the project is already `registered` or legacy `installed`, the first project-related turn must continue the incomplete activation automatically unless the user explicitly limits the task to read-only diagnosis. Do not answer only that the skill is visible.
- If the project is `bootstrapped`, the current fresh conversation is the cold-start acceptance task. On its first project-related turn, read every manifest record completely and present the full recovered context required by startup step 3. Do not merely report that validation is pending, ask the user to start validation, or postpone it to another task. The user or an independent evaluator will judge the answer; the task must not promote its own state before that judgment is written back.
- If the project is `handoff-pending`, the current fresh conversation is the required second handoff. It must still recover all nine items from project records, but it must explicitly identify the first task and its natural write-back as already complete. Its immediate next step is independent evaluation of this second answer followed by final acceptance/state write-back. It must not restart the first-test sequence or request a third fresh task.
- A same-task follow-up is not a fresh conversation. When the current task already performed the `bootstrapped` recovery, any later closure message in that same task must stop at `handoff-pending`; it cannot satisfy the second-handoff requirement.
- Before sending that first answer, check that it explicitly covers all nine items: (1) real goal, (2) main evolution, (3) confirmed decisions, (4) the user's reasons for those decisions, (5) superseded or reopened routes, (6) source and evidence gaps, (7) current state, (8) the exact authorization and prohibition boundary, and (9) the immediate next action plus its completion test. Implying an item indirectly is not enough; omitting any item fails acceptance.
- The real goal in item 1 is the target project's product, business, research, or operational outcome, not "preserve continuity", "help the next conversation", or "maintain project memory". State the domain goal and user-facing deliverables first, then separately state that continuity activation is the current task. Never let the continuity mechanism replace the project's purpose.
- Begin the answer by making clear that this current conversation is performing the cold-start recovery now. Do not say that the next step is to create another fresh task; after the full answer, the immediate next step is user or independent evaluation of this answer, followed by natural closure/write-back and a second fresh continuation only if it passes.
- Cold-start project facts must come only from the project records named by the manifest. The canonical global skill and the project's own `AGENTS.md` may be read as process instructions, but they are not factual evidence about the project. Do not read global memory, old tasks, the internet, external project notes, hidden evaluator answers, or additional project business documents not named by the manifest. State the concrete gaps recorded in the project, not the phrase "evidence gaps" as an unanswered checklist item.
- Before accepting a fresh-task result, inspect its actual tool/source trace. A task's own claim that it used only project records is not evidence. Active reads of global memory, internet sources, evaluator material, or non-manifest business documents fail isolation even when the final answer happens to be correct.

## Natural-language trigger gate

- Invoke this skill automatically before answering the first project-related user message in each new conversation. This includes questions such as "你知道这个项目吗", "这个技能装好了吗", and "现在做到哪里"; no special continuation keyword is required.
- Invoke this skill automatically when the user's meaning, in any language, is to resume or continue a long-running project. Typical Chinese expressions include "继续这个项目", "接着上次", "恢复进度", "从上次的位置继续", and "开始下一个对话". The user does not need to name or select the skill.
- Invoke it automatically before the final response when the user's meaning is to finish, close, or hand off the current project conversation. Typical Chinese expressions include "完成", "收尾", "做个交接", "结束本轮", "到这里", and "准备开新对话".
- Match the user's intent, not a literal substring. A word such as "完成" does not trigger closure when it appears only in a future plan, condition, example, quotation, test string, status description, or unrelated one-off question.
- A startup trigger runs the startup workflow before substantive work. A closure trigger runs the closure workflow before the final response; it does not turn incomplete or unverified work into completed work.
- If the conversation changed no project decision, implementation, verification result, risk, authorization, or unfinished position, do not edit continuity records merely to create file churn. State that no write-back was needed.

## Startup workflow

1. Read the nearest `AGENTS.md` files and run the project's normal repository/status check. Do not revert or hide existing user changes.
2. Read the manifest. If it names an overview, timeline, handoff, source index, or acceptance record, read the complete named files before acting.
3. State in plain language: the real goal, the main evolution, confirmed decisions and their reasons, superseded or reopened routes, current status, evidence boundary, unauthorized work, and this task's completion test.
   For a `bootstrapped` or `handoff-pending` project this full statement is mandatory in the first answer, even if the user's question is only whether the skill is installed or known. A one-sentence status reply, replacing the domain goal with the continuity goal, an implicit authorization boundary, an unspecified immediate next step, external-source use, postponing the test to another task, or listing a gap category without its actual known facts fails cold-start acceptance.
4. If records conflict or are stale, return to the original conversation/source. Mark missing, interrupted, duplicated, damaged, or unreadable material as a gap; do not infer it away.
5. For a `registered` or legacy `installed` project, continue the activation contract automatically. Inventory the complete available source boundary and build the records; do not merely propose a later bootstrap or claim the history is restored early.

## Source and decision rules

- Original conversations or complete archives prove what happened. Project notes explain why the project changed. The current handoff only points to the current work position; none may silently replace another.
- Label each material item as a user decision, assistant suggestion, implementation choice, external fact, verification result, or pending question.
- A decision record must preserve the user's reason, considered or rejected alternatives, scope, accepted risk, confirmation source, current status, reopening condition, and any superseded record. Append a new record when premises change; do not rewrite history in place.
- A later task must not call an accepted decision a conflict merely because a later audit or implementation disagrees. Locate the source and rationale, show genuinely new evidence or changed premises, and leave reconsideration pending until authorized.
- A source from another project or directory that affects this project must be registered explicitly as a cross-project source. It is not a newly discovered local conversation.

## Writing and verification

- Keep the overview stable: purpose, scope, authority, and durable boundaries.
- Keep the timeline append-only: why the work started, what changed, the decision and reason, result, unfinished work, and source location.
- Keep the handoff short: current position, recent change, unresolved items, next authorized work, and the exact completion test.
- At the end of important work, update the timeline and handoff. If no user decision was made, say so explicitly.
- On a closure trigger, record the real state even when it is partial or blocked: why the conversation started, material decisions and reasons, actual result, evidence, unfinished work, authorization boundary, and the exact continuation point. Never copy a vague chat summary over stronger project records.
- Complete the project's required checks and repository closure after write-back. Report the current branch, remaining changes, and commit state according to the project's own rules; do not claim handoff completion while required records remain uncommitted.
- Verify the user's real path at the layer requested: source fidelity, build/script checks, UI or runtime path, write-back, and then repository status. Do not use a script result, screenshot, build, or backend result as a substitute for a different layer.
- Report `registered`, `bootstrapped`, `handoff-pending`, `cold-start-validated`, `live-validated`, `repository committed`, `remote verified`, and `user path verified` separately. Do not call wiring or a partial result activation.

## First bootstrap and acceptance

When a project moves beyond `registered` or legacy `installed`, use the templates in `assets/` only when the project has no equivalent authoritative files. Use `references/method.md` for the detailed evidence model. The minimum bootstrap evidence is a source index plus a timeline, overview, and current handoff. A cold-start test must use only those project records and must not name the skill. A live-validation test additionally needs authorized real work, user-path evidence, write-back, and a second fresh-task rerun.

Use `scripts/validate_project.py <project-root>` after registration and after each state transition. `scripts/install_project.py` is a low-level registration helper that only writes the marked project rule and manifest; it preserves unrelated text but does not activate a project by itself.

## Boundaries

- Project activation authorizes reading available history and writing continuity records, but it does not authorize editing product code, data, runtime, remote services, or formal business rules.
- Global skill discovery alone does not activate every project. Once the user registers or activates the skill for a specific project, finish that project's continuity activation automatically instead of leaving it in a wiring-only state.
- Do not create a second competing "current handoff" after a project has its own authoritative continuity entry.
