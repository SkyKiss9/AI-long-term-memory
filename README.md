# AI Long-Term Memory — Project Continuity for Codex, Claude Code & DeepSeek Harness

> 给 Codex、Claude Code 和 DeepSeek Harness (dsh) 的长期项目连续性技能 · 脱敏公开版  
> A redacted bilingual project-continuity skill for Codex, Claude Code and DeepSeek Harness (dsh)

`Codex Skill` · `Claude Code Skill` · `DeepSeek Harness Plugin` · `dsh` · `AGENTS.md` · `Project Continuity` · `Long-Term Memory`

## 中文说明

这是一个给 Codex、Claude Code 和 DeepSeek Harness (dsh) 长期项目使用的连续性技能。它解决的不是“怎么写一段交接摘要”，而是“当新对话没有旧上下文时，怎样准确恢复项目目标、演变、用户决定、决定理由、边界、当前状态和下一步”。

这个公开版本已经脱敏，只保留通用方法和通用工具，不包含任何真实项目记录、业务数据、历史对话、账号信息、日志、凭证或私有仓库内容。

### 它解决什么问题

- 新对话只拿到压缩摘要，项目真实目标、边界和当前状态丢失。
- 助手把自己的建议误当成用户已经确认的决定。
- 接手时不知道哪些路线已经被替代、哪些风险已经被接受、下一步到底该做什么。
- 本轮文件修改没有妥善提交，后续任务无法区分自己的工作与遗留改动。

### 它怎么工作

1. 新项目直接在该项目里建档；老项目在该项目自己的工作区新开对话重新激活，再决定入口、保留范围和落实方式。
2. 原始材料保留事实，时间线用两三句话记录缘由、决议及已知理由、实际结果和直接来源；当前交接只作为当前位置。
3. 普通新对话只读当前交接，然后直接处理用户的工作。
4. 信息不足或冲突时，AI按引用局部回查；不默认加载完整历史。
5. 决议、验收和阶段进展及时写回；收尾核对整轮，安全提交本轮改动并保护其他工作，用户不需要管理记忆系统。

### 新项目、老项目与专项审计

- 新项目：直接建立清单、规则块、时间线和当前交接。
- 老项目：由用户在该项目工作区新开对话重新激活，再按项目证据决定入口和保留范围；不要从别的项目批量迁移或统一入口。
- 日常接续：只读当前交接，必要时局部回查。
- 首次建档、完整历史审计和多轮失真复核：属于专项工作，才读取完整来源。
- 清单里的状态只是历史说明，不能自动把普通对话变成考试。

### 30秒快速开始（Codex）

1. 把 `skills/maintain-project-continuity` 放进你的 Codex 技能目录。
2. 在目标项目里登记 `.codex/project-continuity.json`。
3. 把规则块写进目标项目的 `AGENTS.md`。
4. 运行校验脚本确认项目记录结构完整。

校验结果使用 `output_schema_version: 1`，只表示结构检查；不包含记忆、业务或用户体验验收结论。

示例：

```bash
python skills/maintain-project-continuity/scripts/install_project.py <project-root> --project-name "My Project"
python skills/maintain-project-continuity/scripts/validate_project.py <project-root>
```

### Claude Code 快速开始

1. 把 `skills/maintain-project-continuity` 链接（或放）到 `~/.claude/skills/`。
2. 在 `~/.claude/settings.json` 加一个 SessionStart 钩子，运行技能里的 `scripts/claude_session_start.py`；配置样例见 `references/claude-code.md`。
3. 之后在已登记项目里新开会话，方法分工、总览与时间线位置、时间线写回要求（缘由、决议及理由、结果、来源，只追加不改写）、当前交接和本会话编号会自动进入上下文；上下文压缩后也会重新注入并提醒摘要不能当证据。钩子只读，不写记录、不提交。

### DeepSeek Harness (dsh) 快速开始

1. 在本仓库目录运行 `dsh plugin --profile web add ./dsh-plugin`。
2. 运行 `node node_modules/@skykiss9/dsh-continuity/scripts/install.mjs` 把技能装进 dsh 用户技能目录。
3. 重启 `dsh web`（或新开会话），接续技能即可在技能列表中使用。

> Windows 注意：`dsh plugin add` 的本地路径不能含空格；如果仓库路径含空格，先把 `dsh-plugin` 目录复制到无空格路径（例如 `C:\dsh-continuity`）再执行安装。

### 这个仓库包含什么

- 通用技能正文
- 通用项目规则块
- 通用模板
- 通用安装脚本
- 通用校验脚本
- 一个脱敏示例清单
- 技能契约测试
- `dsh-plugin/`：DeepSeek Harness (dsh) 插件包

### 这个仓库不包含什么

- 任何真实项目的总览、时间线、当前交接
- 真实对话归档
- 用户数据、业务数据、密钥、账号、远端环境信息
- 针对某个具体项目的私有决策记录

### 核心方法

1. 原始材料证明事实。
2. 时间线保留起因、重要决议及已知理由、实际结果和直接来源；后来的改变追加，不覆盖旧历史。
3. 当前交接保留目标提示、有效决定、当前位置、验证边界和下一项已授权工作，不积累历史。
4. Git 保存归属明确的本轮改动；无法安全提交时写清剩余及处置，不强求整个工作区干净，不自动推送。

### 技能里最关键的几个约束

- 普通开始只读当前交接，不默认读完整时间线和全部来源。
- 用户照常工作和决策，AI负责查找、维护和写回。
- 只有首次建档、明确审计或局部回查无法解决冲突时才读取完整历史。
- 检查脚本只检查结构，不证明记忆、业务或用户体验已经通过。
- 项目事实只能来自该项目自己登记的记录，不能偷偷拿全局记忆、旧任务或外部资料补历史。

### 目录结构

- `skills/maintain-project-continuity/`：技能本体
- `skills/maintain-project-continuity/assets/`：规则块与模板
- `skills/maintain-project-continuity/references/`：方法说明
- `skills/maintain-project-continuity/scripts/`：安装与校验脚本
- `skills/maintain-project-continuity/tests/`：契约测试
- `dsh-plugin/`：DeepSeek Harness (dsh) 插件包

### 公开命名

这个公开仓库使用展示名 **AI Long-Term Memory（AI长期记忆）**，面向 Codex、Claude Code 与 DeepSeek Harness (dsh)。  
为了兼容已有触发方式，技能内部技术名仍然保留为 `maintain-project-continuity`。

---

## English

This is a continuity skill for long-running projects in **Codex, Claude Code and DeepSeek Harness (dsh)**. It does not try to solve “how to write a short handoff summary”. It solves “how a fresh conversation can accurately recover the project goal, evolution, user decisions, decision rationale, boundaries, current state, and next step without inheriting hidden context”.

This public version is fully redacted. It keeps only the generic method and generic tooling. It does not include real project notebooks, business data, conversation archives, account information, logs, credentials, or private repository content.

### What problem it solves

- Fresh conversations inherit compressed summaries and lose the real goal, boundaries, and current state.
- Assistant proposals get misread as user-approved decisions.
- Handoffs lose track of superseded routes, accepted risks, and the true next action.

### How it works

1. Original sources preserve facts; the timeline records origins, decisions and their known reasons, results and sources in two or three sentences; the handoff is a current bookmark.
2. An ordinary fresh conversation reads the current handoff and starts the user's work.
3. When something is missing or contradictory, the AI follows targeted references instead of loading all history.
4. The AI records decisions and milestones during work, reconciles the whole conversation at closeout, and safely commits attributable changes without disturbing other work. The user does not administer the memory system.

New projects create records directly in that project. Old projects are reactivated from a fresh conversation in their own workspace, then choose the entry point and preserved scope from local evidence instead of being batch-migrated from elsewhere.

### New projects, old projects, and audits

- New projects create the manifest, rules block, timeline, and handoff directly.
- Old projects reactivate from a fresh conversation in their own workspace, then choose the entry point and preserved scope from local evidence; do not batch-migrate or auto-unify them from elsewhere.
- Daily continuation reads only the current handoff and expands through targeted lookup when needed.
- First-time reconstruction, full-history audits, and multi-round drift studies are special verification work.
- Manifest states are historical labels, not a router that turns ordinary conversations into exams.

### 30-second quick start (Codex)

1. Put `skills/maintain-project-continuity` in your Codex skills directory.
2. Register `.codex/project-continuity.json` inside the target project.
3. Insert the managed continuity block into the target project's `AGENTS.md`.
4. Run the validation script and confirm the project record structure is complete.

Validator output uses `output_schema_version: 1` and reports structure only; it does not certify memory, business results, or user experience.

Example:

```bash
python skills/maintain-project-continuity/scripts/install_project.py <project-root> --project-name "My Project"
python skills/maintain-project-continuity/scripts/validate_project.py <project-root>
```

### Claude Code quick start

1. Link (or copy) `skills/maintain-project-continuity` into `~/.claude/skills/`.
2. Add one SessionStart hook to `~/.claude/settings.json` that runs the skill's `scripts/claude_session_start.py`; see `references/claude-code.md` for the snippet.
3. New sessions in registered projects then receive the method, the overview and timeline locations, the duty to append timeline entries (origin, decision and known reason, result, source; append, never rewrite), the current handoff and the session id automatically. They are re-injected after compaction with a reminder that the summary is not evidence. The hook is read-only: it never writes records or commits.

### DeepSeek Harness (dsh) quick start

1. From this repository checkout, run `dsh plugin --profile web add ./dsh-plugin`.
2. Run `node node_modules/@skykiss9/dsh-continuity/scripts/install.mjs` to install the skill into the dsh user skill root.
3. Restart `dsh web` (or start a new session); the continuity skill appears in the skill list.

> Windows note: `dsh plugin add` cannot take a local path containing spaces. If your checkout path contains spaces, copy the `dsh-plugin` directory to a space-free path (e.g. `C:\dsh-continuity`) first, then install from there.

### What this repository includes

- The generic skill body
- A generic project-rules block
- Generic templates
- A generic installation script
- A generic validation script
- A redacted example manifest
- Contract tests for the skill
- `dsh-plugin/`: a DeepSeek Harness (dsh) plugin bundle

### What this repository does not include

- Any real project's overview, timeline, or current handoff
- Real conversation archives
- User data, business data, secrets, accounts, or remote-environment details
- Private decision records tied to a specific project

### Core method

1. Original sources prove facts.
2. The timeline preserves origins, important decisions and their known reasons, results and direct sources; later changes append rather than rewrite history.
3. The handoff keeps the goal, relevant effective decisions, current position, verification limits and next authorized action, without accumulating history.
4. Git preserves attributable changes; an unsafe commit leaves an explicit remainder and disposition, not a falsely clean workspace or an automatic push.

### The most important rules

- New projects are recorded directly; old projects are reactivated from their own workspace before choosing entry point and preserved scope.
- Ordinary starts read only the current handoff, not the full timeline or source history.
- The user works and decides normally; the AI owns lookup, maintenance, and write-back.
- Full history is read only for first-time reconstruction, an explicit audit, or a conflict that targeted lookup cannot resolve.
- Validation scripts check structure only; they do not certify memory, business results, or user experience.
- Project facts must come from the project's own registered records, not from global memory, old tasks, or outside material.

### Repository layout

- `skills/maintain-project-continuity/`: the skill itself
- `skills/maintain-project-continuity/assets/`: rule block and templates
- `skills/maintain-project-continuity/references/`: method notes
- `skills/maintain-project-continuity/scripts/`: install and validation scripts
- `skills/maintain-project-continuity/tests/`: contract tests
- `dsh-plugin/`: DeepSeek Harness (dsh) plugin bundle

### Public naming

This public repository uses the display name **AI Long-Term Memory (AI长期记忆)**, for Codex, Claude Code and DeepSeek Harness (dsh).  
For compatibility with existing triggers, the internal technical skill name remains `maintain-project-continuity`.
