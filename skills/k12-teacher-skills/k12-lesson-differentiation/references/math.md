# 数学 — 分层教学法

当学科为**数学**时由 `k12-lesson-differentiation` 加载。

## 识别源课程与课程教材

**识别 IM 使用情况。** 在做任何事之前，检查教师是否在使用 Illustrative Mathematics。在对话的任何地方寻找信号：明确点名（"IM"、"Illustrative Mathematics"、"IM 360"）、IM 专属术语（MLRs、cool-down、"Stronger and Clearer Each Time"、导入—探究—讨论结构、IM 单元或课次引用），或上传的 IM 教师用书。如果确认，全程视为 **IM 已确认**——在教师教案中使用 IM 的话语语言和结构。

然后识别适用哪个场景：

**场景 A — 源课程存在于之前的对话中**
如果本对话前文中已经生成或讨论过一节课，直接使用它。不要重复要求教师分享。

**场景 B — 教师上传源课程**
先读文件。确认：年级、学科、标准、学习目标、课程结构。如果第一次尝试无法读取文件，清楚地说明错误并请教师重新分享。绝不静默编造一节课。

**场景 B2 — 教师用 URL 链接源课程**
先抓取 URL 并阅读其内容。然后与场景 B 完全一样地确认年级、学科、标准、学习目标和课程结构。如果抓取失败或返回不可用内容，清楚地说明错误并请教师粘贴课程文本或上传文件。绝不静默编造一节课。

**抓取课程只完成第 1 步——它不替代标准锚定。** 继续执行第 2 步——锚定标准。URL 抓取之后跳过第 2 步，与上传课程后跳过它一样属于严重失误。

**场景 C — 没有源课程**
继续之前询问：
> "很乐意帮你做分层。你心里有具体的一节课吗？你可以粘贴过来、分享文件，或者告诉我年级 + 主题 + 标准，我据此来做。"

---

## 标准锚定

遵循 SKILL.md 中的**第 2 步 — 锚定标准**：如果 Learning Commons 知识图谱
已连接，使用 `references/learning-commons-kg.md` 的数学部分；如果未连接，
依据最佳知识继续并在教师教案中加上免责声明脚注。

## 分层规则

把全部八条规则应用到每一节分层课程。

### R1 — 输出结构

**1 份完整连贯的面向教师分层教案 + 3 份纯粹的学生练习页。绝不产出 3 份按水平混合编排的教案。**

混合模式——3 份按水平各自混杂教师注释和学生题目的文档——
是一种具体的失败模式。教师教案在一份文档中覆盖所有水平；
练习页只含学生内容。

### R2 — 标准范围保全

**每个层级都针对原标准。标准的每个要素在所有层级中都保留——包括难题情形。**

标准中最难的情形恰恰是低水平学生最需要在支架支持下
遇到的东西，而不是要被砍掉的情形。为低水平学生缩减标准的
认知范围不是分层。

**Below（低于水平）层级的参与度必须保全。** 不要把有趣的真实问题
情境分给 At/Above（达到/超出水平），把程序性操练分给 Below。同样的
情境、同样的导入钩子——只是支持不同。这既是严谨性要求，
也是公平性要求。

### R3 — 通过具名预备知识向上教学

**低水平支架把学生向上引导到年级水平的学习，锚定在具名的预备知识上。不是"只是更容易"。**

- ✓ "低于水平组用 [视觉模型] 来显现来自 [先前标准] 的 [概念]；学生把该表征应用到年级水平的题目上。"
- ✗ "低于水平组用更简单的数字 / 更短的文本 / 更少的步骤。"

#### 标准框架识别

在确定预备知识之前，先判断教师的标准属于哪个框架。按以下
回退链执行，在第一个能产出结果的步骤停下：

1. 知识图谱查询——用教师的标准代码调用 find_standards_progression_from_standard。如果知识图谱为教师的框架返回了前序标准，逐字使用它。无论框架是 CCSS、TEKS 还是其他州体系，这都是首选路径。

2. **部分匹配** — 最接近的 Common Core 预备标准及其**学习成分**（标准拆解成的更小子技能）。教师的框架没有完全对应项，
因此把该标准作为 CCSS 参照来呈现，并用学习成分来挑选
Below 层级支架所基于的具体先备子技能。
**非 CCSS 框架的输出规则：** 采用 CCSS 参照路径时，不要把 CCSS
代码放在教师教案正文的主要位置。改用平实语言描述：
- 在分层概览 (Differentiation Overview) 中："低于水平组的支架建立在先前对
  [概念描述] 的理解之上，它是 [年级水平概念] 的预备知识。"
- 在预备知识锚定 (Grounded in prerequisite) 中："预备概念：[平实描述]——参照
  [CCSS 参照代码]，使用它是因为 TEKS 进阶尚未收录进知识图谱。"
- 把 CCSS 代码移到教师教案底部的一条脚注中："* 预备知识
  锚定使用 CCSS [代码] 作为与 TEKS [教师的标准代码] 最接近的对齐标准。"
得州教师的教案不应在显眼位置出现 CCSS 代码。

3. **概念级回退** — 如果不存在 CCSS 对应项，用平实语言把预备知识
描述为一个概念：*"预备概念：[描述]——该州框架没有可用的具体
标准。"*

教师教案中**预备知识锚定**一行必须反映实际走的是哪条路径。绝不让
这一行留空或泛泛而谈——即使没有标准代码，概念级描述也总是
可以做到的。

**为什么预备知识在数学中不可妥协。** 与 ELA 或科学不同——那里
"同一目标、不同通道"常常已经足够——数学学习是累积的：
缺少先前年级概念的学生无法仅靠支架理解当前概念。
预备知识缺口通常才是真正的障碍，而不是当前年级的概念。
像其他学科那样绕开预备知识识别来设计，在数学中会是一种
教学法上的妥协。

#### CRA 切入点

| 层级 | CRA（具象—表征—抽象）切入点 |
|---|---|
| Below | 具象（教具或实物模型）→ 表征（图示、视觉模型） |
| At | 表征 → 抽象（符号、数值） |
| Above | 抽象 → 联结（概括、结构性洞见、后续标准） |

### R4 — 低水平支架

**支架支持思考而不泄露答案。绝不给泄露答案的提示。绝不用关键词策略。**

失败模式：
- ❌ 关键词策略（"看到'一共'——那就是要加起来"）——破坏那些专门考查学生是否依赖捷径的标准
- ❌ 在概念理解之前预教算法
- ❌ 预填好的模板，只留下答案空白
- ❌ 原任务要求开放式产出时改成选择题

可接受的支架：
- ✓ 句子支架："我知道 ____ 和 ____。我不知道的部分是 ____。"
- ✓ 与数学概念匹配的视觉组织图（见表）。
- ✓ 衔接抽象任务的教具或具象提示（按 R3 的 CRA）
- ✓ 词汇词库（用于词汇，而不是用于选择答案）
- ✓ 降低复杂度但带明确的迁移步骤："先用这些数试试，然后应用到原题上。"

#### 概念 → 主要视觉模型

| 数学概念类型 | 主要视觉模型 |
|---|---|
| 部分—整体 / 加法推理 | 带状图或部分—整体图 |
| 乘法 / 比值 / 比率推理 | 双数轴或比值表 |
| 数轴上作为量的分数 | 数轴 |
| 面积 / 乘法结构 | 面积模型或阵列 |
| 比例关系 / 线性函数 | 数值表或坐标图 |
| 代数结构 / 方程推理 | 方程天平模型或变量表征 |
| 几何关系 | 带标注部分的标示图 |

#### 支架密度上限

**嵌入支架上限为每题 1–2 个。**

| 类型 | 是否计入上限？ |
|---|:-:|
| 嵌入式——印在每道题上（组织图、句子支架、提示文字） | 是 |
| 页眉级——词汇框、练习页顶部的句子支架 | 否 |
| 教师侧——按需提供的教具、个别指导话术 | 否 |

先选一个主支架。只有当第二个支架贡献了真正不同的
模式时才加。如果第二个与主支架做的是同样的认知工作，删掉它。

### R5 — 必需的教学基础设施

**每节分层课程必须包含全部四项：**

| 部分 | 是什么 | 位置 |
|---|---|---|
| **形成性检查** | 分层出门票或课中检查提示。不是"巡视学生"。 | 教师教案 + 各水平练习页 |
| **锚活动 (Anchor activity)** | 给先完成学生的对齐标准的任务。不是打发时间的杂活。以面向学生的写法写进 `shared.anchor_activity` 并印在每份练习页上——只作为教案描述存在的锚活动属于失败。 | 教师教案 + 全部三份练习页 |
| **弹性分组用语** | 层级归属与本课的证据挂钩，明确可在形成性检查之后修订。不是固定的能力轨道。 | 教师教案 |
| **分水平的迷思概念注释** | 错误模式 + 教师提示 + 小组辅导信号。有知识图谱来源时优先使用。 | 教师教案 |

**每份练习页都以一个开放式反思提示收尾，三个层级都有**——
例如"解释你的思考过程"、"你用了什么策略，为什么？"对任何层级都
不可省略。把它存为 `shared.reflect_prompt`，并在教师教案中每个层级的
**练习页任务 (Worksheet tasks)** 一行中点名它——教案从未提及的
已打印任务属于失败。(Rubric R3.)

### R6 — 隐形调整

**各层级同一故事 / 同一情境 / 同一核心问题。只有支持不同。**

可以不同的：练习页上的支架；教师个别指导支持；拓展提示的深度。

绝不能不同的：问题情境；核心问题；标准所针对的结构性挑战。

**不要向学生宣布支架的撤除。** 如果第 1 题有支架而第 3 题没有，
它的缺席是静默的——不加标签、旁白或评论（例如不写
"（这次没有组织图）"或"试试不用图来做"）。支架只是不出现；
学生按题目本来的样子面对它。

默认使用同样的数字。只有 Below 层级可以换数字，且必须完整保留
数学结构——不要消除关键挑战（例如不要把分数换成整数）。

### R7 — 层级内渐进撤除支架

**每份练习页按渐进认知要求编排题目顺序。**

#### 低水平支架撤除模式

| 题目 | 嵌入支架 | 模式 |
|---|:-:|---|
| 第 1 题 | 至多 2 个 | 有支架 |
| 第 2 题 | 至多 1 个 | 有引导 |
| 第 3 题及以后 | 0 个嵌入式 | 独立 |
| 出门票 | 0–1 个 | 掌握度检查 |

#### 高水平拓展质量检验

每个高水平拓展都必须回答：**它要求了什么达到水平的学生
没有在做的新思考？**

| 类型 | 它要求什么 |
|---|---|
| 新的认知操作 | 达到水平在应用；超出水平在分析、评价或创造（布鲁姆/DOK 层级上移） |
| 结构性洞见 | 达到水平当作单个实例处理的概括、等价或逆关系 |
| 后续标准预览 | 来自更高年级标准的真实概念要素——不只是记号或词汇 |
| 开放生成任务 | 学生自己编题、设计反例，或从零构建论证 |

以下情况驳回：只是换记号、只是更多同类题，或只是换个说法。

### R8 — 范围与默认值

**如果未指定层级范围，问一个合并问题：**

> "我会把这节课分成低于 / 达到 / 超出年级水平三个层级——分这三个
> 合适吗？还有没有什么我该知道的具体学习者需求？如果没有，
> 我会应用 UDL 默认值（所有层级都有句子起始句和词汇支持）。"

**静默采用的默认值：**
- 层级：低于 / 达到 / 超出
- UDL 特征：**全部三份**学生练习页都有句子起始句和词汇表
  （不只 Below——量规 O5）
- 范围：完整课程，含出门票

**FA 追问提示——生成默认教案之后询问：**

> "你有没有出门票结果、诊断分数，或学生卡在哪里的记录——
> 比如他们是理解了概念但程序上丢了分，还是对概念本身的
> 意思显得困惑？"

这个提示在分层教案交付*之后*触发，而不是之前。在数学中，FA 数据
可以改变哪种支架类型合适（概念性还是程序性），而不只是
微调现有方案——这是所有学科中风险最高的追问。即使是
非正式的教师观察（"我一展示面积模型他们就愣住了"）也是
定位预备知识热身的有用信号。

---

### 文档内容 — 教师教案（`id: teacher_plan`）——最多 3 页

**篇幅预算：渲染后约 1,200 词（即 3 页上限的实际含义）。** 先收紧层级
部分和概览，再动收尾部分（弹性分组、设计依据、后续
步骤）——最常见的超支是练习页任务行复述了练习页内容
而不是点名它。**"设计依据 (1)"和"设计依据 (2)"是必需的，
不能为了满足篇幅预算而删掉——先削减层级部分的文字。**

下方大纲定义教师教案文档 `sections` 的内容与顺序：
每个 `##` 标题成为一个章节，其正文成为该章节的内容块
（标准、迷思概念和出门票用 `from_shared` 块；粗体字段用
`labeled` 块）。

```markdown
# Differentiation Plan: [Lesson Title]

**Standard:** [verbatim]  **Grade:** [X]  **Duration:** [X min]  **Curriculum:** [IM / General]
*Learner needs: [If no specific needs were provided: "UDL defaults applied — sentence supports and vocabulary support across all tiers." If learner needs were specified, describe them here instead.]*

## Learning Objective
[Same objective across all tiers — preserved from source lesson]

## Differentiation Overview
[1 short paragraph, ≤3 sentences: approach, prerequisite named by code + short gist,
forward standard named by code + short gist. Never paste full standard text here — the
target standard is already verbatim in the header. Use KG-returned state standard (preferred when state is known and KG has it), CCSS proxy with reference in footnote, or concept-level fallback.]

## Tier Design
[ONE `table` block — never three labeled paragraph stacks. Columns: Below (Group A) / At (Group B) / Above (Group C).
Rows (a cell may be "—" where a field doesn't apply to that tier):
- **Grounded in** — Below: prerequisite by code + gist (or "CCSS proxy: [code]" / "Prerequisite
  concept: [description]" per whichever R3 path applied). Above: forward standard by code +
  gist. At: "—".
- **Scaffolds / extension** — fragments, ≤25 words per cell: Below scaffolds in play; At
  supports; Above extension + which R7 quality type it meets.
- **Conferring move** — one specific prompt per tier.
- **Worksheet tasks** — ≤40 words per cell, written LAST: read that tier's FINAL worksheet
  document's blocks top-to-bottom and name every printed task in order — problems by number
  with their printed scaffolds (e.g. "P1 (tape diagram + frame), P2 (frame), P3"), every
  tier-only add-on or extension sub-part by its printed heading, exit ticket, "If you finish
  early" anchor task, Reflect prompt. List items; don't restate their text. Name nothing
  unprinted — no "on request" supports, no planned organizer the worksheet dropped. Never
  copy another tier's cell.]

[Then ONE `callout` (note style): misconception watch — pattern + teacher prompt, ≤2
sentences per tier that needs one. Never bury these in the table or a paragraph.]

## Formative Check
[Two required elements:
1. **Mid-lesson checkpoint:** A specific check during work time — name the trigger or artifact (e.g., "After P2, scan whiteboards: if fewer than half show a correct representation, pause and remodel with a tape diagram before P3"). 'Circulate and observe' does not pass.
2. **Exit ticket with explicit sort criteria:** State what a student must produce or demonstrate to land in each bucket for THIS lesson, e.g.: "Got it — [e.g., solves a parallel problem and explains strategy in a sentence] / Almost there — [e.g., correct answer but no explanation or one step missing] / Needs re-teaching — [e.g., cannot set up the representation independently]." Generic bucket labels without lesson-specific criteria do not pass.]

## Anchor Activity
[`from_shared: anchor_activity` — the same student-facing task printed on every worksheet — plus one teacher-only line: when to deploy it and why it requires mathematical reasoning]

## Flexible Grouping
[One bullet per tier, ≤15 words each: the placement signal for that tier.]
[Then ONE sentence: evidence basis (e.g., "Placed based on prior exit ticket on [standard]"
or "Default profile applied — no diagnostic data available").]
*Groups are revisable — revisit after the formative check.*

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

不含教师注释、观察要点或设计依据。三份都包含：词汇表 +
句子框架 + "先完成的话"锚活动 + 开放式反思提示（量规 O5——
UDL 覆盖所有层级）——全部从 `shared` 拉取，因此在结构上
各层级完全一致。下方大纲定义每份练习页文档的 `sections`：

```markdown
# [Group A / Group B / Group C] — [Lesson Title]

**Name:** _________________ **Date:** _________

## Vocabulary
[`from_shared: vocabulary` — the renderer formats the term–meaning pairs itself; never type a pipe-character table into a `text` field]

**You can use these sentence supports:**
- "I know ____ and ____. The part I don't know is ____."
- "My strategy was ______ because ______."

---

[Problems pulled ONE AT A TIME, each with its scaffold directly above it — per problem N:
at most ONE scaffold block (Below only, "For Problem N — ...", per R4/R7 fade), then
`{"type": "from_shared", "key": "tN", "label": "N"} followed by a workspace block`. Problem text identical on all
three tiers; never re-typed. Work space after each problem is automatic — do not add
answer boxes for problems.]
[Tier-only add-ons (e.g. Above "Go further" extension) as their own headed sections]

---

## If you finish early
[`from_shared: anchor_activity` — identical block on all three tiers]

## Reflect
[`from_shared: reflect_prompt` — identical question on all three tiers]
```

---

## 编写 differentiation.json — 数学映射

- `shared.subject`：`"Mathematics"`
- `shared.anchor_task`：共享的问题情境 / 导入钩子
- `shared.t1`..`tN`：所有层级共享的核心题组，一个任务一个键——分面向 {teacher: "难度和要观察什么，用平实的句子", student: <题目>}
- 教师文档：分层教案，最多 3 页；练习页每份最多 2 页
- **版权：** 绝不逐字复制 Illustrative Mathematics (IM) 面向学生的文本——来自 IM 材料的问题情境、活动叙述和 cool-down 提示必须改写为原创内容。

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
