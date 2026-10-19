# Project notebook, not chained summaries

Original sources establish what was said or done. A chronological notebook retains the origin, decisions, reasons and changes. A current handoff points to today's work. Git preserves attributable file changes. None substitutes for the others.

## Minimal records

Reuse the project's overview, timeline and handoff; do not add a new layer or per-chat report by default. The overview preserves why the project began, the desired outcome and durable constraints. Record later goal changes in the timeline without rewriting the original intent.

A normal notebook entry is two or three sentences with a date and direct source. Record the known reason for an important decision, distinguish a suggestion from a decision and distinguish work done from verification. Important decisions without file changes still count. Split independent matters rather than dropping meaningful reasons or limits to satisfy a word count.

For example (fictional):

> 2026-10-16: To let the warehouse work without network access, the user chose a local export instead of a cloud-only page; online publishing is not authorized. The export is implemented but not yet tested with the warehouse's files. Source: conversation A, user turn 3; export change in commit B.

A later decision to publish online would be a new entry with its new reason and scope, not an edit claiming the original decision was online-first. If the user later says to stop the task, record cancellation rather than successful validation.

## Current bookmark

The manifest only locates records; keep its note static. Current state lives in the handoff alone, so a dated status in the manifest note becomes a competing bookmark.

Keep the goal/origin pointer, relevant effective decisions and reasons or links, latest deliverable and verification level, unresolved/stopped matters, authority boundary and next authorized action. Include an exact disposition for this round's uncommitted changes when any remain. Omit empty sections.

Build updates from the current conversation and observed artifacts while retaining still-valid decisions. Replace outdated state instead of stacking summaries. Do not mechanically compress the last handoff into the next. Long history stays in the timeline, not in the startup bookmark.

## Retrieval and repair

Ordinary starts read the manifest and current handoff. Retrieve only the timeline entries and original sources needed to understand a relevant decision, resolve a contradiction or change direction. No default full-history reading or memory exam.

Each substantive entry needs a recoverable source: a conversation identifier and turn when available (for Claude Code, the session id the hook supplies), or a precise document, commit or observation. A bare “this conversation” without an identifier is not a durable locator. If the ordinary conversation reader returns no content, try the known local transcript or compressed archive when available. If the source still cannot be read, mark the gap instead of treating another summary as proof.

Do not merge competing entries or migrate old projects from elsewhere. Resolve the relevant authority conflict in that project's own workspace, preserve previous records, and ask only if evidence and existing decisions cannot settle a consequential choice. Project-wide rebuilding is for first registration or explicitly scoped repair, not daily use.

## Closeout and tests

Record milestones during work. At closeout, reconcile the whole conversation with the saved notebook, refresh the bookmark, apply the separate Git closeout procedure and give a truthful short receipt. Repetition requires no duplicate entry. A conversation ending does not itself complete or cancel the task.

Structural checks detect missing, malformed or stale files, not faithful memory or safely attributed commits. Authorized behavioral tests need real source fixtures and fresh context; check the saved artifacts and commit content, not just the agent's claim. Never infer all-project reliability from a few passing cases.
