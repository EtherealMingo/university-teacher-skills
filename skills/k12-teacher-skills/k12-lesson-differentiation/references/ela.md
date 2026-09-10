# ELA — 分层教学法

当学科为 **ELA（英语语言艺术）** 时由 `k12-lesson-differentiation` 加载。

## 识别源课程与课程教材

识别适用哪个场景：

**场景 A — 源课程存在于之前的对话中**
如果本对话前文中已经生成或讨论过一节课，直接使用它。不要重复要求教师分享。

**场景 B — 教师上传源课程**
先读文件。确认：年级、ELA 板块（阅读、写作或读写结合）、标准、学习目标和课程结构。如使用了文本，也识别所用文本。如果第一次尝试无法读取文件，清楚地说明错误并请教师重新分享。绝不静默编造一节课。

**场景 B2 — 教师用 URL 链接源课程**
先抓取 URL 并阅读其内容。然后与场景 B 完全一样地确认年级、ELA 板块、标准、学习目标、课程结构和所用文本。如果抓取失败或返回不可用内容，清楚地说明错误并请教师粘贴课程文本或上传文件。绝不静默编造一节课。

**抓取课程只完成第 1 步——它不替代标准锚定。** 继续执行第 2 步——锚定标准。URL 抓取之后跳过第 2 步，与上传课程后跳过它一样属于严重失误。

**场景 C — 没有源课程**
继续之前询问：
> "很乐意帮你做分层。你心里有具体的一节课吗？你可以粘贴过来、分享文件，或者告诉我年级 + 板块（阅读、写作或两者）+ 标准，我据此来做。"

---

## 标准锚定

遵循 SKILL.md 中的**第 2 步 — 锚定标准**：如果 Learning Commons 知识图谱
已连接，使用 `references/learning-commons-kg.md` 的 ELA 部分；如果未连接，
依据最佳知识继续并在教师教案中加上免责声明脚注。

**州感知的标准解析：** 当第 0 步已知州时，所有输出使用州 ELA 框架
代码。按 learning-commons-kg.md 的规定在知识图谱调用中传入 jurisdiction。

## 分层规则

把全部八条规则应用到每一节分层课程。

### R1 — 输出结构

**1 份完整连贯的面向教师分层教案 + 3 份纯粹的学生材料。绝不产出 3 份按水平混合编排的教案。**

混合模式——3 份按水平各自混杂教师注释和学生任务的文档——
是一种具体的失败模式。教师教案在一份文档中覆盖所有水平；
学生材料只含学生内容，没有教师注释、观察要点或设计依据。

### R2 — 标准与板块范围保全

**每个层级都针对原标准。每个学习成分在所有层级中都保留。**

ELA 课程通常在一节课内交织多个读写板块——阅读理解、
词汇和写作。分层必须覆盖其中出现的每个板块。不要为低水平
学生砍掉某个板块；为它搭支架。

标准中要求最高的要素（例如识别作者的论证、写带证据的
主张）恰恰是低水平学生最需要在支持下遇到的东西——
而不是要被移除的要素。

**Below 层级的参与度必须保全。** 不要把更丰富的文本或提示分给
At/Above，把操练式作业分给 Below。所有层级都读同一篇文本、
探究同一个核心问题——只是支持不同，不是任务不同。

### R3 — 文本通道：同一文本，不同支架

**三个层级都读同一篇年级水平文本。不调整文本复杂度——调整的是进入文本的通道。**

这是 ELA 分层的根本原则。把更简单的文本递给低水平学生，
是关上了年级水平学习的大门，而不是在通往它。正确的做法是
为学生如何进入年级水平文本搭支架。

三个层级映射为从有支持的进入到独立分析的进阶：

| 层级 | 认知切入点 |
|---|---|
| Below | 有支持的进入 → 有支架的产出。学生借助分段阅读、预教词汇、批注指南和句子支架读年级水平文本并完成任务。 |
| At | 标准参与。学生读年级水平文本并按设计完成任务。 |
| Above | 独立分析 / 综合。学生读年级水平文本，并超越信息提取，走向作者笔法、评价、跨文本联结或生成性产出。 |

当知识图谱点名了预备标准时，识别学生从该标准中已具备的阅读
或写作技能——并把低水平支架建成从该先备技能通向年级水平
任务的桥梁。

**写作课：** 各层级保持同一写作提示和写作目的。变化的是
结构支持（框架、组织图、范文）。不要降低写作目的（例如不要
为低水平学生把论证改成概述）。

### R3.5 — 基础读写预备知识检查（仅 K–5）

**对于 K–5 年级的课，在选择支架之前，先判断低水平学生最可能的障碍是解码/流利度缺口还是理解/词汇缺口。两者需要不同的应对。**

解码和阅读流利度是理解类学习的硬预备条件——不是理解类支架
能弥补的缺口。一个无法流利解码文本的学生无法被支架搭进
对该文本的理解。这是 K–5 低水平分层中最常见的失败模式：
给根本问题在基础层面的学生用理解类支架。

**按年级段：**

- **K–2：** 可能存在拼读或解码缺口，尤其是学生正在接受第二层
  (Tier 2) 支持时。理解类支架适合作为并行支持，但要把它当作
  并行支持——而不是针对根因的干预。
- **3–5：** 默认的低水平画像是流利度天花板——解码准确率尚可，
  自动化程度低，占用工作记忆并损害理解。在使用理解类支架的
  同时，优先采用支持流利度的结构（允许听读、结对读、跟读）。
  这是误判风险最高的年级段：一个看似有理解问题的学生
  实际上可能是流利度缺口。

**如果主要障碍看起来是解码或流利度，在教师教案的 BELOW TIER（低于水平组）部分加一条提示。例如：**

> *"⚠ 基础读写提示：如果学生不能流利地朗读这篇文本，理解类支架
> 将无法弥合缺口——预备性需求是另行实施的解码/流利度干预。
> 在该支持到位期间，听读是合适的通道桥梁，但它不是干预的
> 替代品。"*

6–12 年级不要加这条提示，除非有晚发现的阅读障碍的具体信号。
在那些年级，低水平的理解困难更可能由词汇缺口、背景知识
薄弱或推理技能不足引起。

### R4 — 低水平支架

**支架支持思考而不泄露答案。使用句子支架、图形组织图、批注提示和词汇支持。绝不给泄露答案的提示。绝不用简化版内容替代。**

要避免的失败模式：

- ❌ 为低水平学生换成更简单的文本、篇章或写作提示。这移除的是年级水平的参与，不是在搭支架。
- ❌ 在标准要求原有形式时降低写作目的（例如把论证改成概述，或把多段改成单句）。
- ❌ 预填好的图形组织图，只留下最终答案的空白。
- ❌ 在学生读之前告诉他们文本讲了什么（泄露理解的预读）。
- ❌ 替学生回答了任务的句子起始句（"作者论证奴隶制是错的，因为……"），而不是组织学生自己的思考（"作者论证 ______，因为 ______"）。

可接受的支架：

- ✓ 分段阅读加引导批注提示："读这一段时标出：中心思想（圈出）、一条证据（下划线）、一个你不认识的词（?）"
- ✓ 词汇支持：3–5 个预教关键词，用学生友好的语言定义，在阅读和写作期间可用。
- ✓ 组织思考而不替学生完成的句子支架："作者用 ______ 来表现 ______。" / "我的主张是 ______。一个理由是 ______。"
- ✓ 与读写任务匹配的图形组织图（见下表）。
- ✓ 允许听读或结对读（教师侧，不嵌入练习页）——对正在接受独立拼读干预、有解码缺口的学生，这是合适的通道桥梁。它不是该干预的替代品。见 R3.5。
- ✓ 减少要求的文本证据条数——同时保留任务类型（例如找 1 条证据而非 3 条，而不是换成另一种任务类型）。

#### 读写任务 → 主要支架

根据读写任务而不是年级选择主要支架：

| 读写任务 | 主要支架 |
|---|---|
| 阅读理解（叙事类） | 故事地图：人物 / 问题 / 事件顺序 / 结局 |
| 阅读理解（信息类） | 中心思想 + 证据组织图 |
| 论证 / 观点写作 | 主张—理由—证据框架 |
| 叙事写作 | 故事脊柱或结构化故事地图 |
| 信息类 / 说明类写作 | 网状组织图 → 段落框架 |
| 文本分析（作者笔法、结构） | 批注指南 + "作者用 ______ 来 ______"框架 |
| 比较/对照（文本或人物） | T 形图或带标注类别的维恩图 |
| 语境中的词汇 | 词汇地图：定义 / 例 / 反例 / 造句 |

用这张表在应用密度上限之前选定**主要支架**。如果一节课跨多个
任务类型，为低水平学生最需要支持的任务选支架。

检验标准：支架是把智力工作留给学生，还是替学生完成了工作？
如果是后者，它就不是支架。

#### 支架密度上限

**嵌入支架上限为每个任务 1–2 个。** 过度支架会把认知负荷转移到
摆弄支持工具上，而不是投入文本或写作——与支架不足同样有害。

| 类型 | 是否计入上限？ |
|---|:-:|
| 嵌入式——印在每个任务上（组织图、句子支架、批注提示） | 是 |
| 页眉级特征——词汇框、页面顶部的句子支架 | 否 |
| 教师侧支持——允许听读、个别指导话术、教具 | 否 |

**先选一个主支架。** 只有当第二个支架贡献了真正不同的模式时
（例如视觉组织图 + 语言框架）才加。如果第二个支架要求学生
做与主支架同样的脑力工作，删掉它。

### R5 — 必需的教学基础设施

**每节分层课程必须包含全部四项：**

| 部分 | 是什么 | 位置 |
|---|---|---|
| **形成性检查** | 具体的课中或课尾检查准备度的提示——分层出门票即可。不是"巡视学生"。 | 教师教案 + 各水平学生材料 |
| **锚活动** | 给先完成学生的对齐标准的任务。不是打发时间的杂活。应与本课的 ELA 板块相关（例如自主阅读、写作笔记本拓展）。以面向学生的写法写进 `shared.anchor_activity` 并印在每份学生材料上——只作为教案描述存在的锚活动属于失败。 | 教师教案 + 全部三份学生材料 |
| **弹性分组用语** | 层级归属与本课的证据挂钩，明确可根据形成性检查结果修订。不是固定的阅读水平轨道。 | 教师教案 |
| **分水平的迷思概念 / 常见错误注释** | 各层级特有的常见错误 + 教师提示 + 小组辅导信号。阅读课：理解类错误；写作课：笔法或结构类错误。 | 教师教案 |

此外：**每份学生材料都以一个开放式或反思性提示收尾，三个层级
都有**——例如"你认为作者的主要目的是什么？用文本中的证据
说明。" / "你写作中最难的部分是什么？你会改什么？"这对任何层级都
不可省略。把它存为 `shared.reflect_prompt`，并在教师教案中每个层级的
**练习页任务**一行中点名它——教案从未提及的已打印任务属于失败。

### R6 — 隐形调整

**在教学法允许的前提下，各层级同一文本 / 同一提示 / 同一核心任务。只有支持不同。**

可以不同的：学生材料中嵌入的支架；个别指导时可选的教师支持；
拓展或反思提示的深度。

不应不同的：学生读的文本；写作目的或提示；标准所针对的
结构性挑战；主题或情境。

**不要向学生宣布支架的撤除。** 如果任务 1 有支架而任务 3 没有，
它的缺席是静默的——不加标签、旁白或评论（例如不写
"（这次没有组织图）"或"试试不用框架来写"）。支架只是不出现；
学生按任务本来的样子面对它。

写作：默认所有层级用同一个提示。要求的例证数量或结构支持
可以变化，但任务本身不能变。

阅读：不要通过简化句子或缩短篇幅来制作文本的"低水平版"。
如果文本确实无法进入（例如由于学生的语言状况），在教师教案中
把它标注为一个单独的 ELD 考量——而不是一个标准的分层层级。

### R7 — 层级内渐进撤除支架

**每个层级的学生材料按渐进认知要求编排任务顺序。不是整齐划一的难度。**

#### 低水平支架撤除模式

| 任务 | 嵌入支架 | 模式 |
|---|:-:|---|
| 任务 1 | 至多 2 个 | 有支架 |
| 任务 2 | 至多 1 个 | 有引导 |
| 任务 3 及以后 | 0 个嵌入式 | 独立 |
| 出门票 | 0–1 个 | 掌握度检查 |

目标是真正的撤除（2 → 1 → 0），而不是所有任务上均匀
分布的支架密度。

#### 高水平拓展质量检验

每个高水平拓展都必须回答：**它要求了什么达到水平的学生
没有在做的新思考？** 如果你说不出新思考是什么，这个拓展
就是表面文章，不应交付。

一个真正的 ELA 拓展至少要求以下之一：

| 类型 | 它要求什么 |
|---|---|
| 作者笔法分析 | 从"文本说了什么"走向"作者为什么做这个选择，它创造了什么效果"。 |
| 视角转换 | 从另一人物/叙述者的视角重述；论证对立主张；换一个修辞目的改写。 |
| 跨文本综合 | 联结第二篇文本，比较论证、结构、作者视角或主题。 |
| 结构性洞见 | 关于体裁、结构或作者策略的概括，而达到水平的任务只把它当作单个实例处理。 |
| 开放生成任务 | 学生产出新东西：模仿作者风格的原创作品、反驳、供全班讨论的问题。 |
| 后续标准预览 | 来自更高年级 ELA 标准的真实概念要素——不只是它的词汇。 |

以下情况驳回：只是更多同类、只是换记号/词汇，或只是换个说法。

如果只有一项有意义的拓展，就只放这一项。

### R8 — 范围与默认值

**如果未指定层级范围，生成之前问一个合并问题：**

> "我会把这节课分成低于 / 达到 / 超出年级水平三个层级——分这三个
> 合适吗？还有没有什么我该知道的具体学习者需求（ELL 等级、
> IEP 目标）？如果没有，我会应用 UDL 默认值（所有层级都有
> 句子支架和词汇支持）。"

如果范围已被指定，静默采用默认值并继续。

**未指定时静默采用的默认值：**
- 层级：低于 / 达到 / 超出
- UDL 特征：**全部三份**学生材料都有句子支架和词汇表
  （不只 Below——量规 O5）
- 范围：完整课程（所有阶段 + 出门票）
- 文本：所有层级读同一篇年级水平文本（绝不替换）

**缺少形成性数据时的默认低水平画像：**

当没有诊断数据可用时（没有口语阅读流利度 (ORF) 分数、阅读记录、
拼读筛查结果或出门票数据），按年级段为最可能的画像设计：

- **K–2：** 可能存在拼读或解码缺口。把理解类支架作为并行支持；
  把允许听读作为教师侧选项；检查是否需要基础读写提示 (R3.5)。
- **3–5：** 默认画像是流利度天花板——解码准确率尚可，自动化
  程度低。在使用理解类支架的同时，优先采用支持流利度的结构
  （允许听读、结对/跟读）。词汇预教是第二个杠杆。
- **6–8 和 9–12：** 默认画像是词汇和背景知识缺口。学术性第二层
  (Tier 2) 和第三层 (Tier 3) 词汇是最常见的瓶颈。先为语义和句法搭
  支架；解码对识字来说多半已够用。

在没有形成性数据时，假定低水平学生在本课主要读写技能的
最近预备条件上有缺口：以理解为重点的课，缺在词汇和流利度；
以写作为重点的课，缺在组织和句子层面的结构。

**生成分层教案之后，向教师追问形成性数据：**

> *"你有没有什么阅读数据——ORF 分数、阅读记录、拼读筛查，
> 或写作样本——能帮助我选准支架？哪怕是学生卡在哪里的
> 非正式记录也有帮助。"*

按年级段调整追问：
- **K–5：** 具体询问 ORF 分数、阅读记录或拼读筛查结果。这是
  ELA 中风险最高的 FA 追问——低水平学生是解码缺口还是理解
  缺口会改变整个支架方案。为解码缺口学生搭的理解类支架
  是在浪费教学时间。
- **6–12：** 询问能显示推理或论证结构在哪里断裂的出门票结果或
  写作样本。这里的 FA 数据通常印证默认假设（词汇/背景知识），
  而不是推翻它。

对 K–5 不要把 FA 追问当作可选项。默认的分层教案只是最可能的
猜测；解码型学生和理解型学生之间的差距影响重大，
在数据可能可得的情况下不能不确认。

---

### 文档内容 — 教师教案（`id: teacher_plan`）——最多 3 页

**篇幅预算：渲染后约 1,200 词（即 3 页上限的实际含义）。** 先收紧层级
部分和概览，再动收尾部分（弹性分组、设计依据、后续
步骤）——最常见的超支是练习页任务行复述了学生材料的内容
而不是点名它。

下方大纲定义教师教案文档 `sections` 的内容与顺序：
每个 `##` 标题成为一个章节，其正文成为该章节的内容块
（标准、迷思概念和出门票用 `from_shared` 块；粗体字段用
`labeled` 块）。

```markdown
# Differentiation Plan: [Lesson Title]

**Standard:** [verbatim]  **Grade:** [X]  **Strand:** [RL/RI/W/SL/L]  **Duration:** [X min]  **Curriculum:** [name if confirmed / General]
*Learner needs: [If no specific needs were provided: "UDL defaults applied — sentence supports and vocabulary support across all tiers." If learner needs were specified, describe them here instead.]*

## Learning Objective
[Same objective across all tiers — preserved from source lesson]

## Differentiation Overview
[1 short paragraph, ≤3 sentences: approach, text confirmed as shared across all tiers,
prerequisite named by code + short gist (for K–5, note if the foundational literacy flag
applies per R3.5), forward standard named by code + gist. Never paste full standard text
here — the target standard is already verbatim in the header. Use CCSS if state uses
CCSS/CCSS-aligned. Source from state vertical alignment when state is known; footnote CCSS code
when using as proxy for a non-CCSS state.]

## Tier Design
[ONE `table` block — never three labeled paragraph stacks. Columns: Below (Group A) / At (Group B) / Above (Group C).
Rows (a cell may be "—" where a field doesn't apply to that tier):
- **Grounded in** — Below: concept-level prerequisite by code + gist from CCSS vertical
  alignment. Above: forward standard by code + gist. At: "—".
- **Scaffolds / extension** — fragments, ≤25 words per cell: Below scaffolds in play; At
  supports; Above extension + which R7 quality type it meets.
- **Conferring move** — one specific prompt per tier.
- **Worksheet tasks** — ≤40 words per cell, written LAST: read that tier's FINAL student
  material's blocks top-to-bottom and name every printed task in order — tasks by name with
  their printed scaffolds (e.g. "First read (annotation guide), Central-idea organizer,
  Summary"), every tier-only add-on or extension sub-part by its printed heading, exit
  ticket, "If you finish early" anchor task, Reflect prompt. List items; don't restate their
  text. Name nothing unprinted — no "on request" supports, no planned organizer the material
  dropped. Never copy another tier's cell.]


[Then ONE `callout` (note style): misconception / common error watch — pattern + teacher
prompt, ≤2 sentences per tier that needs one.]

[K–5 only, if applicable — a SECOND `callout` (note style), the foundational literacy flag:
⚠ If students cannot read this text aloud fluently, comprehension scaffolds will not close
the gap — the prerequisite need is decoding/fluency intervention delivered separately.
Read-aloud is an appropriate access bridge while that support is in place, not a substitute
for it.]

## Formative Check
[Two required elements:
1. **Mid-lesson checkpoint:** A specific check during reading or writing work time — name the trigger or artifact (e.g., "After the annotation task, collect two student samples: if neither can identify the central idea, pause and re-model the annotation move before moving to the writing task"). 'Circulate and observe' does not pass.
2. **Exit ticket with explicit sort criteria:** State what a student must produce or demonstrate to land in each bucket for THIS lesson, e.g.: "Got it — [e.g., names the central idea and cites two pieces of text evidence] / Almost there — [e.g., names the central idea but cites only one piece of evidence or misidentifies a supporting detail] / Needs re-teaching — [e.g., cannot name the central idea independently]." Generic bucket labels without lesson-specific criteria do not pass.]

## Anchor Activity
[`from_shared: anchor_activity` — the same student-facing task printed on every student material — plus one teacher-only line: when to deploy it and why it requires genuine ELA thinking]

## Flexible Grouping
[Current tier assignments, the evidence or basis for placement (e.g., "Placed based on prior writing sample / ORF score / exit ticket on [standard]" or "Default profile applied — no diagnostic data available"), and an explicit statement that groups are revisable after the formative check]

## Why this works (1)
[One specific tier design choice + reasoning]

## Why this works (2)
[A second specific tier design choice + reasoning]

## Next Steps
**Got it (exit ticket passes):** [connect to forward standard or upcoming lesson]
**Almost there:** [targeted small-group or conferring move — specific gap to address]
**Needs re-teaching:** [specific reteach strategy or Tier 2/3 flag if gap is persistent]

```

### 文档内容 — 学生材料（`id: worksheet_group_a` / `worksheet_group_b` / `worksheet_group_c`）

不含教师注释、观察要点或设计依据。三份都包含：词汇表 +
句子框架 + "先完成的话"锚活动 + 开放式反思提示（量规 O5——
UDL 覆盖所有层级）——全部从 `shared` 拉取，因此在结构上
各层级完全一致。

按板块区分格式：

| 课程板块 | 学生材料格式 |
|---|---|
| 阅读 | 阅读指南：需要时附文本节选、批注提示、理解任务、回应提示 |
| 写作 | 写作框架：范文节选（如课中有）、构思组织图、带支架的起草空间 |
| 读写结合 | 阅读任务后接写作任务，支架按 R7 的撤除节奏布置 |

```markdown
# [Group A / Group B / Group C] — [Lesson Title]

**Name:** _________________ **Date:** _________

## Vocabulary
[`from_shared: vocabulary` — the renderer formats the term–meaning pairs itself; never type a pipe-character table into a `text` field]

**You can use these sentence supports:**
- "The author uses ______ to show ______."
- "My claim is ______. One reason is ______."

---

[Tasks pulled ONE AT A TIME, each with its scaffold directly above it — per task N:
at most ONE scaffold block (Below only, R7 fade: Task 1's block may combine a primary +
secondary scaffold if genuinely different modes; Task 2 gets one lighter scaffold; Task 3+
gets none — the absence is intentional and silent), then
`{"type": "from_shared", "key": "tN", "label": "N"} followed by a workspace block`. Task text identical on all three
tiers; never re-typed. Writing space after each task is automatic — do not add answer
boxes for tasks.]
[Tier-only add-ons (e.g. Above "Go further" extension) as their own headed sections]

---

## If you finish early
[`from_shared: anchor_activity` — identical block on all three tiers]

## Reflect
[`from_shared: reflect_prompt` — identical question on all three tiers]
```

---

## 编写 differentiation.json — ELA 映射

- `shared.subject`：`"ELA"`
- `shared.anchor_task`：共享的文本 + 核心问题
- `shared.t1`..`tN`：所有层级共享的核心读写任务，一个任务一个键——分面向 {teacher: "难度和要观察什么，用平实的句子", student: <任务>}
- 教师文档：分层教案，最多 3 页；学生材料每份最多 2 页
- **版权：** 绝不逐字复制源课程中面向学生的文本——改写为原创内容。

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
