---
name: chapter-content-generator
description: "智能教材的章节正文生成：依据学习图谱与概念影响力分数（CIS）为每个概念分配篇幅预算，生成正文、图示、MicroSim 与练习的规格说明。当章节目录已建好、index.md 里已有标题/摘要/概念清单时使用。Triggers: 「生成章节内容」「把这一章的正文写出来」「按大纲写教材」「帮我补全章节正文」「给这本教材生成内容」。"
metadata:
  ibook.version: "1.11"
  ibook.preferred-model: "sonnet"
---

# 章节内容生成器（Chapter Content Generator）

**版本：** 1.11

**1.11 版特性：**
- **精确、目标优先的 MicroSim 规格**——每个规格块现在都写明学习者必须学会什么、证明什么，以及该模拟所需的完整内容，而不是如何构建它。新增结构化字段（`Bloom Level`、`Bloom Verb`、`Learning Objective`、`Evidence of Mastery`、`Misconceptions`、`Instructional Rationale`、`Content`、`Provenance`、`Rules`、`Learner Activity`、`Feedback`、`Starting State`、`Chapter Anchors`）与配套自检，定义见新文件 `references/microsim-specification-rules.md`。布局、像素尺寸、颜色、控件位置和库调用全部留给 microsim-generator。这些规则来自一次 112 个 MicroSim 的批量运行：代理报告了 450 处规格细节缺失，49% 的模拟不得不偏离其规格。
- **批处理工具可解析的 Bloom 字段**——`**Bloom Level:**` 与 `**Bloom Verb:**` 是独立的头部行。此前的内联写法 `Learning objective (Bloom level: X; verb: Y):` 无法被解析，工具把 112 个模拟中的 109 个误标为 "Create"。
- **修复 `content-element-types.md` 中不可能或相互矛盾的指令**——Bloom 清单只列了六层中的四层；Mermaid 边被要求可点击（Mermaid 做不到）；一个图示例要求在嵌入页内滚轮缩放；示例硬编码 500px iframe 占位；一个未闭合的代码块吞掉了 MicroSim 示例。

**1.10 版特性：**
- **吉祥物摆放规则单一来源**——步骤 2.4 原则 4 不再自带第 1 章自我介绍模式和吉祥物频次数字的副本。两者现在都收敛到权威文件 `$BK_HOME/skills/book-installer/references/mascot-placement-rules.md`，本技能库中每个技能都引用它而不再各自复述。这终结了两个摆放表之间每章数量不一致的漂移问题。
- **版本号记入 frontmatter**——以 `metadata.ibook.version` 形式放在 `metadata:` 之下，而不是裸 `version:` 键（严格的打包校验会拒绝后者）。

**1.09 版特性：**
- **破坏性变更：CIS 驱动的阐述预算**——每个概念的字数与非文本元素要求不再是全章统一的目标（"3000-5000 字、4-6 个非文本元素"）。每个概念现在有自己的字数区间和最低非文本元素要求，由其**概念影响力分数**（Concept Impact Score，CIS）计算得出，CIS 读自 `book-chapter-generator` v1.0.0+ 写入每章「覆盖概念」表的 `CIS Score` 列。基础性的高影响力概念得到充分展开（例题、图示）；狭窄的低影响力概念得到高效、简明的处理。见下文「阐述预算」（步骤 2.3b）。要求章节由 `book-chapter-generator` v1.0.0+（表格格式）生成，且 `learning-graph.json` 来自 `learning-graph-generator` v1.06+（含 `node.cis`）。

**0.09 版特性：**
- **第 1 章吉祥物自我介绍**——当项目的 CONTENT-GENERATION-GUIDE.md 定义了教学吉祥物时，第 1 章的第一个吉祥物提示块必须是自我介绍：点名吉祥物，并枚举它将在全书扮演的每个姿态角色。该模式在全库范围内只定义一次，见 `mascot-placement-rules.md`（步骤 2.4 原则 4）。

**0.07 版特性：**
- **教学脚手架**——先定义后展示规则确保术语在图示使用前先解释、代码参数在代码示例前先解释、表格只巩固而不引入概念（见步骤 2.4 原则 3）。
- **顺序执行**——一次只生成一章，避免 token 用量过高。用户可用「use parallel execution」短语覆盖，但技能会警告这将多消耗 38% 的 token。
- **边方向校验**——强制检查，防止依赖关系颠倒的 bug（见步骤 1.3a）。

## 何时使用本技能

适用情形：
- `book-chapter-generator` 技能已创建带 index.md 的章节目录
- 章节 index.md 含有：标题、摘要、覆盖概念清单
- 需要生成详细的章节正文
- 内容需要适配特定阅读水平（初中、高中、大学、研究生）
- 希望有丰富的非文本元素（图示、MicroSim、信息图）

不适用情形：
- 章节结构尚未创建（先用 `book-chapter-generator`）
- 内容已存在、只需编辑（直接用编辑工具）
- 生成其他类型的内容（提示词、术语表等）
- 用户 token 即将耗尽（5 小时窗口内用量超过 95%）

## 执行模式

### 顺序模式（所有场景的默认）

- 任何情况下一次只处理一章，并行模式开销太大
- 等一章彻底完成并记录会话后，再开始下一章
- 每章完成时明确告知用户

### 并行模式（仅在用户要求时）

仅当用户明确要求并行执行时才使用并行模式。
警告用户：并行执行要付出可观的 token 代价。

### 单章模式

适用于：
- 大纲修订后更新某一章
- 批量生成前测试内容格式

## 工作流

### 阶段 1：准备（顺序执行）

本阶段在任何内容生成之前运行一次，读取所有代理都需要的共享上下文。

#### 步骤 1.1：记录开始时间用于日志

```bash
date "+%Y-%m-%d %H:%M:%S" >>logs/ch-{NN}-content-generation.md
```

其中 {NN} 是补零的两位章节号。

为会话报告记录开始时间。

#### 步骤 1.2：声明技能正在运行

通知用户："Chapter Content Generator Skill v1.11 running in [parallel/sequential] mode."

#### 步骤 1.3：读取共享上下文

为所有代理读取并缓存这些文件：

1. **课程描述**（`docs/course-description.md`）
   - 提取目标读者与阅读水平
   - 记录项目 CONTENT-GENERATION-GUIDE.md 中的课程目标与语气指引
   - 识别项目 CONTENT-GENERATION-GUIDE.md 中的吉祥物或叙事元素（如微积分里的 Delta）

2. **学习图谱**（`docs/learning-graph/learning-graph.json` 和/或 `learning-graph.csv`）
   - 加载概念清单及依赖关系
   - 理解概念关系，用于教学排序
   - **计算 `cis_max`** = 全书所有节点中 `cis` 的最大值
     （`max(n.get('cis', 1) for n in data['nodes'])`）。这一个数字
     在整个会话的每一章中复用——阐述预算归一化（步骤 2.3b）永远是
     **全局的**（对整本书），从不是某一章局部的，因为一个概念的重要性是
     全书级别的论断，不是章内局部的。如果每个节点的 `cis` 都是 `1`，
     说明学习图谱早于 `learning-graph-generator` v1.06——应向用户
     报告并建议先重新生成 `learning-graph.json`，而不是静默退回
     统一字数的做法。

   !!! info "学习图谱 = 概念依赖图（一个 DAG）"
       学习图谱是一张**概念依赖图**——有向无环图（DAG），
       每条边表示一个「依赖于」关系。我们采用**依赖方向**
       （边从一个概念指向它所依赖的概念），因为这符合图论中
       拓扑排序、环检测和传递归约的标准算法。

       有些学习管理系统使用**使能图**（enablement graph），边指向相反
       （从前置概念指向被使能的概念）。那个方向对某些教师更直观，
       但对图算法不自然。本项目只使用依赖方向。

   !!! danger "关键：learning-graph.json 中的边方向"
       在 vis-network 的 JSON 格式中，边**从依赖者指向前置概念**
       （依赖方向）。

       - 边 `{from: 5, to: 1}` 表示「生物多样性（5）依赖于生态学（1）」
       - 它不表示「生态学导出生物多样性」（那将是使能方向）

       **构建前置映射的正确做法：**
       ```python
       # 正确：依赖方向 —— from=依赖者，to=前置概念
       prereqs[edge['from']].add(edge['to'])
       ```

       **绝不要用：**
       ```python
       # 错误：不小心转成了使能方向，把所有依赖关系全部颠倒
       prereqs[edge['to']].add(edge['from'])
       ```

       弄错这一点会产生数百个假违规，浪费大量 token 在无效的章节
       设计上。继续之前务必先做步骤 1.3a 的校验。

3. **术语表**（`docs/glossary.md`）
   - 如存在则加载术语定义，保证术语一致
   - 多数情况下术语表在内容生成之后才创建
   - 记录哪些概念已有术语条目

4. **项目 CONTENT-GENERATION-GUIDE.md**（如存在）
   - 加载项目专属指引
   - 记录阅读水平、吉祥物规格、语气要求或特殊格式

5. **章节清单**（扫描 `docs/chapters/` 目录）
   - 枚举所有章节目录
   - 识别哪些章节需要生成内容（有大纲但无正文）

#### 步骤 1.3a：校验边方向（强制）

在使用任何依赖数据之前，先验证边方向正确。这一步防的是章节生成中最常见、代价最高的 bug——一张被颠倒的依赖映射会静默地产出无效的章节顺序。

**校验过程：**

1. 找出基础概念——CSV 中 Dependencies 为空的概念，或 JSON 中前置为零的概念
2. 用 `prereqs[edge['from']].add(edge['to'])` 构建前置映射
3. 检查基础概念在前置映射中条目数为零

```python
import json
from collections import defaultdict

with open('docs/learning-graph/learning-graph.json') as f:
    data = json.load(f)

# 构建 prereqs：from=依赖者，to=前置概念
prereqs = defaultdict(set)
for e in data['edges']:
    prereqs[e['from']].add(e['to'])

# 找出前置为零的概念（基础概念）
all_ids = {n['id'] for n in data['nodes']}
foundational = all_ids - set(prereqs.keys())

print(f"Foundational concepts (no prerequisites): {len(foundational)}")
for fid in sorted(foundational):
    node = next(n for n in data['nodes'] if n['id'] == fid)
    print(f"  {fid}: {node['label']}")

# 合理性检查：基础概念应当是简单的入门概念
# 如果这里出现高阶概念，说明边方向反了
```

**通过标准：**

- 基础概念应是简单的入门术语（如「生态学」「能量」「系统」）
- 如果高阶概念（如「可持续性」「气候变化」「临界点」）出现在基础概念里，说明边方向颠倒了——停下，修复后再继续
- 基础概念数量应当很小（200-400 个概念的图通常为 3-10 个）
- 如果你看到 50+ 个「基础」概念，方向很可能反了

**校验失败时：** 不要继续生成内容。向用户报告问题，并建议用正确的边方向重新运行。

#### 步骤 1.3b：验证章节依赖顺序（强制）

校验边方向之后，验证每一章涉及的概念前置都已在更早的章节中覆盖。这样内容可以引用已有材料而不会出现前向引用。

```python
# 构建 chapter_map：concept_id -> 章节序号
chapter_map = {}
for i, (title, cids) in enumerate(chapters):
    for cid in cids:
        chapter_map[cid] = i

# 检查：每个概念的所有前置必须在本章或更早章节
violations = []
for i, (title, cids) in enumerate(chapters):
    for cid in cids:
        for dep in prereqs.get(cid, set()):
            if dep in chapter_map and chapter_map[dep] > i:
                violations.append(
                    f"  {nodes[cid]['label']}(ch{i+1}) needs "
                    f"{nodes[dep]['label']}(ch{chapter_map[dep]+1})"
                )

if violations:
    print(f"DEPENDENCY VIOLATIONS: {len(violations)}")
    for v in violations:
        print(v)
    print("\nDo NOT generate content until all violations are resolved.")
else:
    print("All dependencies respected. Safe to generate content.")
```

**通过标准：** 零违规。如有违规，必须先修复章节结构再开始生成内容。

#### 步骤 1.4：确定阅读水平

从课程描述中提取年级阅读水平：

**阅读水平指示词：**
- "grade-school"、"grade school"、"grades 1-6"、"elementary school" → 小学
- "junior-high"、"junior high"、"grades 7-9"、"middle school" → 初中
- "senior-high"、"senior high"、"grades 10-12"、"high school" → 高中
- "college"、"undergraduate"、"bachelor" → 大学
- "graduate"、"master"、"masters"、"master's"、"PhD"、"doctoral" → 研究生

**各阅读水平特征：**
- **小学（1-6 年级）：** 很短的句子（10-14 词）、常见词汇、具体例子、频繁视觉辅助
- **初中（7-9 年级）：** 简单句（12-18 词）、常见词汇、具体例子、频繁视觉辅助
- **高中（10-12 年级）：** 混合句式（15-22 词）、带定义的专业词汇、具体与抽象平衡
- **大学：** 学术风格（18-25 词）、专业术语、案例研究、研究背景
- **研究生：** 复杂行文（20-30+ 词）、完整行话、理论深度、研究文献

未指定时默认十年级（高中）。

#### 步骤 1.5：规划章节批次（并行模式）

把章节划分为并行处理的批次：

**批次大小指引：**
- 4-8 章：2 个代理（每个 2-4 章）
- 9-15 章：3-4 个代理（每个 3-4 章）
- 16-24 章：4-6 个代理（每个 4-5 章）
- 25+ 章：5-6 个代理（每个 5-6 章）

**23 章的示例：**
```
代理 1：第 1-4 章（基础）
代理 2：第 5-8 章（核心概念 上）
代理 3：第 9-12 章（核心概念 下）
代理 4：第 13-16 章（应用 上）
代理 5：第 17-20 章（应用 下）
代理 6：第 21-23 章（进阶主题）
```

### 阶段 2：内容生成（并行或顺序）

#### 并行执行

用 Task 工具同时派出多个代理。每个代理收到：

1. **共享上下文**（课程信息、阅读水平、术语表、语气指引）
2. **分配的章节**（具体章节目录）
3. **内容格式模板**（本技能的标准格式）
4. **输出指令**（把内容写入每章的 index.md）

**代理提示词模板：**

```
You are generating educational content for an intelligent textbook. Generate
detailed chapter content for the following chapters.

COURSE CONTEXT:
- Course: [课程名]
- Target audience: [读者]
- Reading level: [水平] - [特征]
- Tone: [课程描述或 CONTENT-GENERATION-GUIDE.md 中的语气指引]

ELABORATION BUDGET (per concept -- computed in Step 2.3b, see below):
[在此插入本章阐述预算表：Concept | CIS | Tier | Target Words | Required Elements]

CONTENT GUIDELINES:
- Follow the per-concept word count and required-element targets in the
  Elaboration Budget table above -- do NOT apply a flat word count to every
  concept regardless of importance
- No more than 4 paragraphs of pure text without a non-text element
- Use diverse element types (lists, tables, diagrams, MicroSims)
- Present concepts in pedagogical order (simple to complex)
- Include LaTeX equations where appropriate (backslash delimiters: `\( \)` for inline, `\[ \]` for display)

SCAFFOLDING (CRITICAL):
- Define every technical term in prose BEFORE it appears in a diagram, code block, or table
- Before code examples, explain what the code does and what key parameters mean in plain language
- Tables must summarize concepts already explained — never introduce new concepts via tables
- Add bridging sentences before complex elements ("Before we examine this diagram, let's define...")

MASCOT (if a mascot is defined in CONTENT-GENERATION-GUIDE.md):
- The pose-by-pose rules, per-chapter counts, and hard limits are defined in the
  project's CONTENT-GENERATION-GUIDE.md (rendered from the canonical
  $BK_HOME/skills/book-installer/references/mascot-placement-rules.md). Read that
  section before placing any mascot admonition and follow it exactly.
- If you are processing CHAPTER 1, the FIRST mascot admonition must be the
  one-time self-introduction described in those rules. See Step 2.4 principle 4.
- For chapters 2 and beyond, open with a normal mascot-welcome admonition that gets straight into chapter-specific content. Do NOT repeat the self-introduction.

NON-TEXT ELEMENTS:
- Markdown lists and tables: embed directly (blank line before)
- Diagrams, MicroSims, infographics: use <details markdown="1"> blocks with #### Diagram: header

SPECIFICATIONS (read references/microsim-specification-rules.md first):
- Use the block template exactly: sim-id, Library, Status, Bloom Level, Bloom Verb and
  Learning Objective as separate bold header lines
- State WHAT the learner must learn and prove: Evidence of Mastery, Misconceptions,
  Instructional Rationale, complete Content (every item written out), Provenance, Rules, Learner Activity,
  Feedback, Starting State, Chapter Anchors
- Do NOT specify HOW to build it: no pixel sizes, layout, control placement, colors,
  breakpoints, library calls or "Implementation:" lines
- Run the self-check in that file on every specification before writing the chapter

CHAPTERS TO PROCESS:
[列出具体章节目录的完整路径]

FOR EACH CHAPTER:
1. Read the chapter index.md file to get title, summary, and the "Concepts
   Covered" table (Concept | CIS Score)
2. Compute the Elaboration Budget for this chapter's concepts (Step 2.3b) --
   the chapter's total word count is the SUM of each concept's target, not
   a flat chapter-wide number. Chapters with more high-CIS concepts will
   naturally run longer than chapters of mostly narrow, low-CIS concepts --
   this is expected and correct, not an error to normalize away.
3. Generate content following each concept's individual word-count range
   and required-element targets from the budget table
4. Verify all concepts from "Concepts Covered" are addressed AND that each
   one's actual word count and element mix roughly matches its budget tier
5. Write the content to docs/chapters/[chapter-dir]/index.md

METADATA FORMAT (add to top of each file). Put double quotes around every value that contains a
colon, and always around title, description and date. An unquoted value with a colon is invalid YAML:
mkdocs then prints the frontmatter at the top of the page and drops its metadata, without failing
`mkdocs build --strict`. Escape any inner double quote as \".
---
title: "[章节标题]"
description: "[简短描述]"
generated_by: claude skill chapter-content-generator
date: "[YYYY-MM-DD HH:MM:SS]"
version: 1.11
---

REPORT when done:
- Chapter name
- Word count (and how it compares to the sum of the concepts' budgeted targets)
- Non-text elements (lists, tables, admonitions, diagrams, MicroSims)
- Concepts covered (X of Y), with any concept whose actual length fell outside its budget's tolerance flagged
```


#### 顺序执行

顺序模式或少于 4 章时，按下面的逐章步骤一次处理一章。

### 阶段 2 逐章步骤（代理或顺序模式共用）

#### 步骤 2.1：确认章节文件存在

确认章节文件存在且含必需元素。

**预期输入格式：**
- 章节名："01-intro-to-itil-and-config-mgmt" 或 "Chapter 1"
- 完整路径："/docs/chapters/01-intro-to-itil-and-config-mgmt/index.md"
- 相对路径："chapters/01-intro-to-itil-and-config-mgmt/index.md"

**章节目录结构：**
```
/docs/chapters/NN-lowercase-name/index.md
```

其中：
- `NN` = 补零的两位章节号（如 "01"、"07"、"12"）
- `lowercase-name` = URL 友好的小写连字符名，无空格

**启动并行代理：**
仅在用户要求并行执行时进行。

在**同一条消息**里发起多次 Task 工具调用以并行运行：

```markdown
[调用 Task 工具 代理 1：第 1-4 章]
[调用 Task 工具 代理 2：第 5-8 章]
[调用 Task 工具 代理 3：第 9-12 章]
[调用 Task 工具 代理 4：第 13-16 章]
[调用 Task 工具 代理 5：第 17-20 章]
[调用 Task 工具 代理 6：第 21-23 章]
```

**重要：** 所有 Task 调用必须在同一条消息中才能并行执行。分开发送会退化为顺序执行。

#### 步骤 2.2：核对章节大纲

打开章节文件，检查必需元素。

**必需元素：**

1. 一级标题中的**标题**（# Title）
2. 二级标题中的**摘要**（## Summary）
3. 二级标题中的**覆盖概念**（## Concepts Covered），含
   `Concept | CIS Score` 的 Markdown 表格（由 `book-chapter-generator`
   v1.0.0+ 写入；见步骤 1.4a）

**动作：**
1. 解析章节 index.md
2. 提取：
   - 章节标题
   - 摘要文本
   - 覆盖概念表：`(概念名, cis 分数)` 对的列表，按表中行序
     （这就是教学顺序）
3. 缺任一元素时跳过该章或请用户补充
4. 如果「覆盖概念」是不带 CIS 分数的编号列表（v1.0.0 之前的
   `book-chapter-generator` 生成的章节），不要编造 CIS 值——
   向用户报告，并建议用当前版 `book-chapter-generator`
   重新生成该章骨架
5. 保存概念/CIS 清单，供阐述预算（步骤 2.3b）与步骤 2.5 核验使用

#### 步骤 2.3：添加元数据

在 index 文件顶部添加元数据：

```markdown
---
title: "Chapter Title"
description: "Short description of title"
generated_by: claude skill chapter-content-generator
date: "YYYY-MM-DD HH:MM:SS"
version: 1.11
---
```

**Frontmatter 规则：** 任何含冒号的 frontmatter 值都要加双引号，
内部的双引号转义为 `\"`。`title`、`description`、`date` 永远加引号：
标题和描述经常含冒号（"Kinematics: Where Is the Hand?"），时间戳
必定含冒号。`description: A chapter on X: how Y works` 这样的无引号写法
是无效 YAML，mkdocs 会把 frontmatter 原样打印在页面顶部并丢弃元数据，
而 `mkdocs build --strict` 并不报错，页面看起来不对却找不到错误指向。
含冒号的**键**（如 `og:image`）不需要引号，只有值需要。写完一章后，
检查 frontmatter 能否解析：

```bash
python3 -c "import sys,yaml; t=open(sys.argv[1]).read(); d=yaml.safe_load(t.split('---')[1]); print(d['title'], '|', d['date'])" docs/chapters/NN-name/index.md
```

这样 `date` 值是字符串而非 YAML 时间戳，正是下游工具所期望的。

#### 步骤 2.3b：计算阐述预算（CIS 驱动）

**本步骤取代旧的「每章 3000-5000 字、4-6 个非文本元素」统一指令。**
内容长度与丰富度不再按章设定，而是**按概念**设定，由每个概念的
概念影响力分数（CIS）驱动：被许多其他概念传递依赖的概念得到充分展开
（例题、图示），狭窄的低影响力概念得到高效、简明的处理。这模仿了
人类领域专家的自然做法——在基础概念上花的解释力气天然多于
边缘词汇。

**1. 计算每个概念的阐述分 `E(c)`：**

```python
import math

# cis_max 在步骤 1.3 已对全书计算过一次——这里直接复用。
# 归一化永远是全局的，从不是本章局部的：概念重要性是全书级别的论断。
# （开发期试过按章局部归一化，已被否决——它会产生退化结果：
# 本章自己最重要的那个概念永远看起来像全书最重要的概念，即使它不是。）
def elaboration_score(cis, cis_max):
    if cis_max <= 1:
        return 0.0
    return math.log(cis + 1) / math.log(cis_max + 1)
```

`E(c)` 落在 `[0, 1]`。用 `log(cis+1)` 而非原始 CIS 很关键：CIS 是
重尾分布（典型的约 200 概念图上，大约一半概念停在最小值 CIS=1），
线性或总体百分位刻度会让整个下半区彼此无法区分，而一两个枢纽概念
占满量程。开发期确切遇到过这个失效模式并已修复——细节见
《Predicting Concept Content Size》论文（定义 4）。

**2. 按 `E(c)` 分档：**

| 档位 | `E(c)` 区间 | 目标字数 | 必备元素 |
|------|--------------|---------------|--------------------|
| A（充分展开） | `>= 0.5` | 500-750 | >=1 个例题，且 >=1 个图示/图表/表格/MicroSim |
| B（标准） | `0.2 <= E(c) < 0.5` | 250-400 | >=1 个例题 |
| C（简明） | `< 0.2` | 120-200 | 一个清晰定义；短例可选，非必需 |

这些切点和区间是经过验证的起点（开发期用两张 CIS 画像相反的
真实章节核对过——一章偏基础、一章偏专门），不是不可变的常数。
如果某章的分档组合对其实际内容不合理（例如所有概念挤在同一档），
生成前先对分档做合理性检查，但不要静默退回全章统一字数。

**3. 构建本章阐述预算表**（每个概念一行，顺序与「覆盖概念」的
教学顺序一致）：

| Concept | CIS | E(c) | Tier | Target Words | Required Elements |
|---------|-----|------|------|---------------|--------------------|
| [概念 1] | 187 | 0.83 | A | 500-750 | 例题 + 图示 |
| [概念 2] | 4 | 0.22 | B | 250-400 | 例题 |
| [概念 3] | 1 | 0.00 | C | 120-200 | 定义 |

本章**总字数等于各概念目标之和**——不单独设定。含多个 A 档概念的
章节天然比大多是 C 档概念的章节长；这种差异正是目的所在，不是要
抹平的 bug（见下文「常见陷阱」）。

**4. 用这张表驱动步骤 2.4。** 生成正文时，遵循每个概念各自的
预算行，而不是把全章长度在所有概念间均分。

#### 步骤 2.4：生成详细章节内容

基于章节大纲、概念清单和阅读水平生成完整的教学内容。

**内容生成原则：**

1. **阅读水平适配：**
   - 采用适配的句子复杂度、词汇和讲解风格
   - 具体指引见 `references/reading-levels.md`

2. **概念排序：**
   - 简单概念在前，复杂概念在后
   - 遵循自然的教学递进
   - 不必拘泥于「覆盖概念」清单的顺序
   - 在已讲解的概念之上继续构建

3. **脚手架——先定义，后展示：**
   - **词汇先于视觉：** 每个图示、代码示例或表格之前，必须先用正文定义它包含的所有专业术语。如果图示里出现 "vectors" 和 "embeddings"，这两个词必须在图示前的段落里解释过。读者绝不应在一个非文本元素里第一次见到某个术语。
   - **代码前要有过渡句：** 任何代码示例之前，用一句大白话说明这段代码做什么、关键参数是什么含义。绝不要先摆代码、把解释留到后文——解释必须在先。示例："The `temperature` parameter controls randomness (0 = deterministic, 1 = creative). The `max_tokens` parameter sets the maximum response length."
   - **正文先行，表格巩固：** 表格用来总结或比较读者已经理解的信息。绝不用表格引入新概念。模式是：(1) 先用正文讲清概念，(2) 再用表格组织或对比它们。如果读者需要从表格单元格反推含义，这张表就出现得太早了。
   - **预告接下来是什么：** 复杂元素之前加导航提示："Before we examine this diagram, let's define two key terms." 或 "The following table summarizes the three approaches we just discussed." 这些一句式的过渡把内容从参考文档变成有引导的学习体验。

4. **吉祥物摆放（当定义了吉祥物时）：**

   哪个姿态承担哪种教学任务、每章各放几个、硬性上限，
   以及一次性的**第 1 章自我介绍**模式，全部定义在本技能库
   所有技能共享的单一文件中：

   ```
   $BK_HOME/skills/book-installer/references/mascot-placement-rules.md
   ```

   每本书在自己的 `CONTENT-GENERATION-GUIDE.md` 里携带一份
   渲染后的规则副本，位于 `<!-- BEGIN mascot-placement-rules -->`
   哨兵标记之间。**放置任何吉祥物提示块之前先读那一节**，
   并严格照做。

   不要在此复述规则，也不要发明项目未定义的姿态角色。
   规则需要变更时，改权威文件，让所有技能一次性跟上。

   有两点值得重复，因为它们最常被遗漏：

   - 第 1 章的自我介绍只发生**一次**，在吉祥物第一次出现时。
     第 2 章起用普通的 `mascot-welcome` 开场，直接进入本章内容。
   - 吉祥物图片放在提示块**正文**里，用 Markdown 图片语法——
     `![alt](path){ class="mascot-admonition-img" }`——绝不用裸 HTML
     `<img>` 标签。

5. **非文本元素：**
   - 遵循阐述预算（步骤 2.3b）中每个概念的必备元素列——
     A 档概念要求一个例题**加**一个图示/图表/表格/MicroSim；
     B 档要求一个例题；C 档只要求一个清晰定义。这些是按概念的
     下限，不是脱离概念构成去凑的全章元素总数。
   - 目标：连续纯文本不超过 4 段就要出现一个非文本元素。
   - 元素类型要多样（不要重复用同一种）。
   - 特别关注交互元素（信息图、MicroSim）。
   - 适当时用 LaTeX 渲染公式，使用反斜杠定界符：
     - 行内数学：`\( equation \)`，句子内部的公式
     - 展示数学：`\[ equation \]`，独立成行的公式
   - 不要用美元符号定界符（`$` 或 `$$`）
   - 公式的正确格式见 references 目录下的 math-equations.md。

**非文本元素类型：**

直接嵌入 Markdown 的元素（不需要 `<details markdown="1">` 块）：

1. **Markdown 列表**（无序或编号）——列表前**必须**空一行
2. **Markdown 表格**——表格前**必须**空一行

需要图示标题和 `<details markdown="1">` 规格块的元素：

3. **图示/示意图**——系统架构、关系、数据流
4. **交互式信息图**——可点击的概念图、渐进展开、悬停显示与术语表一致的定义提示
5. **MicroSim**——带交互控件的 p5.js 模拟
6. **图表**——带定量数据的柱状、折线、饼图
7. **时间线**——历史演进、顺序事件
8. **地图**——带移动箭头的地理分布
9. **工作流图**——带悬停文字的业务流程
10. **图数据模型**——用 vis-network 表达的实体关系
11. **因果回路图**——用于系统思考与因果解释

**MicroSim 复用检查（编写任何新交互元素规格之前必做）：**

dmccreary/* 系列教材中已有数百个 MicroSim，由 search-microsims
目录索引。在为 MicroSim、工作流图、图表、时间线、地图或信息图
编写规格块之前，先查是否已有托管的 MicroSim 在教同一个概念——
如有，用 iframe 直接嵌入，而不要新写一个需要从零生成和调试的规格。

1. **可用性检查（每次会话一次）：** 运行
   `test -x /Users/dan/Documents/ws/search-microsims/.venv-embeddings/bin/python && test -f /Users/dan/Documents/ws/search-microsims/data/microsims-embeddings.json && echo AVAILABLE`
   如果没有打印 `AVAILABLE`，整个会话跳过本复用步骤，
   完全按下方描述生成规格。优雅降级——绝不让章节生成阻塞在
   检索服务上。
2. **为该元素起草 WHAT 查询**，用嵌入查询格式：
   `Title: <暂定标题> | Topic: <概念> | Subjects: <学科领域> | Grade Level: <水平> | Learning Objectives: <带 Bloom 动词的目标>`
3. **运行复用检索：**
   ```
   /Users/dan/Documents/ws/search-microsims/.venv-embeddings/bin/python \
     /Users/dan/Documents/ws/search-microsims/src/find-similar-templates/find-similar-templates.py \
     --mode reuse --query "<WHAT query>" --top 3 --json --quiet
   ```
   命令报错或超过约 60 秒时，本会话剩余部分退回正常规格生成。
4. **按首个结果的 `recommendation` 字段决策：**
   - `reuse`（WHAT 分数 ≥ 0.75）：输出**复用块**（见下）替代规格。
     先 sanity-check 候选的 `grade_level` 和 `subject` 是否适合本书；
     明显不合适时（如中学教材里混入研究生级模拟）按 `template` 处理。
     如果 `docs/sims/<sim-id>/` 在本书本地已存在，用相对 iframe
     嵌入本地模拟。
   - `template`（0.60 ≤ WHAT 分数 < 0.75）：正常写规格，并在 details
     块里加一行：`**Template:** <首个匹配的 github_url><br/>`，
     让 microsim-generator 以现有模拟代码为起点。
   - `generate`（WHAT 分数 < 0.60）：照常写新规格。
5. **在章节生成小结中记录复用决策**：复用 n 个、模板 n 个、
   新写规格 n 个。

**复用块结构**（复用时替代规格块）：

```markdown
#### Diagram: [现有 MicroSim 的标题]

<iframe src="[检索结果的 fullscreen_url]" width="100%" height="500px" scrolling="no"></iframe>

[Run the [Title] MicroSim fullscreen]([fullscreen_url]){ .md-button }

<details markdown="1">
<summary>[Title] (reused MicroSim)</summary>
Type: [element-type]
**sim-id:** [来源仓库中的 sim 目录名]<br/>
**Library:** [检索结果中的框架]<br/>
**Status:** Reused<br/>
**Source:** [检索结果的 live_url]<br/>
**Source Repo:** [检索结果的 github_url]<br/>
**Bloom Level:** [Remember | Understand | Apply | Analyze | Evaluate | Create]<br/>
**Bloom Verb:** [该层级动词表中的一个动词]<br/>
**Learning Objective:** The learner will [verb] [the objective as used in this chapter].

Reused from the MicroSim catalog (WHAT match score [what_score]).
</details>
```

`**Status:** Reused` 字段的作用是让下游批处理工具不再尝试
搭建或实现该模拟：`generate-todo.py` 把复用规格排除在 TODO.md
之外，`extract-sim-specs.py` 将其记为已完成。`Reused` 是终态——
复用的模拟不再走 `specified → scaffolded → implemented →
validated → deployed` 生命周期；它们在来源仓库中早已部署。

对每个新的 `<details markdown="1">` 规格，**先读
`references/microsim-specification-rules.md`** 并严格使用其块模板：

```markdown
#### Diagram: [标题式命名]

<details markdown="1">
<summary>[标题式命名]</summary>
Type: [microsim | chart | diagram | infographic | timeline | map | workflow | graph-model | causal-loop]
**sim-id:** [kebab-case-directory-name]<br/>
**Library:** [p5.js | Chart.js | Plotly | Mermaid | vis-network | vis-timeline | Leaflet | venn.js | html]<br/>
**Status:** Specified<br/>
**Bloom Level:** [Remember | Understand | Apply | Analyze | Evaluate | Create]<br/>
**Bloom Verb:** [references/blooms-taxonomy.md 中该层级动词表的一个动词]<br/>
**Learning Objective:** The learner will [verb] [specific content] [condition or criterion].

**Prerequisites:** [学习者需要的术语；每个都已在本块上方的正文中定义]

**Evidence of Mastery:** [能证明该动词的学习者行为，以及判定对错的规则]

**Misconceptions:** [该模拟应暴露并纠正的错误观念，或 "none"]

**Instructional Rationale:** [为什么这类活动能在该 Bloom 层级产出该证据]

**Content:** [学习者看到的每一个条目、数值、定义和标签，全部完整写出]

**Provenance:** [章节小节、文件路径或 URL、带种子的合成数据、或示例数据]

**Rules:** [公式、用 >= 或 > 表达的阈值、以 min/max/step/default/unit 表达的区间、并列裁决、边界情况]

**Learner Activity:** [编号步骤：学习者做什么、什么发生变化、应注意什么]

**Feedback:** [题目、顺序、尝试次数、判对规则、答对与答错的提示语、何时揭示答案]

**Starting State:** [学习者最先看到什么、它提出什么问题]

**Chapter Anchors:** [章节正文对该模拟陈述过的每个数字、名称和论断，或 "none"]
</details>
```

新规格不要加 iframe。模拟构建完成后，microsim-generator 会以
正确的高度插入它。

六行头部由批处理工具（`extract-sim-specs.py`、
`create-microsim-todo-json-files.py`、`generate-sim-scaffold.py`）解析：

- **sim-id**——kebab-case 目录名（如 `angle-type-explorer`），
  用于 `docs/sims/<sim-id>/`
- **Library**——从清单中取一个值；决定生成器路线和 CDN。
  "HTML and CSS" 这类自由文本无法识别，会退回 p5.js
- **Status**——新规格用 `Specified`；复用检查命中已有 MicroSim
  时用 `Reused`（批处理工具跳过的终态）
- **Bloom Level** 与 **Bloom Verb**——独立行、裸值
  （写 `Analyze`，不要写 `Analyze (L4)`）
- **Learning Objective**——一句话，后接空行

`<details markdown="1">` 块内的任何文本都不要缩进。块内换行
不要带任何前导空格或制表符。

务必在 details 之前放带 `#### Diagram:` 前缀的四级标题。这是
**强制要求**！

**规格要求**（完整规则、示例与自检见 `references/microsim-specification-rules.md`）：

- **目标在先。** 一个可测量的目标，配一个 Bloom 动词。
  Evidence of Mastery 要点名一个 Learner Activity 真正支持的行为，
  以及判定对错的规则。
- **内容完整。** 学习者看到的每个条目都要写出。绝不要
  「例如」「诸如」「等等」或「12 张卡片为一组」然后只给四张。
  学习者要分类或作答的任何内容，给出正确答案和一句理由——
  这就是反馈。
- **内容有出处。** 每个事实性数值都点名来源：章节小节、文件
  路径或 URL、带种子的合成数据、或示例数据。模拟必须标注合成
  与示例数据。绝不要把真实世界的事实（坐标、日期、统计数字）
  留给生成器去编。
- **规则而非描述。** 阈值用 `>=` 或 `>`，每个可调量都有
  min/max/step/default/unit，默认值落在步进网格上。
- **与章节正文一致。** 正文陈述过的关于该模拟的每个数字，
  都在 Chapter Anchors 下原样出现。
- **不写构建指令。** 像素尺寸、画布高度、布局、控件位置、
  断点、颜色、字体、库调用和 `Implementation:` 行都留给
  microsim-generator。例外：本身就是教学内容的视觉属性。
- 各元素类型适合做什么，见 `references/content-element-types.md`。

**内容结构：**

1. 以衔接章节摘要的引入段开头
2. 按教学顺序（由简到繁）呈现概念
3. 非文本元素自然地贯穿全文
4. 频繁使用 Markdown 列表与表格（前面空一行）
5. 复杂的视觉/交互元素用 `<details markdown="1">` 块
6. 每个 `details` 块前放四级标题
   ```#### Diagram: [图示名]```
7. 以小结或要点回顾收尾

**交互元素强调：**

**关键：每个图示、图表、信息图、MicroSim、时间线、地图、工作流
和图模型都必须是可交互的。** 绝不要规格一张不给学习者任何反馈的
静态图。最低要求：每个视觉元素至少支持以下之一——可点击的
节点/区域/柱条（点击弹出信息框）、可悬停元素（显示提示）、
或可改变渲染结果的控件。Mermaid 图仅在每个节点都有 `click`
指令、能弹出定义或解释信息框时才可接受——没有点击处理的纯
Mermaid 图就是静态图，禁止使用。如果候选图示达不到这个门槛，
重新设计为 MicroSim、交互式信息图或可点击 Mermaid 图——
或者砍掉。完整规格见 `references/content-element-types.md`
「CRITICAL RULE: Every Visual Element Must Be Interactive」。

- 优先选择能够支持以下能力的 MicroSim 与信息图：
  - 学生交互追踪
  - 进度衡量
  - 个性化内容推荐
- 每个交互元素恰好有一个 **Learning Objective**，其
  **Bloom Level** 与 **Bloom Verb** 各占一行头部（见上方模板）
- 层级选自 2001 版布鲁姆分类学：
   - **记忆（Remembering）：** 回忆事实、术语、基本概念和答案，不一定理解其含义。
   - **理解（Understanding）：** 解释思想或概念，通过总结或改写信息展示理解。
   - **应用（Applying）：** 在新的或不熟悉的情境中使用已获得的知识解决问题。
   - **分析（Analyzing）：** 把信息拆解为部分，理解其结构与关系，并作比较。
   - **评价（Evaluating）：** 依据既定准则或标准对信息作判断，需要批判性思维与论证。
   - **创造（Creating）：** 通过组合元素形成新颖整体或方案，产出新的或原创的作品。
- 各层级的行为动词表与详细的出题指引，读权威参考
  `references/blooms-taxonomy.md`（faq-generator 与 quiz-generator 同用）。

#### 步骤 2.5：核验完整性

生成章节内容后，核验所有概念均已覆盖。

**核验过程：**
1. 通读生成的内容
2. 检查「覆盖概念」清单中的每个概念都出现在内容里
3. 建一张清单标明哪些概念已覆盖
4. 如有概念缺失：
   - 补写覆盖这些概念的内容
   - 自然地融入现有结构
5. 用完整的生成内容更新章节 index.md
6. **务必确认**内容已写入章节 index.md。做一次字数统计，
   确保**全部**内容都在、且 TODO 占位符已移除。
7. 对本章每个规格块运行 `references/microsim-specification-rules.md`
   中的**自检**，并修复每一项失败。至少逐块确认：
   - Bloom Level、Bloom Verb、Learning Objective 三行齐全且一致
   - Evidence of Mastery 用所描述的 Learner Activity 确实做得到
   - 规格中每个数量都与 Content 列出的条目对得上
   - 每个数字都与章节正文一致
   - 块内没有像素尺寸、布局、颜色或 `Implementation:` 行

**动作：**
- 用生成的内容替换 "TODO: Generate Chapter Content" 占位符
- 保留已有标题、摘要、概念清单和前置知识小节
- 新内容加在前置知识小节之后

### 阶段 3：汇总（顺序执行，在并行代理全部完成后）

所有并行代理完成后汇总结果。

#### 步骤 3.1：收集各代理结果

等所有 Task 代理完成。从每个代理收集：
- 创建/更新的章节文件清单
- 逐章统计（字数、非文本元素、概念覆盖）
- 遇到的任何错误或问题

#### 步骤 3.2：生成汇总报告

创建全部内容生成的汇总：

```markdown
# Chapter Content Generation Report

Generated: YYYY-MM-DD
Execution Mode: Parallel (6 agents)
Wall-clock Time: X minutes Y seconds

## Overall Statistics

- **Total Chapters:** 23
- **Total Words:** ~100,000
- **Avg Words per Chapter:** ~4,350
- **Total Non-text Elements:** ~115

## Execution Summary (Parallel Mode)

| Agent | Chapters | Words | Elements | Time |
|-------|----------|-------|----------|------|
| Agent 1 | 1-4 | 17,200 | 20 | 3m 15s |
| Agent 2 | 5-8 | 18,100 | 22 | 3m 42s |
| Agent 3 | 9-12 | 17,800 | 19 | 3m 28s |
| Agent 4 | 13-16 | 18,500 | 21 | 3m 51s |
| Agent 5 | 17-20 | 17,900 | 18 | 3m 33s |
| Agent 6 | 21-23 | 13,200 | 15 | 2m 45s |

## Per-Chapter Summary

| Chapter | Words | Lists | Tables | Diagrams | MicroSims | Concepts |
|---------|-------|-------|--------|----------|-----------|----------|
| 1. Foundations | 4,200 | 6 | 3 | 2 | 1 | 15/15 ✓ |
| 2. Limits | 4,500 | 5 | 2 | 3 | 2 | 14/14 ✓ |
| ... | ... | ... | ... | ... | ... | ... |
```

#### 步骤 3.3：记录结束时间并写会话日志

记录结束时间：

```bash
date "+%Y-%m-%d %H:%M:%S"
```

将会话信息导出到 `logs/chapter-content-generator-YYYY-MM-DD.md`：

```markdown
# Chapter Content Generator Session Log

**Skill Version:** 1.11
**Date:** YYYY-MM-DD
**Execution Mode:** Parallel (6 agents)

## Timing

| Metric | Value |
|--------|-------|
| Start Time | YYYY-MM-DD HH:MM:SS |
| End Time | YYYY-MM-DD HH:MM:SS |
| Elapsed Time | X minutes Y seconds |

## Token Usage

| Phase | Estimated Tokens |
|-------|------------------|
| Setup (shared context) | ~20,000 |
| Agent 1 (Ch 1-4) | ~80,000 |
| Agent 2 (Ch 5-8) | ~80,000 |
| ... | ... |
| Aggregation | ~5,000 |
| **Total** | ~500,000 |

## Results

- Total chapters: N
- Total words: ~X
- All chapters written successfully: Yes/No

## Files Created/Updated

[列出所有章节 index.md 文件]
```

#### 步骤 3.4：通知用户

通知用户：

"Chapter Content Generator v1.11 complete!

- **Mode:** Parallel (6 agents)
- **Elapsed time:** X minutes Y seconds
- **Chapters processed:** 23
- **Total words:** ~100,000
- **Non-text elements:** ~115

All chapter content has been written to their respective index.md files.

Session logged to `logs/chapter-content-generator-YYYY-MM-DD.md`"

## 资源

本技能附带以下参考文件，提供内容生成的详细指引：

### references/content-element-types.md

全部非文本元素类型（上文 3-11）的完整规格。包括：
- 何时使用各元素类型
- 规格所需的信息
- 实现途径
- `<details markdown="1">` 块格式的示例规格
- 每个 `details` 元素前放四级 Diagram 标题

```markdown
#### Diagram: [图示名]
```

生成内容时加载本参考，确保图示、MicroSim、信息图、图表、
时间线、地图、工作流和图模型的规格正确。

### references/microsim-specification-rules.md

编写精确规格块的规则。包括：
- 带六行机器可读头部的块模板
- 规则 R1–R14，每个字段一条，各附其防止的失效与正误示例
- 什么该留给 microsim-generator（布局、尺寸、颜色、库调用）
- Type/Library 对照表
- 每章完成前对每个块运行的自检
- 一个完整示例

编写任何 `<details markdown="1">` 规格之前加载本参考。

### references/reading-levels.md

内容适配不同阅读水平的详细指引。包括：
- 句子结构与长度指引
- 词汇选择
- 讲解风格
- 示例复杂度
- 假定背景知识
- 各水平的示例文本

确定如何以适当阅读水平写作时加载本参考。

## 最佳实践

1. **永远先读参考：** 生成内容前加载 `references/content-element-types.md`、
   `references/microsim-specification-rules.md` 与 `references/reading-levels.md`

2. **保持空行：** Markdown 列表和表格前永远空一行（MkDocs 的要求）

3. **教学排序：** 不必受概念清单顺序约束——按最有效的顺序教学

4. **视觉多样：** 混用不同类型的非文本元素，不要反复用同一种

5. **交互优先：** 优先选择能追踪学生参与度的 MicroSim 与信息图

6. **规格精确：** 让每个 `<details markdown="1">` 块把「学习者必须学会
   什么」和「教学所需内容」写完整，生成器永远不必自创内容、规则或
   反馈。「如何构建」留给生成器。见 `references/microsim-specification-rules.md`

7. **概念融合：** 把概念自然地编织在一起，而不是当作孤立主题

8. **深度适配：** 讲解深度匹配阅读水平（初中多脚手架，研究生多理论）

9. **脚手架——阅读体验：** 生成的内容要读起来像有引导的教程，
   而不是参考文档。每个非文本元素（图示、代码块、表格）都应像是
   前面正文的自然收获。自问：「如果学生从上到下线性阅读，到达
   每个元素时，他们具备理解它所需的词汇和上下文吗？」不具备，
   就在元素前补过渡文字。

10. **核验：** 永远检查「覆盖概念」清单中的概念全部出现在生成内容里

11. **风格一致：** 全章保持一致的声音、术语和视觉风格

12. **并行执行：** 处理 4 章以上时，永远用并行模式提效

13. **真实时间戳：** 永远用真实系统时间戳，绝不用合成数据

14. **Emoji 纪律：** 只在 emoji 表达本章所教隐喻时使用。装饰性
    emoji 会与教材吉祥物、加粗定义词汇的模式争夺注意力——
    不要放。按 Mayer 的一致性原则，装饰性视觉即使让学生觉得
    亲切，也会可测量地降低保持率。参与度不等于学习。

15. **吉祥物摆放：** 当项目 CONTENT-GENERATION-GUIDE.md 定义了
    吉祥物时，严格遵循其中渲染的吉祥物摆放规则——姿态选择、
    每章数量、硬上限，以及一次性的第 1 章自我介绍。未定义吉祥物
    则整体跳过。见步骤 2.4 原则 4。

## 常见陷阱

**依赖方向（最高优先级）：**
- ❌ 用 `prereqs[edge['to']].add(edge['from'])` 构建前置映射——这会**颠倒**所有依赖
- ❌ 跳过边方向校验（步骤 1.3a）——颠倒的映射会静默地产出无效章节
- ❌ 存在依赖违规时仍继续生成章节（步骤 1.3b）
- ✅ 永远用 `prereqs[edge['from']].add(edge['to'])`——from=依赖者，to=前置概念
- ✅ 继续之前永远先确认基础概念看起来是对的
- ✅ 生成任何内容之前永远先确认依赖违规为 0

**CIS 驱动的阐述预算（高优先级——v1.09 新增）：**
- ❌ 不管 CIS 分数，对一章中每个概念套统一字数
- ❌ 只用本章概念归一化 `E(c)`，而不用步骤 1.3 算出的全书 `cis_max`——开发期试过，产生退化结果
- ❌ 把章与章之间的字数差异当成要抹平的错误——含多个 A 档概念的章节**本来就应**比大多是 C 档概念的章节长
- ❌ 为了「感觉完整」给 C 档概念硬塞不需要的图示/MicroSim，或者写得顺手时把 A 档概念留成裸定义
- ✅ 每个概念的字数和必备元素来自它的阐述预算行（步骤 2.3b），不是全章平均值
- ✅ `cis_max` 在步骤 1.3 对全书计算一次，每章复用
- ✅ 汇报本章实际字数时，对照预算目标之和，而不是对照 3000-5000 的固定区间

**脚手架（关键——读者体验）：**
- ❌ 图示使用了前文未定义的术语（如 "vectors"、"embeddings"）
- ❌ 代码示例中的参数（如 `temperature`、`max_tokens`）到后面小节才解释
- ❌ 表格引入新概念，而不是总结正文已讲清的概念
- ❌ 复杂元素出现时没有过渡句（"Before we look at this diagram..."）
- ✅ 非文本元素中的每个专业术语都在紧邻的正文中定义过
- ✅ 代码示例前有大白话解释它做什么、参数什么含义
- ✅ 表格只巩固和组织——从不引入
- ✅ 导航提示（"Let's define two terms before examining this diagram"）引导读者完成过渡

**吉祥物使用：**
- ❌ 第 1 章第一个吉祥物提示块跳过自我介绍、直奔本章内容
- ❌ 第 2 章起重复吉祥物自我介绍（它应当只出现一次，在第 1 章）
- ❌ 发明项目 CONTENT-GENERATION-GUIDE.md 未定义的姿态角色
- ❌ 把吉祥物当装饰而非信号，或超过渲染版摆放规则定义的上限
- ✅ 第 1 章第一个吉祥物提示块是自我介绍，列出吉祥物扮演的所有姿态角色
- ✅ 第 2 章起用普通的 mascot-welcome 开场，直奔内容
- ✅ 吉祥物提示块彼此间隔（永不背靠背），是挣来的，不是装饰

**内容质量：**
- ❌ 超过 4 段没有非文本元素
- ❌ 反复使用同一种元素类型
- ❌ 「覆盖概念」清单中有概念缺失
- ❌ 内容对阅读水平而言过难或过易

**MicroSim 规格（高优先级——v1.11 新增）：**
- ❌ 把 Bloom 层级写进目标句里（`Learning objective (Bloom level: X; verb: Y): ...`）——批处理工具无法解析，会把模拟误标为 "Create"
- ❌ 目标动词是 "understand"、"learn"、"know" 或 "explore"，或一个目标揉成两个
- ❌ 只点名内容种类而不供给内容（"twelve cards, for example..."、"three datasets"、"six objectives"）
- ❌ 活动无法证明的目标（五层配置但只有三个选项；声称「四种节点形状」但只定义三种）
- ❌ 测验或检查没有题数、尝试规则、判对规则或反馈文案
- ❌ 阈值写成 "above 0.95" 而不是 `>= 0.95`；区间没有步进或单位；默认值不在步进网格上
- ❌ 规格中的数字与章节正文不一致（规格写 12 种，正文写 13 种）
- ❌ 规定布局、像素尺寸、画布高度、颜色、控件位置、断点或库调用——大多数自相矛盾的规格由此而来
- ❌ 要求 Mermaid 边可点击、Mermaid `<--` 箭头、或嵌入模拟内滚轮缩放
- ❌ Library 字段写自由文本（"HTML and CSS"、"Mermaid with a click directive on every node"）
- ✅ `**Bloom Level:**`、`**Bloom Verb:**`、`**Learning Objective:**` 各自独立成行
- ✅ 内容完整写出，每个条目附正确答案和一句理由
- ✅ 每个事实性数值都有 Provenance；合成与示例数据有标注
- ✅ Evidence of Mastery、Feedback、Chapter Anchors 填写完整，且每个块都跑过自检

**格式：**
- ❌ 列表或表格前缺空行
- ❌ `<details>` 块内内容缩进
- ❌ details 块前缺 `#### Diagram:` 标题
- ❌ 缺闭合 `</details>` 标签
- ❌ 含冒号的 frontmatter 值未加引号（`description: Kinematics: where is the hand?`，或 `date: 2026-10-07 08:49:36`）
- ✅ 含冒号的值一律加双引号；`title`、`description`、`date` 永远加引号

**并行执行：**
- ❌ Task 调用分多条消息发送（会顺序执行）
- ❌ 未等全部代理完成就汇总
- ❌ 忘记汇总所有代理的统计
- ❌ 用合成时间戳代替真实时间戳

## 输出文件汇总

**必需（每章）：**
1. 章节内容：`docs/chapters/[chapter-name]/index.md`

**推荐（汇总）：**
2. `logs/chapter-content-generator-YYYY-MM-DD.md`——带计时的会话日志

**可选：**
3. 带逐章统计的汇总报告

## 示例会话

### 并行模式（默认）

**用户：** "Generate content for all chapters"

**代理（使用本技能）：**

1. 记录开始时间
2. 通知："Chapter Content Generator Skill v1.11 running in parallel mode."
3. 读共享上下文（课程描述、学习图谱、术语表、CONTENT-GENERATION-GUIDE.md）
4. 确定阅读水平（如高中）
5. 扫描章节目录，发现 23 章需要内容
6. 规划批次：6 个代理，每个约 4 章
7. 在**同一条消息**中派出 6 个 Task 代理（并行执行）
8. 等所有代理完成
9. 汇总各代理结果
10. 记录结束时间
11. 写会话日志
12. 汇报："Chapter Content Generator v1.11 complete! Mode: Parallel. Time: 18m 32s. Chapters: 23. Words: ~100,000."

### 顺序模式

**用户：** "Generate content for Chapter 3 only"

**代理（使用本技能）：**

1. 读共享上下文
2. 确认第 3 章文件存在且含必需元素
3. 确定阅读水平
4. 按每个概念的 CIS 分数计算阐述预算（步骤 2.3b）——
   例如 4 个 A 档、6 个 B 档、5 个 C 档，本章目标合计约 4000 字
5. 按各概念自己的预算生成内容，各档必备元素齐全
6. 核验概念全覆盖，且大致落在各自预算字数区间
7. 内容写入章节 index.md
8. 汇报："Generated content for Chapter 3. Words: 4,050 (budget: 3,950). Elements: 7. Concepts: 15/15."

## 示例报告

```
✅ Chapter content generated successfully!

Chapter: 01-intro-to-itil-and-config-mgmt
Reading level: Graduate
Content length: ~3,500 words

Non-text elements:
- 6 markdown lists
- 3 markdown tables
- 2 diagrams (CMDB architecture, ITIL process flow)
- 1 interactive timeline (ITIL evolution)
- 1 MicroSim (Configuration drift simulator)
- 1 workflow diagram (Change management process)

Interactive elements: 2 (timeline, MicroSim)
Skills required: 2 (microsim-p5 for MicroSim, infographic-generator for timeline)

All 20 concepts covered: ✓
```

!!! Note
   admonition 生效需要 mkdocs.yml 启用 admonition 与 pymdownx.details。

---

## 来源与许可

本技能收录自上游仓库 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills)，
2026-10-19 补录（因 `question-writing` 等五件的 `$BK_HOME` 引用指向本技能）。
上游仓库**无 LICENSE 文件**，依法默认保留全部权利；本仓库收录其内容副本**未获授权**，
复用、分发或商用前请先联系原作者取得许可。详见仓库根目录 `THIRD_PARTY_NOTICES.md`。

收录时做过的修改：frontmatter `description` 改写为中文并补充 Triggers；
删除 frontmatter 中上游自称的 `license: CC BY-NC 4.0` 字段（与「仓库无 LICENSE」矛盾）；
正文译为简体中文；代码块、命令、文件路径与模板保持原文。
`references/` 下除 `blooms-taxonomy.md` 外，其余参考文档本批次保留英文原文，后续批次翻译。
