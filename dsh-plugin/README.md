# dsh-continuity

AI Long-Term Memory project continuity for DeepSeek Harness (dsh): handoff-first continuation, targeted lookup, and safe automatic write-back for long-running projects.

The actual capability is a standard `SKILL.md` bundle. dsh can discover standard skills from user and project skill roots, so a Cordis runtime patch is not required for this feature.

## Install from this repository

```bash
node ./dsh-plugin/scripts/install.mjs
```

This stages a complete copy and then replaces `$DSH_HOME/skills/maintain-project-continuity` as one directory. Reinstalling removes stale files from older versions instead of leaving a mixed old/new skill tree.

If `DSH_HOME` is not set, the default target is `~/.dsh/skills/maintain-project-continuity`.

## Verify

```bash
ls "$DSH_HOME/skills/maintain-project-continuity/SKILL.md"
```

If `DSH_HOME` is unset, use `~/.dsh/skills/...` instead. Start a new dsh session after installation; if an already-running instance does not refresh its skill catalog, restart that instance.

## Cordis bundle note

`cordis.patch.yml` is intentionally empty. `dsh plugin add` installs packages into a profile's `node_modules`, but this continuity feature does not need a mounted runtime row; it only needs the skill directory in a discovery root.

## What it does not install

Real project handoffs, timelines, or business data stay in your own workspace. This package only provides the generic method, templates, scripts, and validation rules.
