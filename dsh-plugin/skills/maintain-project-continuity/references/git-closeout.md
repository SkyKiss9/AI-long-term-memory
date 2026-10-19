# Scoped Git closeout

Read before editing and when closing a project conversation. These are attribution and preservation rules, not an automatic commit script.

## Before edits

- Identify the actual Git root and current branch, including any parent repository. Inspect staged, unstaged and untracked changes and preserve a baseline of affected files/index content. A file already dirty is not wholly owned by this round.
- For an authorized continuing project without Git, initialize only the confirmed project root unless prohibited. Do not initialize an unrelated parent directory, create a remote, or silently change branches. Never require a clean workspace before useful work can begin.
- If another conversation is editing the same files, reread before writing and again before staging. Do not overwrite intervening changes. Reuse a safe existing branch; follow the project's branch naming rule if a new branch is needed.

## At closeout

1. Compare the current differences with the starting baseline. Identify this round's attributable edits, including continuity records; distinguish user work, concurrent work, sensitive data and disposable outputs. Inspect content, not just filenames.
2. Perform the checks already authorized for this work and inspect the diff for accidental data exposure. If functional tests are not authorized or remain incomplete, do not run them just for closeout. Where project rules permit, save a clearly labelled unverified checkpoint and record what remains; do not call it validated or complete.
3. Stage only the exact owned files or separable hunks. Do not use blanket staging. If unrelated content is already staged, preserve that index and use a genuinely isolated commit method; otherwise leave this round uncommitted with a precise blocker. Do not silently unstage or commit someone else's work. Mixed same-file edits require hunk/content attribution; ambiguous ownership is a reason to stop committing, not a reason to guess.
4. Inspect the proposed commit diff and verify no unrelated content is included, then commit the authorized changes. Do not bypass failing hooks, change signing/identity configuration or rewrite history to force success. Record a failure truthfully; do not repeatedly retry an unchanged failure.
5. Inspect the actual commit content and remaining staged/unstaged/untracked state. Preserve the original unrelated work and index. Report this round as committed only when that is evidenced. No changes means no commit.

## Remainders

- Related but not safely committable work: identify files/hunks in the project handoff, why they remain, verification level and the permitted next disposition. Do not turn the blocked commit into a claim of successful delivery.
- Unrelated pre-existing work: preserve it, identify it briefly when relevant to safe continuation, and do not adopt it as a new task.
- Secrets, private data or large transient artifacts: keep out of Git. Record only a safe locator and the necessary preservation boundary, never secret values. Do not delete or alter ignore rules merely to hide an unexplained leftover.
- A commit records a checkpoint; it does not imply tests passed, changes were deployed, or a remote backup exists. Push, deployment and cross-project cleanup require their own authorization.

If an explicit no-write or stop instruction prevents bookkeeping, stop and explain what was not saved without trying to tidy the workspace first.
