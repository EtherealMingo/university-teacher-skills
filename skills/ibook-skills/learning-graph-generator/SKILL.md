---
name: learning-graph-generator
description: 从课程描述生成完整的学习图谱（learning graph），包含 300–600 个概念及其依赖关系、分类法（taxonomy）归类与质量校验报告。当用户想为教学内容创建结构化知识图谱时使用。Triggers: 「帮我把这门课的知识点整理成一张依赖关系图」「为我的教材生成学习图谱」「把课程大纲拆成几百个概念并标出学习先后顺序」「检查一下我的课程描述够不够格生成学习图谱」。
metadata:
  ibook.version: "1.07"
---

# 学习图谱生成器（Learning Graph Generator）

**版本：** 1.07

### 更新日志

- **v1.07** — 版本号现在记录在 SKILL.md frontmatter 的 `metadata.ibook.version` 中。它放在 `metadata:` 之下而不是单独的 `version:` 键，因为严格的打包校验会拒绝六个规范字段之外的任何 frontmatter 键。无行为变化。

- **v1.06** — **破坏性变更：** `csv-to-json.py`（升级到 v1.04）现在为每个节点计算**概念影响力分数（Concept Impact Score，CIS）**，并将其写入 `learning-graph.json` 的 `node.cis` 字段。CIS 是一种类似 PageRank 的递归重要性度量：`CIS(x) = 1 + sum(CIS(d) for d in direct dependents of x)`，用于刻画整本书的理解在多大程度上传递性地建立在某个概念之上——不同于简单的入度（in-degree），入度会低估那些只是间接处于基础地位的概念（例如典型代数课程中的「常数」或「系数」，它们的直接依赖者很少，但传递依赖者很多）。由于图是 DAG，CIS 可以在一趟拓扑排序中精确计算——无需阻尼系数或迭代。下游技能（`book-installer` 的图谱查看器、`book-chapter-generator`、`chapter-content-generator`）现在直接读取该字段，而不再各自重新计算重要性度量。完整推导请参见 schema 的 `nodes[].cis` 字段以及《Predicting Concept Content Size》论文（定义 3、命题 1）。这是对 `learning-graph.json` 输出格式的破坏性变更（属于新增字段，旧的读取方不会出错，但下游技能现在假定它存在）——在运行更新后的 `book-chapter-generator` 或 `chapter-content-generator` 之前，请为任何已有教材重新生成 `learning-graph.json`。
- **v0.06** —（更早历史未以本更新日志格式记录）

你的任务是根据课程描述生成一份完整的高质量学习图谱。
学习图谱是智能教材的基础数据结构，智能教材可以据此推荐学习路径。
学习图谱就像一张概念（Concept）路线图，帮助学生达成学习目标。
学习图谱是一个 DAG（有向无环图）概念图。每条箭头代表一种「学习依赖（Learning Dependency）」关系，暗示学习顺序。
你生成的 markdown 必须兼容 mkdocs 版本的 markdown。请确保在任何列表之前留一个空行。

请认真遵循以下步骤：

## Markdown 生成规则

1. 在任何 markdown 列表之前务必留一个空行。这是 mkdocs markdown 工具的要求。

## Mkdocs 导航规则

每添加一个 markdown 文件（任何扩展名为 `.md` 的文件）后，务必把该文件加入 mkdocs.yml 文件的导航结构中。下面是学习图谱部分的 nav 示例：

```yml
  - Learning Graph:
    - Introduction: learning-graph/index.md
    - Course Description Assessment: learning-graph/course-description-assessment.md
    - Concept Enumeration: learning-graph/list-concepts.md
    - Graph Quality Analysis: learning-graph/graph-quality-analysis.md
    - Concept Taxonomy: learning-graph/concept-taxonomy.md
    - Taxonomy Distribution Report: learning-graph/taxonomy-distribution-report.md
```

## 第 0 步：环境准备

告诉用户他们正在运行的是哪个版本的图谱生成器，并告知上面的版本号。

默认的使用场景是：在 claude code 中运行本技能，工作目录是一本已从 GitHub 检出的智能教材的主目录。
该 git 主目录中应有一个 docs 目录和一个标准的 mkdocs.yml 文件。
如果 `/docs/learning-graph` 目录尚不存在，你需要创建它。
路径相对于 git 主目录。假定 `/docs` 相对于启动 claude 时所在的目录。

`mkdir -p docs/learning-graph; cd docs/learning-graph`

你将把本技能包中的 Python 程序复制到 `/docs/learning-graph` 目录中。
你将在该目录中执行 python。

如果没有看到 `docs` 目录和 `mkdocs.yml` 文件，建议用户从以下位置克隆一本示例教材：

`git clone https://github.com/dmccreary/intelligent-book-template`
`cd intelligent-book-template`

## 第 1 步：课程描述质量评估

在开始本步骤之前，先确认它尚未完成。
方法是检查 `docs/course-description.md` 文件中的 yml 元数据。

yml 元数据示例如下：

```markdown
---
title: Course Description
description: A detailed course description 
quality_score: 95
---
# Course Description
```

如果看到 quality_score 高于 85，你可以告诉用户找到了高于 85 的分数并跳过整个本步骤。告诉他们这是节省 token 的一种方式。

如果质量分数低于 85，则分析 [course-description.md](../course-description.md) 中提供的课程描述，确保其内容足以生成至少 300 个高质量概念：

1. 核实课程是否有标题、先修要求、目标受众、教学目标和预期成果（「学完本课程后，学生将能够……」）。如果缺少这些字段，向用户索取这些信息。
1. 考察所覆盖主题的深度与广度
2. 评估材料是否有足够的颗粒度，能拆出至少 300 个不同的概念
3. 检查主题领域与学习目标的多样性
4. 向用户提供详细反馈：
   - 列出你找到的应含内容
   - 估计能推导出的概念数量
   - 将该概念数量与同类课程比较
   - 说明课程描述在哪些方面写得较好
   - 指出任何缺口或可能着墨不足的领域
   - 建议如何借助 2001 版布鲁姆分类法（布鲁姆教育目标分类：记忆 remember、理解 understand、应用 apply、分析 analyze、评价 evaluate、创造 create）改进成果描述
   - 给出客观的整体质量评估，量表为 1（差）到 100（完美）
   - 建议用户：除非质量分数达到 70 或以上，否则不要继续

使用以下评分细则创建质量分数：

### 2.2 课程描述质量评分体系

使用这套 100 分制评分体系评估课程描述：

| 要素 | 分值 | 标准 |
|---------|--------|----------|
| **标题（Title）** | 5 | 有清晰、描述性的课程标题 |
| **目标受众（Target Audience）** | 5 | 指明了具体受众（例如「大学本科在校生」） |
| **先修要求（Prerequisites）** | 5 | 列出了先修要求，或明确写明「无」 |
| **覆盖的主要主题（Main Topics Covered）** | 10 | 有全面的主题清单（理想为 5–10 个主题） |
| **排除的主题（Topics Excluded）** | 5 | 为「不涵盖的内容」划定了清晰边界 |
| **学习成果引导语（Learning Outcomes Header）** | 5 | 有明确表述：「学完本课程后，学生将能够……」 |
| **记忆层级（Remember Level）** | 10 | 有多条具体的记忆/回忆类成果 |
| **理解层级（Understand Level）** | 10 | 有多条具体的理解/解释类成果 |
| **应用层级（Apply Level）** | 10 | 有多条具体的应用/运用类成果 |
| **分析层级（Analyze Level）** | 10 | 有多条具体的分析/拆解类成果 |
| **评价层级（Evaluate Level）** | 10 | 有多条具体的评价/判断类成果 |
| **创造层级（Create Level）** | 10 | 有多条具体的创造/综合类成果；包含顶点项目（capstone）设想 |
| **描述性背景（Descriptive Context）** | 5 | 有关于课程重要性、相关性或价值的补充背景 |

**评分准则：**
- 要素完整且质量高，给满分
- 要素存在但不完整或含糊，给部分分
- 要素缺失，给 0 分
- 对布鲁姆分类法各层级，要求至少 3 条具体、可操作的成果才给满分

告诉用户他们的得分，并建议他们改进课程描述，直到分数超过 80。

将此报告保存到 [course-description-assessment.md](./course-description-assessment.md)

5. **询问用户是否继续**生成学习图谱

## 第 2 步：生成概念标签

课程描述获批后，从课程内容生成概念标签：

**要求：**
- 每个概念标签必须使用标题式大写（Title Case）
- 最大长度：32 个字符
- 标签应清晰、具体、在教学上站得住脚
- 覆盖课程材料的全部广度
- 概念标签是实体名称，不是疑问句
- 不要在概念标签中使用疑问句。不要写「什么是 Git」，只写「Git」

**概念数量：**

对于简单的书，300 个概念的清单即可。
对于复杂的技术类书籍，最多可以生成 600 个概念。
除非有充分理由且用户批准，否则不要超过 600 个概念。
请记住：概念越多，生成概念依赖关系就越复杂。

!!! note
  由于这些概念标签会用在网络图中，它们不能太长。
  否则图会难以阅读。

**输出：**
- 把编号清单保存到 [concept-list.md](./concept-list.md)
- 格式：markdown 文件中的简单编号列表（1–600）
- 确保每个编号唯一，以便用作 ConceptID
- 告知用户文件已创建
- 告诉用户他们现在应该查看清单并增删概念
- 告诉用户最好在后续步骤之前审阅概念清单

现在请用户花一些时间人工审阅整个概念标签清单。
如果有不合适的概念，现在就应该删除。
如果需要补充更多概念，现在就应该添加。
日后再改内容会耗费大量额外 token。
这是确保教材质量的重要审阅步骤。
请特别注意概念标签的长度以及任何缩略语的质量。

## 第 3 步：生成依赖图

创建一个映射概念间依赖关系的 CSV 文件：

**格式：**
- 文件名：[learning-graph.csv](./learning-graph.csv)
- 列：`ConceptID,ConceptLabel,Dependencies`
- ConceptID：整数（1–600）
- ConceptLabel：与第 2 步完全一致的标签
- Dependencies：以竖线分隔的 ConceptID 列表（例如 "1|3|7"）

**依赖规则：**
- 基础性/先修概念没有依赖（Dependencies 字段为空）
- 其他所有概念必须至少有一个依赖
- 任何概念都不能依赖自身
- 图必须是有向无环图（DAG）——不允许环
- 创建有意义的学习路径，而不仅仅是线性链条
- 仔细斟酌先修关系

**注意：** JSON 文件将在后续步骤（第 7–8 步）中、在把分类法加入 CSV 文件之后创建。完整的 JSON 将包含 metadata、groups、nodes 和 edges 几个部分，并符合 learning-graph-schema.json。

## 第 4 步：学习图谱质量校验

使用本技能中的 Python 程序 analyze-graph.py
对依赖图执行全面质量检查。
它将进行以下检查：

1. **验证 DAG 结构**：确保不存在环
2. **检查自依赖**：任何概念都不应依赖自身
3. **基础概念**：识别依赖数为零的概念
4. **终端节点（terminal nodes）**：识别没有任何概念依赖它们的节点（叶子节点）。这些是正常且符合预期的——不要与孤立节点（orphaned nodes，完全没有任何连接）混淆
5. **不连通的子图**：检查是否所有概念都连在主图上
6. **线性链条**：如果过多概念只依赖紧邻的前一个概念，则标记出来
7. **入度分析**：计算入度（依赖每个概念的概念数量）

Shell 命令 `python analyze-graph.py learning-graph.csv quality-metrics.md`

核实报告已写入 [quality-metrics.md](./quality-metrics.md)

**生成学习图谱质量指标报告：**
- 依赖数为零的概念总数——出向箭头（基础性先修概念）
- 有 1 个及以上依赖的概念总数
- 每个概念的平均依赖数
- 最长依赖链长度
- 没有其他概念依赖的终端（叶子）节点数量
- 不连通子图的数量
- 入度最高的前 10 个概念（被依赖最多的概念）

给用户一个总体质量分，量表为 1（差）到 100（完美）。
如果学习图谱得分不高于 70，建议用户迭代上述流程。

## 第 5 步：创建概念分类法

建立一个用于组织概念的类别分类法（taxonomy）：

**要求：**
- 目标：约 12 个类别（如果出现自然的分组，可以上下浮动 2–3 个）
- 各类别应均匀分配概念
- 避免任何单一类别超过概念总数的 30%
- 使用清晰、描述性的类别名称，采用标题式大写并带空格
- 为每个类别创建 3–5 个字母的缩写（TaxonomyID）
- 注意：稍后将创建该分类法的 JSON 表示，构成学习图谱的 groups 部分

**输出：**
- 把分类法保存到 [concept-taxonomy.md](./concept-taxonomy.md)
- markdown 格式，包含：
  - 类别名称
  - TaxonomyID 缩写（3–5 个大写字母）
  - 简要描述哪些概念属于该类别

## 第 5b 步：创建分类法名称 JSON

**关键步骤**——这一步可防止一个常见 bug：图谱查看器的图例和报告中显示分类法 ID 而不是人类可读的名称。

从 concept-taxonomy.md 中提取「分类法 ID → 人类可读名称」的映射，并保存为 JSON 文件：

**创建文件：** `taxonomy-names.json`

**格式：**
```json
{
  "FOUND": "Foundation Concepts",
  "EDA1": "Exploratory Data Analysis I",
  "EDA2": "Exploratory Data Analysis II",
  "REG": "Regression & Correlation",
  ...
}
```

**规则：**
- 键是 TaxonomyID 缩写（大写，3–5 个字母）
- 值是标题式大写、带空格的人类可读类别名称
- CSV 中用到的每个分类法 ID 都必须有对应名称
- 名称应对学生而言具有描述性、有意义

csv-to-json.py 需要这个文件才能在 learning-graph.json 中生成正确的 `classifierName` 值。没有它，图谱查看器的图例会显示 "EDA1" 这样莫名其妙的 ID，而不是 "Exploratory Data Analysis I"。

---

## 第 6 步：把分类法加入 CSV

更新依赖关系 CSV 文件：

1. 如果现有 CSV 文件还没有 `TaxonomyID` 列，则新增该列
2. 为每个概念分配最匹配的 TaxonomyID
3. 对没有明确类别归属的概念使用 "MISC"
4. 把更新后的文件保存到 [learning-graph.csv](./learning-graph.csv)

你可以把本技能中的 Python 程序 add-taxonomy.py 当作模板
来完成这一替换。

**最终 CSV 列：** `ConceptID,ConceptLabel,Dependencies,TaxonomyID`

## 第 7 步：创建 learning-graph.json 文件的 `metadata` 部分

metadata 部分包含从 course-description.md 文件中提取的、受都柏林核心（Dublin Core）启发的教材字段。学习图谱的 JSON schema 位于本技能内的 learning-graph-schema.json 文件中。

**必填字段：**
- `title`：从课程描述标题中提取
- `description`：从课程描述中提取或概括

**可选但建议的字段：**
- `creator`：作者或机构名称
- `date`：当前日期，YYYY-MM-DD 格式
- `version`：版本号（例如 "1.0"）
- `format`："Learning Graph JSON v1.0"
- `schema`：指向 JSON schema 的 URL
- `license`：许可信息（例如 "CC BY-NC-SA 4.0 DEED"）

metadata 部分示例如下：

```json
"metadata": {
    "title": "Title Text From Course Description",
    "description": "A description of the course in a few sentences.",
    "creator": "Your Name",
    "date": "2025-11-01",
    "version": "1.0",
    "format": "Learning Graph JSON v1.0",
    "schema": "https://raw.githubusercontent.com/dmccreary/learning-graphs/refs/heads/main/src/schema/learning-graph-schema.json",
    "license": "CC BY-NC-SA 4.0 DEED"
  }
```

你可以创建一个包含这些字段的 metadata.json 文件，在第 9 步中传给 csv-to-json.py 程序。

## 第 8 步：创建 JSON 文件的 groups 部分

把分类法类别转换为 JSON 格式，作为 learning-graph.json 文件的 groups 部分。学习图谱的 JSON schema 位于本技能内的 learning-graph-schema.json 文件中。

groups 部分为可视化创建一份带区分颜色的概念类型图例。

**重要：**
- groups 部分使用分类法 ID（例如 "FOUND"、"DEF"）作为键
- 每个组必须有 `classifierName` 字段，其值为**描述性的人类可读名称**（例如 "Foundation Concepts"，而不是仅仅写 "FOUND"）
- 每个组必须有 `color` 字段，使用**CSS 命名颜色**（不要用 "#E74C3C" 这样的十六进制色值）
- 每个组应有一个带 `color` 字段的 `font` 对象——深色背景用 `white`，浅色背景用 `black`。`csv-to-json.py` v1.04+ 会根据背景自动选择合适的字体颜色。

**关键结构：**
- **组键**：使用 CSV 中的 TaxonomyID（大写、无空格，例如 "FOUND"）
- **classifierName**：标题式大写、带空格的描述性显示名称（例如 "Foundation Concepts"）。绝不要只是重复 TaxonomyID 缩写。
- **color**：使用下方推荐区分色板中的 CSS 命名颜色。避免使用 AliceBlue（页面背景色）。
- **font.color**：深色背景用 `white`，浅色背景用 `black`。由 csv-to-json.py 自动分配。

### 推荐区分色板（24 色）

`csv-to-json.py` v1.04+ 的默认色板经过人工调校，使相邻图例行永不撞色，同色系族之间以明度区分。它可以轻松支持多达 24 个不同类别。使用此色板（或其子集，按此顺序，通过 `color-config.json` 传入），即使分类法很多也能保持视觉清晰：

| 位置 | 颜色（CSS 名称） | 建议类别族 | 字体 |
|---|---|---|---|
| 1 | SteelBlue | 基础 | white |
| 2 | DarkSlateBlue | 角色 / 治理 | white |
| 3 | DarkGreen | 架构 | white |
| 4 | LimeGreen | 应用开发 | black |
| 5 | Gold | 数据管理 | black |
| 6 | DarkGoldenrod | 数据治理 | white |
| 7 | Khaki | 商业智能 | black |
| 8 | Teal | 企业系统 | white |
| 9 | DodgerBlue | 网络 / 电信 | white |
| 10 | LightSkyBlue | 云计算 | black |
| 11 | Crimson | 安全 | white |
| 12 | DarkRed | 隐私 / 合规 | white |
| 13 | MediumPurple | 项目管理 | white |
| 14 | Indigo | 流程管理 | white |
| 15 | DarkOrchid | 系统分析与设计 | white |
| 16 | HotPink | 人机交互 | black |
| 17 | OliveDrab | IT 服务管理 | white |
| 18 | Orange | AI 能力 | black |
| 19 | Coral | 负责任 AI | black |
| 20 | Peru | AI 法律 / 监管 | black |
| 21 | SaddleBrown | AI 安全 | white |
| 22 | Tomato | AI 生产力 | white |
| 23 | DeepPink | 知识图谱 / 强调色 | white |
| 24 | DimGray | 新兴 / 杂项 | white |

**设计理由：**

- **按学科族做色相分组**——基础与基础设施用冷蓝色，构建/架构用绿色，数据带用黄色/金色，安全用红色，项目/流程用紫色，AI 集群用橙色/棕色，知识图谱作为连接性组织用强调色（DeepPink），新兴主题用中性灰。
- **每个色相族内部明度交替**，使相邻者永不撞色（Gold → DarkGoldenrod，DodgerBlue → LightSkyBlue，MediumPurple → Indigo，等等）。
- **深底白字，浅底黑字**——`csv-to-json.py` v1.04+ 会自动强制执行。深色集合包括 SteelBlue、DarkSlateBlue、DarkGreen、DarkGoldenrod、Teal、DodgerBlue、Crimson、DarkRed、MediumPurple、Indigo、DarkOrchid、OliveDrab、SaddleBrown、Tomato、DeepPink、DimGray。

### color-config.json（推荐）

把选定的色板保存到 `docs/learning-graph/color-config.json`，这样将来任何重新生成都会保持每个分类法 ID 的精确颜色分配。示例：

```json
{
  "FOUND": "SteelBlue",
  "ROLE": "DarkSlateBlue",
  "ARCH": "DarkGreen",
  "APPDEV": "LimeGreen",
  "DATA": "Gold",
  "SEC": "Crimson",
  "MISC": "DimGray"
}
```

传给 csv-to-json.py：`python csv-to-json.py learning-graph.csv learning-graph.json color-config.json metadata.json taxonomy-names.json`

### groups 部分示例

```json
"groups": {
    "FOUND": {
      "classifierName": "Foundation Concepts",
      "color": "SteelBlue",
      "font": { "color": "white" }
    },
    "DATA": {
      "classifierName": "Data and Information Management",
      "color": "Gold",
      "font": { "color": "black" }
    },
    "SEC": {
      "classifierName": "Security of Information Assets",
      "color": "Crimson",
      "font": { "color": "white" }
    },
    "AIIS": {
      "classifierName": "AI in Information Systems",
      "color": "Orange",
      "font": { "color": "black" }
    },
    "MISC": {
      "classifierName": "Miscellaneous Concepts",
      "color": "DimGray",
      "font": { "color": "white" }
    }
  }
```

**注意：** csv-to-json.py 程序会根据 CSV 文件中的分类法自动生成 groups 部分。如果没有 `color-config.json`，它会按图例顺序从 24 色默认色板中按位置分配颜色——本身已经互不冲突，但仍建议保存一份 `color-config.json`，以便多次重新生成之间分配保持稳定。

## 第 9 步：生成完整的学习图谱 JSON

现在你已经创建了 metadata.json 文件（第 7 步）、taxonomy-names.json（第 5b 步），并有了带分类法的 CSV（第 6 步），运行 csv-to-json.py 程序生成完整的 learning-graph.json 文件：

```bash
python csv-to-json.py learning-graph.csv learning-graph.json color-config.json metadata.json taxonomy-names.json
```

**重要：** 强烈建议提供 `taxonomy-names.json` 文件，以确保图谱查看器图例中显示人类可读的类别名称。没有它，显示名称将使用分类法 ID（如 "EDA1"）而不是规范名称（如 "Exploratory Data Analysis I"）。

该命令将：
1. 读取 learning-graph.csv 文件（含 ConceptID、ConceptLabel、Dependencies、TaxonomyID 列）
2. 使用 metadata.json 中的元数据
3. 使用 taxonomy-names.json 中的人类可读名称填充 `classifierName` 字段
4. 根据 CSV 中的分类法自动生成 groups 部分
5. 创建带正确组引用（使用 TaxonomyID）的节点
6. 根据依赖关系创建边
7. **为每个节点计算概念影响力分数（CIS）**，并附加为 `node.cis`（见上文更新日志）
8. 输出符合 schema 的完整 learning-graph.json 文件
9. 若任何分类法 ID 缺少人类可读名称则发出警告

核实文件 [learning-graph.json](./learning-graph.json) 存在且有效。控制台输出会列出 CIS 最高的前 10 个概念——请做合理性检查：它们应当是课程中真正的基础性概念（被广泛依赖的思想），而不是狭窄的终端主题。如果某个狭窄/高阶概念高居 CIS 榜首，边的方向很可能画反了（诊断方法见 `book-chapter-generator` 技能的边方向校验）。

可选：你可以对照 schema 校验 JSON：

```bash
./validate-learning-graph.sh learning-graph.json
```

> **依赖说明**：该脚本调用系统 `python3`，需已安装 `jsonschema` 库
> （`pip install jsonschema`）。若不想污染系统环境，可用 uv 一次性运行：
> `uv run --with jsonschema python validate-learning-graph.py learning-graph.json learning-graph-schema.json`
> （注意直接调 `.py` 时需显式给出数据文件与 schema 文件两个参数）。

## 第 10 步：分类法分布报告

生成分布分析：

1. 统计每个类别的概念数
2. 计算百分比
3. 识别占比过高的类别（>30%）
4. 必要时建议替代的分类方案

使用本技能中的 Python 报告程序 taxonomy-distribution.py。

**输出：**
- 保存到 [taxonomy-distribution.md](./taxonomy-distribution.md)
- markdown 表格格式，列为：
  - 类别名称
  - TaxonomyID
  - 数量
  - 百分比

## 第 11 步：从 index-template.md 创建新的 index.md

从本技能中的 index-template.md 文件，在 learning-graph 目录中创建一个新的 `index.md` 文件。
定制新的 index.md 文件，使其反映这本智能教材的名称。查找全大写的占位值（TEXTBOOK_NAME）
并替换为适当的值。

## 第 12 步：撰写会话日志

把会话日志导出到 logs/learning-graph-generator-VERSION-DATE.md

其中：

1. VERSION 是本技能的版本号。
2. DATE 是今天的日期，ISO 格式 yyyy-mm-dd。

注意，会话日志还应列出所用各 Python 程序的版本。
例如，要记录本次会话中使用的 csv-to-json.py 程序的版本号。
这对调试很重要。

## 第 13 步：完成

告知用户学习图谱生成已完成！向他们表示祝贺，并祝他们在教材或课程材料上取得成功。
告诉用户：如果想查看学习图谱，应运行 /book-installer 技能并按照「安装学习图谱」指南操作，它会在 @docs/sims/graph-viewer 中创建一个 microsim。
这一步虽是可选的，但强烈建议执行。
告诉他们下一个合乎逻辑的步骤是运行 /book-chapter-generator 技能，但在执行下一步之前，务必审阅章节概览、
概念清单、概念分类法和学习图谱。
生成章节内容会消耗大量 token，最好确保每份
章节概览和概念清单都已完善。

**创建的文件：**
- [course-description-assessment.md](./course-description-assessment.md)——课程描述的质量评估
- [concept-list.md](./concept-list.md)——多达 600 个概念的编号清单
- [learning-graph.csv](./learning-graph.csv)——带分类法的完整依赖图
- [taxonomy-names.json](./taxonomy-names.json)——分类法 ID 到人类可读名称的映射（对图谱查看器至关重要）
- [metadata.json](./metadata.json)——学习图谱的元数据（标题、描述、创建者等）
- [learning-graph.json](./learning-graph.json)——vis-network.js JSON 格式的完整学习图谱，含 metadata、groups、nodes 和 edges
- [concept-taxonomy.md](./concept-taxonomy.md)——类别定义
- [quality-metrics.md](./quality-metrics.md)——质量校验报告
- [taxonomy-distribution.md](./taxonomy-distribution.md)——类别分布分析
- [index.md](./index.md)——学习图谱部分的介绍页

## 重要说明

- 在整个过程中保持教学上的严谨性
- 依赖关系应反映真实的先修知识
- 在颗粒度与全面性之间取得平衡
- 确保概念在逻辑上层层递进
- 学习图谱应支持多条学习路径，而不仅仅是一条线性路径

## 附录：JSON Schema 与校验

（本节内容由上游 README.md 合并而来。）

文件 [learning-graph-schema.json](learning-graph-schema.json) 包含一个用于校验学习图谱的 JSON schema。

### Unix Shell 脚本

我们提供了一个 UNIX shell 脚本，可对任何学习图谱运行校验器。
只需把文件名作为第一个参数传给 `validate-learning-graph.sh` 文件。
（依赖系统 `python3` 的 `jsonschema` 库，替代用法见第 9 步的依赖说明。）

```sh
./validate-learning-graph.sh ../../docs/vis/combined-viewer/learning-graph.json 
```

**示例响应：**

```
Validating learning graph...
Input file: ../../docs/vis/combined-viewer/learning-graph.json
Schema file: $HOME/Documents/ws/learning-graphs/src/schema/learning-graph-schema.json

✓ Validation successful!

Summary:
  Title: Graph Theory Learning Graph
  Creator: Dan McCreary
  Version: 1.0
  Groups: 10
  Nodes: 25
  Edges: 24
  Orphaned nodes: 0

✓ Learning graph is valid!
```

### Schema 概览

该 schema 使用 JSON Schema Draft 2020-12 校验学习图谱，内容包括：

#### Metadata 部分（必需）

- 必填字段：
  - **title：** 学习图谱标题
  - **description：** 详细描述
- 可选字段：
  - **dcreator：** 作者/机构
  - **ddate：** 创建日期（YYYY-MM-DD 格式）
  - **dversion：** 版本号（例如 "1.0"）
  - **dformat：** 格式规格
  - **dschema：** 指向本 schema 的 URL
  - **dlicense：** 许可信息

#### Groups 部分（必需）

带样式属性的分类法分组：
- 必需：color（CSS 颜色值）
- 可选：
  - font（含 color 和 size 属性）
  - shape（组的默认形状）

#### Nodes 部分（必需）

概念节点数组，具有：
- 必需：id、label、group
- 可选：shape、color、font、x、y、fixed、hidden
- 所有样式均可覆盖组默认值

#### Edges 部分（必需）

依赖边数组，具有：
- 必需：from、to（节点 ID）
- 可选：id、label、arrows、color、width、dashes

#### 校验特性

- ✓ 校验数据类型（string、integer、number、boolean、array、object）
- ✓ 强制必填字段
- ✓ 校验 CSS 颜色模式（#hex、命名颜色、rgb/rgba）
- ✓ 校验日期格式（YYYY-MM-DD）
- ✓ 校验版本格式（语义化版本）
- ✓ 校验 schema URL 的 URI 格式
- ✓ 校验形状枚举（box、circle、star 等）
- ✓ 强制最小值（ID >= 1、size >= 1 等）
- ✓ 在适当位置禁止额外属性

#### 校验示例输出

```
✓ Schema is valid JSON
✓ All required keys present in learning-graph.json
✓ Metadata fields: 8 properties
✓ Groups count: 10
✓ Nodes count: 25
✓ Edges count: 24
```

## 来源与许可

上游 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills)。⚠ 上游仓库无 LICENSE 文件，依法默认保留全部权利；本包仅以副本供本机自用，若需对外分发须先取得作者授权。原文英文，本包译为简体中文。
