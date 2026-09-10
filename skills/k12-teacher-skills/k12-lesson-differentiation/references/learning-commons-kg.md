# Learning Commons 知识图谱 — 调用序列（分层）

**仅当 LC 知识图谱连接器可用时**供 `k12-lesson-differentiation` 第 2 步
使用。如果未连接，完全跳过本文件（SKILL.md 第 2 步有备用方案）。
下文每一节是一个学科的调用序列。已连接时调用知识图谱是
强制的；不调用属于严重失误。

## 解析标准（所有学科通用）

用 `find_standard_statement` 解析标准，已知时传入 `academicSubject` 和
`jurisdiction`（美国州名）：

- **提供了代码**（源课程中点名或教师给出）：按代码搜索——`find_standard_statement(code=<code>, academicSubject="<subject>")`。代码搜索同时匹配代码本身及其下的一切（前缀匹配）：像 `3.NF.A.1` 这样的叶子代码只返回该标准，而像 `2.OA` 这样的父级代码返回 `2.OA` 加上所有 `2.OA.*`。**如果没有返回结果**，很可能是代码格式与图谱不匹配——退回到关键词搜索（见下）；其结果带有真实的 `code` 值，能揭示正确格式，你可以用它重试代码搜索。
- **未提供代码**：从关键词搜索开始——`find_standard_statement(keywords=["<词或短语>", "<词或短语>", …], academicSubject="<subject>")`。`keywords` 是主题词/短语的**列表**；只要其中任何一个出现在标准的描述中即算匹配。从返回的 `standards` 数组中挑选最匹配的标准——它的 `code` 可以作为后续代码搜索的种子来查找相关标准（例如用其父级前缀拉出整个标准族）。

当返回的标准有子标准时，它们会出现在其 `subStandards` 数组中——
用标准本身或其子标准中对用户请求最相关的那个。

从选定的标准中提取：逐字的陈述文本、其 `code` 和
`caseIdentifierUUID`（存好——后续所有调用都需要）。

## 数学

**起草之前完成全部三个调用。已连接而不调用属于严重失误。**

记下源课程点名的任何标准代码——解析步骤在代码存在时按它搜索。

标准解析完成后，进阶调用（两个方向）、迷思概念和
学习成分都只依赖其 `caseIdentifierUUID`——把这四个调用作为一个
并行批次发出，各自带全下方指定的参数。第 5 步按自己的规则
运行（它自己的查询模式和教师确认），不受该批次影响。

**可用工具：** `find_standard_statement`、`find_standards_progression_from_standard`、`find_misconceptions_for_standard`、`find_learning_components_from_standard`、`find_curriculum_lessons`、`find_materials_for_lesson`。

1. **标准**：按上文*解析标准*以 `academicSubject="Mathematics"` 解析标准；
   当第 0 步的州识别已知州时，加 `jurisdiction="<州>"` → 逐字陈述
   文本和 `caseIdentifierUUID`。

   当传入了 jurisdiction 且知识图谱返回州专属标准时，逐字使用该
   标准的代码和文本。只有当教师的州未知且无法推断时，
   才使用 math.md R3 中的 CCSS 回退链。

2. **预备标准与后续标准**：调用 `find_standards_progression_from_standard(caseIdentifierUUID, direction="backward")` → 提取唯一的主要预备标准，逐字——它锚定 Below 层级。调用 `find_standards_progression_from_standard(caseIdentifierUUID, direction="forward")` → 提取唯一的主要后续标准，逐字——它锚定 Above 层级。缺少任何一个都属于严重失误。

3. **迷思概念**：调用 `find_misconceptions_for_standard(caseIdentifierUUID, subject="Mathematics")` → 提取最相关的 3 个迷思概念。每个只保留学生行为和教师动作，用你自己的话改写。如果没有结果，从训练知识起草 3 个。

4. **学习成分**（可选，用于教师教案）：调用 `find_learning_components_from_standard(caseIdentifierUUID)` → 提取至多 5 条子技能描述。用于验证 R2：所有成分必须在所有层级中出现。

5. **IM 课程材料**（仅当两个条件同时成立：IM 已确认为所用课程教材，且教师是点名该课——场景 B3——而不是上传或链接它）：用 `author="Illustrative Mathematics"` 调用 `find_curriculum_lessons`。使用与教师所提供信息匹配的模式：
   - **教师按位置点名**（如"六年级第 2 单元第 3 课"）：用 `ordinalName="Grade N, Unit N, Lesson N"`。先展开缩写。
   - **教师按标题点名**：用 `lessonName="<标题中的内容词>"`。不要带年级/单元/课次编号。

   如果返回多个候选，把 `fullOrdinalName` 和 `lessonName` 回显给教师确认。确认后，调用 `find_materials_for_lesson(lessonIdentifier, materialSource=["lesson", "activity"])` → 提取：(a) 活动名称和顺序，(b) 涉及的题型和未知数位置，(c) 话语动作。用于把层级任务设计锚定到真实的课程结构上——不要逐字复制面向学生的文本。

   如果教师上传或链接了课程（场景 B 或 B2），跳过这一步——课程内容已经可得。

**课程教材术语检查（如果未确认 IM）：** 继续之前，扫描你的工作笔记，
确认其中没有提及 "Illustrative Mathematics"、"IM"、任何 MLR 名称
(MLR 1–8)、"Compare and Connect"、"Stronger and Clearer Each Time"
或任何 IM 课次/活动标题。清除任何残留——未确认 IM 的教师
绝不能在任何层级文档、教师教案或对话中收到 IM 专属术语
（与 SKILL.md 的版权护栏同一条规则）。

**如果知识图谱未连接：** 依据最佳知识继续；在教师教案中加脚注：
*"Generated without the Learning Commons KG. Prerequisite grounding and
misconceptions reflect general best practice."*（未连接 Learning Commons 知识图谱
生成。预备知识锚定与迷思概念反映通用最佳实践。）

---

## ELA

**起草之前调用这些工具。已连接而不调用属于严重失误。**

记下源课程点名的任何标准代码——解析步骤在代码存在时按它搜索。

**CCSS 板块识别：** CCSS ELA 标准分不同板块——文学阅读 (RL)、
信息类阅读 (RI)、写作 (W)、听说 (SL) 和语言 (L)。调用知识图谱
之前先确定标准属于哪个板块。它决定分层的组织方式（例如
写作标准的低水平支架与阅读标准的看起来不同）。

1. 按上文*解析标准*以 `academicSubject="English Language Arts"` 解析标准；
   当第 0 步的州识别已知州时，加 `jurisdiction="<州>"` → 逐字标准
   文本、其 `code` 和 `caseIdentifierUUID`。

   当传入了 jurisdiction 且知识图谱返回州专属标准时，逐字使用该
   标准的代码和文本。

2. `find_learning_components_from_standard(caseIdentifierUUID)` → 至多 5 条子技能描述。**仅对 K-2 标准调用它；3 年级及以上，知识图谱中尚无学习成分——跳过该调用，从标准陈述起草子技能。** 用子技能验证 R2：所有学习成分必须在全部三个层级中保留在范围内。

**ELA 进阶：** `find_standards_progression_from_standard` 对 ELA 标准不返回
数据——不要调用它。预备标准和后续标准从相应板块的 CCSS
纵向衔接知识中获取（例如上一年级的平行标准、下一年级的
平行标准）。在教师教案中加脚注：*"Standard text retrieved from the
Learning Commons KG. Prerequisite and forward standard grounding reflects
CCSS [strand] vertical alignment."*（标准文本取自 Learning Commons 知识图谱。
预备与后续标准锚定反映 CCSS [板块] 纵向衔接。）

**如果知识图谱未连接：** 依据最佳知识继续；在教师教案中加脚注：
*"Generated without the Learning Commons KG. Standard text, prerequisite grounding, and
learning components reflect general best practice."*（未连接 Learning Commons 知识图谱
生成。标准文本、预备知识锚定与学习成分反映通用最佳实践。）

---

## 科学

**起草之前完成全部三个调用。已连接而不调用属于严重失误。**

记下源课程点名的任何 NGSS 表现预期代码——解析步骤在代码存在时
按它搜索。

**可用工具：** `find_standard_statement`、`find_curriculum_lessons`、`find_materials_for_lesson`。

注意：`find_learning_components_from_standard` 和 `find_standards_progression_from_standard`
对科学标准**不**返回数据——不要调用它们。

1. **标准**：按上文*解析标准*以 `academicSubject="Science"` 解析标准；
   当第 0 步的州识别已知州时，加 `jurisdiction="<州>"`。得州使用
   TEKS 科学——教师所在州为得州时传 `jurisdiction="Texas"`。
   返回 PE 逐字文本 + `caseIdentifierUUID`。

   当传入了 jurisdiction 且知识图谱返回州专属标准时，逐字使用该
   标准的代码和文本。

2. **在知识图谱中找源课程**：用 `author="OpenSciEd"` 调用 `find_curriculum_lessons`。这个调用有双重作用：它检索课程背景，而且对场景 B3 来说，它本身就是识别课程的方式（教师是点名而不是上传或链接）。每次调用只使用一种模式：

   - **已知课程位置**（教师按位置点名——场景 B3——或单元/课次号在上传的/抓取的课程中可见——如"Science Grade 5, Unit 2, Lesson 3"）：用 `ordinalName="Science Grade 5, Unit 2, Lesson 3"`。传入前先展开缩写（G5 U2 L3 → Science Grade 5, Unit 2, Lesson 3）。这是最精确的模式；可用时优先。
   - **已知标题但不知位置**（教师按标题点名——场景 B3——或标题在上传的/抓取的源课程中可见）：用 `lessonName="<课名中的词>"`。只传有区分度的内容词——省略年级/单元/课次编号。结果按匹配度从高到低返回。
   - **只有标准 UUID**（上传的/抓取的课程无法恢复位置或标题——不适用于场景 B3）：用 `caseIdentifierUUID=<第 1 步的 uuid>`。注意：OpenSciEd 课程只对齐 Multi-State (NGSS) 标准——没有精确对应关系的州专属 PE UUID 不返回结果。

   如果返回多个候选，把它们的 `fullOrdinalName` 和 `lessonName` 回显给
   教师，确认是哪一课之后再取材料。确认后，调用
   **`find_materials_for_lesson(lessonIdentifier)`** → 提取：(a) 锚定现象；
   (b) 单元驱动性问题；(c) 本课的探究现象或问题；(d) 本课在
   单元故事线中的位置；(e) 前置的 SEP 和 CCC；(f) 使用的
   例行环节或活动结构。

3. **进阶。** 从课程材料或知识图谱数据中确定：(a) 低水平支架应让学生
   *从其上出发*的先前年级 PE 或 DCI 要素；(b) 高水平拓展应预告的
   后续 PE。两者都逐字点名。缺少任何一个都属于严重失误。

**如果知识图谱未连接：** 依据最佳知识继续；在教师教案中加脚注：
*"Generated without the Learning Commons KG. PE grounding, OpenSciEd alignment, and
progression reflect general best practice."*（未连接 Learning Commons 知识图谱生成。
PE 锚定、OpenSciEd 对齐与进阶反映通用最佳实践。）

---

## 社会学科

**起草之前完成所有查询。已连接而不调用属于严重失误。**

记下源课程点名的任何标准代码——解析步骤在代码存在时按它搜索。

1. **标准**：按上文*解析标准*以 `academicSubject="Social Studies"` 和
   `jurisdiction="<州>"` 解析标准（必需——`Multi-State` 下没有社会学科
   标准）→ 逐字陈述文本、其 `code` 和 `caseIdentifierUUID`
   （存好——后续所有调用都需要）。所有输出中逐字使用陈述文本。

**关于标准进阶的说明：** `find_standards_progression_from_standard` 对
社会学科标准不返回数据——不要调用它。预备标准和后续标准从
州标准纵向衔接知识中获取（例如同一主题链中相邻年级的
标准）。在教师教案中加脚注：*"Standard text retrieved from the
Learning Commons KG. Prerequisite and forward standard grounding reflects
[state] standards vertical alignment."*（标准文本取自 Learning Commons 知识图谱。
预备与后续标准锚定反映 [州] 标准纵向衔接。）

**如果知识图谱未连接：** 依据最佳知识继续；在教师教案中加脚注：
*"Generated without the Learning Commons KG. Standard text, prerequisite grounding, and
misconceptions reflect general best practice."*（未连接 Learning Commons 知识图谱生成。
标准文本、预备知识锚定与迷思概念反映通用最佳实践。）

→ **知识图谱阶段完成。立即进入第 3 步。**

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
