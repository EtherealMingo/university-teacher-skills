# 研究智能体编排

何时阅读本文件：创建新课程时（Tier 1 主动调研），或用户求助、想要更深入的背景、卡住时（Tier 2 按需调研）。

## Tier 1：主动调研（课程创建）

撰写新课时，如果当前客户端支持后台研究智能体，就使用它们；
否则在定稿课程前内联完成调研。课程大纲可以先写出来，
待调研完成后再充实内容。

### 派发协议

识别主题类别并使用相应的调研路径：

**编程语言或框架：**

Claude Code 风格的后台任务示例：
```
Agent(subagent_type="general-purpose", run_in_background=true, prompt="
  Use the context7 plugin to research [specific concept].
  1. Resolve the library ID for [language/framework]
  2. Query docs for [concept being taught]
  3. Return: current API signatures, best practices, common patterns, gotchas
  4. Note any recent changes or deprecations
")
```

**NotebookLM notebook 覆盖的主题：**

Claude Code 风格的后台任务示例：
```
Agent(subagent_type="nlm-researcher", run_in_background=true, prompt="
  Query NotebookLM for [concept].
  Mode: answer
  Look in notebooks tagged with [relevant category].
  Return: authoritative content with source citations.
")
```

**科学领域（由 sciagent-skills 插件覆盖）：**

当主题属于科学领域时 —— 生物信息学、化学信息学、生物统计、
蛋白质组学、基因组学、药物发现、科学计算、细胞生物学、实验室自动化或
科学写作 —— 检查是否存在匹配的 sciagent-skills 技能。这些技能提供精选
工作流、参数表和经过验证的代码，远比通用网络结果可靠。

检测方法：将主题与 sciagent 领域关键词比对：

| 领域 | 关键词（任一匹配） |
|---|---|
| 基因组学 / 生物信息学 | RNA-seq、ChIP-seq、GWAS、single-cell、scRNA-seq、variant calling、differential expression、genome assembly、sequence alignment、FASTQ、BAM、VCF、BED、FASTA、gene expression、phylogenetics |
| 结构生物学 / 药物发现 | molecular docking、SMILES、cheminformatics、virtual screening、drug-likeness、protein structure、fingerprint、pharmacogenomics、ADMET、binding affinity |
| 生物统计 | survival analysis、Bayesian modeling、statistical test、regression、mixed effects、hypothesis testing、power analysis、effect size、p-value |
| 细胞生物学 / 成像 | microscopy、flow cytometry、cell segmentation、histopathology、whole-slide image、DICOM、fluorescence |
| 蛋白质组学 | mass spectrometry、protein identification、Western blot、LC-MS、proteomics pipeline |
| 科学计算 | network analysis、graph neural network、optimization、simulation、dimensionality reduction、time series、geospatial |
| 实验室自动化 | liquid handling、Opentrons、protocol、plate reader、LIMS |
| 科学写作 | manuscript、peer review、figure preparation、citation、journal submission |

如果关键词匹配命中，解析出最匹配的 sciagent 技能名。
Claude Code 风格的后台任务示例：

```
Agent(subagent_type="general-purpose", run_in_background=true, prompt="
  Invoke the sciagent-skills skill: /sciagent-skills:[skill-name]
  Extract and return these sections:
  1. Workflow (step-by-step pipeline with code blocks)
  2. Key Parameters table (parameter, default, range, effect)
  3. Common Recipes (self-contained code snippets for variants)
  4. Troubleshooting table (problem, cause, solution)
  5. When to Use section (for routing to alternative tools)
  Do NOT return the full skill verbatim — summarize into lesson-appropriate content.
  Note which sections had the most relevant material for the concept being taught.
")
```

如果主题横跨多个技能（例如一条涉及 STAR、featureCounts 和 DESeq2 的
RNA-seq 流水线），解析出所有匹配的技能并记下流水线顺序。
这将指导多课程单元的规划。

如果没有匹配的 sciagent 技能或插件未安装，退化为通用网络检索。

**通用或新兴主题：**

Claude Code 风格的后台任务示例：
```
Agent(subagent_type="general-purpose", run_in_background=true, prompt="
  Research [concept] using WebSearch and WebFetch.
  Find: current best practices, authoritative references, recent developments.
  Return: summary with source URLs.
")
```

### 吸收调研结果

调研完成后，把结果编织进课程讲义：
- 添加来源署名：“根据 Go 官方文档……”
- 把调研到的示例用作参考材料（而非练习答案）
- 标出模型内置知识与当前文档之间的任何出入

## Tier 2：按需调研（练习期间）

当用户说“我卡住了”、“再深入一点”、“我需要更多背景”，或提出具体技术问题时触发。

### 派发规则

- **API 语法问题** → context7（快、具体、返回确切签名）
- **科学工具/流水线问题** → sciagent-skills（精选工作流、参数指导、故障排查）。先检查工作区配置中的 `sciagent_skills` —— 如果已经挂载了技能，先查它的 Troubleshooting 和 Key Parameters 部分，再考虑生成任何智能体。这是科学领域最快的路径。
- **概念深度** → NLM 研究员或网络调研（更广的背景）
- **“X 在实践中怎么用？”** → 网络调研（文章、博客、示例）
- **源材料问题** → 用 NotebookLM 查询工作区的源 PDF

使用**单一**且精准的调研路径，不要三个都用。让问题匹配正确的工具。

### 呈现结果

- 不要把原始调研输出直接丢给用户
- 把结果综合成对话式的讲解
- 指出可进一步阅读的具体文档/章节
- 不要泄露练习答案 —— 引导理解

## 源材料查询

如果工作区配置了 PDF 源（`.study-config.json` → `sources[]`）：

**NotebookLM 后端：**
```
Agent(subagent_type="nlm-researcher", prompt="
  Query notebook [notebook_id] about [concept].
  Use conversation_id [prev_id] for follow-up context if available.
  Return cited answer.
")
```

这支持苏格拉底式追问 —— 针对教材的多轮问答。

**分块降级（无 NLM）：**
用 Grep 在 `sources/` 目录中搜索相关段落，然后综合。

## 优雅降级

本技能在运行时检测可用工具。如果某个工具缺失，则降级：

| 集成 | 可用时 | 缺失时 | 检测方式 |
|---|---|---|---|
| context7 插件 | 实时框架/库文档 | 模型内置知识 | 检查 `mcp__plugin_context7_context7__resolve-library-id` 工具是否存在 |
| NotebookLM MCP | 基于 notebook 的深度调研 | 跳过，无影响 | 检查 `mcp__notebooklm-mcp__notebook_query` 工具是否存在 |
| sciagent-skills 插件 | 精选科学工作流、参数表、故障排查 | 科学主题退化为网络检索 | 检查可用技能列表中是否出现 `sciagent-skills:*` |
| WebSearch | 最新文章和示例 | 仅训练知识 | 检查 `WebSearch` 工具是否存在 |
| visual-explainer 技能 | 概念的 HTML 图示 | 讲义中的 ASCII 图示 | 检查 visual-explainer 是否在可用技能中 |
| LSP 插件 | 实时代码校验 | 用户手动测试 | 检查对应语言的 LSP 工具 |

工具缺失时绝不报错。静默使用当前最佳可用选项。
