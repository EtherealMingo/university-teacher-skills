# Learning Commons 知识图谱 — 调用序列

**仅当 LC 知识图谱工具可用时**供 `k12-lesson-plan-creation` 第 2 步使用。
如果不可用，完全跳过本文件（SKILL.md 第 2 步有备用方案）。
下文每一节是一个学科的调用序列。已连接时调用知识图谱是
强制的；不调用属于严重失误。

## 解析标准（所有学科通用）

用 `find_standard_statement` 解析标准，已知时传入 `academicSubject` 和
`jurisdiction`（美国州名）：

- **提供了代码**（源课程中点名或教师给出）：按代码搜索——`find_standard_statement(code=<code>, academicSubject="<subject>")`。代码搜索同时匹配代码本身及其下的一切（前缀匹配）：像 `3.NF.A.1` 这样的叶子代码只返回该标准，而像 `2.OA` 这样的父级代码返回 `2.OA` 加上所有 `2.OA.*`。**如果没有返回结果**，很可能是代码格式与图谱不匹配——退回到关键词搜索（见下）；其结果带有真实的 `code` 值，能揭示正确格式，你可以用它重试代码搜索。
- **未提供代码**：从关键词搜索开始——`find_standard_statement(keywords=["<词或短语>", "<词或短语>", …], academicSubject="<subject>")`。`keywords` 是主题词/短语的**列表**；只要其中任何一个出现在标准的描述中即算匹配。从返回的 `standards` 数组中挑选最匹配的标准——它的 `code` 可以作为后续代码搜索的种子来查找相关标准（例如用其父级前缀拉出整个标准族）。

当返回的标准有子标准时，它们会出现在其 `subStandards` 数组中——
用标准本身或其子标准中对用户请求最相关的那个。

**搜索尝试总数上限为 3 次。** 来自错误年级段或课程的结果算
一次落空——高中美国史的请求却返回小学代码，说明搜索
词没命中，应用剩余的尝试换不同的关键词（课程名称、
时代、标准族），而不是早早退回。如果 3 次
`find_standard_statement` 调用后仍无可用的标准，停止搜索——
依据训练知识中为该年级和主题选最匹配的标准继续，并
在教案中加上覆盖不全的脚注。绝不要调用 `find_curriculum_lessons`
来定位标准。

从选定的标准中提取：逐字的陈述文本、其 `code` 和
`caseIdentifierUUID`（存好——后续所有调用都需要）。当陈述有
字母编号的子部分时，逐字引用的是本课所针对的
子部分，父级按代码点名。

## 数学

在起草之前调用。已连接而不调用属于严重失误。完成所有调用，只提取
下方指定的内容，然后直接进入第 3 步——知识图谱的发现只通过
草案中的一行标准复述呈现在对话中，绝不做结果总结。

跨调用的数据依赖只有标准的 `caseIdentifierUUID`（供第 2–5 步使用）和
`find_curriculum_lessons` 返回的 `lessonIdentifier`（供
`find_materials_for_lesson` 使用）。所以：先解析标准，然后把第 2–4 步的
调用和 `find_curriculum_lessons`——各自带全下方指定的参数——
作为一个并行批次发出，然后获取材料。

**可用工具：** `find_standard_statement`、`find_standards_progression_from_standard`、`find_misconceptions_for_standard`、`find_learning_components_from_standard`、`list_standards_for_mathematical_practice`、`find_curriculum_lessons`、`find_materials_for_lesson`。

1. **标准**：按上文*解析标准*以 `academicSubject="Mathematics"` 解析标准。在教案的标准标注块中逐字使用其陈述文本原文。

2. **预备标准**：调用 `find_standards_progression_from_standard(caseIdentifierUUID, direction="backward")` → 提取：唯一的主要预备标准，逐字。用于学习目标 (LEARNING GOAL) 一节。不可妥协——不点名先前标准属于严重失误。

3. **学习成分**：调用 `find_learning_components_from_standard(caseIdentifierUUID)` → 提取：至多 5 条子技能描述（未知数位置、题型）。直接用作 SWBAT 要点和课堂观察模板中的观察要点行标签。其余舍弃。

4. **迷思概念**：调用 `find_misconceptions_for_standard(caseIdentifierUUID, subject="Mathematics")` → 提取：最相关的 3 个迷思概念。每个只保留学生行为和教师动作，用你自己的话改写。如果没有结果，从训练知识起草 3 个。

5. **课程材料**：调用 `find_curriculum_lessons(caseIdentifierUUID=<第 1 步的 uuid>, author="Illustrative Mathematics")` → 选择最相关的一课（年级匹配优先）。调用 `find_materials_for_lesson(lessonIdentifier, materialSource=["lesson", "activity"])` 一次获取课程概览和活动材料 → 提取：(a) 活动名称和顺序，(b) 涉及的题型和未知数位置，(c) 任何明确的话语动作。舍弃完整的活动叙述和面向学生的文本——这些绝不能逐字复制。

6. **SMP（数学实践标准）**：从训练知识中选 2–3 条。无需知识图谱调用。

**课程教材术语检查（如果未确认 IM）：** 继续之前，扫描你的工作笔记，
确认其中没有提及 "Illustrative Mathematics"、"IM"、任何 MLR 名称
(MLR 1–8)、"Compare and Connect"、"Stronger and Clearer Each Time"
或任何 IM 课次/活动标题。清除任何残留——未确认 IM 的教师
绝不能在课程或对话中收到 IM 专属术语（与 SKILL.md 的
版权护栏同一条规则）。

**如果知识图谱未连接：** 依据最佳知识起草；加脚注：*"Generated without
the Learning Commons Knowledge Graph. Standards and misconceptions reflect
general best practice."*（未连接 Learning Commons 知识图谱生成。标准与迷思概念
反映通用最佳实践。）

→ **知识图谱阶段完成。立即进入第 3 步。**

---

## ELA

在起草之前调用。已连接而不调用属于严重失误。按顺序完成所有调用，
只提取指定的内容，然后直接进入第 3 步——知识图谱的发现只通过
草案中的一行标准复述呈现在对话中，绝不做结果总结。

**可用工具：** `find_standard_statement`、`find_learning_components_from_standard`

1. **标准**：按上文*解析标准*以 `academicSubject="English Language Arts"` 解析标准（代码形如 RL.4.3、RI.6.6、RF.1.2b、W.8.1、L.5.4）。在第 1 节中逐字使用其陈述文本原文。

2. **学习成分**：调用 `find_learning_components_from_standard(caseIdentifierUUID)` → 提取：如可用，至多 5 条子技能描述。直接用作第 2 节的 SWBAT 要点。其余舍弃。

3. **文本复杂度检查**：如果已确定锚文本（来自教师或知识图谱），注意其 Lexile 蓝思值是否落在正确的 CCSS 年级段区间内。超出区间时标注提示。

**如果知识图谱未连接：** 依据最佳知识起草；加脚注：*"Generated without
the Learning Commons Knowledge Graph. Standards and misconceptions reflect
general best practice."*（未连接 Learning Commons 知识图谱生成。标准与迷思概念
反映通用最佳实践。）

→ **知识图谱阶段完成。立即进入第 3 步。**

---

## 科学

在起草之前调用。已连接而不调用属于严重失误。按顺序完成所有调用，
只提取指定的内容，然后直接进入第 3 步——知识图谱的发现只通过
草案中的一行标准复述呈现在对话中，绝不做结果总结。

**可用工具：** `find_standard_statement`、`find_curriculum_lessons`、`find_materials_for_lesson`。

注意：`find_learning_components_from_standard` 和 `find_standards_progression_from_standard`
对科学标准**不**返回数据——不要调用它们。

1. **标准**：按上文*解析标准*以 `academicSubject="Science"` 解析标准（代码是 NGSS 表现预期，如 `MS-LS2-3`、`3-LS1-1`、`HS-PS1-1`）。在第 1 节中逐字使用其陈述文本原文。

2. **OpenSciEd 单元与课次**：调用 `find_curriculum_lessons(caseIdentifierUUID=<第 1 步的 uuid>, author="OpenSciEd")` → 选择最相关的一课（年级匹配优先，其次主题最接近）。调用 `find_materials_for_lesson(lessonIdentifier, materialSource=["activity"])` → 提取：(a) 单元锚定现象；(b) 单元驱动性问题；(c) 本课的探究现象或问题；(d) 本课在单元故事线中的位置；(e) 前置的 SEP 和 CCC；(f) 使用的具体例行环节或活动结构。**绝不逐字复制 OSE 面向学生的文本、探究提示或讨论问题——这些必须改写为原创内容。**

**如果知识图谱未连接：** 依据最佳知识起草；加脚注：*"Generated without
the Learning Commons Knowledge Graph. Standards and OpenSciEd alignment reflect
general best practice."*（未连接 Learning Commons 知识图谱生成。标准与 OpenSciEd
对齐反映通用最佳实践。）

→ **知识图谱阶段完成。立即进入第 3 步。**

---

## 社会学科

用知识图谱查找该主题和年级段的权威标准陈述。这让课程锚定在
真实的标准上，而不是转述。

1. **标准**：按上文*解析标准*以 `academicSubject="Social Studies"` 和
   `jurisdiction="<州>"` 解析标准（必需——社会学科标准只挂在各州之下，
   绝不在 `Multi-State` 下）。在教案头部的 `**Standard:**` 下逐字使用
   其陈述文本，并让它锚定驱动性问题和形成性任务。

**如果找不到标准：** 让课程对齐训练知识中最相关的州专属标准，
并简要注明：*"Standard lookup not available for [state/code]."*（[州/代码]
的标准查询不可用。）不要中止生成。

→ **知识图谱阶段完成。立即进入第 3 步。**

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
