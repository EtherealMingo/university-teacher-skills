---
name: glossary-generator
description: 根据学习图谱的概念清单生成术语表，定义符合 ISO 11179 规范（精确、简洁、非循环）。在学习图谱的概念清单定稿之后使用。Triggers: 「根据概念清单帮我生成一份术语表」「给这本教材生成术语表」「帮我把这些概念都写上符合 ISO 11179 的定义」「术语表里的定义帮我检查一下质量」。
license: 
metadata:
  ibook.version: "1.0"
  ibook.preferred-model: "sonnet"
---

# 术语表生成器

**版本：** 1.0

根据学习图谱的概念清单生成一份全面的术语表，定义符合 ISO 11179 规范。

## TOKEN 效率警告

**本技能会生成大文件（2,000+ 行）。对于预算有限的教师用户，Token 成本远比耗时重要。**

**默认做法：单个串行 Task 代理**，把所有定义直接写入一个临时文件。这是最省 Token 的方式，因为：

- 系统提示词 / 工具描述的开销只付**一次**（约 12K tokens）
- 没有协调与拼装的开销
- 实测用 **约 31K tokens** 即可完成一份 350 词条的术语表（2026-03-14 基准测试）

### 实测 Token 经济账（350 词条基准，2026-03-14）

| 构成 | Tokens | 说明 |
|-----------|--------|-------|
| 代理开销（系统提示词 + 工具） | ~12K | 串行付一次；并行要付 4 次 |
| 定义生成（350 词条） | ~19K | 不可避免的 LLM 工作 |
| 拼装（Python 脚本） | ~700 | 简单的编程任务 |
| **合计（串行）** | **~31K** | |

**每词条 Token：合计约 88，边际约 54**（减去一次性开销后）。

边际成本的计算方式：(30,788 − 12,000) / 350 = **约 54 tokens/词条**。
可用它估算任意规模术语表的成本：

| 术语表规模 | 预估总 tokens |
|---------------|----------------------|
| 100 词条 | ~17K（12K 开销 + 5.4K 生成） |
| 200 词条 | ~23K |
| 350 词条 | ~31K（实测） |
| 500 词条 | ~39K |

### 为什么绝不应该使用并行执行

每个并行代理都要独立支付完整的约 12K 系统提示词开销。
对术语表生成来说，各词条定义完全独立——并行带来的提速收益抵不上成本。串行代理一次 Write 调用写入全部词条，约 6 分钟完成，完全可以接受。

| 方案 | 代理开销 | 生成 | 拼装 | 合计 | 浪费 |
|----------|---------------|------------|----------|-------|-------|
| **1 个串行代理（推荐）** | ~12K（一次） | ~19K | ~700 | **~31K** | — |
| 4 个并行代理 + 脚本 | ~48K（4 倍） | ~19K | ~700 | **~68K** | +37K（119%） |
| 4 个并行代理 + 手工 Edit | ~48K（4 倍） | ~19K | ~200K | **~267K** | +236K（761%） |

并行执行让 Token 成本**翻倍还多**，而质量毫无提升。
对于 Claude Pro 套餐的教师（五小时约 200K token 预算），串行方案约占其预算的 16%，而并行占 34%，手工拼装则超过 100%。

**绝不使用并行代理生成术语表。Token 浪费得不偿失。**

**始终使用串行方案。不要把并行作为一个选项提供给用户。**

拼装步骤（排序并写出最终文件）必须始终使用 Python 脚本——绝不通过 Edit/Write 工具调用手工输出术语表内容。完整复盘见 `logs/glossary-generation-very-inefficient.md`。

## 用途

本技能通过把学习图谱中的概念标签转换为格式规范的术语定义，自动化智能教材的术语表创建工作。每条定义遵循 ISO 11179 元数据注册标准：精确（precise）、简洁（concise）、可区分（distinct）、非循环（non-circular），且不含业务规则。本技能确保术语一致性、校验交叉引用，并产出按字母顺序排列、附相关例子的词条。

在简短定义之后，你可以补充说明该术语在教材中的重要性，并举一个术语使用的例子。

## 何时使用本技能

在学习图谱技能完成、概念清单定稿之后使用本技能。`/docs` 目录下的所有 Markdown 内容也可以一并扫描，找出普通高中学生可能看不懂的词或短语。

术语表依赖学习图谱概念枚举阶段产出的一份完整、经过评审的概念清单。具体而言，在以下情形触发本技能：

- 概念清单文件已存在（通常是 `docs/learning-graph/02-concept-list-v1.md`）
- 概念清单已经评审并获得认可
- 课程描述已存在且学习成果明确
- 准备创建或更新教材的术语表

## 工作流程

### 第 1 步：校验输入质量

在生成定义之前，先评估概念清单的质量：

1. 读取概念清单文件（通常是 `docs/learning-graph/02-concept-list-v1.md`）
2. 检查重复的概念标签（目标：100% 唯一）
3. 验证 Title Case（标题式大写）格式（目标：95%+ 合规）
4. 校验长度约束（目标：98% 在 32 字符以内）
5. 评估概念清晰度（无歧义术语）

计算质量分（1–100 分制）：

- 90–100：所有概念唯一、格式规范、长度合适
- 70–89：多数概念达标，有少量格式问题
- 50–69：存在一些重复概念或格式不一致
- 50 以下：问题严重，需要人工审查

**用户对话触发条件：**

- 得分 < 70：询问「概念清单存在质量问题。是否先审查并清理清单，再生成术语表？」
- 发现重复：询问「发现 [N] 个重复概念。自动去重，还是您先过目？」
- 格式问题：询问「发现 [N] 个概念存在格式问题。是否自动修复？」

### 第 2 步：读取课程上下文

读取课程描述文件（`docs/course-description.md`）以及 `/docs/**/*.md` 下的其他 Markdown 文件，以了解：

- 目标受众（决定例子的复杂程度）
- 课程目标（用于术语对齐）
- 先修要求（用于背景知识假设）
- 学习成果（用于概念使用的语境）

### 第 3 步：用单个串行代理生成定义

**默认做法（最省 Token）：** 启动一个 Task 代理，生成全部定义并直接写入单个临时文件。

```
Task 代理提示词：
"为以下 [N] 个术语生成符合 ISO 11179 规范的术语表定义。
把所有词条以 Markdown 形式（#### 标题，附定义、例子和讨论）
用 Write 工具写入文件 /tmp/glossary-raw.md。
每个词条用 #### 作为术语标题。不要在回复中返回内容——
只需确认文件已写好并报告词条数。

[在此粘贴完整术语清单]

[在此粘贴课程描述上下文，供把握受众水平]"
```

单个代理把所有定义写入一个文件。这样系统提示词开销只付一次（约 12K tokens），并避免所有协调成本。实测 **350 词条的术语表约 31K tokens**（合计约 88 tokens/词条，边际约 54 tokens/词条）。

**不要使用并行代理生成术语表。** 原因见上文「TOKEN 效率警告」一节——并行让 Token 成本翻倍还多，而质量毫无提升。

对清单中的每个概念，创建一条遵循 ISO 11179 标准的定义：

**精确性（25 分）：** 准确捕捉概念的含义

- 在课程语境下具体地定义概念
- 使用适合目标受众的术语
- 确保定义与课程中概念的实际用法一致

**简洁性（25 分）：** 定义保持简短（目标：20–50 字）

- 避免冗余的字词或解释
- 快速直达核心含义
- 使用清晰、直接的语言

**可区分性（25 分）：** 让每条定义独特且可分辨

- 避免照搬其他来源的定义
- 确保没有两条定义过于相似
- 突出该概念与相关概念的区别

**非循环性（25 分）：** 避免循环依赖

- 定义中不引用未定义的术语
- 不形成循环链（A 依赖 B，B 又依赖 A）
- 在定义中使用更简单、更基础的术语

**示例格式：**

以概念「Learning Graph（学习图谱）」为例：

```markdown
#### Learning Graph

A directed graph of concepts that reflects the order that concepts should be learned to master a new concept.

Learning graphs are the foundational data structure use for intelligent textbooks.  They are used to guide
intelligent agents and recommend learning paths for students.

**Example:** In a programming course, the learning graph shows that "Variables" must be understood before "Functions," which must be understood before "Recursion."
```

### 第 4 步：添加例子（60–80% 的词条）

为大多数概念（目标：60–80%）附上一个贴切的例子：

- 以「**Example:**」开头（冒号后不换行）
- 提供来自课程领域的具体例证
- 例子保持简短（1–2 句）
- 确保例子澄清概念而非制造困惑

### 第 5 步：添加交叉引用

在适当处引用相关术语：

- 相关概念用「See also:」（另见）
- 相对概念用「Contrast with:」（对比）
- 确保所有被交叉引用的术语都存在于术语表中
- 每个词条的交叉引用控制在 1–3 条

### 第 6 步：用 Python 脚本拼装术语表文件

**关键：绝不通过 Edit/Write 工具调用手工拼装术语表。**
按字母排序和合并文件是简单的编程任务。用 LLM 文本生成手工做这件事会浪费 100,000+ tokens，那可是真金白银。

**强制做法：** 编写一个 Python 脚本并通过 Bash 工具执行，脚本完成：

1. 读取代理输出文件——`/tmp/glossary-raw.md`（串行）或 `/tmp/glossary-part-*.md`（并行）
2. 按 `#### ` 标题切分词条
3. 用 `sorted()` 按字母排序（不区分大小写）
4. 一次性写出最终的 `docs/glossary.md`

**参考脚本（按需调整路径）：**

```python
#!/usr/bin/env python3
"""Merge glossary parts into a single sorted glossary."""
import glob, os, re

entries = {}

# Support both serial (single file) and parallel (multiple files)
if os.path.exists('/tmp/glossary-raw.md'):
    sources = ['/tmp/glossary-raw.md']
else:
    sources = sorted(glob.glob('/tmp/glossary-part-*.md'))

for path in sources:
    with open(path) as f:
        content = f.read()
    for block in re.split(r'\n(?=#### )', content):
        block = block.strip()
        m = re.match(r'#### (.+)', block)
        if m:
            entries[m.group(1).strip()] = block

sorted_terms = sorted(entries.keys(), key=lambda t: t.lower())

with open('docs/glossary.md', 'w') as out:
    out.write('# Glossary of Terms\n\n')
    for term in sorted_terms:
        out.write(entries[term] + '\n\n')

print(f"Wrote {len(sorted_terms)} terms to docs/glossary.md")
```

通过 Bash 工具运行：`python3 /tmp/assemble_glossary.py`。
总成本：脚本约 500 tokens + 输出约 200 tokens = **约 700 tokens**
（若通过 Edit 调用手工完成则要 200,000+ tokens）。

**绝不要做以下任何一件事：**

- 通过 Write 或 Edit 工具直接写入术语表词条
- 把子代理的输出复制粘贴到 Edit 工具的 old_string/new_string 参数里
- 通过按字母顺序逐条吐出来手工排序
- 通过 Edit 调用一节一节地追加到术语表文件

**拼装文件的格式规则：**

- **术语只允许使用四级标题（`####`）。** 术语表内部不要使用 `##` 章节标题、`###` 子标题或任何其他级别的标题。文件中唯一的 `#` 标题是页面标题（`# Glossary of Terms`）。其余一律 `####`。
- **术语只能按字母排序（不区分大小写）。绝不按类别、领域或主题分组。** 术语表是一个扁平的字母序列表——不要分节线、不要类别标题、不要主题分组。字母序是唯一的组织原则。
- 术语表中不要出现任何 `---` 字符串，不需要它们。
- 例子用「**Example:**」（粗体，带冒号）
- 词条之间保持一致的间距（词条间空一行）

### 第 7 步：生成质量报告

创建 `docs/learning-graph/glossary-quality-report.md`，内容包括：

**ISO 11179 元数据注册合规指标：**

对每条定义按 5 项标准评分（每项 25 分）：

1. 精确性：是否准确捕捉了含义？
2. 简洁性：是否简短（20–50 字）？
3. 可区分性：是否独特且可分辨？
4. 非循环性：是否没有循环依赖？
5. 不含业务规则：是否没有夹带具体政策或规则？

**总体质量指标：**

- 定义平均长度：[X] 字
- 满足全部 4 项标准的定义：[X]%
- 发现的循环定义：[X] 条
- 例子覆盖率：[X]%
- 交叉引用：共 [X] 条，其中失效 [X] 条

**可读性：**

- Flesch-Kincaid 年级水平：[X]
- 是否适合目标受众：是/否

**改进建议：**

- 列出所有得分 < 70/100 的定义
- 指出需要修复的循环依赖
- 建议需要补例子的概念
- 标注失效的交叉引用

### 第 8 步：校验输出

执行最终校验：

1. 验证字母排序（要求 100% 合规）
2. 检查所有交叉引用指向存在的术语
3. 确保输入清单中的所有概念都已收录
4. 验证 Markdown 语法渲染正常
5. 确认不存在循环定义

**成功标准：**

- 总体质量分 > 85/100
- 零循环定义
- 100% 字母排序
- 概念清单中的术语全部收录
- 在 MkDocs 中 Markdown 渲染正常

### 第 9 步：更新导航（可选）

如果 `mkdocs.yml` 的 `nav:` 中还没有 `- Glossary: glossary.md`，将其加在靠近末尾处（在 License/Contact 之前），遵循 `$BK_HOME/skills/book-installer/references/mkdocs-nav-editing.md` 中的权威导航编辑规则。

### 第 10 步：生成交叉引用索引（可选）

创建 `docs/learning-graph/glossary-cross-ref.json`，供语义搜索使用：

```json
{
  "terms": [
    {
      "term": "Learning Graph",
      "related_terms": ["Concept Dependency", "Directed Acyclic Graph"],
      "contrasts_with": ["Linear Curriculum"],
      "category": "Educational Technology"
    }
  ]
}
```

这个 JSON 文件可支撑未来的功能，例如：

- 跨术语表的语义搜索
- 概念关系可视化
- 自动推荐相关术语

## 质量评分参考

使用以下评分细则给每条定义打分（1–100 分制）：

**85–100：优秀**

- 满足全部 4 项 ISO 11179 标准（每项 20+ 分）
- 长度适当（20–50 字）
- 包含贴切的例子
- 语言清晰、无歧义
- 无循环依赖

**70–84：良好**

- 满足 3–4 项 ISO 标准
- 长度可接受（15–60 字）
- 可能缺少例子
- 总体清晰
- 无严重问题

**55–69：合格**

- 满足 2–3 项 ISO 标准
- 长度有问题（过短或过长）
- 在有帮助的地方缺少例子
- 有些歧义
- 轻微循环引用

**55 以下：需要修订**

- 多项 ISO 标准不达标
- 严重长度问题
- 含混或循环
- 缺少上下文
- 需要完全重写

## 常见误区

**循环定义：**

- 差：「学习图谱是展示学习的图。」
- 好：「一种概念的有向图，反映为掌握新概念而应遵循的学习顺序。」

**过于含糊：**

- 差：「一种用于教育的东西。」
- 好：「一种反映先修关系的概念有向图。」

**过长：**

- 差：「学习图谱是一种特殊类型的有向无环图结构，常用于教育技术和教学设计语境中，表示学生为达成特定学习成果而需掌握的不同概念元素之间的层级与顺序关系。」
- 好：「一种概念的有向图，反映为掌握新概念而应遵循的学习顺序。」

**夹带业务规则：**

- 差：「学生必须先完成先修概念，才能进入依赖它的概念。」
- 好：「一种展示概念之间先修关系的有向图。」

**引用未定义术语：**

- 差：「采用 DAG 结构」（如果 DAG 不在术语表中）
- 好：「采用有向无环图结构」

## 输出文件汇总

**必需：**

1. `docs/glossary.md`——完整术语表，按字母排序，定义符合 ISO 11179 规范

**推荐：**

2. `docs/learning-graph/glossary-quality-report.md`——质量评估与改进建议

**可选：**

3. `docs/learning-graph/glossary-cross-ref.json`——供语义搜索使用的 JSON 映射
4. 若导航中缺少术语表链接，更新 `mkdocs.yml`

## 示例会话

**用户：** 「根据我的概念清单生成一份术语表」

**Claude（使用本技能）：**

1. 读取概念清单文件和 `docs/course-description.md`（约 5K tokens）
2. 校验质量（查重、查格式）（约 1K tokens）
3. 启动一个串行 Task 代理，把所有定义写入 `/tmp/glossary-raw.md`（约 19K tokens）
4. 编写 Python 拼装脚本到 `/tmp/assemble_glossary.py`（约 500 tokens）
5. 通过 Bash 运行脚本——解析、排序并写出 `docs/glossary.md`（约 200 tokens）
6. 用 `grep -c "^####" docs/glossary.md` 核对词条数（约 100 tokens）
7. 按需更新 `mkdocs.yml` 导航（约 500 tokens）
8. 汇报：「已创建包含 350 个词条的术语表，70% 的词条附了例子。」

**实测结果（2026-03-14）：** 350 个词条的生成与拼装共消耗 **约 31K tokens**。
按约 88 tokens/词条（减去代理开销后约 54 tokens/词条）计算，这是可能做到的最高效方案。

**切记：** 子代理负责生成文本（不可避免的 LLM 工作）。拼装是编程任务——用 `sorted()`，不要用 Edit 工具。绝不使用并行代理。

## 来源与许可

上游 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills)。⚠ 上游仓库无 LICENSE 文件，依法默认保留全部权利；本包仅以副本供本机自用，若需对外分发须先取得作者授权。原文英文，本包译为简体中文。
