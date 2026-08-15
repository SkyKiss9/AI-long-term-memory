# dsh-continuity

AI Long-Term Memory project continuity as a **DeepSeek Harness (dsh)** plugin bundle: handoff-first continuation, targeted lookup, and automatic write-back for long-running projects.

This package ships the same redacted, bilingual `maintain-project-continuity` skill published in this repository's root `skills/` directory.

## Install

```bash
# from this repository checkout
dsh plugin --profile web add ./dsh-plugin

# install the skill files into the dsh user skill root
node node_modules/@skykiss9/dsh-continuity/scripts/install.mjs
```

Then restart `dsh web` (or start a new session). The continuity skill appears in the skill list and is available in every workspace.

> Windows note: `dsh plugin add` cannot take a local path containing spaces. If your checkout path contains spaces (for example `E:\Codex OpenAI\...`), copy the `dsh-plugin` directory to a space-free path such as `C:\dsh-continuity` and run the commands from there.

## Verify

```bash
ls "$HOME/.dsh/skills/maintain-project-continuity/SKILL.md"
dsh --profile web --dump-config   # shows the bundle in dsh.profile.bundles
```

## What it does not install

Real project handoffs, timelines, or business data stay in your own workspace. This package only provides the generic method, templates, and validation scripts.
