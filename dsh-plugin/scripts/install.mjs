#!/usr/bin/env node
// Install the continuity skill into the dsh user skill root using a staged,
// whole-directory replacement so interrupted upgrades do not leave a mixed tree.
import { access, cp, mkdir, mkdtemp, rename, rm } from "node:fs/promises";
import { constants } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const pkgRoot = resolve(here, "..");
const dshHome = process.env.DSH_HOME || join(homedir(), ".dsh");
const skillName = "maintain-project-continuity";
const parent = join(dshHome, "skills");
const target = join(parent, skillName);
const source = join(pkgRoot, "skills", skillName);

async function exists(path) {
  try {
    await access(path, constants.F_OK);
    return true;
  } catch {
    return false;
  }
}

if (!(await exists(source))) {
  console.error(`source skill missing: ${source}`);
  process.exit(1);
}

await mkdir(parent, { recursive: true });
const stagingRoot = await mkdtemp(join(parent, `.${skillName}.tmp-`));
const staged = join(stagingRoot, skillName);
const backup = join(parent, `.${skillName}.backup-${process.pid}-${Date.now()}`);
let oldMoved = false;
let newActivated = false;

try {
  await cp(source, staged, { recursive: true, force: true });

  if (await exists(target)) {
    await rename(target, backup);
    oldMoved = true;
  }

  await rename(staged, target);
  newActivated = true;

  if (oldMoved) {
    await rm(backup, { recursive: true, force: true });
    oldMoved = false;
  }

  console.log(`installed continuity skill -> ${target}`);
} catch (error) {
  try {
    if (newActivated && (await exists(target))) {
      await rm(target, { recursive: true, force: true });
    }
    if (oldMoved && (await exists(backup))) {
      await rename(backup, target);
      oldMoved = false;
    }
  } catch (rollbackError) {
    console.error(`rollback failed: ${rollbackError.message}`);
  }
  throw error;
} finally {
  await rm(stagingRoot, { recursive: true, force: true });
  if (!oldMoved) {
    await rm(backup, { recursive: true, force: true });
  }
}
