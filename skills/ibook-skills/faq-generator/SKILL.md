---
name: faq-generator
description: 根据课程内容、学习图谱（learning graph）与术语表为智能教材生成一套分类 FAQ。在学习图谱与术语表已生成、且至少 30% 章节内容已写完之后使用。Triggers: 「帮我为这本教材生成一份常见问题 FAQ」「根据课程内容整理一份 FAQ」「把 FAQ 导成聊天机器人能用的 JSON」「内容更新了不少，帮我刷新一下 FAQ」。
license: Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)
metadata:
  ibook.version: "1.0"
  ibook.preferred-model: "sonnet"
---

# FAQ 生成器

**版本：** 1.0

从教材内容生成全面、分类整理的 FAQ，并导出聊天机器人可直接使用的 JSON。FAQ 写入文件 `docs/faq.md`，本次会话的结果记录到 `logs/faq.md`。

## 用途

本技能通过分析课程内容、学习图谱和术语表来生成相关的问题与答案，从而自动化智能教材的 FAQ 创建工作。技能按类别和难度组织问题，确保布鲁姆分类法（Bloom's Taxonomy）在各认知层级上的分布合理，答案附带来源内容链接，并导出可直接接入 RAG 系统的结构化 JSON 数据。

## 何时使用本技能

在以下产物齐备之后使用本技能：

1. 课程描述已定稿，且质量分高于 70
2. 学习图谱已创建
3. 术语表已生成
4. 至少 30% 的章节内容已写完

具备这些前提条件，FAQ 生成器才有足够的上下文来创建有意义、切题的问题。在以下情形触发本技能：

- 为一本新教材构建初始 FAQ
- 内容大量增加后更新 FAQ
- 为接入聊天机器人或 AI 助手准备内容
- 识别现有内容中的知识缺口

## Markdown 格式规范

1. FAQ 标题使用 Markdown 一级标题（#）
2. 每个类别使用二级标题（##）
3. 每个问题使用三级标题（###）
4. 答案放在正文段落中

使用技能 references 目录下的 faq-template.md 作为模板。

## 关键规则：禁止使用锚点链接

!!! warning "绝不使用锚点链接"
    **所有链接只能指向文件本身，绝不带 `#` 锚点片段。**

    锚点链接（`file.md#section-name`）极易失效，因为：

    - 内容编辑过程中章节标题会变动
    - 锚点对大小写和空白字符敏感
    - MkDocs 的锚点自动生成行为不可预测
    - 失效锚点会引发构建警告并困扰用户

    ✅ **正确：** `[参见欧姆定律](chapters/02-ohms-law/index.md)`

    ❌ **错误：** `[参见欧姆定律](chapters/02-ohms-law/index.md#series-circuits)`

## 工作流程

### 第 1 步：评估内容完备度

计算内容完备度得分（1–100 分制），判断 FAQ 生成的可行性：

**所需输入：**

1. 读取 `docs/course-description.md`
   - 检查：标题、受众、先修要求、学习成果
   - 确认存在按布鲁姆分类法组织的学习成果
   - 计分：完整得 25 分

2. 读取 `docs/learning-graph/03-concept-dependencies.csv`
   - 校验 DAG（有向无环图）结构（无环）
   - 统计概念数与依赖数
   - 计分：DAG 有效且连通性良好得 25 分

3. 读取 `docs/glossary.md`
   - 统计词条数（50+ 为良好，100+ 为优秀）
   - 计分：100+ 得 15 分，50–99 得 10 分，<50 得 5 分

4. 扫描全部 `docs/**/*.md` 文件
   - 计算总字数
   - 目标：10,000+ 字以支撑全面的 FAQ
   - 计分：1 万字以上得 20 分，5 千–1 万得 15 分，<5 千得 10 分

5. 计算概念覆盖率
   - 学习图谱中有多大比例的概念有对应的章节内容？
   - 计分：80%+ 得 15 分，60–79% 得 10 分，<60% 得 5 分

**内容完备度得分区间：**

- 90–100：所有输入齐备且质量高
- 70–89：核心输入齐备，内容有若干缺口
- 50–69：缺少部分可选输入，或字数偏低
- 50 以下：关键输入缺失

**用户对话触发条件：**

- 得分 < 60：询问「可用于生成 FAQ 的内容有限。是先生成一份基础版 FAQ，还是等内容更多后再做？」
- 无术语表：询问「未找到术语表。仍然生成 FAQ（技术类问题会受限），还是先创建术语表？」
- 字数偏低：询问「仅找到 [N] 字内容，FAQ 质量可能受限。是否继续？」

如果用户同意在得分 < 60 的情况下继续，则照常生成 FAQ，但在质量报告中注明内容受限的免责声明。

### 第 2 步：分析内容，挖掘提问机会

阅读并分析所有内容来源，识别常见的提问模式：

**来自课程描述：**

- 「这门课讲什么？」（范围）
- 「这门课适合谁？」（受众）
- 「我能学到什么？」（学习成果）
- 「开始学习前需要掌握什么？」（先修要求）

**来自学习图谱：**

- 「什么是 [概念]？」（定义类问题）
- 「[概念 A] 和 [概念 B] 有什么关系？」（关系类问题）
- 「学习 [概念] 之前需要先掌握什么？」（先修类问题）
- 「学完 [概念] 之后学什么？」（进阶类问题）

**来自术语表：**

- 「[术语] 是什么意思？」（术语类问题）
- 「[术语 A] 和 [术语 B] 有什么区别？」（对比类问题）
- 「能举一个 [术语] 的例子吗？」（应用类问题）

**来自章节内容：**

- 识别反复出现的主题或话题
- 标注学生可能遇到困难的地方（复杂概念）
- 提取文中提到的常见误解
- 找出实际应用的例子

**来自已有 FAQ（如存在）：**

- 若 `docs/faq.md` 已存在则读取
- 保留人工精选的问题
- 与新生成的问题合并
- 去除重复，冲突时保留人工版本

### 第 3 步：生成问题类别

创建 6 个与学习进程对齐的标准类别。关于如何在各个布鲁姆层级上写问题（提问起手式、答案特征、常见错误）的详细指导，请阅读权威参考 `$BK_HOME/skills/chapter-content-generator/references/blooms-taxonomy.md`。

**1. 入门问题（10–15 题）**

目标布鲁姆层级：60% 记忆（Remember），40% 理解（Understand）

- 课程概览与目标
- 先修要求与学前准备
- 如何使用本教材
- 导航与结构
- 时间投入与难度

示例：
- 「这门课讲什么？」
- 「这门课适合谁？」
- 「开始学习前我需要先掌握什么？」
- 「这本教材是怎么组织的？」

**2. 核心概念问题（20–30 题）**

目标布鲁姆层级：20% 记忆，40% 理解，30% 应用（Apply），10% 分析（Analyze）

- 学习图谱中的关键概念（优先选择中心度高的节点）
- 基本原理
- 概念间的关系与依赖
- 概念如何层层递进

示例：
- 「什么是学习图谱？」
- 「为什么概念依赖很重要？」
- 「如何创建概念分类体系？」
- 「脚手架式教学和先修概念之间是什么关系？」

**3. 技术细节问题（15–25 题）**

目标布鲁姆层级：30% 记忆，40% 理解，20% 应用，10% 分析

- 术语表中的术语
- 定义与解释
- 技术性对比
- 规格细节

示例：
- 「ISO 11179 是什么含义？」
- 「术语表校验器是怎么工作的？」
- 「什么时候应该使用交叉引用？」

**4. 常见疑难问题（10–15 题）**

目标布鲁姆层级：10% 记忆，30% 理解，40% 应用，20% 分析

- 需要额外解释的难点概念
- 常见误解
- 排错场景
- 错误处理

示例：
- 「为什么我的学习图谱显示有环？」
- 「如何修复循环定义？」
- 「概念覆盖率低是什么原因造成的？」

**5. 最佳实践问题（10–15 题）**

目标布鲁姆层级：10% 理解，40% 应用，30% 分析，15% 评价（Evaluate），5% 创造（Create）

- 如何有效地应用概念
- 推荐做法
- 何时使用特定技术
- 真实世界中的应用

示例：
- 「什么时候该用 MicroSim，什么时候该用示意图？」
- 「如何平衡内容深度与认知负荷？」
- 「讲授抽象概念最好的方法是什么？」

**6. 进阶主题问题（5–10 题）**

目标布鲁姆层级：10% 应用，30% 分析，30% 评价，30% 创造

- 复杂的集成
- 边界情况
- 性能优化
- 未来方向

示例：
- 「如何设计一个自适应学习系统？」
- 「自动生成内容有哪些利弊权衡？」
- 「如何把多种教学方法结合起来？」

### 第 4 步：生成问题与答案

对每个类别，按以下准则生成问题：

**问题格式：**

- 使用二级标题（##）
- 写成真正的问题（以问号结尾）
- 问题要具体、可被搜索到
- 使用术语表中的术语
- 问题保持简洁（5–15 字）

**答案格式：**

- 每个问题使用三级标题（###）
- 答案完整、可独立成立
- 40% 的答案要包含例子
- 链接到相关章节（目标：60%+ 带链接）
- 目标长度：100–300 字
- 使用清晰、直接的语言
- 把问题回答完整

**布鲁姆分类法指导：**

**记忆（Remember）：** 回忆事实、术语、基本概念

- 「什么是 [概念]？」
- 「[术语] 是什么意思？」
- 「[系统] 由哪些组成部分构成？」

**理解（Understand）：** 解释思想或概念

- 「[概念] 是如何工作的？」
- 「为什么 [概念] 重要？」
- 「[A] 和 [B] 有什么区别？」

**应用（Apply）：** 在新情境中使用信息

- 「如何 [完成某项任务]？」
- 「什么时候应该使用 [技术]？」
- 「能举一个 [概念] 的实际应用例子吗？」

**分析（Analyze）：** 在观点之间建立联系

- 「[A] 和 [B] 之间是什么关系？」
- 「[概念] 与 [另一概念] 有何关联？」
- 「[问题] 的根本原因是什么？」

**评价（Evaluate）：** 为某个决定或立场提供依据

- 「对于 [场景]，哪种方法最好？」
- 「[技术] 有哪些利弊权衡？」
- 「如何在 [A] 和 [B] 之间做选择？」

**创造（Create）：** 产出新的或原创的成果

- 「如何设计一个满足 [需求] 的 [系统]？」
- 「组合 [概念] 的最佳方式是什么？」
- 「如何把 [技术] 改造用于 [新情境]？」

**答案质量检查清单：**

- [ ] 标题、类别和问题使用了正确的 Markdown 标题级别
- [ ] 直接回答了问题
- [ ] 一致地使用术语表中的术语
- [ ] 抽象概念附带了例子（目标 40%）
- [ ] 链接到相关章节文件（目标 60%）——**不得带锚点片段**
- [ ] 长度适当（100–300 字）
- [ ] 对目标受众来说清晰易懂
- [ ] 内容与教材相符、准确无误
- [ ] 不使用术语表之外的行话
- [ ] **含 `#` 锚点的链接为零**（硬性要求）

### 第 5 步：创建 FAQ 文件

按规范结构生成 `docs/faq.md`：

```markdown
# [课程名称] FAQ

## 入门问题

### 这门课讲什么？

[答案：概述，并链接到课程描述]

### 这门课适合谁？

[答案：描述目标受众]

[继续写 10–15 个入门问题……]

## 核心概念

### 什么是 [关键概念]？

[答案：定义加例子，并链接到章节]

[继续写 20–30 个核心概念问题……]

## 技术细节问题

[继续写术语与技术类问题……]

## 常见疑难问题

[继续写排错类问题……]

## 最佳实践问题

[继续写应用类问题……]

## 进阶主题问题

[继续写进阶问题……]
```

**格式要求：**

- 标题使用一级标题
- 类别名使用二级标题
- 问题使用三级标题
- 答案使用正文
- 用 Markdown 链接指向章节文件：`[文字](path.md)`——**绝不使用锚点链接**
- 强调用粗体：`**重要术语**`
- 代码用代码块：` ```language ```
- 保持一致的间距

**关键：禁止锚点链接**

绝不给链接添加锚点片段（`#section-name`）。锚点极易失效，因为：
- 编辑过程中章节标题会变动
- 锚点对大小写和空白字符敏感
- MkDocs 的锚点生成不可预测
- 失效锚点会引发构建警告并困扰用户

✅ **正确：** `[欧姆定律](chapters/02-ohms-law/index.md)`
❌ **错误：** `[欧姆定律](chapters/02-ohms-law/index.md#series-circuits)`

只链接到章节文件本身，用户进入页面后可以自行浏览定位。

### 第 6 步：生成聊天机器人训练 JSON

创建 `docs/learning-graph/faq-chatbot-training.json`，供 RAG 集成使用：

```json
{
  "faq_version": "1.0",
  "generated_date": "YYYY-MM-DD",
  "source_textbook": "Course Name",
  "total_questions": 87,
  "questions": [
    {
      "id": "faq-001",
      "category": "Getting Started",
      "question": "What is this course about?",
      "answer": "Full answer text here...",
      "bloom_level": "Understand",
      "difficulty": "easy",
      "concepts": ["Course Overview", "Learning Objectives"],
      "keywords": ["course", "overview", "objectives", "goals"],
      "source_links": [
        "docs/course-description.md",
        "docs/index.md"
      ],
      "has_example": false,
      "word_count": 142
    },
    {
      "id": "faq-002",
      "category": "Core Concepts",
      "question": "What is a Learning Graph?",
      "answer": "A Learning Graph is...",
      "bloom_level": "Understand",
      "difficulty": "medium",
      "concepts": ["Learning Graph", "Concept Dependency"],
      "keywords": ["learning graph", "dependencies", "prerequisites"],
      "source_links": [
        "docs/concepts/learning-graph.md",
        "docs/glossary.md"
      ],
      "has_example": true,
      "word_count": 218
    }
  ]
}
```

**JSON Schema 要求：**

- 每个问题有唯一 ID（faq-001、faq-002 等）
- 类别为 6 个标准类别之一
- 布鲁姆层级取自六层分类法
- 难度：easy、medium、hard
- 概念列表来自学习图谱
- 关键词用于搜索优化
- 来源链接指向原始内容
- 是否含例子的布尔标记
- 答案字数

### 第 7 步：生成质量报告

创建 `docs/learning-graph/faq-quality-report.md`：

```markdown
# FAQ Quality Report

Generated: YYYY-MM-DD

## Overall Statistics

- **Total Questions:** 87
- **Overall Quality Score:** 82/100
- **Content Completeness Score:** 78/100
- **Concept Coverage:** 73% (145/198 concepts)

## Category Breakdown

### Getting Started
- Questions: 12
- Avg Bloom's Level: Remember/Understand
- Avg Word Count: 156

[Continue for all categories...]

## Bloom's Taxonomy Distribution

Actual vs Target:

| Level | Actual | Target | Deviation |
|-------|--------|--------|-----------|
| Remember | 18% | 20% | -2% ✓ |
| Understand | 32% | 30% | +2% ✓ |
| Apply | 24% | 25% | -1% ✓ |
| Analyze | 16% | 15% | +1% ✓ |
| Evaluate | 7% | 7% | 0% ✓ |
| Create | 3% | 3% | 0% ✓ |

Overall Bloom's Score: 25/25 (excellent distribution)

## Answer Quality Analysis

- **Examples:** 38/87 (44%) - Target: 40%+ ✓
- **Links:** 54/87 (62%) - Target: 60%+ ✓
- **Avg Length:** 187 words - Target: 100-300 ✓
- **Complete Answers:** 87/87 (100%) ✓

Answer Quality Score: 24/25

## Concept Coverage

**Covered (145 concepts):** [list]

**Not Covered (53 concepts):**
- [Concept 1] - Priority: High (high centrality in learning graph)
- [Concept 2] - Priority: Medium
- [Concept 3] - Priority: Low

Coverage Score: 22/30 (73% coverage)

## Organization Quality

- Logical categorization: ✓
- Progressive difficulty: ✓
- No duplicates: ✓
- Clear questions: ✓

Organization Score: 20/20

## Overall Quality Score: 82/100

- Coverage: 22/30
- Bloom's Distribution: 25/25
- Answer Quality: 24/25
- Organization: 20/20

## Recommendations

### High Priority
1. Add questions for high-centrality concepts: [list top 10]
2. Slightly increase Remember-level questions (+2%)

### Medium Priority
1. Add examples to 3 more answers (to reach 47%)
2. Link 5 more answers to source content

### Low Priority
1. Consider adding 2-3 more Advanced Topics questions
2. Review question phrasing for searchability

## Suggested Additional Questions

Based on concept gaps, consider adding:

1. "What is [Uncovered Concept 1]?" (Core Concepts)
2. "How does [Uncovered Concept 2] work?" (Technical Details)
[Continue with top 10 suggestions...]
```

### 第 8 步：生成覆盖缺口报告

创建 `docs/learning-graph/faq-coverage-gaps.md`：

```markdown
# FAQ Coverage Gaps

Concepts from learning graph not covered in FAQ.

## Critical Gaps (High Priority)

High-centrality concepts (many dependencies) without FAQ coverage:

1. **[Concept Name]**
   - Centrality: High (12 dependencies)
   - Category: Core Concepts
   - Suggested Question: "What is [Concept] and why is it important?"

[Continue for all high-priority gaps...]

## Medium Priority Gaps

Moderate-centrality concepts without FAQ coverage:

[Continue...]

## Low Priority Gaps

Leaf nodes or advanced concepts without FAQ coverage:

[Continue...]

## Recommendations

1. Add questions for all critical gaps (15 concepts)
2. Consider adding questions for medium priority (23 concepts)
3. Low priority can be addressed in future updates (15 concepts)
```

### 第 9 步：校验输出质量

执行全面校验：

**1. 唯一性检查：**

- 扫描所有问题查重
- 检查近似重复（相似度 >80%）
- 报告发现的重复

**2. 链接校验：**

- 从答案中提取全部 Markdown 链接
- **凡是包含 `#` 锚点片段的链接一律拒绝**——必须移除
- 验证每个链接目标文件存在
- 报告失效链接
- 链接应只指向文件（如 `chapters/01-intro/index.md`），绝不带锚点

**3. 布鲁姆分布：**

- 计算全部问题的实际分布
- 与目标分布对比
- 按偏差计分（±10% 以内可接受）

**4. 阅读难度：**

- 计算答案的 Flesch-Kincaid 年级水平
- 验证是否适合目标受众
- 标记过难或过易的答案

**5. 答案完整性：**

- 检查每个答案是否回应了问题
- 验证没有残缺或未答完的答案
- 确保提供了足够的上下文

**6. 技术准确性：**

- 与术语表交叉核对术语
- 验证与章节内容一致
- 标记任何矛盾或不准确之处

**成功标准：**

- 总体质量分 > 75/100
- 至少生成 40 个问题
- 概念覆盖率至少 60%
- 布鲁姆分类法分布均衡（偏差 ±15% 以内）
- 所有答案附带来源引用
- 聊天机器人 JSON 通过 schema 校验
- 零重复问题
- 所有内部链接有效（文件存在）
- **零锚点链接**——任何链接中都不含 `#` 片段

### 第 10 步：更新 mkdocs.yml 导航（可选）

如果 `nav:` 中还没有 `- FAQ: faq.md`，将其加在靠近末尾的位置（与术语表相邻），并把各质量报告挂到 `Learning Graph:` 之下（`faq-quality-report.md`、`faq-coverage-gaps.md`）。遵循 `$BK_HOME/skills/book-installer/references/mkdocs-nav-editing.md` 中的权威导航编辑规则。

## 质量评分参考

使用以下评分细则计算 FAQ 总体质量分（1–100）：

**覆盖率（30 分）：**

- 覆盖 80%+ 概念：30 分
- 70–79%：25 分
- 60–69%：20 分
- 50–59%：15 分
- <50%：10 分

**布鲁姆分类法分布（25 分）：**

计算每个层级与目标的偏差，对绝对偏差求和：

- 总偏差 0–10%：25 分
- 总偏差 11–20%：20 分
- 总偏差 21–30%：15 分
- 总偏差 >30%：10 分

**答案质量（25 分）：**

- 例子：40%+ 得 7 分，30–39% 得 5 分，<30% 得 3 分
- 链接：60%+ 得 7 分，50–59% 得 5 分，<50% 得 3 分
- 长度：平均 100–300 字得 6 分，可接受区间得 4 分
- 完整性：100% 得 5 分，95–99% 得 4 分，<95% 得 2 分

**组织（20 分）：**

- 分类合理：5 分
- 难度递进：5 分
- 无重复：5 分
- 问题清晰：5 分

## 常见误区

**重复问题：**

- 不要在不同类别中问同一个问题
- 相关概念的提问要变换措辞
- 把相似的问题合并为一个有完整答案的问题

**答案不完整：**

- 不要只回答一半
- 不要只写「详见第 X 章」而不给摘要
- 始终提供可独立成立的上下文

**缺少链接：**

- 不要忘记把答案链接到来源内容
- 只链接到章节文件——绝不使用锚点片段（`#section-name`）
- 定稿前验证所有链接指向的文件真实存在

**锚点链接失效：**

- 绝不使用 `file.md#section-name` 这样的锚点链接
- 标题被编辑、重命名或重构时锚点就会失效
- 只链接到章节/页面文件：`file.md`
- 这是硬性规则——没有例外

**提问措辞不当：**

- 避免「它是怎么工作的？」这类含糊的问题
- 使用术语表中的具体术语
- 让问题可被搜索到

**布鲁姆层级失衡：**

- 不要过度集中在记忆/理解层
- 要包含高阶思维问题
- 六个层级之间保持平衡

## 输出文件汇总

**必需：**

1. `docs/faq.md`——完整 FAQ，含分类问题与答案

**推荐：**

2. `docs/learning-graph/faq-quality-report.md`——质量指标与改进建议
3. `docs/learning-graph/faq-chatbot-training.json`——供 RAG 系统使用的结构化数据

**可选：**

4. `docs/learning-graph/faq-coverage-gaps.md`——未被 FAQ 覆盖的概念
5. 若导航中缺少 FAQ 链接，更新 `mkdocs.yml`

## 使用方式

**触发语：**

- 「帮我为这本教材生成一份 FAQ」
- 「创建一份常见问题列表」
- 「根据我的课程内容整理一份 FAQ」

**前提条件：**

- 课程描述文件存在（`docs/course-description.md`）
- 学习图谱已创建（`docs/learning-graph/03-concept-dependencies.csv`）
- 术语表已生成（`docs/glossary.md`，50+ 词条）
- 至少 30% 章节内容已写完（5,000+ 字）

**典型流程：**

1. 用户请求生成 FAQ
2. 技能评估内容完备度（1–100 分）
3. 技能分析内容、挖掘提问机会
4. 技能在 6 个类别中生成 40+ 个问题
5. 技能创建 `docs/faq.md`，组织好问答
6. 技能导出聊天机器人训练 JSON
7. 技能生成带改进建议的质量报告

## 示例输出

**FAQ 文件**（`docs/faq.md`）：

```markdown
# Intelligent Textbooks FAQ

## Getting Started

## What is this course about?

This course teaches you how to build intelligent textbooks using
open source tools like MkDocs and AI-powered content generation.
You'll learn to create interactive educational resources that adapt
to student needs through learning graphs, MicroSims, and automated
quality assessment.

**See:** [Course Description](course-description.md)

## Core Concepts

## What is a Learning Graph?

A Learning Graph is a directed graph of concepts that reflects the
order concepts should be learned to master a new concept. It maps
prerequisite relationships as a Directed Acyclic Graph (DAG),
ensuring students learn foundational concepts before advanced ones.

**Example:** In a programming course, the learning graph shows
"Variables" must be understood before "Functions," which must be
understood before "Recursion."

**See:** [Learning Graph Concept](concepts/learning-graph.md),
[Glossary](glossary.md#learning-graph)

...
```

**聊天机器人 JSON**（`docs/learning-graph/faq-chatbot-training.json`）：

```json
{
  "faq_version": "1.0",
  "generated_date": "2025-01-31",
  "source_textbook": "Building Intelligent Textbooks",
  "total_questions": 87,
  "questions": [
    {
      "id": "faq-001",
      "category": "Getting Started",
      "question": "What is this course about?",
      "answer": "This course teaches you how to build...",
      "bloom_level": "Understand",
      "difficulty": "easy",
      "concepts": ["Course Overview", "Intelligent Textbooks"],
      "keywords": ["course", "overview", "intelligent", "textbooks"],
      "source_links": ["docs/course-description.md"],
      "has_example": false,
      "word_count": 142
    }
  ]
}
```

## 最佳实践（给用户）

1. **确保前提产物齐备**——先生成学习图谱和术语表
2. **积累足够的内容**——建议 5,000+ 字再生成高质量 FAQ
3. **查看质量报告**——按建议改进覆盖率
4. **按需迭代**——为未覆盖的概念补充问题
5. **接入聊天机器人**——用 JSON 导出训练 AI 助手

## 常见问题排查

### 「内容完备度得分偏低（<60）」

**原因：** 可用于生成高质量 FAQ 的内容不足

**对策：**
- 撰写更多章节内容（目标：10,000+ 字）
- 确保术语表有 50+ 词条
- 补全学习图谱的依赖关系
- 定稿含学习成果的课程描述

### 「布鲁姆分布失衡」

**原因：** 低认知层级的问题过多

**对策：**
- 增加应用/分析类问题（场景、关系）
- 加入评价类问题（利弊权衡、方案推荐）
- 加入少量创造类问题（设计、创新）
- 参考布鲁姆指南中的提问模板

### 「概念覆盖率低（<60%）」

**原因：** 学习图谱中许多概念未在 FAQ 中体现

**对策：**
- 查看覆盖缺口报告
- 优先为中心度高的概念补问题
- 聚焦核心概念类别
- 考虑某些概念是否粒度过细

### 「缺少例子或链接」

**原因：** 答案缺少具体例证或引用

**对策：**
- 为抽象或复杂概念补充例子
- 把答案链接到相关章节
- 例子要取自课程所属领域

## 相关技能

- **Learning Graph（学习图谱生成）**——生成用于提问的概念依赖
- **Glossary Generator（术语表生成）**——创建术语类问题所引用的术语表
- **Chapter Content Generator（章节内容生成）**——产出 FAQ 所分析的内容
- **Concept Validator（概念校验）**——校验 FAQ 对所有概念的覆盖
- **Quiz Generator（测验生成）**——创建测评题目（与 FAQ 互补）

## 示例会话

**用户：** 「帮我为教材生成一份 FAQ」

**Claude（使用本技能）：**

1. 评估内容完备度（得分：78/100）
2. 读取课程描述、学习图谱、术语表、各章节
3. 识别提问机会
4. 在 6 个类别中生成 87 个问题
5. 创建答案：44% 带例子，62% 带链接
6. 导出聊天机器人训练 JSON
7. 生成质量报告（得分：82/100）
8. 创建覆盖缺口报告（53 个未覆盖概念）
9. 汇报：「已创建包含 87 个问题的 FAQ，覆盖 73% 的概念。总体质量：82/100。已添加 38 个例子和 54 个链接。改进建议详见质量报告。」

## 版本历史

- **v1.0**（2025-01-31）——首次发布
  - 6 个标准类别
  - 布鲁姆分类法分布
  - 聊天机器人 JSON 导出
  - 质量评分与报告

## 来源与许可

上游 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills)。⚠ 上游仓库无 LICENSE 文件，依法默认保留全部权利；本包仅以副本供本机自用，若需对外分发须先取得作者授权。原文英文，本包译为简体中文。
