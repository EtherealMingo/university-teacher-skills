# 智能体适配器

何时阅读本文件：在 Claude Code 之外安装或运行 study 技能时，
或检查当前智能体客户端中有哪些可选工具可用时。

## 可移植核心

可移植单元是整个技能目录：

```
study/
├── SKILL.md
├── references/
├── templates/
└── scripts/
```

所有客户端都应保留该目录结构。不要只复制 `SKILL.md`；
FSRS 调度器、目录工具、模板与参考文档都是完整工作流所必需的。

每个客户端都必须能够：

1. 在生成的学习工作区中读写文件。
2. 运行 shell 命令：git、FSRS 二进制程序，以及可选的目录工具。
3. 向用户提简短的问题。
4. 严格按照 `references/workspace-lifecycle.md` 的描述持久化
   `.study-config.json`。

子智能体、MCP 工具、浏览器工具和实时文档都是可选的加速器。
如果缺失，就使用本地文件和常规的网络/模型知识继续。

## Claude Code

作为 Claude Code 技能或插件安装，若暴露为斜杠命令则用 `/study ...` 调用。
Claude Code 特有的便利能力可能包括 `Agent(...)`、
`AskUserQuestion`、`WebSearch` 和插件斜杠命令。

本地技能副本的安装方式：
```bash
mkdir -p ~/.claude/skills
cp -R /path/to/study ~/.claude/skills/study
cd ~/.claude/skills/study/scripts/fsrs
go build -o fsrs ./cmd/fsrs/
```

## Codex CLI、IDE 与 App

Codex 在 CLI、IDE 扩展和 App 中都支持 Agent Skills。
仓库级安装：把本目录放到 `.agents/skills/study`；个人级
安装：放到 `~/.agents/skills/study`。Codex 可以用 `$study` 显式调用
技能，或根据 `description` 隐式选择。

推荐提示词：

```text
$study study init "Go 并发"
```

Codex 专属指引：

- 仓库约定写在 `AGENTS.md`；学习工作流写在本技能中。
- `references/agent-adapters.md` 仅用于客户端安装配置，状态流转用
  `references/workspace-lifecycle.md`。
- `<skill-dir>` 要从已加载的技能路径解析，而不是从 `~/.claude`。
- 执行 `study init` 时，用纯文本提出学习方式和目录源材料的问题，
  并等待用户回复。Codex CLI 在这些检查点上不需要特殊的
  `AskUserQuestion` 工具。

## Hermes Agent

Hermes 的技能位于 `~/.hermes/skills/`，具有一流的技能支持与面向恢复的
CLI 行为。安装本技能：

```bash
mkdir -p ~/.hermes/skills
cp -R /path/to/study ~/.hermes/skills/study
cd ~/.hermes/skills/study/scripts/fsrs
go build -o fsrs ./cmd/fsrs/
```

Hermes 专属指引：

- Hermes 会话可以用它自己的会话标志恢复，但学习会话的恢复
  必须仍然从读取工作区 `.study-config.json` 开始。
- 用于定时任务或消息网关场景时，确保任务的 `workdir` 是学习
  工作区，这样 `AGENTS.md`/工作区文件和 `.study-config.json` 才可见。
- 不要依赖 Hermes 的记忆来保存学习状态。记忆可以帮助个性化
  教学，但 `.study-config.json`、`lessons/`、`practice/`、`notes/` 和
  `.fsrs/cards.json` 才是事实来源。

## Cline

Cline 技能在工作区级位于 `.cline/skills/`，全局位于 `~/.cline/skills/`。
复制完整目录并在 Cline 设置中启用 Skills。

```bash
mkdir -p ~/.cline/skills
cp -R /path/to/study ~/.cline/skills/study
```

如果 Cline 将技能暴露为斜杠命令，使用 `/study`；否则按名字让 Cline 使用
`study` 技能。

## OpenCode

OpenCode 在当前版本中原生支持 Agent Skills。把技能目录复制到你的
OpenCode 安装所支持的技能位置，或使用其原生的技能发现机制。较旧的
OpenCode 环境可以使用社区维护的 `opencode-agent-skills` 插件，但优先
使用内置技能支持。

## 通用 Agent Skills 客户端

如果客户端支持开放的 Agent Skills 标准，把完整目录安装到该客户端
发现技能的位置。如果它不直接支持技能，在客户端的项目指引中
加一条说明：

```text
当用户请求学习工作流时，阅读 /path/to/study/SKILL.md 并遵循
其中引用的文件。把 /path/to/study 视为 <skill-dir>。
```

## 可选工具映射

| 能力 | Claude Code | Codex | Hermes | 通用降级 |
|---|---|---|---|---|
| 技能调用 | `/study` 或技能触发 | `$study` 或隐式技能触发 | 技能命令或已加载技能 | 让智能体阅读 `SKILL.md` |
| 持久仓库指引 | `CLAUDE.md`/插件文档 | `AGENTS.md` | `AGENTS.md`、`HERMES.md`、记忆 | 项目说明 |
| 子智能体/后台调研 | `Agent(...)` | 可用时使用子智能体 | Hermes 子智能体/技能 | 内联完成调研 |
| 实时库文档 | context7 MCP/插件 | 若已配置则用 MCP | 若已配置则用 MCP/工具网关 | 官方文档/网络 |
| 源材料 notebook | NotebookLM MCP | 若已配置则用 MCP | 若已配置则用 MCP/工具网关 | 本地 `sources/` grep |
| 浏览器检查 | Playwright 插件/MCP | 浏览器或 Playwright MCP（若已配置） | 浏览器/工具网关 | 跳过或手动 |

绝不要让任何可选集成成为 `study init`、`study start`、
`study break` 或 `study review` 的必需条件。
