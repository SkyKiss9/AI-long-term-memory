# AI长期记忆 / AI Long-Term Memory

## 中文说明

这是一个给 Codex 长期项目使用的连续性技能。它解决的不是“怎么写一段交接摘要”，而是“当新对话没有旧上下文时，怎样准确恢复项目目标、演变、用户决定、决定理由、边界、当前状态和下一步”。

这个公开版本已经脱敏，只保留通用方法和通用工具，不包含任何真实项目记录、业务数据、历史对话、账号信息、日志、凭证或私有仓库内容。

### 这个仓库包含什么

- 通用技能正文
- 通用项目规则块
- 通用模板
- 通用安装脚本
- 通用校验脚本
- 一个脱敏示例清单
- 技能契约测试

### 这个仓库不包含什么

- 任何真实项目的总览、时间线、当前交接
- 真实对话归档
- 用户数据、业务数据、密钥、账号、远端环境信息
- 针对某个具体项目的私有决策记录

### 核心方法

1. 先找全项目已有来源，而不是凭摘要猜历史。
2. 按时间线记录项目如何变化，重要决定要保留理由和边界。
3. 新对话先恢复真实上下文，再从当前授权位置继续。

### 技能里最关键的几个约束

- 仅“注册”技能，不等于已经可用。
- 真正激活，必须经过来源重建、项目内记录、一次全新冷启动接手、自然写回、第二次全新接手。
- 首次项目相关消息就要恢复上下文，不要等用户反复提醒“继续”。
- 项目事实只能来自该项目自己登记的记录，不能偷偷拿全局记忆、旧任务或外部资料补历史。

### 目录结构

- `skills/maintain-project-continuity/`：技能本体
- `skills/maintain-project-continuity/assets/`：规则块与模板
- `skills/maintain-project-continuity/references/`：方法说明
- `skills/maintain-project-continuity/scripts/`：安装与校验脚本
- `skills/maintain-project-continuity/tests/`：契约测试

### 安装方式

1. 把 `skills/maintain-project-continuity` 放到你的 Codex 技能目录。
2. 在目标项目里登记 `.codex/project-continuity.json`。
3. 把规则块写进目标项目的 `AGENTS.md`。
4. 运行校验脚本，确认项目记录结构完整。

### 公开命名

这个公开仓库使用展示名 **AI长期记忆 / AI Long-Term Memory**。  
为了兼容已有触发方式，技能内部技术名仍然保留为 `maintain-project-continuity`。

---

## English

This is a continuity skill for long-running Codex projects. It does not try to solve “how to write a short handoff summary”. It solves “how a fresh conversation can accurately recover the project goal, evolution, user decisions, decision rationale, boundaries, current state, and next step without inheriting hidden context”.

This public version is fully redacted. It keeps only the generic method and generic tooling. It does not include real project notebooks, business data, conversation archives, account information, logs, credentials, or private repository content.

### What this repository includes

- The generic skill body
- A generic project-rules block
- Generic templates
- A generic installation script
- A generic validation script
- A redacted example manifest
- Contract tests for the skill

### What this repository does not include

- Any real project's overview, timeline, or current handoff
- Real conversation archives
- User data, business data, secrets, accounts, or remote-environment details
- Private decision records tied to a specific project

### Core method

1. Recover the full available source boundary before summarizing history.
2. Rebuild the story in time order, and preserve rationale and boundaries for material decisions.
3. Make every fresh conversation restore the real context first, then continue only from the currently authorized position.

### The most important rules

- Registering the skill does not mean it is activated.
- Activation requires source reconstruction, project-local records, one fresh cold-start recovery, natural write-back, and a second fresh handoff.
- The first project-related user message should trigger context recovery automatically.
- Project facts must come from the project's own registered records, not from global memory, old tasks, or outside material.

### Repository layout

- `skills/maintain-project-continuity/`: the skill itself
- `skills/maintain-project-continuity/assets/`: rule block and templates
- `skills/maintain-project-continuity/references/`: method notes
- `skills/maintain-project-continuity/scripts/`: install and validation scripts
- `skills/maintain-project-continuity/tests/`: contract tests

### Installation

1. Copy `skills/maintain-project-continuity` into your Codex skills directory.
2. Register `.codex/project-continuity.json` inside the target project.
3. Insert the managed continuity block into the target project's `AGENTS.md`.
4. Run the validation script and confirm the project record structure is complete.

### Public naming

This public repository uses the display name **AI长期记忆 / AI Long-Term Memory**.  
For compatibility with existing triggers, the internal technical skill name remains `maintain-project-continuity`.
