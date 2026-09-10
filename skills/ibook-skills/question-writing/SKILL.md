---
name: question-writing
description: 为智能教材各章节生成交互式选择题测验：题目对齐学习图谱概念、按布鲁姆教育目标分类法（Bloom's Taxonomy）认知层级分布、采用 mkdocs-material 题目折叠块格式（A/B/C/D 选项），并保证干扰项（distractor）质量、答案位置均衡与完整解析。在章节内容和学习图谱均已就绪后使用。Triggers: 「帮我给第三章出一套选择题」「为整本书每一章各出 10 道测验题」「这些选择题的干扰项太明显了，帮我改写」「检查一下这份测验的答案分布均不均匀」「把整本书的测验汇总成题库」。
metadata:
  ibook.version: "0.5"
  ibook.preferred-model: "sonnet"
---

# 智能教材测验生成器（Quiz Generator for Intelligent Textbooks）

**版本：** 0.5

## 概述
1. 对每个 markdown 章节，为教材章节生成带干扰项质量分析的交互式选择题测验。
2. 生成 markdown 格式的质量报告。
3. 更新 mkdocs.yml 导航，把测验与报告纳入其中。

## 目的

本技能通过分析章节内容生成贴合上下文的选择题，从而自动化智能教材的测验创建。每份测验都对齐学习图谱中的具体概念，按布鲁姆教育目标分类法的认知层级分布，并采用 mkdocs-material 的题目折叠块（question admonition）格式，使用大写字母（A、B、C、D）选项。本技能确保干扰项质量、答案位置均衡，并提供有教学价值的完整解析。

## 何时使用本技能

在以下条件满足后使用本技能：

1. 章节内容已生成或写完（每章 1000+ 词）
2. 学习图谱已存在，含概念依赖关系
3. 已有术语表（推荐，用于术语类题目）

在以下时机触发本技能：

- 为新章节创建测验
- 内容修订后更新测验
- 为整本教材构建完整的题库
- 导出测验数据供 LMS（学习管理系统）或聊天机器人集成

## Token 效率：仅串行执行

!!! warning "除非用户明确要求，否则绝不使用并行 Agent"
    **测验生成始终使用单个串行 Agent。** 这是一条硬性
    要求，不是建议。不要把并行执行作为一个选项提供。

每个派生的 Agent 都会产生约 12,000 token 的启动开销（系统提示、
工具 schema、项目上下文）。并行执行会成倍放大这一开销，
却不会带来任何质量收益。以下是 17 章测验生成的实测数据：

| 方案 | 系统开销 | 总 Token | 浪费 |
|----------|----------------|--------------|-------|
| **串行（1 个 Agent）** | ~12,000 | ~310,000 | — |
| 并行（4 个 Agent） | ~48,000 | ~358,000 | +48,000（13%） |

生产环境中还观察到并行执行的其他问题：

1. **行为不一致：** 各 Agent 独立选择不同策略，
   相同工作量的工具调用次数出现 5 倍差异（8 次对 39 次）
2. **文件编辑冲突：** 多个 Agent 同时修改 mkdocs.yml，
   造成需要人工修复的不一致
3. **无法共享经验：** 每个 Agent 都从零开始，没有从前面的章节
   积累任何上下文

本技能支持两种模式：
- **串行模式**（默认，始终如此）：一个 Agent 顺序处理所有章节
- **单章模式**：只为某一章生成测验

## 工作流

### 阶段 1：准备（顺序执行）

本阶段在测验生成前运行一次，读取共享上下文。

#### 步骤 1.1：记录开始时间

```bash
date "+%Y-%m-%d %H:%M:%S"
```

记录开始时间，供会话报告使用。

#### 步骤 1.2：告知技能正在运行

通知用户：「Quiz Generator Skill v0.5 正在以串行模式运行。」

#### 步骤 1.3：读取共享上下文

为所有 Agent 读取并缓存以下文件：

1. **课程描述**（`docs/course-description.md`）
   - 提取目标受众与阅读水平
   - 记录布鲁姆分类法的学习成果

2. **学习图谱**（`docs/learning-graph/learning-graph.csv` 或类似文件）
   - 加载带依赖关系的概念清单
   - 计算概念中心性用于排定优先级

3. **术语表**（`docs/glossary.md`）
   - 加载术语定义，用于术语类题目
   - 记录哪些概念有术语表条目

4. **章节清单**（扫描 `docs/chapters/` 目录）
   - 枚举所有章节目录
   - 统计每章词数，评估就绪程度

#### 步骤 1.4：评估内容就绪度

为每个目标章节计算内容就绪分数（1–100）：

**质量检查：**

##### 1. **章节词数：**
   - 2000+ 词 = 优秀（20 分）
   - 1000–1999 词 = 良好（15 分）
   - 500–999 词 = 基础（10 分）
   - <500 词 = 不足（5 分）

##### 2. **示例覆盖度：**
   - 60%+ 的概念有示例 = 优秀（20 分）
   - 40–59% = 良好（15 分）
   - 20–39% = 基础（10 分）
   - <20% = 不足（5 分）

##### 3. **术语表覆盖度：**
   - 80%+ 的章节概念有定义 = 优秀（20 分）
   - 60–79% = 良好（15 分）
   - 40–59% = 基础（10 分）
   - <40% = 不足（5 分）

##### 4. **概念清晰度：**
   - 所有概念都有清晰解释（20 分）
   - 大多数概念清晰（15 分）
   - 部分概念不清晰（10 分）
   - 许多概念不清晰（5 分）

##### 5. **学习图谱对齐度：**
   - 所有章节概念均已映射（20 分）
   - 大多数已映射（15 分）
   - 部分已映射（10 分）
   - 很少映射（5 分）

**内容就绪度区间：**

- 90–100：内容丰富，可产出优秀质量的测验
- 70–89：内容良好，可产出扎实的测验
- 50–69：内容基础，只能产出有限的测验
- 低于 50：内容不足以产出高质量测验

**用户对话触发条件：**

- 分数 < 60：询问「第 [X] 章内容有限（[N] 词）。生成较短的测验还是跳过？」
- 无术语表：询问「未找到术语表。定义类题目将会受限。继续吗？」
- 概念缺口：询问「本章有 [N] 个概念不在学习图谱中。用现有概念继续吗？」
- 无学习成果：询问「课程描述中没有布鲁姆分类法成果。使用默认分布吗？」

### 阶段 2：测验生成（串行）

启动一个 Agent，顺序处理所有章节。该 Agent 读取每一
章，生成 10 道题，写好测验文件，再进入下一
章。这样约 12K 的系统提示开销只付一次。

**Agent 提示词模板：**

```
You are generating quizzes for an intelligent textbook. Generate quizzes for
ALL of the following chapters, processing them one at a time.

COURSE CONTEXT:
- Course: [course name]
- Target audience: [audience]
- Reading level: [level]

BLOOM'S TAXONOMY TARGETS:
- Introductory chapters (1-3): 40% Remember, 40% Understand, 15% Apply, 5% Analyze
- Intermediate chapters (4-N): 25% Remember, 30% Understand, 30% Apply, 15% Analyze
- Advanced chapters: 15% Remember, 20% Understand, 25% Apply, 25% Analyze, 10% Evaluate, 5% Create

CHAPTERS TO PROCESS:
[List ALL chapter directories with full paths]

FOR EACH CHAPTER:
1. Read the chapter content at the index.md file
2. Identify the key concepts covered in that chapter
3. Generate exactly 10 questions following the format below
4. Ensure answer balance: A (2-3), B (2-3), C (2-3), D (2-3)
5. Write the quiz to docs/chapters/[chapter-dir]/quiz.md

QUIZ FORMAT - Each question MUST follow this exact format:

#### [N]. [Question text ending with ?]

<div class="upper-alpha" markdown>
1. [Option A text]
2. [Option B text]
3. [Option C text]
4. [Option D text]
</div>

??? question "Show Answer"
    The correct answer is **[LETTER]**. [Explanation 50-100 words]

    **Concept Tested:** [Concept Name]

---

QUIZ FILE STRUCTURE:
# Quiz: [Chapter Title]

Test your understanding of [topic] with these review questions.

---

[Questions 1-10 following the format above]

REPORT when done:
- Chapter name
- Number of questions
- Bloom's distribution (R:#, U:#, Ap:#, An:#)
- Answer distribution (A:#, B:#, C:#, D:#)
```

### 阶段 2 步骤（逐章执行）

#### 步骤 2：确定目标分布

根据章节类型（入门、进阶、高阶），设定布鲁姆教育目标分类法的目标分布：

**入门章节（通常为第 1–3 章）：**
- 40% 记忆（Remember）
- 40% 理解（Understand）
- 15% 应用（Apply）
- 5% 分析（Analyze）
- 0% 评价（Evaluate）
- 0% 创造（Create）

**进阶章节：**
- 25% 记忆
- 30% 理解
- 30% 应用
- 15% 分析
- 0% 评价
- 0% 创造

**高阶章节：**
- 15% 记忆
- 20% 理解
- 25% 应用
- 25% 分析
- 10% 评价
- 5% 创造

章节类型的判定依据：
- 在教材中的位置（前 3 章 = 入门）
- 概念在学习图谱中的中心性（中心性高 = 高阶）
- 章节元数据中的显式标记
- 用户指定

目标题量：每章 8–12 题（默认：10）

#### 步骤 3：识别要考查的概念

分析章节内容和学习图谱，为概念排定优先级：

**优先级 1（必考）：**
- 学习图谱中高中心性的概念
- 章节标题或引言中提到的概念
- 有独立小节的概念
- 加粗强调或有术语表链接的关键术语

**优先级 2（应考）：**
- 有大量解释的辅助性概念
- 有示例的概念
- 本章复习到的先修概念
- 来自学习目标的概念

**优先级 3（可考）：**
- 仅简要提及的边缘概念
- 用于提供背景的相关概念
- 预告的未来主题

目标是覆盖 80%+ 的优先级 1 概念。

#### 步骤 4：按布鲁姆层级生成题目

对每个选定考查的概念，按照目标分布在适当的布鲁姆层级生成题目。各层级的行为动词与出题指南，请阅读权威参考 `$BK_HOME/skills/chapter-content-generator/references/blooms-taxonomy.md`。

**重要格式要求：**

所有题目必须使用 mkdocs-material 题目折叠块格式，并使用大写字母列表样式：

```markdown
#### 1. What is the primary purpose of a learning graph?

<div class="upper-alpha" markdown>
1. To create visual decorations for textbooks
2. To map prerequisite relationships between concepts
3. To generate random quiz questions
4. To organize files in a directory structure
</div>

??? question "Show Answer"
    The correct answer is **B**. A learning graph is a directed graph that maps prerequisite relationships between concepts, showing which concepts must be learned before others. This ensures proper scaffolding in educational content.

    **Concept Tested:** Learning Graph

    **See:** [Learning Graph Concept](../concepts/learning-graph.md)
```

**格式规则：**

1. 使用四级标题（####）并带题号
2. 题目写成以 ? 结尾的完整句子
3. 使用 `<div class="upper-alpha" markdown>` 包裹
4. 4 个选项写成编号列表（1、2、3、4）
5. 使用 `??? question "Show Answer"` 折叠块
6. 答案内容缩进 4 个空格
7. 以「The correct answer is **[字母]**.」开头
8. 包含概念名称及指向来源的链接
9. div 前后各留一个空行

**出题指南：**

**记忆层级（Remember）：**
- 考查术语表中的定义
- 测试事实回忆
- 辨识术语
- 示例：「[概念] 的定义是什么？」

**理解层级（Understand）：**
- 要求作出解释
- 测试对概念关系的理解
- 比较/对照概念
- 示例：「哪个选项最好地描述了 [A] 与 [B] 之间的关系？」

**应用层级（Apply）：**
- 给出需要运用概念的场景
- 测试用所学方法解决问题的能力
- 示例：「给定 [场景]，你会用哪种方法？」

**分析层级（Analyze）：**
- 要求识别模式或成因
- 测试拆解概念的能力
- 示例：「[现象] 背后的根本原因是什么？」

**评价层级（Evaluate）：**
- 要求依据准则作出判断
- 测试批判性思维
- 示例：「对于 [目标]，哪种方法最有效？」

**创造层级（Create）：**
- 要求设计方案
- 测试概念的综合运用
- 示例：「你会如何设计一个满足 [需求] 的 [系统]？」

#### 步骤 5：撰写高质量干扰项

对每个错误选项（干扰项，distractor），确保：

**可信性（Plausibility）：**
- 对没学过该材料的人来说听起来合理
- 使用相关术语
- 避免明显错误的答案
- 长度与正确答案相近

**教学价值：**
- 针对常见误解
- 测试对相关概念的理解
- 能区分不同的知识水平
- 不是脑筋急转弯或文字游戏

**常见干扰项模式：**

- 部分真实（在别的语境下正确）
- 反向倒置（与正确答案相反）
- 相似术语（相关但不同的概念）
- 常见错误（学生的典型失误）

**避免：**
- 「以上皆是」或「以上皆非」
- 玩笑或无意义选项
- 语法上与题干不一致的选项
- 互相重叠或都可能是正确的答案

#### 步骤 6：撰写解析

为每道题撰写解析，要求：

**确认正确答案：**
- 明确写出：「The correct answer is **[字母]**。」
- 解释为什么该答案正确
- 引用章节内容或概念定义
- 目标：50–100 词

**有教学性（可选但推荐）：**
- 简要解释干扰项为什么错误
- 澄清常见误解
- 提供补充背景
- 链接到章节小节以便深入了解

**解析示例：**

```
The correct answer is **B**. A learning graph is a directed graph that maps
prerequisite relationships between concepts. Option A is incorrect because
learning graphs serve a structural purpose, not decorative. Option C is
incorrect because quiz generation is not the primary purpose. Option D
confuses learning graphs with file systems.

**Concept Tested:** Learning Graph

**See:** [Learning Graph Concept](../concepts/learning-graph.md#definition)
```

#### 步骤 7：确保答案位置均衡

检查正确答案在 A、B、C、D 上均匀分布：

**目标分布：**
- A：25%（±5%）
- B：25%（±5%）
- C：25%（±5%）
- D：25%（±5%）

**避免的模式：**
- 连续全是 C
- A-B-A-B 交替
- 可预测的序列
- 位置偏向（总是第一个/最后一个正确）

**随机化策略：**
- 写测验前先生成随机序列
- 逐题打乱
- 完成后核验分布
- 不均衡则调整

#### 步骤 8：创建测验文件

按正确结构生成测验文件：

**独立测验文件**（`docs/chapters/[章节名]/quiz.md`）：

```markdown
# Quiz: [Chapter Name]

Test your understanding of [chapter topic] with these questions.

---

#### 1. [Question text]?

<div class="upper-alpha" markdown>
1. [Option 1]
2. [Option 2]
3. [Option 3]
4. [Option 4]
</div>

??? question "Show Answer"
    The correct answer is **[LETTER]**. [Explanation]

    **Concept Tested:** [Concept Name]

---

#### 2. [Question text]?

[Continue for all questions...]
```

**格式要求：**
- 题目之间使用水平分隔线（---）
- 题目顺序编号（1、2、3……）
- 保持间距一致
- 确保所有 markdown 正确渲染

### 阶段 3：汇总

串行 Agent 完成后，收集其结果：
- 已创建的测验文件清单
- 各章统计（题量、布鲁姆分布、答案均衡）
- 遇到的任何错误或问题

#### 步骤 10：生成元数据文件（可选）

为每章创建 `docs/learning-graph/quizzes/[章节名]-quiz-metadata.json`：

```json
{
  "chapter": "Chapter Name",
  "chapter_file": "docs/chapters/chapter-name/index.md",
  "quiz_file": "docs/chapters/chapter-name/quiz.md",
  "generated_date": "YYYY-MM-DD",
  "total_questions": 10,
  "content_readiness_score": 85,
  "overall_quality_score": 78,
  "questions": [
    {
      "id": "ch1-q001",
      "number": 1,
      "question_text": "What is the primary purpose of a learning graph?",
      "correct_answer": "B",
      "bloom_level": "Understand",
      "difficulty": "medium",
      "concept_tested": "Learning Graph",
      "source_link": "../concepts/learning-graph.md",
      "distractor_quality": 0.85,
      "explanation_word_count": 67
    }
  ],
  "answer_distribution": {
    "A": 2,
    "B": 3,
    "C": 3,
    "D": 2
  },
  "bloom_distribution": {
    "Remember": 2,
    "Understand": 4,
    "Apply": 3,
    "Analyze": 1,
    "Evaluate": 0,
    "Create": 0
  },
  "concept_coverage": {
    "total_concepts": 12,
    "tested_concepts": 10,
    "coverage_percentage": 83
  }
}
```

#### 步骤 11：生成题库（汇总）

创建或更新 `docs/learning-graph/quiz-bank.json`，纳入全部题目：

```json
{
  "textbook_title": "Building Intelligent Textbooks",
  "generated_date": "YYYY-MM-DD",
  "total_chapters": 20,
  "total_questions": 187,
  "questions": [
    {
      "id": "ch1-q001",
      "chapter": "Introduction to Learning Graphs",
      "question_text": "What is the primary purpose of a learning graph?",
      "options": {
        "A": "To create visual decorations for textbooks",
        "B": "To map prerequisite relationships between concepts",
        "C": "To generate random quiz questions",
        "D": "To organize files in a directory structure"
      },
      "correct_answer": "B",
      "explanation": "A learning graph is a directed graph...",
      "bloom_level": "Understand",
      "difficulty": "medium",
      "concept": "Learning Graph",
      "chapter_file": "docs/concepts/learning-graph.md",
      "source_section": "#definition",
      "tags": ["graph", "prerequisites", "scaffolding"]
    }
  ]
}
```

**题库的用途：**
- LMS 导出（Moodle、Canvas、Blackboard XML）
- 测验随机抽题（选取子集）
- 生成测验的替代版本
- 聊天机器人集成（练习题）
- 学习类 App 集成

#### 步骤 12：生成质量报告

创建 `docs/learning-graph/quiz-generation-report.md`：

```markdown
# Quiz Generation Quality Report

Generated: YYYY-MM-DD
Execution Mode: Serial (1 agent)
Wall-clock Time: X minutes Y seconds

## Overall Statistics

- **Total Chapters:** 20
- **Total Questions:** 187
- **Avg Questions per Chapter:** 9.4
- **Overall Quality Score:** 76/100

## Per-Chapter Summary

| Chapter | Questions | Quality Score | Bloom's Score | Coverage |
|---------|-----------|---------------|---------------|----------|
| Ch 1: Introduction | 10 | 82/100 | 24/25 | 83% |
| Ch 2: Learning Graphs | 12 | 78/100 | 22/25 | 90% |
| ... | ... | ... | ... | ... |

## Bloom's Taxonomy Distribution (Overall)

| Level | Actual | Target | Deviation |
|-------|--------|--------|-----------|
| Remember | 22% | 25% | -3% ✓ |
| Understand | 28% | 30% | -2% ✓ |
| Apply | 27% | 25% | +2% ✓ |
| Analyze | 18% | 15% | +3% ✓ |
| Evaluate | 4% | 4% | 0% ✓ |
| Create | 1% | 1% | 0% ✓ |

**Bloom's Distribution Score:** 24/25 (excellent)

## Answer Balance (Overall)

- A: 24% (45/187)
- B: 26% (49/187)
- C: 25% (47/187)
- D: 25% (46/187)

**Answer Balance Score:** 15/15 (perfect distribution)

## Recommendations

[Include recommendations based on aggregated data]
```

#### 步骤 13：质量校验

对所有已生成的测验做全面校验：

**1. 无歧义：**
- 每道题只有一个站得住脚的正确答案
- 题干清晰完整
- 无语法错误

**2. 干扰项质量：**
- 所有错误答案都有可信性
- 干扰项考的是理解，而不是瞎猜
- 长度与语法结构相近
- 答案之间互不重叠

**3. 语法与清晰度：**
- 全篇行文专业
- 动词时态一致
- 标点正确
- 无错别字

**4. 答案均衡：**
- 正确答案分布在 A、B、C、D 上
- 每个选项在 20–30% 之间（目标：25%）
- 无可预测的模式

**5. 布鲁姆分布：**
- 与章节类型的目标相符
- 偏差在 ±15% 以内可接受
- 测验内难度循序渐进

**6. 概念覆盖：**
- 考查了 75%+ 的主要概念
- 重要概念有多道题
- 没有过度考查琐碎概念

**7. 无重复：**
- 所有测验中题目唯一
- 没有近重复（相似度 >80%）

**8. 解析质量：**
- 所有题目都有解析
- 解析有教学性，而不只是确认答案
- 目标 50–100 词
- 引用章节小节

**9. 链接有效性：**
- 所有来源链接都指向存在的内容
- 适当使用小节锚点
- 链接渲染正常
- 不要在 quiz.md 文件中放置打不开的链接
- 不要使用指向不存在小节的链接文字

**10. 偏见检查：**
- 无文化偏见
- 无性别偏见
- 不对读者背景做假设
- 语言通俗易懂

**成功标准：**
- 总体质量分 > 70/100
- 每章 8–12 题
- 布鲁姆分布在目标 ±15% 以内
- 概念覆盖 75%+
- 答案均衡在每个选项 20–30% 之间
- 100% 的题目有解析
- 无重复题
- 所有链接有效

#### 步骤 14：更新站点导航

在 `mkdocs.yml` 中，于每章之下嵌套一个 `Quiz:` 条目，并在
`Learning Graph:` 之下添加 `Quiz Generation Report:`。遵循权威
的导航编辑规则
`$BK_HOME/skills/book-installer/references/mkdocs-nav-editing.md`——
尤其是：先读后写；**当并行地为许多章节生成测验时，把导航编辑串行化**
（在结束时一次性应用所有导航变更）；把章节页标记为
`Content:`；并且绝不在标签中使用 "Chapter" 字样：

```yml
    - 1. Introduction to AI and Intelligent Textbooks:
      - Content: chapters/01-intro-ai-intelligent-textbooks/index.md
      - Quiz: chapters/01-intro-ai-intelligent-textbooks/quiz.md
```

#### 步骤 15：记录结束时间并撰写会话日志

记录结束时间：

```bash
date "+%Y-%m-%d %H:%M:%S"
```

把会话信息导出到 `logs/quiz-generator-YYYY-MM-DD.md`：

```markdown
# Quiz Generator Session Log

**Skill Version:** 0.4
**Date:** YYYY-MM-DD
**Execution Mode:** Serial (1 agent)

## Timing

| Metric | Value |
|--------|-------|
| Start Time | YYYY-MM-DD HH:MM:SS |
| End Time | YYYY-MM-DD HH:MM:SS |
| Elapsed Time | X minutes Y seconds |

## Token Usage

| Phase | Estimated Tokens |
|-------|------------------|
| Setup (shared context) | ~15,000 |
| Serial agent (all chapters) | ~295,000 |
| Aggregation + nav update | ~5,000 |
| **Total** | ~315,000 |

## Results

- Total chapters: N
- Total questions: N × 10
- Quality score: XX/100
- All quizzes written successfully: Yes/No

## Files Created

[List all quiz.md files and report files]
```

#### 步骤 16：通知用户

通知用户：

「Quiz Generator v0.5 完成！

- **模式：** 串行（1 个 Agent）
- **耗时：** X 分 Y 秒
- **已处理章节：** 23
- **已生成题目：** 230
- **质量分：** 82/100

`mkdocs.yml` 中的站点导航已更新，为每章加入了 Content/Quiz 链接，并在 learning-graph 部分加入了测验生成报告。

会话已记录到 `logs/quiz-generator-YYYY-MM-DD.md`」

## 题目格式参考

### 包含全部要素的完整示例

```markdown
#### 3. Given a course with 50 concepts, what is the most important factor in organizing the learning graph?

<div class="upper-alpha" markdown>
1. Alphabetical order of concept names
2. Prerequisite relationships between concepts
3. The length of concept definitions
4. The visual appearance of the graph diagram
</div>

??? question "Show Answer"
    The correct answer is **B**. Prerequisite relationships are the most important factor because they determine the order in which concepts must be learned. A learning graph maps these dependencies to ensure students learn foundational concepts before advanced ones. Alphabetical order (A) and visual appearance (D) are organizational preferences, not educational requirements. Definition length (C) does not affect concept sequencing.

    **Concept Tested:** Learning Graph Structure

    **See:** [Learning Graph](../concepts/learning-graph.md#prerequisites)
```

### 格式检查清单

- [ ] 带题号的四级标题
- [ ] 以 ? 结尾的完整句子
- [ ] `<div class="upper-alpha" markdown>` 包裹
- [ ] 选项用编号列表（1、2、3、4）
- [ ] 闭合 `</div>` 标签
- [ ] `??? question "Show Answer"` 折叠块
- [ ] 答案块 4 空格缩进
- [ ] 「The correct answer is **[字母]**.」语句
- [ ] 解析（50–100 词）
- [ ] **Concept Tested:** 标签
- [ ] **See:** 链接，路径正确
- [ ] div 前后各一个空行

## 应避免的常见坑

**格式错误：**
- ❌ 忘记 `<div class="upper-alpha" markdown>` 包裹
- ❌ 列表中使用字母（A、B、C、D）而不是数字
- ❌ 答案块缩进不正确
- ❌ 缺少闭合 `</div>` 标签

**题目质量：**
- ❌ 有多个正确答案的歧义题
- ❌ 「以上皆是」或「以上皆非」选项
- ❌ 脑筋急转弯或文字游戏
- ❌ 只考琐碎事实的题目

**干扰项质量：**
- ❌ 明显错误的答案
- ❌ 玩笑选项或无意义内容
- ❌ 干扰项比正确答案长/短得多
- ❌ 互相重叠或互相矛盾的选项

**解析质量：**
- ❌ 只是复述题目
- ❌ 没有教学价值
- ❌ 链接缺失或失效
- ❌ 太短（< 30 词）或太长（> 150 词）

**Token 效率：**
- ❌ 使用并行 Agent（每多一个 Agent 就在系统提示开销上浪费约 12K token）
- ❌ 在单个串行 Agent 就能产出相同结果时派生多个 Agent
- ❌ 在用户没有明确要求的情况下，把并行执行作为一个选项提供

## 输出文件汇总

**必需（每章）：**
1. 测验 markdown 文件：`docs/chapters/[章节名]/quiz.md`

**推荐（汇总）：**
2. `docs/learning-graph/quiz-generation-report.md`——质量指标
3. `logs/quiz-generator-YYYY-MM-DD.md`——带耗时信息的会话日志

**可选：**
4. `docs/learning-graph/quiz-bank.json`——全部题目的数据库
5. `docs/learning-graph/quizzes/[章节名]-quiz-metadata.json`——各章元数据
6. 对 `mkdocs.yml` 的导航更新

## 使用方式（由上游 README 合并而来）

**触发短语示例：**

- 「为第 3 章生成一份测验」
- 「为我的章节创建测验题」
- 「根据这份内容出一份测验」
- 「为所有章节生成测验」

**前提条件：**

- 章节内容已存在（建议每章 1000+ 词）
- 学习图谱已创建（`docs/learning-graph/learning-graph.csv`）
- 已有术语表（`docs/glossary.md`）——推荐
- 课程描述含学习成果——可选

### 执行模式说明

- **串行模式（本 SKILL 版本的默认且唯一推荐）：** 一个 Agent 顺序处理全部章节。上游早期版本曾尝试过并行模式（4–6 个 Agent 同时跑，23 章挂钟时间从约 10 分钟降到约 2–3 分钟，总 token 不变），但实测发现它带来约 48K token 的额外系统开销、行为不一致与 mkdocs.yml 编辑冲突，因此本版本已明确禁用并行，除非用户明确要求。
- **单章模式：** 只更新一份测验：「只为第 3 章生成测验」

### 质量评分构成（Quiz Quality Score，1–100）

五个组成部分：

1. **题目质量（30 分）：** 清晰、无歧义、构题规范
2. **布鲁姆分布（25 分）：** 与章节类型的目标相符
3. **概念覆盖（20 分）：** 考查 75%+ 的主要概念
4. **答案均衡（15 分）：** 正确答案均匀分布
5. **教学价值（10 分）：** 解析有教学性、提供了链接

### 干扰项写作指南

本技能在 `references/distractor-writing-guide.md` 中提供了撰写高质量干扰项的详尽指南。该参考涵盖：

- 有效干扰项的四个品质（可信性、教学价值、区分度、公平性）
- 干扰项构造模式
- 应避免的常见错误
- 质量检查清单
- 按布鲁姆层级给出的示例
- 修订策略

生成答案选项时应参照该文档。

### 故障排查

#### 「内容就绪分数偏低（<60）」

**原因：** 章节内容不足以产出高质量测验

**解决：**
- 扩写章节内容（目标：1000+ 词）
- 为关键概念补充示例
- 确保概念解释清晰
- 核实术语表覆盖度

#### 「布鲁姆分布失衡」

**原因：** 过多题目集中在某一认知层级

**解决：**
- 复核章节类型（入门、进阶、高阶）
- 检查该章节类型的目标分布
- 增加更多高层级题目（应用、分析、评价）
- 减少过多的记忆/理解题

#### 「答案均衡差」

**原因：** 正确答案集中在某个选项上（例如全是 B）

**解决：**
- 随机化正确答案的位置
- 目标：A、B、C、D 各占 25%（±5% 可接受）
- 避免模式（A-B-A-B、全是 C 等）
- 每加一道题就检查一次

#### 「题目折叠块不渲染」

**原因：** markdown 格式错误

**解决：**
- 核实有 `<div class="upper-alpha" markdown>` 包裹
- 检查编号列表用的是 1、2、3、4（不是 A、B、C、D）
- 确保存在闭合 `</div>` 标签
- 核实答案块为 4 空格缩进
- 检查 div 前后有空行

#### 「干扰项太明显」

**原因：** 错误答案不可信

**解决：**
- 复习干扰项写作指南
- 使用相关术语
- 基于常见误解构造
- 确保与正确答案长度相近
- 避免无意义或玩笑选项

## 示例会话

### 全部章节（默认串行模式）

**用户：**「为所有章节生成测验」

**Claude（使用本技能）：**

1. 记录开始时间
2. 通知：「Quiz Generator Skill v0.5 正在以串行模式运行。」
3. 读取共享上下文（课程描述、学习图谱、术语表）
4. 扫描章节目录，找到 23 章
5. 评估内容就绪度（所有章节 2000+ 词）
6. 启动一个串行 Agent，顺序处理全部 23 章
7. Agent 读取每一章，生成 10 道题，写好 quiz.md，再进入下一章
8. 收集该单个 Agent 的结果
9. 生成质量报告（得分：82/100）
10. 更新 mkdocs.yml 导航
11. 记录结束时间
12. 撰写会话日志
13. 报告：「Quiz Generator v0.5 完成！模式：串行。耗时：33 分钟。题目：230。质量：82/100。」

### 单章模式

**用户：**「只为第 3 章生成一份测验」

**Claude（使用本技能）：**

1. 评估第 3 章内容就绪度（得分：82/100）
2. 判定章节类型：进阶
3. 设定目标分布：25% 记忆、30% 理解、30% 应用、15% 分析
4. 识别出 12 个待考概念（10 个优先级 1，2 个优先级 2）
5. 用题目折叠块格式生成 10 道题
6. 创建高质量干扰项
7. 确保答案均衡（A: 2，B: 3，C: 3，D: 2）
8. 撰写解析，未核实的链接不放
9. 把测验写入 `docs/chapters/03-chapter-name/quiz.md`
10. 报告：「已为第 3 章创建 10 题测验。质量分：78/100。」

## 来源与许可

上游 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills)。⚠ 上游仓库无 LICENSE 文件，依法默认保留全部权利；本包仅以副本供本机自用，若需对外分发须先取得作者授权。原文英文，本包译为简体中文。
