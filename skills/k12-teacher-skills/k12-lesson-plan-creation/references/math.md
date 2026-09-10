# 数学 — 课程教学法

当学科为**数学**时由 `k12-lesson-plan-creation` 加载。

## 澄清

在提出任何问题之前，先根据所有可用的对话信号评估以下各项：

**1. 州识别。** 扫描对话中的任何州信号——教师提到某个州名、使用州专属的标准代码（TEKS、SOL、OAS、CA-CCSS 等），或说"我在 [某州] 教书"。如果发现，记为 state = [州名]，并在知识图谱标准查询中作为 jurisdiction（辖区）传入。同时把默认标准框架更新为与之匹配。

**2. 课程教材识别。** 在提出任何问题之前，判断教师是否很可能在使用 IM (Illustrative Mathematics) 课程教材。在对话的任何地方寻找信号——不限于当前输入：明确点名（"IM"、"Illustrative Mathematics"、"IM 360"）、IM 专属术语（MLRs、cool-down、"Stronger and Clearer Each Time"、IM 单元或课次引用），或使 IM 使用可能性很高的上下文。如果信号存在，视为 **IM 已确认**并继续。如果没有，视为**未确认 IM**。

当关键信息缺失时，提问。优先级：(1) 年级（若缺失），(2) 主题（若缺失），(3) 课程教材（若无法推断），(4) 州（若无法推断）。其余一切靠推断。静默采用的默认值：45–60 分钟、全纳式设计 (universal access design)、CCSS（当州识别发现州框架时被其覆盖）。

---

## 标准锚定

遵循 SKILL.md 中的**第 2 步 — 锚定标准**：如果 Learning Commons 知识图谱
已连接，使用 `references/learning-commons-kg.md` 的数学部分；如果未连接，
依据最佳知识继续并加上免责声明脚注。

## 构建课程

**所有课程通用**
至少包含一个登记在 `shared` 中的视觉支架（一个 `data_table`、`number_line`
或 `fill_table` 组织图），并拉入教案中，
旁边配上面向教师的设计依据。它是否同时出现在学生页面上取决于
它是什么：学生要填写的空白 `fill_table` 或学生要标记的 `number_line`
属于练习页；而展示运算过程或答案结构的已填好的参考表
仅限教师使用——印出来等于泄露思考过程。

确保整体时间和每个环节的时间都切实可行——不要让课程超载。

### 课程教材分支 — 起草前先应用

**如果 IM 已确认：**
严格使用 **Launch → Explore → Discuss → Synthesize → Exit Ticket（导入 → 探究 → 讨论 → 综合 → 出门票）**。应用 IM 专属特征：
- 课堂话语：*Compare and Connect*（比较与联结）、*Stronger and Clearer Each Time*（每次更强大更清晰）、*Think-Pair-Share*（思考—结对—分享）
- MLRs（数学语言惯例）：使用知识图谱的建议；否则默认在 Explore 用 MLR 2 (Collect and Display)、在 Discuss 用 MLR 7 (Compare and Connect)、在讨论需要支持处用 MLR 8 (Discussion Supports)
- 在第 1 节逐字点名 2–3 条 SMP（数学实践标准）；语气保持教师友好，不要学究气

**如果未确认 IM：**
使用 **Launch → Explore → Discuss → Synthesize → Exit Ticket**（问题驱动式）。不使用 IM 专属术语：不用 MLR 名称、不用 *Compare and Connect*、不用 *Stronger and Clearer Each Time*。使用 Think-Pair-Share 和 Turn-and-Talk（同桌互说）。
- **K–2**：CGI（认知引导教学）——Explore 必须包含至少一道起始量未知题和一道变化量未知题；对于加/减故事题标准，题组要覆盖全部四种情境类型（加入 (add-to)、拿走 (take-from)、合起来/拆开 (put-together/take-apart)、比较 (compare)）；出门票必须针对起始量未知或变化量未知；在学生尝试之前不做策略示范；学生使用的视觉模型（带状图、数字分解图、图画）出现在材料本身之中——在练习页或锚图上——而不是作为可选项提供
- **3–5**：问题驱动，渐进放手；Discuss 中使用阵列/面积模型
- **6–8**：问题驱动；比值表、双数轴、坐标图
- **9–12**：数学建模；在 Synthesize 而非 Launch 中形式化记号

### 题组 — 结构多样性是硬性要求，不是可选项

在编写练习题（`shared.p1`..`pN`）之前，先枚举该标准的结构性情形——完整的跨度，
从基线情形（每个学生都必须掌握的那种）到结构上最难的情形
（学生最常出错的那种：K–2 故事题的起始量未知；小数乘法中
积比两个因数都小的情形；勾股定理中缺直角边的情形；四舍五入中
恰好在中点或略低于边界的数；比例关系中
线性但不成比例的情形；其他标准依此类推）。然后编写题组，使每一种
被枚举的情形都成为一道编号必做题（或出门票），并在该题的
`teacher` 面向中点名其情形。

覆盖规则：
- 只出现在文字叙述中的结构性情形——SWBAT（学生将能够……）、预设难点、
  教师动作或 Discuss 笔记——不算已覆盖。如果教案的文字点到了某个情形，
  就必须有一道编号题把它呈现给学生。
- 强调最难情形绝不意味着可以丢掉基线情形：一套全是难题的
  题组与一套全是易题的题组一样通不过覆盖检查。
- 标准的数域是多样性的一部分：如果标准或 SWBAT 说的是
  有理数，至少有一道必做题使用分数或小数——
  只含整数的题组不算覆盖。
- 绝不把必需的结构性情形降级为可选的拓展或附加题——如果它只
  作为挑战附加题出现，大多数学生永远不会遇到它。
- 明确说明一次哪道题承载哪种情形（出门票也算）——覆盖缺口
  应当一目了然，对你和对教师都是如此。

### 章节结构 — 两条路径通用

1. **一览 (At a glance)** — 在 `special` 标注块中逐字引用标准（这是唯一的逐字引用——其他地方标准一律用代码 + 简短要点）；一行课程弧线，点名各阶段及分钟数（"Launch 8 → Explore 15 → Discuss 12 → Synthesize 5 → Exit 5"），让这节课的形状在任何细节之前可见；材料——每项平实点名（如"数字卡 0-20"）；点名的 SMP
2. **学习目标** — 大观念 (Big Idea)（持久性理解，1 句话）；SWBAT；预备知识（按代码引用先前标准 + 一句平实的话说明学生已经会什么、今天如何在此基础上进阶）
3. **词汇与预设难点** — 3–5 个关键术语附简要定义；2–3 个迷思概念 (misconceptions)，每个按：*学生怎么做* / *为什么发生* / *教师动作*
4. **课程流程** — 阶段按上文的课程教材分支；**Discuss 至少 10 分钟**（如果是简短的预热式请求，压缩其他阶段，而不是 Discuss）；在 Explore 中：3 条以上观察要点 (look-fors)，每条点名学生的反应、为什么重要、以及如何利用它——如果锚任务 (anchor task) 允许多于一种正确答案或算式，必须有一条观察要点明确说明这一点，让教师接受全部正确答案；在 Discuss 中：至少一个具名的生生对话动作（Think-Pair-Share、Turn-and-Talk、同伴比较、同意/不同意）+ 具体的话语提示（不能是泛泛的）
5. **设计说明** — 最后一节，在出门票之后：改编时应保持完整的 2–3 个
   要素，附简要理由，包括本课的核心表征（学生使用的视觉
   或模型）及其一句话说明。设计依据放在这里，在教学路径之后——
   备课的教师先读课程弧线，再读背后的道理。

## 出门票设计指南

出门票是课程流程的最后一个阶段（在其阶段标题下以 `from_shared:exit_ticket` 引用）。

- 它就是**结构上最难的那个枚举情形**（来自上文的题组枚举；K–2 为
  起始量未知或变化量未知），绝不用中等难度的题目代替。用
  **迷思概念检验**来选题：一个持有本课主要预设迷思概念的学生
  必须把出门票答错。如果那样的学生也能答对，说明你选的是
  一道印证性实例——换成有区分度的那道（区分 X 与非 X 的课，
  用非 X 情形收尾；纠正某种定位习惯的课，用该习惯会产生
  错误答案的情形收尾）。在 `shared.exit_ticket.teacher` 中点名该情形。

- **通过实际演算来验证出门票和每一份答案**：所述答案必须
  是该题实际产生的结果，且运算步骤数与标准相符（
  一节一步方程的课，出门票就该是一步方程）。

- 3 个分拣桶——*掌握了 (Got it)* / *差不多了 (Almost there)* / *需要重教 (Needs re-teaching)*——
  **每个都带明确标准**，描述落入该桶的回答是什么样子
  （例如"掌握了：算式正确，且未知数的位置与故事中一致"，
  而不是光秃秃的标签）；全部三条标准都要出现在教案中，
  绝不截断为只有标签。

---

## 编写 lesson.json — 数学映射

当你执行到 SKILL.md 的第 5 步（输出）时，在 `shared` 中登记数学内容并像这样组织
`documents[]`：

- `shared.subject`：`"Mathematics"`；`shared.smps`：逐字点名的 2–3 条 SMP。
- `shared.anchor_task`：`{teacher: <导入话术 + 引导提示>, student: <学生读到的任务，第二人称>}`。
- 每道练习题各占一个键——`shared.p1`..`pN`：`{student: <题目文本>}`，
  可选 `{teacher: <此题要观察什么>}` 和 `stimulus: [blocks]`（多题共享的
  `data_table`、`number_line` 等）。被多道题共享的数据集可以
  单独成键（如 `shared.prices_table`），在题组之前拉入一次。
- 把视觉支架登记为独立的 `shared` 键（如 `shared.hundreds_chart`、
  `shared.prices_table`、`shared.tape_diagram`）——一个 `data_table`、`number_line` 或
  `fill_table` 块——并拉入教案中紧挨设计依据的位置。只有当它是
  学生要动手操作的东西时才拉到学生页面上（空白组织图、要标记的
  数轴、题目要分析的数据集）；教师用来组织微型课的
  已填好的参考表留在教师侧。
- `shared.exit_ticket`：`{student: <题目——一道新题，绝不与练习题重复>, teacher: <收集说明>}`。分拣标准是一个 `cards` 块，在教案中拉入出门票之后放置（见 `example_lesson.json`）。
- `shared.vocabulary`、`shared.misconceptions`、`shared.look_fors`：每个都登记为
  你希望渲染成的块（迷思概念用 `table`，观察要点用 `list`）——
  不存在按键名的特殊渲染。

**学生页布局**（`id: "student_materials"` 文档）——从这个骨架出发
按需调整：

```
sections:
  "<warm-up heading, kid-facing>"  group[ from_shared:anchor_task, answer_box ]
  "<practice heading>"     optional callout(student-note) — a brief reminder, only when one helps
                           from_shared:<visual-scaffold key>   ← only when it is something
                             students work with (blank fill_table, number_line, the data
                             set the problems analyze) — a worked reference table is
                             teacher-only
                           for each problem k:
                             group[ {type: from_shared, key: pk, label: "k"},
                                    answer_box (bare -- it sizes to the grade band;
                                    ruled: true when the answer is composed sentences) ]
                           on the ONE problem whose hard part is the writing move, its
                             group also carries the sentence support -- plain text before
                             the answer_box (see Sentence supports in `references/output.md`)
                           page_break
  "<exit heading, kid-facing>"     group[ from_shared:exit_ticket, answer_box ]
```

**课堂观察模板布局**（`id: "observation_template"` 文档）：

```
sections:
  "How to use this"        one-paragraph instructions
  "Look-fors"              from_shared:look_fors
                           fill_table headers=[Student, Strategy seen, Next step] blank_rows=8
  "Anticipated challenges" from_shared:misconceptions
  "Exit-ticket sort"       from_shared:exit_ticket
```

完整示例：`references/example_lesson.json`。

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
