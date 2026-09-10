---
name: study-skill
description: "交互式学习导师：基于 FSRS 间隔重复、研究助手与可安全重启的学习工作区。当用户想学习新事物时使用：教教我、我想学习、帮我学、学习 X、创建某主题的课程、某主题的教程、带我入门。也适用于 study init、study start、study status、study review、study break 等命令，以及书籍目录的构建与检索。兼容 Claude Code、Codex、Hermes、Cline、OpenCode 及其他 Agent Skills 兼容客户端，适用于编程、数学、物理、科学、工程等结构化学习场景。Triggers: 教我学 Go 并发；帮我制定一个量子力学的学习计划；我想系统学习 Rust，带练习那种；陪我刷题复习之前学过的内容；帮我用这本 PDF 教材学习操作系统。"
---

# 学习工作区 —— 交互式导师

一个结构化的学习环境：**代码由你来写**，智能体（agent）负责教学、引导与监督。每节课都包含讲义和由你亲自实现的练习，并通过间隔重复（spaced repetition）实现长期记忆。

## 理念

- **由你动手** —— 智能体负责教学和监督，实现由你完成
- **结构化课程** —— 每节课 = 讲义 + 练习 + 复盘
- **间隔重复** —— FSRS 算法在你遗忘之前重新唤起概念
- **研究支撑的内容** —— 课程由实时文档、notebook、网络检索以及 sciagent-skills 领域专长充实
- **ADHD 友好** —— 精力门控（energy gating）、复习量封顶、无愧疚机制、详细的暂停状态
- **Git 追踪进度** —— 所有尝试均被保存，可以放心实验

## 智能体兼容性

本技能遵循开放的 Agent Skills 目录结构：`SKILL.md` 加上可选的
`references/`、`templates/` 和 `scripts/`。持久生效的是学习工作区契约，
而非任何单一智能体客户端的斜杠命令实现。

在新客户端中运行工作流之前，请先阅读：
- `references/agent-adapters.md` —— Claude Code、Codex、Hermes、Cline、OpenCode
  及通用智能体的安装配置。
- `references/workspace-lifecycle.md` —— 所有智能体共享的 init/start/break/resume
  状态契约。

## 安装与快速开始

1. 为你的智能体安装完整的技能目录：

   Claude Code：
   ```bash
   mkdir -p ~/.claude/skills
   cp -R study/ ~/.claude/skills/study/
   ```

   Codex：
   ```bash
   mkdir -p ~/.agents/skills
   cp -R study/ ~/.agents/skills/study/
   ```

   Hermes：
   ```bash
   mkdir -p ~/.hermes/skills
   cp -R study/ ~/.hermes/skills/study/
   ```

2. 构建 FSRS 调度器：
   ```bash
   cd <已安装的-study-技能>/scripts/fsrs
   go build -o fsrs ./cmd/fsrs/
   ```

3. 开始学习：
   ```text
   /study init "Go 并发"
   /study start
   ```

   在 Codex 中，如有需要可显式提及技能：
   ```text
   $study study init "Go 并发"
   ```

### 前置依赖

**必需：**

- **Agent Skills 兼容客户端**，如 Claude Code、Codex、Hermes、Cline 或 OpenCode
- **Go 1.22+** —— 用于构建 FSRS 间隔重复二进制程序
- **Python 3.11+** 与 **uv** —— 用于书籍目录构建（仅在使用 `study catalog` 时需要）

**推荐（增强体验，非必需）：**

| 插件/技能 | 带来的能力 | 安装方式 |
|---|---|---|
| [SciAgent-Skills](https://github.com/jaechang-hits/SciAgent-Skills) | 精选的生物信息学与生命科学技能 —— 领域感知的课程、参数表、故障排查、科学主题的练习校验 | 按该项目当前的智能体专属说明安装 |
| context7 | 课程中引入实时的框架/库文档 | 通过你的智能体的 MCP/插件机制安装 |
| Playwright | 可视化图表的浏览器预览 | 通过你的智能体的 MCP/插件机制安装 |
| [visual-explainer](https://github.com/nicobailon/visual-explainer) | 为课程内容生成自包含的 HTML 图表与可视化 | 按该项目当前的智能体专属说明安装 |

**可选：**

| 插件/MCP | 带来的能力 |
|---|---|
| [NotebookLM MCP](https://github.com/jacob-bd/notebooklm-mcp-cli) | 通过 Google NotebookLM 导入 PDF 教材并进行语义查询（见下文） |
| LSP 插件（gopls、pyright 等） | 练习评审时的实时代码校验 |
| pdfkb-mcp 或 rag-cli | 本地 PDF RAG（NotebookLM 的替代方案） |
| calibre 或 pandoc | 电子书格式转换（epub/mobi → PDF 以便导入） |

#### NotebookLM MCP 配置

NotebookLM MCP 支持免费与付费 Google 账号，不需要 Google Cloud 项目。它使用 Google 账号认证，而非官方公开的 NotebookLM API。

由 [Jacob Ben-David](https://github.com/jacob-bd) 构建。配置当前的统一 CLI/MCP 包：
1. 安装 MCP 服务器：`uv tool install notebooklm-mcp-cli`
2. 认证：`nlm login`（打开浏览器完成一次性 Google 登录）
3. 接入 Claude Code：`nlm setup add claude-code`

> **注意：** NotebookLM MCP 使用未公开的浏览器 API（基于 cookie 的认证），并非 Google 官方 API。它工作稳定，但如果 Google 修改内部接口可能会失效。这就是本技能为源材料准备了降级策略（本地 RAG、分块文本）的原因。

### 优雅降级

本技能会根据可用能力自适应。缺少任何插件都不会崩溃：

| 能力 | 有插件时 | 无插件时 |
|---|---|---|
| 科学领域 | 通过 SciAgent-Skills 提供精选工作流、参数表、故障排查 | 退化为网络检索 |
| 课程调研 | 通过 context7 获取实时文档 | 模型内置知识 |
| 源材料 | 通过 NotebookLM 语义检索 | 对提取的文本做 grep，或跳过 |
| 概念图示 | 通过 visual-explainer 生成 HTML | 课程讲义中的 ASCII 图示 |
| 代码校验 | LSP 实时检查 | 用户手动运行测试 |
| 书籍目录 | 跨书库模糊检索 | 手动指定 `--source` 路径 |

## 命令

### `study init <topic> [--template=<name>] [--source <path>]`

初始化一个新的学习工作区。

**步骤：**

0. 阅读 `references/workspace-lifecycle.md` 了解共享的工作区契约。
1. 将主题清洗为目录名，创建工作区，执行 `git init`
2. **模板解析** —— 阅读 `references/template-resolution.md`：
   - 从主题自动检测语言 → 选择模板与模式（code-as-subject 代码即主题 / code-as-tool 代码即工具）
   - 检测科学领域 → 若已安装插件则挂载匹配的 sciagent-skills
   - 复制模板文件，创建 `lessons/`、`practice/`、`notes/`、`.fsrs/`
3. **询问学习方式**：
   ```
   你希望怎样学习？
   1. 项目驱动 —— 一课一课地构建一个真实作品（我会问你想做什么）
   2. 概念驱动 —— 聚焦的课程配合独立练习（默认）
   3. 挑战驱动 —— 难度递进，最少的手把手指导
   ```
   若选择**项目**：询问想构建什么 → 存为 `end_goal`，创建 `lessons/plan.md` 大纲
   若选择**项目**且挂载了 `sciagent_skills`：以主技能的 Workflow 步骤作为课程计划骨架。每个工作流步骤映射为一节课 —— 如何提取技能内容见 `references/research-agents.md`。
   - 在没有专用提问界面的客户端中，用纯文本提问并等待用户回答。
     除非用户要求非交互式安装，否则不要静默选择默认值。
4. **源材料** —— 若提供了 `--source`：
   - 阅读 `references/research-agents.md` 了解后端选择
   - NotebookLM 可用 → 创建 notebook，将 PDF 添加为源
   - 降级方案 → 通过 pdfplumber 提取文本，保存到 `sources/`
   - 将源信息存入配置
5. **书籍目录** —— 若 `~/.config/study/book-catalog.json` 存在：
   - 在目录中检索主题匹配项
   - 展示最相关的书籍（标题、格式、路径）
   - 询问：“要把这些添加为源材料吗？回复编号、路径，或跳过。”
   - 等待用户回答。除非没有匹配项或用户要求非交互式安装，否则不要跳过此询问。
6. 创建 `.study-config.json`（见下方配置模式），提交，展示欢迎信息

### `study start`

开始或恢复一个学习会话。

**恢复检查 —— 永远最先执行：**

修改 `.study-config.json` 前，先阅读 `references/workspace-lifecycle.md`。

1. 读取 `.study-config.json`
2. 如果 `session_state.phase` 不是 `idle`：
   - 这是被恢复的会话。读取当前课程文件。
   - 告诉用户：“正在恢复 —— 你之前在课程 N《标题》中[正在做 X]”
   - 检查 `session_state.energy`：“你之前剩[一半]电量。现在感觉如何？”
   - 从保存的阶段继续
3. 如果是 `idle`：全新会话，`session_count` 加一

**全新会话流程：**

1. **精力检查**：“开始之前 —— 满电、半电，还是快没电了？”
2. **精力门控**：
   - 满电 → 新课 + 复习热身
   - 半电 → 继续已有练习或仅复习
   - 快没电 → 仅复习（轻量）或建议稍后再来
3. **可选的时间预算**：“你今天有多长时间？（跳过则不限制）”
4. **FSRS 复习热身** —— 阅读 `references/fsrs-spaced-repetition.md`：
   - 将 `<skill-dir>` 解析为包含本 `SKILL.md` 的目录
   - 运行：`FSRS_STORE=.fsrs/cards.json <skill-dir>/scripts/fsrs/fsrs schedule`
   - 若有到期项：最多呈现 3 条作为回忆练习（限时 5 分钟）
   - 若无到期项：直接进入课程
5. **主课程循环**（见下文）

**主循环：**

```
LOOP:
  1. 智能体回合：教学
     - 编写课程讲义（主动调研 —— 阅读 references/research-agents.md）
     - 布置练习
     - 提交讲义：[agent] lesson N: topic
     - 更新 session_state.phase = "teaching"

  2. 用户回合：实现
     - 用户在 practice/lesson-NN/ 中工作
     - 用户可以提问、请求提示，或说“done（完成）”
     - 更新 session_state.phase = "practicing"

  3. 评审与反馈
     - 查看 git diff 检查用户的工作
     - 若挂载了 sciagent 技能：阅读 references/difficulty-adaptation.md 了解校验协议
     - 给出具体的反馈（引用其代码，解释原因）
     - 跟踪指标：review_rounds、hints_requested
     - 更新 session_state.phase = "reviewing"

  4. 完成
     - 当练习通过评审：
       - 添加 FSRS 卡片：FSRS_STORE=.fsrs/cards.json <skill-dir>/scripts/fsrs/fsrs add "lesson-NN" "topic" N
       - 将课程状态更新为 "completed"
       - 检查难度自适应（阅读 references/difficulty-adaptation.md）
       - 询问：下一课、复习，还是休息？

  REPEAT
```

### `study status`

展示进度概览。读取 `.study-config.json` 并借助
`references/workspace-lifecycle.md` 解读 `session_state`。若
visual-explainer 可用，生成 HTML 仪表盘；否则输出文本：

```
学习主题：[topic]（[学习方式]）
难度：[level]
进度：[N] 节课已完成，[M] 条在复习队列

课程：
  1. [标题] ✓
  2. [标题] ✓
  3. [标题] ← 当前
  4. [标题]（计划中）

复习：[N] 条到期 | 下次复习：[日期]
源材料：[N] 本书已挂载
```

### `study review`

独立的复习会话。完整协议见 `references/fsrs-spaced-repetition.md`。不讲新课，只对全部到期项做回忆练习。

### `study add-source <path>`

向当前工作区添加 PDF/电子书。后端选择与导入方式见 `references/research-agents.md`。

### `study catalog build <library-path>`

构建书籍目录：
```bash
cd <skill-dir>/scripts/catalog && uv run study-catalog build <library-path>
```

### `study catalog search <query>`

检索目录：
```bash
cd <skill-dir>/scripts/catalog && uv run study-catalog search "<query>"
```

### `study break`

保存会话状态并干净地退出：
先阅读 `references/workspace-lifecycle.md`。
1. 提交所有未提交的变更
2. 更新 `.study-config.json`：
   - `session_state.phase` = 当前阶段（不要设为 `idle` —— 那会丢失上下文）
   - `session_state.pending_action` = 具体的下一步
   - `session_state.context` = 关于当前进展的简要说明
   - `session_state.energy` = 当前精力水平
3. 将会话小结写入 `notes/session-YYYY-MM-DD.md`
4. 提交：`[session] end session N`

## 课程结构

`lessons/NN-topic.md` 中的每个课程文件：

```markdown
# 第 N 课：主题

## 概念
[清晰的讲解 —— 由研究智能体的调研结果充实]

## 要点
- 要点 1
- 要点 2

## 参考示例（不要照抄！）
[有助于理解概念的小示例]

## 常见陷阱
- 陷阱及其规避方法

## 练习

### 要构建什么
[清晰的描述]

### 要求
1. 要求 1
2. 要求 2

### 成功标准
- [ ] 标准 1
- [ ] 标准 2

### 在哪里工作
在以下目录创建你的实现：`practice/lesson-NN/`
```

## 教学规则

1. **绝不为用户编写实现代码。** 讲义中的小型参考示例（2-5 行）是可以的。练习必须完全由用户实现。
2. **引导，而非代解。** 给提示不给答案。指向概念，不指向代码。用提问引导思考。
3. **反馈要具体。** 引用他们的代码。解释为什么错/好。建议思路，不给确切改法。
4. **鼓励实验。** 弄坏东西也是学习。Git 保障一切安全。

## 用户交互

**呈现新课后：**
```
你想做什么？
1. 阅读课程并开始练习
2. 我对概念还有些疑问
3. 休息一下
```

**提供反馈后：**
```
接下来？
1. 我来修改实现
2. 关于反馈的疑问
3. 我觉得完成了 —— 最终评审？
4. 进入下一课
5. 休息一下
```

**当用户卡住时：**
- 询问具体哪里困惑
- 给提示，不给解法
- 必要时按需生成研究智能体（阅读 `references/research-agents.md`）
- 指向课程讲义或源材料的相关章节

## 可视化增强

当教授的概念适合可视化呈现时，阅读 `references/visual-libraries.md` 选择合适的渲染方案：

- **公式** → KaTeX（Web 原生，CDN）
- **函数图像、相图** → JSXGraph（Web 原生，CDN）
- **3D 曲面** → Plotly.js（Web 原生，CDN）
- **物理仿真** → p5.js + Matter.js（Web 原生，CDN）
- **电路图** → SchemDraw（Python 生成 SVG）
- **分子结构** → Kekule.js（Web 原生）或 RDKit（生成 SVG）
- **星图** → Starplot（Python 生成 SVG）
- **乐谱** → LilyPond（CLI 生成 SVG）

如果客户端支持子智能体或后台任务，可调用 visual-explainer 并在提示词中指明库选择：

```
Agent(subagent_type="general-purpose", prompt="
  Using the visual-explainer skill, create an HTML page showing [concept].
  Use KaTeX for equations and JSXGraph for the function plot.
  Save to practice/lesson-NN/diagrams/
")
```

对于 SVG 生成类任务（电路、分子等），生成一个 Python 脚本，通过 Bash 运行，再把 SVG 嵌入 HTML。

对于挂载了 sciagent-skills 的科学主题，插件的可视化技能（`matplotlib-scientific-plotting`、`plotly-interactive-visualization`、`seaborn-statistical-visualization`）提供领域合适的绘图模式（火山图、UMAP 嵌入、热图、生存曲线）。把相关的 sciagent 可视化技能名传给 visual-explainer 智能体以获得领域专属输出。

如果 visual-explainer 不可用，就在课程讲义中使用 ASCII 图示。可视化只是增强，永远不是依赖项。

## 配置模式（v3）

`.study-config.json`：

```json
{
  "version": 3,
  "topic": "Go Concurrency",
  "template": "go-idiomatic",
  "template_mode": "code-as-subject",
  "approach": "concept",
  "end_goal": null,
  "difficulty": "beginner",
  "difficulty_override": null,
  "next_calibration_at_lesson": 4,
  "mode": "tutorial",
  "created": "2026-04-04T10:00:00Z",
  "sciagent_skills": [],
  "sciagent_primary": null,
  "progress": {
    "current_lesson": 0,
    "lessons_completed": 0,
    "session_count": 0,
    "last_session": null
  },
  "lessons": [],
  "session_state": {
    "phase": "idle",
    "pending_action": null,
    "context": null,
    "energy": null,
    "time_budget_minutes": null
  },
  "sources": [],
  "review": {
    "fsrs_data_path": ".fsrs/cards.json",
    "items_due": 0,
    "last_review": null
  },
  "catalog_path": "~/.config/study/book-catalog.json"
}
```

## Git 约定

- `[agent]` —— 当前智能体撰写的课程讲义、反馈、指导
- `[user]` —— 用户的实现工作
- `[session]` —— 会话开始/结束标记

在智能体与用户之间切换回合前，务必先提交。这能保持
git 历史整洁，并让 `git diff HEAD` 可靠地用于评审用户的工作。

## 工作区结构

```
workspace/
├── .study-config.json
├── .fsrs/cards.json
├── lessons/
│   ├── plan.md              （仅项目驱动方式）
│   ├── 01-intro.md
│   └── 02-next-topic.md
├── practice/
│   ├── lesson-01/
│   └── lesson-02/
├── notes/
│   ├── feedback-2026-04-04.md
│   └── session-2026-04-04.md
├── sources/                  （PDF 分块文本，无 NLM 时使用）
└── [模板文件]                （go.mod、Makefile 等）
```

## 学习方式

- **concept**（默认）—— 聚焦的课程配合独立练习，无贯穿性项目
- **project** —— 朝着一个可用的最终产品构建；每节课推进一点进度
- **challenge** —— 难度递进，讲义最少，练习最多

存于 `.study-config.json` → `approach`。决定练习的生成方式。

## 模式

每个会话内的模式，可在一种学习方式下切换：

- **tutorial**（默认）—— 结构化课程：概念 + 练习
- **practice** —— 只做练习，不学新概念
- **exploration** —— 用户驱动，智能体协助并答疑
- **review** —— 通过 FSRS 重访旧课，查漏补缺

## 停止与恢复

停止/恢复由工作区驱动，而非智能体记忆驱动。权威状态保存在
`.study-config.json`、`lessons/`、`practice/`、`notes/` 和
`.fsrs/cards.json` 中。任何智能体都可以通过阅读
`references/workspace-lifecycle.md`，然后遵循 `session_state.phase`、
`pending_action` 和 `context` 来恢复一个工作区。

这对 Hermes 及其他自带记忆或会话恢复系统的智能体尤其重要：这些系统
有助于恢复聊天上下文，但学习工作区才是事实来源（source of truth）。

## 间隔重复（FSRS）

已完成的课程会变成复习卡片，由 [FSRS-6 算法](https://github.com/open-spaced-repetition/free-spaced-repetition-scheduler)跟踪。系统采用混合复习模型：

- **集成式** —— 到期项在会话开始时自动作为热身出现（最多 3 条，限时 5 分钟）
- **独立式** —— `study review` 用于专门的复习会话

没有连击计数，没有因错过复习而产生的愧疚。算法会静默地重新排期。

## 难度自适应

本技能跟踪练习表现（请求提示次数、评审轮次、回忆评分），并在四个等级间调整课程深度：

```
beginner → intermediate → advanced → expert
```

调整自动进行，并配有定期校准检查，你可以在校准时覆盖。

## 模板

| 模板 | 适用场景 |
|---|---|
| `go-idiomatic` | 学习 Go —— cmd/、internal/、Makefile |
| `go-flat` | 用 Go 做物理/数学 —— 扁平的 main.go |
| `python` | Python 主题或以 Python 为工具 |
| `typescript` | TypeScript/JS 主题 |
| `rust` | Rust 或系统编程 |
| `c` | C 或底层编程 |
| `plain` | 非代码主题（理论、数学、科学） |

自定义模板：在 `~/.config/study/templates/<name>/` 创建。

## ADHD 友好设计

- **精力门控** —— 布置任务前先问电量
- **复习热身封顶** —— 最多 3 条，不搞马拉松式复习
- **详细的暂停状态** —— 精确记录你停在哪里，无缝恢复
- **无愧疚机制** —— 没有连击、没有“你已经 N 天没来”、没有评判
- **时间预算感知** —— 可选的会话时长，据此调整课程节奏

## 项目结构

```
study/
├── SKILL.md                    # 核心编排器
├── references/
│   ├── fsrs-spaced-repetition.md
│   ├── research-agents.md
│   ├── difficulty-adaptation.md
│   ├── template-resolution.md
│   └── visual-libraries.md
├── templates/
│   ├── go-idiomatic/
│   ├── go-flat/
│   ├── python/
│   ├── typescript/
│   ├── rust/
│   ├── c/
│   └── plain/
└── scripts/
    ├── fsrs/                   # Go —— FSRS-6 调度器
    └── catalog/                # Python —— 书籍目录构建工具
```

## 开发

在仓库根目录运行检查：
```bash
make setup
make test
make lint
make typecheck
make coverage
```

Python 目录工具是一个嵌套的 uv 项目，锁文件位于
`scripts/catalog/uv.lock`。Go FSRS 调度器是位于 `scripts/fsrs` 的嵌套 Go 模块。

确定性的生命周期冒烟测试会创建一个临时学习工作区，
写入一节课、添加一张 FSRS 卡片、记录一次暂停状态，并验证另一个
智能体可以凭 `.study-config.json` 恢复会话：

```bash
scripts/e2e/study-lifecycle-smoke.sh
```

## 来源与许可

- 上游仓库：[mordor-forge/study-skill](https://github.com/mordor-forge/study-skill)，MIT 许可证。
- 原文为英文，本包已译为简体中文；代码与配置文件保持原样。
- 上游仓库的 CI 配置（`.github/`、`.pre-commit-config.yaml` 等）未收录。
