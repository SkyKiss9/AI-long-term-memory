# AI长期记忆 / AI Long-Term Memory

> 脱敏双语版 Codex 长期项目连续性技能  
> A redacted bilingual Codex continuity skill for long-running projects

## 中文说明

这是一个给 Codex 长期项目使用的连续性技能。它解决的不是“怎么写一段交接摘要”，而是“当新对话没有旧上下文时，怎样准确恢复项目目标、演变、用户决定、决定理由、边界、当前状态和下一步”。

这个公开版本已经脱敏，只保留通用方法和通用工具，不包含任何真实项目记录、业务数据、历史对话、账号信息、日志、凭证或私有仓库内容。

### 它解决什么问题

- 新对话只拿到压缩摘要，项目真实目标、边界和当前状态丢失。
- 助手把自己的建议误当成用户已经确认的决定。
- 接手时不知道哪些路线已经被替代、哪些风险已经被接受、下一步到底该做什么。

### 它怎么工作

1. 原始材料保留事实，时间线用一两行记录变化和来源，当前交接只作为书签。
2. 普通新对话只读当前交接，然后直接处理用户的工作。
3. 信息不足或冲突时，AI按引用局部回查；不默认加载完整历史。
4. 有实质变化时由AI自动写回，用户不需要管理记忆系统。

### 日常接续与专项审计

- 日常接续：只读当前交接，必要时局部回查。
- 首次建档、完整历史审计和多轮失真复核：属于专项工作，才读取完整来源。
- 清单里的状态只是历史说明，不能自动把普通对话变成考试。

### 30秒快速开始

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

1. 原始材料证明事实。
2. 时间线只记日期、实质变化和直接来源；理由仅在确有必要时补一句。
3. 当前交接只保留当前位置、边界和下一项已授权工作，不积累历史。

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

### 公开命名

这个公开仓库使用展示名 **AI长期记忆 / AI Long-Term Memory**。  
为了兼容已有触发方式，技能内部技术名仍然保留为 `maintain-project-continuity`。

---

## English

This is a continuity skill for long-running Codex projects. It does not try to solve “how to write a short handoff summary”. It solves “how a fresh conversation can accurately recover the project goal, evolution, user decisions, decision rationale, boundaries, current state, and next step without inheriting hidden context”.

This public version is fully redacted. It keeps only the generic method and generic tooling. It does not include real project notebooks, business data, conversation archives, account information, logs, credentials, or private repository content.

### What problem it solves

- Fresh conversations inherit compressed summaries and lose the real goal, boundaries, and current state.
- Assistant proposals get misread as user-approved decisions.
- Handoffs lose track of superseded routes, accepted risks, and the true next action.

### How it works

1. Original sources preserve facts, the timeline records each material change and source in one or two lines, and the handoff is only a bookmark.
2. An ordinary fresh conversation reads the current handoff and starts the user's work.
3. When something is missing or contradictory, the AI follows targeted references instead of loading all history.
4. The AI writes back material changes automatically; the user does not administer the memory system.

### Daily continuation versus audits

- Daily continuation reads only the current handoff and expands through targeted lookup when needed.
- First-time reconstruction, full-history audits, and multi-round drift studies are special verification work.
- Manifest states are historical labels, not a router that turns ordinary conversations into exams.

### 30-second quick start

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

1. Original sources prove facts.
2. The timeline records only the date, material change, and direct source; add a reason only when it matters.
3. The handoff keeps only the current position, boundary, and next authorized work instead of accumulating history.

### The most important rules

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

### Public naming

This public repository uses the display name **AI长期记忆 / AI Long-Term Memory**.  
For compatibility with existing triggers, the internal technical skill name remains `maintain-project-continuity`.
