# 科学 — 分层教学法

当学科为**科学**时由 `k12-lesson-differentiation` 加载。

## 识别源课程

三个场景——识别哪个适用：

**场景 A — 源课程存在于之前的对话中**
如果本对话前文中已经生成或讨论过一节课，直接使用它。不要重复要求教师分享。

**场景 B — 教师上传源课程**
先读文件。确认：年级、表现预期 (Performance Expectation, PE)、锚定现象、课程结构与阶段、前置的 SEP 和 CCC。如果第一次尝试无法读取文件，清楚地说明错误并请教师重新分享。绝不静默编造一节课。

**场景 B2 — 教师用 URL 链接源课程**
先抓取 URL 并阅读其内容。然后与场景 B 完全一样地确认年级、表现预期 (PE)、锚定现象、课程结构与阶段，以及前置的 SEP/CCC。如果抓取失败或返回不可用内容，清楚地说明错误并请教师粘贴课程文本或上传文件。绝不静默编造一节课。

**抓取课程只完成第 1 步——它不替代标准锚定。** 继续执行第 2 步——锚定标准。URL 抓取之后跳过第 2 步，与上传课程后跳过它一样属于严重失误。

**场景 C — 没有源课程**
继续之前询问：
> "很乐意帮你做分层。你心里有具体的一节课吗？你可以粘贴过来、分享文件，或者告诉我年级 + 主题 + 标准，我据此来做。"

**识别 OpenSciEd 使用情况。** 满足以下任一条件即为 OpenSciEd 已确认：
1. 教师明确说明："OpenSciEd"、"OSE"、"我们用的是 OpenSciEd"
2. 上传的源课程包含 OSE 结构标志：
   - 提到驱动性问题板 (Driving Question Board, DQB)
   - 科学家圆桌 (Scientists Circle) 或共识模型活动
   - 学习目标中出现"我们要弄明白什么？"的措辞

**教师的明确表述优先于所提供课程中的信号。** 如果教师说"我用
OpenSciEd"，而提供的课程带有任何课程教材品牌标记，按 OSE 已确认处理。

---

## 标准锚定

遵循 SKILL.md 中的**第 2 步 — 锚定标准**：如果 Learning Commons 知识图谱
已连接，使用 `references/learning-commons-kg.md` 的科学部分；如果未连接，
依据最佳知识继续并在教师教案中加上免责声明脚注。

**州感知的标准：** 当第 0 步已知州时，在知识图谱调用中传入相应的
jurisdiction。

## 分层规则

把全部八条规则应用到每一节分层课程。

### R1 — 输出结构

**1 份整合的面向教师教案 + 3 份纯粹的学生练习页。绝不产出 3 份独立的按水平编排的教案。**

教案是一份教师可以替代（或配合）源课程使用的单一文档。
按课程阶段组织。所有学生一起学习的阶段（导入现象、
意义建构讨论、综合）只写一遍。学生独立学习的阶段
（探究、解释/CER 任务）以叠放的带标签块展示全部三个层级。

不要产出 3 份各自混杂教师注释和学生任务的文档。

### R2 — 三维范围保全

**每个层级都针对原 PE。每个 SEP、CCC 和 DCI 要素都必须在所有层级中出现——包括难题情形。**

对于得州以外的各州，NGSS 的全部三个维度都不可妥协：
- **SEP（科学与工程实践）**：同一前置实践出现在每个层级的任务中（例如，如果本课前置于"建构解释"，每个层级都要建构解释）
- **CCC（跨学科概念）**：每个层级都应用同一跨学科概念视角
- **DCI（学科核心观念）**：同一学科核心观念是所有层级的内容目标

为低水平学生缩减认知范围——去掉一个维度、用阅读代替探究、
或简化现象——不是分层。

**Below 层级的参与度必须保全。** 不要给 At/Above 层级有趣的开放式
探究，却给 Below 层级一张结构化练习单，让别的学生做科学。
所有层级探究同一个现象——只是支持不同，不是任务不同。

### R3 — 通过"观察 → 表征 → 解释"进阶向上教学

**低水平支架把学生向上引导到年级水平的解释，而不是绕过它。不是"只是更简单的任务"。**

| 层级 | O→R→E 进阶中的切入点 |
|---|---|
| Below | 观察 → 表征（结构化，有支持），然后借助有支架的 CER 框架进入解释 |
| At | 表征 → 解释（标准 CER） |
| Above | 解释 → 拓展（概括、反例现象、定量化、工程应用） |

**低水平支架必须：**
- 帮助学生进入并理解他们的观察（结构化观察提示、带标注的图示）
- 为从观察到数据表征的跨越提供支架（引导式数据表、待填充的半成品模型模板）
- 借助句子支架支持 CER 的建构——而不是提供解释本身

**意义建构冲突不可妥协。** 不要为低水平学生抹平先前概念与观察
之间的认知冲突——帮助他们把它说出来：*"我原以为 ____，
但我观察到 ____。现在我认为 ____。"*

**确定概念性预备知识：**
使用 PE 中的 DCI 代码。NGSS 的 DCI 进阶是明确的——同一个核心
观念在 K–2、3–5、6–8 和 9–12 以递增的复杂度出现。确定先前
年级段的学生为这个 DCI 建立了什么概念模型，把它作为低水平
支架的桥梁。在三维地图 (Three-Dimensional Map) 中把它点名为预备知识。
它通常是同一年级段内或相邻年级段的概念性依赖，而不是
跨多年级的连锁链条。

- ✓ "低于水平组用 [先前年级段关于能量传递的模型]；学生把该表征应用到解释新现象上。"
- ✗ "低于水平组做更容易版本的探究。"

### R4 — 低水平支架

**目标是在意义建构中保留有生产力的挣扎，而不是消除它。支架支持学生穿过探究，而不是绕过探究。绝不把低水平学生从探究中分流出去。**

要避免的失败模式：

- ❌ 在学生探究之前预先告知解释。
- ❌ 为低水平学生移除探究——在其他学生探究时给他们阅读材料或视频。
- ❌ 简化现象——所有层级观察同一个现象。
- ❌ 关键词策略："看到'热'这个词——那就是能量传递。"
- ❌ 泄露答案的辅导站。
- ❌ 只用读写支架代替科学实践支架。

可接受的支架：

- ✓ **引导/分析问题**，按观察 → 联系 → 意义排序：*"什么变了？什么没变？你认为是什么引起的？"*
- ✓ **CER 句子支架**：*"我的主张是 ____。我的证据是 ____。它支持我的主张，因为 ____。"*
- ✓ **半成品模型模板**——学生填充的结构化图示，而不是让他们标注的完成图。
- ✓ **词汇支持**——任务顶部的词库或简释（页眉级）。附日常语言定义。
- ✓ **结构化观察表**，带明确提示（*"画出你看到的。给任何变化加标注。圈出任何意外的现象。"*）
- ✓ **引导式数据表**，列标题和单位已预填——学生填观察，不填解读。
- ✓ **先前知识激活**——*"还记得我们弄明白 [先前概念] 的时候吗？它可能怎样帮你解释你现在看到的现象？"*

#### 支架密度上限

**嵌入支架上限为每个任务 1–2 个。不得超过。**

| 类型 | 是否计入上限？ |
|---|:-:|
| 嵌入式——印在每道题或每个任务上（组织图、句子支架、提示文字） | 是 |
| 页眉级特征——词汇框、练习页顶部的 CER 框架 | 否 |
| 教师侧工具——按需提供的辅导站、个别指导话术 | 否 |

先选一个主支架。只有当第二个支架贡献了真正不同的模式时
才加。如果第二个覆盖同样的认知范围，删掉它。

### R5 — 必需的教学基础设施

**每节分层科学课必须包含全部五项。内联嵌入教案之中。**

| 要素 | 是什么 | 在教案中的位置 |
|---|---|---|
| **形成性检查** | 具体的课中或课尾提示——出门票或 CER 检查。不是"巡视观察"。 | 内联在其发生的阶段中 |
| **锚活动** | 给先完成学生的对齐标准的拓展。不是打发时间的杂活——必须要求前置的 SEP。以面向学生的写法写进 `shared.anchor_activity` 并印在每份练习页上——只作为教案描述存在的锚活动属于失败。 | 教案末尾 + 全部三份练习页 |
| **弹性分组用语** | 层级归属与本课的证据挂钩；课中可根据形成性检查修订。 | 教案头部的紧凑标注框 |
| **分水平的迷思概念注释** | 各水平的常见科学迷思概念 + 教师个别指导动作 + 小组辅导信号。 | 内联标注，置于每个分层活动块之内——每水平最多 2 句 |
| **意义建构冲突提示** | 一个明确引出先前概念与观察之间张力的提示。 | 嵌入探究或 CER 任务中 |

**如果 OSE 已确认，另有三个要素在所有层级都不可妥协：**
- **共识模型**——所有层级都为班级共识模型做贡献并修订它。Below：半成品模型模板。At：空白模型。Above：扩展模型以解释一个额外情形。
- **驱动性问题板**——所有层级都向 DQB 添加内容并引用它。
- **CER 结构**——各层级一致；只有框架支持不同（Below：句子支架。At：只有提示。Above：增加反驳 + 驳论。）

此外：**每份学生练习页都以一个反思提示收尾，三个层级都有：**
*"你还在好奇什么？"* 把它存为 `shared.reflect_prompt`，并在教案中
每个层级的**练习页任务**一行中点名它——教案从未提及的
已打印任务属于失败。

### R6 — 隐形调整

**各层级同一现象、同一探究、同一核心解释任务。只有支持不同。**

所有层级观察同一个现象。所有层级用同样的材料和流程探究。
在整合教案中，共享的探究和现象在"全体学生 (ALL STUDENTS)"下
只出现一次。各层级块只展示不同之处——支架、个别指导话术、
拓展。

不要在每个层级块中重述探究全文——引用它，只描述不同之处。

**不要向学生宣布支架的撤除。** 如果任务 1 用了结构化观察表而
任务 3 没用，它的缺席是静默的——不加标签、旁白或评论（例如
不写"（这次没有模板）"或"试试不用框架来做"）。支架只是不出现；
学生按任务本来的样子面对它。

数字、数据集和材料用量默认各层级一致。只有 Below 层级可以调整，
且必须完整保留探究结构。

### R7 — 层级内渐进撤除支架

**每个水平的练习页按渐进认知要求编排任务顺序。**

#### 低水平支架撤除模式

| 任务 | 嵌入支架 | 模式 |
|---|:-:|---|
| 观察任务 | 至多 2 个 | 结构化 |
| 表征任务 | 至多 1 个 | 有引导 |
| CER 任务 | 0–1 个嵌入式（页眉级框架可以） | 有生产力的挣扎 |
| 反思提示 | 0 | 独立 |

#### 高水平拓展质量检验

每个高水平拓展都必须回答：**它要求了什么达到水平的学生
没有在做的新思考？**

一个真正的拓展至少要求以下之一：
- **工程应用**：运用该科学概念设计一个解决方案
- **反例现象或异常情形**：现象表现不同的情境，需要概括
- **定量化**：把定性解释与数学关系联系起来（3 年级及以上）
- **后续 PE 预览**：DCI 进阶中的下一个 NGSS PE——概念要素，而不只是词汇
- **科学论证**：评估一个竞争性解释、找证据挑战自己的主张，或写一段驳论
- **社会/伦理维度**：这个现象如何与现实世界的问题或决策相联系？（6–12 年级）

以下情况驳回：只是更多同类探究、只是更长的练习页，或只是
换记号。

### R8 — 范围与默认值

**如果未指定层级范围，生成之前问一个合并问题：**

> "我会把这节课分成低于 / 达到 / 超出年级水平三个层级——分这三个
> 合适吗？还有没有什么我该知道的具体学习者需求（ELL 等级、
> IEP 目标领域）？如果没有，我会应用 UDL 默认值（所有层级都有
> 句子支架和词汇支持）。"

如果范围已被指定，静默采用默认值并继续。

**未指定时静默采用的默认值：**
- 层级：低于 / 达到 / 超出
- UDL 特征：**全部三份**学生练习页都有 CER 句子支架和词汇表
  （不只 Below——量规 O5）
- 范围：完整课程（所有阶段 + 出门票 / CER 任务）
- OSE 结构：OSE 已确认时应用；否则不应用

**当没有形成性评估数据可用时**，默认低水平画像如下：
- 对现象有观察通道，但还叫不出机制的名字——有感知通道但缺解释性语言
- 很可能持有该 DCI 的至少一个常见迷思概念；意义建构冲突框架
  （*"我原以为 ____，但我观察到 ____"*）是主要支架
- 能做出观察，但需要结构才能独立把它与模型或 CER 联系起来
- （按 R3 确定的）最近概念性预备知识可能不牢固

据此设计默认低水平支架：结构化观察提示 → 引出迷思概念的
句子支架 → CER 框架。不要预先为解释内容本身搭支架。

如果推断的缺口宽于段内的一步概念跨越，在后续步骤
(Next Steps) 块中加一条提示：课程层级的分层之外可能还需要
Tier 2/3 干预支持。

生成默认分层教案之后，向教师追问：*"你有没有上节课的
记录——观察笔记、CER 样本或出门票结果——能告诉我哪个迷思概念
正在起作用，或者学生是能进入现象但卡在解释上？"* 这可以把
假定的迷思概念换成已确认的，并弄清楚学生卡在
观察→表征这一步还是表征→解释这一步，从而改变支架的
着力点。FA 数据在科学中很少推翻默认方案，但能切实使其更精准。

---

### 文档内容 — 整合教案（`id: teacher_plan`）——最多 5 页

按阶段组织。沿用源课程的阶段结构（例如导入现象 →
探究 → 意义建构讨论 → 解释任务 → 综合 → 出门票）。
不要发明源课程中没有的阶段。

下方大纲定义本文档 `sections` 的内容与顺序：每个 `##`
标题成为一个章节，其正文成为该章节的内容块（PE、
迷思概念和出门票用 `from_shared` 块；阶段用 `phase_header` 块；
粗体字段用 `labeled` 块）。

**篇幅预算：渲染后约 2,000 词（即 5 页上限的实际含义）。** 先收紧
阶段和层级部分，再动收尾部分（设计依据、后续步骤）——
最常见的超支是练习页任务行复述了练习页内容而不是点名它。
**"设计依据 (1)"和"设计依据 (2)"是必需的，不能为了满足篇幅预算
而删掉——先削减阶段或层级部分的文字。**

```markdown
# Differentiated Lesson Plan: [Lesson Title]

**PE:** [verbatim]  **Grade:** [X]  **Duration:** [X min]
**Anchoring Phenomenon:** [one sentence]
*Learner needs: [If no specific needs were provided: "UDL defaults applied — CER sentence supports and vocabulary support across all tiers." If learner needs were specified, describe them here instead.]*

## Learning Objective
[One statement covering all tiers. For OSE-confirmed: "Students will figure out [DCI element] by using [SEP] to make sense of [phenomenon]."]

## Three-Dimensional Map
- **SEP(s):** [name + ≤10-word gist — the PE is already quoted verbatim in the header]
- **CCC(s):** [name + ≤10-word gist]
- **DCI:** [brief]
- **Conceptual prerequisite:** [code + ≤10-word gist] — grounds Below scaffolds
- **Forward PE:** [code + ≤10-word gist] — grounds Above extension

(Density rule applies: the PE appears verbatim exactly once, in the header. Never re-paste
full standard text in this map — code + gist only.)

## Tier Grouping
[One bullet per tier, ≤15 words each: the placement signal for that tier.]
[Then ONE sentence: evidence basis ("Based on prior CER exit ticket on [PE]" or "Default
profile applied — no FA data available").]
*Tier assignments are revisable — revisit after the formative check.*

---

## [Phase Name — whole class]
[Teacher facilitation moves, key questions, what NOT to do. For OSE-confirmed: consensus model update move + DQB reference.]

## [Phase Name — tiered activity]
**ALL STUDENTS:** [shared setup — same phenomenon, same materials; ONE sentence]

[ONE `table` block — never three labeled paragraph stacks. Columns: Below (Group A) / At (Group B) / Above (Group C).
Two rows:
- **Students do** — ≤25 words per cell, fragments not sentences: the task path and the
  scaffolds in play (plus the extension prompt in the Above cell).
- **Worksheet tasks** — ≤40 words per cell, written LAST: read that tier's FINAL worksheet
  document's blocks top-to-bottom and name every printed task in order — investigation/CER
  tasks by name with their printed scaffolds (e.g. "Observation sheet (structured), CER
  paragraph (frame)"), every tier-only add-on or extension sub-part by its printed heading,
  exit ticket, "If you finish early" anchor task, Reflect prompt. List items; don't restate
  their text. Name nothing unprinted — no "on request" supports, no planned organizer the
  worksheet dropped. Never copy another tier's cell.]

[Then ONE `callout` (note style): misconception watch + conferring move — one sentence per
tier that needs one, ≤2 sentences per level. Never bury these inside the table cells or a
paragraph.]

## Formative Check
[Two required elements:
1. **Mid-lesson checkpoint:** A specific check during the investigation or sense-making phase — name the trigger or artifact (e.g., "After the observation table is complete, scan three notebooks: if students are describing observations without connecting to the phenomenon, pause and use the CCC prompt before the CER task"). 'Circulate and observe' does not pass.
2. **Exit ticket with explicit sort criteria:** State what a student must produce or demonstrate for THIS lesson's PE, e.g.: "Got it — [e.g., writes a CER that names the specific mechanism and cites data from the investigation] / Almost there — [e.g., claim and evidence present but reasoning does not connect to the DCI] / Needs re-teaching — [e.g., cannot state a claim from the data without prompting]." Generic bucket labels without lesson-specific criteria do not pass.]

## Anchor Activity
[`from_shared: anchor_activity` — the same student-facing task printed on every worksheet — plus one teacher-only line: when to deploy it; must require the foregrounded SEP]

## Why this works (1)
[One specific tier design choice + reasoning]

## Why this works (2)
[A second specific tier design choice + reasoning]

## Next Steps
**Got it (exit ticket passes):** [connect to forward standard or upcoming lesson]
**Almost there:** [targeted small-group or conferring move — specific gap to address]
**Needs re-teaching:** [specific reteach strategy or Tier 2/3 flag if gap is persistent]

```

### 文档内容 — 练习页（`id: worksheet_group_a` / `worksheet_group_b` / `worksheet_group_c`）

任何练习页中都不含教师注释、观察要点或设计依据。词汇、
CER 句子支架、"先完成的话"锚活动和反思提示都从 `shared`
拉取，因此在结构上各层级完全一致。

在印刷页面上，绝不要把任何东西标注为"CER"或"意义建构"——
那是教师用语（见 `references/output.md`，面向学生的用语）。
组织图的标签写作*主张 / 证据 / 推理*；意义建构框架
以*"检查你的想法"*引入。

| 水平 | 练习页特征 |
|---|---|
| Below | 与 At 相同的现象和探究。支架按 R4 嵌入，撤除模式按 R7。结构化观察表、半成品模型模板、页眉级的 CER 句子支架。 |
| At | 保留源练习页或仅做轻度重排。标准 CER 提示。 |
| Above | 同一探究 + 按 R7 的拓展提示。CER + 反驳 / 驳论提示。 |

```markdown
# [Group A / Group B / Group C] — [Lesson Title]

**Name:** _________________ **Date:** _________

## Vocabulary
[`from_shared: vocabulary` — the renderer formats the term–meaning pairs itself; never type a pipe-character table into a `text` field]

**You can use these sentence supports:**
- "I claim ____. My evidence is ____. This supports my claim because ____."
- "I thought ____ but I observed ____. Now I think ____."

---

[Tasks pulled ONE AT A TIME, each with its scaffold directly above it — per task N: at most
ONE scaffold block (Below only, "For Task N — ...", per R4/R7 fade), then
`{"type": "from_shared", "key": "tN", "label": "N"} followed by a workspace block`. Investigation/CER task text
identical on all three tiers; never re-typed. Writing space after each task is automatic —
do not add answer boxes for tasks.]
[Tier-only add-ons (e.g. Above "Go further" extension) as their own headed sections]

---

## If you finish early
[`from_shared: anchor_activity` — identical block on all three tiers]

## Reflect
[`from_shared: reflect_prompt` — "What are you still wondering about?"]
```

---

## 编写 differentiation.json — 科学映射

- `shared.subject`：`"Science"`
- `shared.standard_code` / `shared.standard_text`：表现预期，逐字引用
- `shared.anchor_task`：锚定现象
- `shared.t1`..`tN`：所有层级共享的探究与 CER 任务，一个任务一个键——分面向 {teacher: "难度和要观察什么，用平实的句子", student: <任务>}
- `shared.sentence_frames`：CER 框架，纯文本，空白按手写量留好，与任务的书写空间放在一起
- 教师文档：**整合的分层教案**（按阶段组织），最多 5 页；练习页每份最多 2 页
- **版权：** 绝不逐字复制 OpenSciEd (OSE) 面向学生的文本——这适用于取材自 OSE 材料的探究指令、现象描述和 CER 提示。

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
