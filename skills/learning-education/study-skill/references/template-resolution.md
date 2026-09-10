# 模板解析

何时阅读本文件：处理 `study init`，需要确定为工作区应用哪个模板时。

## 解析顺序

1. **显式标志**：`--template=go-idiomatic` → 直接使用该模板
2. **从主题自动检测**：解析主题字符串中的语言/框架线索
3. **询问用户**：如果有歧义，列出选项
4. **默认**：`plain` 模板

## 自动检测逻辑

### 第 1 步：识别是否提及了编程语言

将主题字符串（不区分大小写）与已知语言比对：

| 模式 | 语言 |
|---|---|
| `go`、`golang` | Go |
| `python`、`py` | Python |
| `typescript`、`ts` | TypeScript |
| `rust` | Rust |
| `c programming`、`c language`、`learn c` | C |

避免误报：“going further” 中的 “go” 不是 Go。要匹配完整单词或
语言专属的限定词（例如 “go concurrency”、“in Go”、“golang”）。

### 第 2 步：检测科学领域（sciagent-skills）

如果安装了 sciagent-skills 插件，检查主题中的科学领域关键词
（领域关键词表见 `references/research-agents.md`）。此步骤独立于语言
检测运行 —— 一个主题可以同时有语言和领域。

如果领域匹配命中：

1. 从插件注册表解析出最匹配的 sciagent 技能名
2. 存入 `.study-config.json` → `sciagent_skills`（技能名数组）
3. 指定一个主技能：`sciagent_primary`（与主题最相关的技能）
4. 如果第 1 步没有检测到语言，默认使用 `python` 模板（大多数科学工具基于 Python）

**示例：**

| 主题 | 语言（第 1 步） | 领域（第 2 步） | 模板 | sciagent_skills |
|---|---|---|---|---|
| “用 Scanpy 做 scRNA-seq 分析” | Python | 基因组学 | `python` | `["scanpy-scrna-seq"]` |
| “分子对接” | 无 → Python | 药物发现 | `python` | `["autodock-vina-docking", "rdkit-cheminformatics"]` |
| “用 PyMC 做贝叶斯建模” | Python | 生物统计 | `python` | `["pymc-bayesian-modeling"]` |
| “RNA-seq 差异表达流水线” | 无 → Python | 基因组学 | `python` | `["star-rna-seq-aligner", "featurecounts-rna-counting", "pydeseq2-differential-expression"]` |
| “Go 并发” | Go | 无 | `go-idiomatic` | `[]` |
| “统计检验选择” | 无 | 生物统计 | `plain` | `["statistical-analysis"]` |

对于多技能主题（例如完整流水线），数组中的技能顺序应遵循
流水线执行顺序。这将指导课程计划的生成 —— 每个工作流步骤可以
映射为一节课。

如果 sciagent-skills 插件未安装，跳过此步骤。`sciagent_skills`
字段默认为 `[]`。

### 第 3 步：确定模板模式

如果检测到了语言，需要在 code-as-subject 与 code-as-tool 之间做选择：

**Code-as-subject 代码即主题**（idiomatic 模板）：主题本身就是学习这门语言。
- “学 Go”、“Go 并发模式”、“Rust 所有权”
- “TypeScript 泛型”、“Python 装饰器”

**Code-as-tool 代码即工具**（扁平模板）：主题把语言当作探索其他事物的手段。
- “用 Go 做物理仿真”、“用 Python 学线性代数”
- “数据结构（用 Rust 实现）”

启发式规则：如果主题以语言名开头，或语言是主要名词，则为
code-as-subject；如果语言出现在“用 / 以 / in / with / using”之后，
或是括号内的补充说明，则为 code-as-tool。

### 第 4 步：选择模板

| 语言 | Code-as-subject | Code-as-tool |
|---|---|---|
| Go | `go-idiomatic` | `go-flat` |
| Python | `python` | `python`（相同 —— Python 结构本来就扁平） |
| TypeScript | `typescript` | `typescript`（相同） |
| Rust | `rust` | `rust`（相同 —— Cargo.toml 总是需要） |
| C | `c` | `c`（相同） |
| 未检测到 | — | `plain` |

只有 Go 区分 idiomatic/扁平两套模板，因为它的项目结构约定
（cmd/、internal/）足够复杂，足以影响学习。

## 模板路径解析

模板按以下顺序搜索：

1. **用户自定义**：`~/.config/study/templates/<name>/`
2. **技能内置**：`<skill-directory>/templates/<name>/`

技能自身目录即包含已加载 `SKILL.md` 的目录。
不同智能体客户端暴露该路径的方式不同；见 `references/agent-adapters.md`。
如果智能体只拿到一个复制后的技能目录路径，直接使用该路径：
```bash
SKILL_DIR=/path/to/study
```

如果用户自定义模板与内置模板同名，用户自定义优先。这让用户
无需修改技能即可覆盖模板。

## 应用模板

`study init` 创建工作区时：

1. 把所选模板的全部文件复制到工作区根目录
2. 运行 `git init` 并提交模板文件
3. 创建标准学习目录：`lessons/`、`practice/`、`notes/`、`.fsrs/`
4. 创建 `.study-config.json`，写入 `template` 和 `template_mode` 字段

在 init 期间**不要**运行 `npm install`、`go mod tidy`、`cargo build`
或任何依赖安装。用户可能还没装工具链 —— 让他们自己处理。

## 随附模板

| 名称 | 模式 | 内容 | 最适合 |
|---|---|---|---|
| `go-idiomatic` | code-as-subject | cmd/、internal/、go.mod、Makefile | 学习 Go 本身 |
| `go-flat` | code-as-tool | main.go、go.mod | 用 Go 做物理/数学 |
| `python` | 两者皆可 | src/、requirements.txt | Python 主题或以 Python 为工具 |
| `typescript` | 两者皆可 | src/、package.json、tsconfig.json | TypeScript 或 JS 主题 |
| `rust` | 两者皆可 | src/main.rs、Cargo.toml | Rust 或系统主题 |
| `c` | 两者皆可 | src/main.c、Makefile、.clang-format | C 或底层主题 |
| `plain` | 不适用 | README.md | 非代码主题（理论、概念） |

## 创建自定义模板

用户可以在 `~/.config/study/templates/<name>/` 创建模板：

1. 创建一个以模板名命名的目录
2. 添加所需的脚手架文件
3. 使用：`study init "我的主题" --template=<name>`

模板就是文件目录 —— 它们会被原样复制到新工作区中。
