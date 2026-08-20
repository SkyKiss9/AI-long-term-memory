# Long-Term Project Continuity Method

## The simple relationship

Original sources prove what happened. The timeline explains what changed and why. The current handoff points to where work should continue.

Information moves from source to timeline to handoff. The handoff names the timeline events it is based on; timeline events carry direct source locators. When verification is needed, follow those pointers back to original evidence instead of treating one summary as evidence for another.

## Ordinary use

An ordinary new conversation reads the current handoff first and starts the user's work. It opens only the timeline events and original sources needed for the current task. The complete history is not a startup dependency.

The user does not maintain this system. The AI records material changes and their source, refreshes the current handoff, and performs targeted lookup when something is unclear.

## What the handoff contains

- Revision
- Current position
- Current boundary or blocker
- Next authorized work
- Basis timeline event IDs

It is a short bookmark, not a second project history. Replace stale details instead of accumulating them.

## What the timeline contains

The timeline is a light chronological notebook. A normal entry is one or two lines with a stable event ID, date, what materially changed, and a direct source locator. Add the reason only when it helps explain the change. Later changes are appended rather than written over earlier decisions.

## Concurrent work

Only the coordinating/main agent writes shared continuity records. Before write-back it rereads the current handoff and timeline tail; if another session changed them, it merges the newer state rather than overwriting it. Subagents return evidence and findings to the coordinator.

## When full history is appropriate

Use broad source reconstruction for a project with no usable records, an explicit history audit, or a widespread conflict that targeted lookup cannot resolve. Long histories are processed in bounded batches; "full history" means all relevant evidence may be visited, not that it is loaded into one model context.

## Tool boundary

Tools may check structure and broken references. They cannot certify source fidelity, memory accuracy, business completion, or real user experience. Registration alone is not a claim that ordinary continuation is ready.
