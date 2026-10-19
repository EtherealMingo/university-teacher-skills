<!-- 权威副本。不要分叉复制进其他技能；按路径引用：
     $BK_HOME/skills/chapter-content-generator/references/blooms-taxonomy.md

     `$BK_HOME` 指向 ibook-skills 的检出位置，与具体代理无关。
     不要使用 `~/.claude/skills/`、`~/.codex/skills/` 或
     `~/.gemini/antigravity/skills/` 下的路径——那些路径各自绑定某一个
     代理框架，而这些技能要在所有框架上运行。如果 `$BK_HOME` 未设置，
     本文件位于包含调用方技能的技能根目录下的
     `chapter-content-generator/references/blooms-taxonomy.md`。 -->

# 布鲁姆分类学（2001 修订版）——权威参考

由 chapter-content-generator（学习目标）、faq-generator（问题分布）
与 quiz-generator（问题层级）共用。由旧文件 `bloom-taxonomy-verbs.md`
与 `blooms-taxonomy-guide.md` 合并而成。

## 第 1 部分：各层级行为动词

## 记忆 Remember（L1）
list, define, recall, identify, name, recognize, locate, describe

## 理解 Understand（L2）
explain, summarize, interpret, classify, compare, contrast, exemplify, infer

## 应用 Apply（L3）
use, execute, implement, solve, demonstrate, calculate, apply, practice

## 分析 Analyze（L4）
differentiate, organize, attribute, compare, contrast, examine, deconstruct, distinguish

## 评价 Evaluate（L5）
judge, critique, assess, justify, prioritize, recommend, validate, defend

## 创造 Create（L6）
design, construct, develop, formulate, compose, produce, invent, generate

## 第 2 部分：各层级的出题方法

以下指引原为 FAQ 生成而写；其中的提问起手式、答案特征与层级
区分同样适用于测验题。

## 六个认知层级

### 1. 记忆 Remember（知识）

**定义：** 回忆事实、术语、基本概念和答案。

**认知动作：**
- Define, duplicate, list, memorize, recall, repeat, reproduce, state

**提问起手式：**
- "What is...?"
- "What does [term] mean?"
- "What are the components of...?"
- "Can you list...?"
- "What are the main...?"

**FAQ 示例：**

✓ "What is a Learning Graph?"
✓ "What does MicroSim mean?"
✓ "What are the five levels of intelligent textbooks?"
✓ "What is the ISO 11179 standard?"

**答案特征：**
- 事实性、直截了当
- 取材自术语表或定义
- 50-150 词
- 可附来源链接供进一步了解

**FAQ 中的目标占比：** 20%

---

### 2. 理解 Understand（领会）

**定义：** 解释思想或概念；展示对事实与思想的理解。

**认知动作：**
- Classify, describe, discuss, explain, identify, locate, recognize, report, select, translate

**提问起手式：**
- "How would you explain...?"
- "Why is [concept] important?"
- "What is the difference between...?"
- "How does [concept] work?"
- "Can you summarize...?"
- "What is the main idea of...?"

**FAQ 示例：**

✓ "Why are learning graphs important for textbook design?"
✓ "What is the difference between a glossary and an index?"
✓ "How does scaffolding improve learning outcomes?"
✓ "What's the relationship between Bloom's Taxonomy and question difficulty?"

**答案特征：**
- 解释性、有上下文
- 可比较/对比概念
- 常含 "because" 或 "in order to"
- 100-250 词
- 例子有助于澄清

**FAQ 中的目标占比：** 30%

---

### 3. 应用 Apply（运用）

**定义：** 在新情境中使用信息；用所需技能或知识解决问题。

**认知动作：**
- Apply, build, choose, construct, develop, implement, interview, make use of, organize, solve, utilize

**提问起手式：**
- "How would you use...?"
- "What examples can you find...?"
- "How would you solve...?"
- "How would you show...?"
- "What approach would you use to...?"
- "How would you apply...?"

**FAQ 示例：**

✓ "How do I create a learning graph for my course?"
✓ "What's the best way to use MicroSims in my chapters?"
✓ "How can I apply Bloom's Taxonomy to my quiz questions?"
✓ "When should I use an infographic vs. a MicroSim?"

**答案特征：**
- 程序性、指导性
- 分步骤指引
- 实例具体
- 聚焦「怎么做」
- 150-300 词
- 可含代码或具体步骤

**FAQ 中的目标占比：** 25%

---

### 4. 分析 Analyze（分析）

**定义：** 在思想之间建立联系；确定部分与整体结构或目的的关系。

**认知动作：**
- Analyze, break down, compare, contrast, diagram, differentiate, distinguish, examine, experiment, identify, investigate, relate

**提问起手式：**
- "What is the relationship between...?"
- "What are the parts or features of...?"
- "How does [X] relate to [Y]?"
- "What evidence can you find...?"
- "What is the underlying cause of...?"
- "What patterns can you identify...?"

**FAQ 示例：**

✓ "What's the relationship between concept dependencies and learning order?"
✓ "How do the five levels of textbook intelligence build on each other?"
✓ "What factors determine whether a concept needs a MicroSim?"
✓ "How does prerequisite structure affect chapter organization?"

**答案特征：**
- 分析性、探究性
- 拆解关系
- 识别模式或成因
- 可使用图示或图表
- 200-300 词
- 考虑多个视角

**FAQ 中的目标占比：** 15%

---

### 5. 评价 Evaluate（评估）

**定义：** 为某个决定或行动方案作论证；依据准则与标准作判断。

**认知动作：**
- Appraise, argue, defend, judge, select, support, value, critique, evaluate, assess, recommend

**提问起手式：**
- "Which approach is best for...?"
- "What are the trade-offs of...?"
- "How would you decide between...?"
- "What criteria would you use to...?"
- "How would you prioritize...?"
- "What are the strengths and weaknesses of...?"

**FAQ 示例：**

✓ "Which approach is better for teaching complex concepts: text or MicroSim?"
✓ "What are the trade-offs between comprehensive glossaries and brief definitions?"
✓ "How do I decide which concepts need prerequisite validation?"
✓ "What's the best balance between content depth and cognitive load?"

**答案特征：**
- 评价性、比较性
- 讨论利弊
- 用准则作判断
- 可呈现多个都成立的选项
- 200-350 词
- 有分寸、考虑情境

**FAQ 中的目标占比：** 7%

---

### 6. 创造 Create（综合）

**定义：** 产出新的或原创的作品；把元素重组为新的模式或结构。

**认知动作：**
- Assemble, construct, create, design, develop, formulate, generate, plan, produce, propose, invent

**提问起手式：**
- "How would you design...?"
- "What would happen if...?"
- "Can you create a...?"
- "How could you improve...?"
- "What's the best way to combine...?"
- "How would you adapt [X] for [Y]?"

**FAQ 示例：**

✓ "How would I design a textbook for a completely new subject area?"
✓ "What's the best way to combine learning graphs with adaptive learning?"
✓ "How could I create an innovative assessment beyond traditional quizzes?"
✓ "How would you design a MicroSim to teach a highly abstract concept?"

**答案特征：**
- 创造性、生成性
- 提出新颖方案
- 鼓励试验
- 开放式指引
- 250-400 词
- 建议多种途径

**FAQ 中的目标占比：** 3%

---

## 各类别的目标分布

不同的 FAQ 类别应侧重不同的布鲁姆层级：

### 入门起步（60% 记忆，40% 理解）

聚焦基本事实与课程结构的理解。

**示例问题：**
- "What is this course about?"（理解）
- "What are the prerequisites?"（记忆）
- "How is the textbook organized?"（理解）

### 核心概念（20% 记忆，40% 理解，30% 应用，10% 分析）

定义、理解与应用保持平衡。

**示例问题：**
- "What is a learning graph?"（记忆）
- "Why are concept dependencies important?"（理解）
- "How do I create a concept taxonomy?"（应用）
- "What's the relationship between scaffolding and prerequisites?"（分析）

### 技术细节（30% 记忆，40% 理解，20% 应用，10% 分析）

侧重术语与技术理解。

**示例问题：**
- "What does ISO 11179 mean?"（记忆）
- "How does the glossary validator work?"（理解）
- "When should I use cross-references?"（应用）
- "How do metadata standards improve consistency?"（分析）

### 常见挑战（10% 记忆，30% 理解，40% 应用，20% 分析）

聚焦问题解决与排错。

**示例问题：**
- "Why is my learning graph showing cycles?"（理解）
- "How do I fix circular definitions?"（应用）
- "What causes low concept coverage?"（分析）

### 最佳实践（10% 理解，40% 应用，30% 分析，15% 评价，5% 创造）

侧重应用与高阶思维。

**示例问题：**
- "When should I use a MicroSim vs. a static diagram?"（评价）
- "How do I balance content depth with cognitive load?"（应用）
- "What patterns indicate good chapter structure?"（分析）
- "How could I combine multiple teaching approaches effectively?"（创造）

### 进阶主题（10% 应用，30% 分析，30% 评价，30% 创造）

推向更高认知层级。

**示例问题：**
- "How would you design an adaptive learning system?"（创造）
- "What are the trade-offs of automated vs. manual content generation?"（评价）
- "How do different textbook intelligence levels relate to learning outcomes?"（分析）

---

## 出题指引

### 记忆类问题

**应该：**
- 问具体事实或定义
- 使用术语表中的术语
- 答案保持简短（50-150 词）
- 链接到术语表或相关小节

**不应该：**
- 要求解释或推理
- 要求理解关系
- 问题过于宽泛

### 理解类问题

**应该：**
- 问「为什么」或「如何」
- 要求解释或总结
- 比较/对比概念
- 给出上下文

**不应该：**
- 只问定义（那是记忆）
- 要求应用（那是应用）
- 要求评价或创造

### 应用类问题

**应该：**
- 给出具体情境
- 问 "how would you..."
- 要求分步骤过程
- 含实例

**不应该：**
- 问题停留在抽象
- 只要求理解
- 回避具体语境

### 分析类问题

**应该：**
- 问关系
- 要求识别模式
- 要求拆解为部分
- 比较底层结构

**不应该：**
- 只罗列组成部分（那是记忆）
- 停在表层解释（那是理解）
- 要求价值判断（那是评价）

### 评价类问题

**应该：**
- 要求判断或决策
- 呈现准则或取舍
- 要求给建议
- 考虑多个选项

**不应该：**
- 只呈现一个选项
- 回避准则或论证
- 跳过决策背后的「为什么」

### 创造类问题

**应该：**
- 要求新颖方案
- 鼓励创新
- 要求设计或提案
- 允许开放式回答

**不应该：**
- 限制为单一答案
- 只是组合已有元素
- 规定得太死

---

## 常见错误与纠正

### 错误：标错布鲁姆层级

❌ **问题：** "What is the best way to create a learning graph?"

**错误标注：** 记忆（它并不是要求回忆事实）

**正确标注：** 应用（问的是如何在实践中使用知识）

**更好的表述：** "How do I create a learning graph for my course?"（明确是应用）

---

❌ **问题：** "List the steps in the ADDIE model"

**错误标注：** 应用（它并没有要求使用这些步骤）

**正确标注：** 记忆（要求回忆信息）

---

❌ **问题：** "Explain why Bloom's Taxonomy is useful"

**错误标注：** 记忆（不只是回忆事实）

**正确标注：** 理解（要求解释）

---

### 错误：问题太含糊

❌ "How does it work?"

✓ "How does concept dependency validation work in the learning graph generator?"

---

❌ "What's the difference?"

✓ "What's the difference between a learning graph and a concept taxonomy?"

---

### 错误：一问多问

❌ "What is a MicroSim and how do I create one and when should I use it?"

✓ 拆成三个问题：
- "What is a MicroSim?"（记忆）
- "How do I create a MicroSim?"（应用）
- "When should I use a MicroSim vs. a static diagram?"（评价）

---

## 分布平衡

### 总体目标分布

| 布鲁姆层级 | 目标占比 | 题数（以 100 题计） |
|---------------|----------|-------------------------------------|
| 记忆 | 20% | 20 |
| 理解 | 30% | 30 |
| 应用 | 25% | 25 |
| 分析 | 15% | 15 |
| 评价 | 7% | 7 |
| 创造 | 3% | 3 |

### 可接受偏差

每层 ±10% 以内可接受：

- 记忆：10-30% ✓
- 理解：20-40% ✓
- 应用：15-35% ✓
- 分析：5-25% ✓
- 评价：0-17% ✓
- 创造：0-13% ✓

超出 ±10% 即为失衡，应当纠正。

### 如何调整

**记忆/理解题太多？**
- 把一部分改写成应用题，问 "How do I..."
- 增加情境题
- 增加排错题

**分析/评价/创造题太少？**
- 增加比较题
- 加入取舍讨论
- 要求给建议或做设计
- 呈现复杂情境

**创造题太多？**
- 把一部分改成评价（取舍、建议）
- 把一部分改成分析（关系、模式）
- 记住创造应占小比例（目标 3%）

---

## 质量检查清单

逐题核验：

- [ ] **布鲁姆层级正确：** 问题与认知动作匹配
- [ ] **表述清晰：** 具体、可检索、无歧义
- [ ] **类别恰当：** 归入正确的小节
- [ ] **答案完整：** 充分回答该问题
- [ ] **长度适当：** 100-300 词（大多数问题）
- [ ] **含示例：** 40% 的问题带例子
- [ ] **含链接：** 60% 的问题链接到来源
- [ ] **术语一致：** 使用术语表术语
- [ ] **难度适当：** 符合该类别的预期
- [ ] **无重复：** 不与别处的题目重复
