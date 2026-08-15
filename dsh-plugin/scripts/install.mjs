#!/usr/bin/env node
// Install the AI Long-Term Memory continuity skill into the DeepSeek Harness
// user skill root (<DSH_HOME>/skills) so dsh discovers it automatically.
import { cp, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const pkgRoot = resolve(here, "..");
const dshHome = process.env.DSH_HOME || join(homedir(), ".dsh");
const target = join(dshHome, "skills", "maintain-project-continuity");
const source = join(pkgRoot, "skills", "maintain-project-continuity");

if (!existsSync(source)) {
  console.error(`source skill missing: ${source}`);
  process.exit(1);
}
await mkdir(dirname(target), { recursive: true });
await cp(source, target, { recursive: true, force: true });
console.log(`installed continuity skill -> ${target}`);
