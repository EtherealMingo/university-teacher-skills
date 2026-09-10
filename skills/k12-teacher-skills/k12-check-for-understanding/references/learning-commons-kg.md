# Learning Commons KG——k12-check-for-understanding 的调用序列

仅在连接器 (connector) 可用时供第 2 步使用；否则按 SKILL.md 的"未连接"分支执行。已连接时调用
KG 是强制要求。每一次调用都发生在**设计任何题目之前**，且任何原始结果都不进入对话。

---

## 解析标准

先从主题推断编码，然后调用
`find_standard_statement(code="<code>", academicSubject="Mathematics")`。

- **指名的州框架**（TEKS、SOL、OAS、CA、MA……）：传入 `jurisdiction="<state>"`，并使用该框架
  自己的编码，而不是用 CCSS 近似替代。
- **没有返回结果：** 改用 `keywords=[...]` 加上最有辨识度的内容词重试。
- **返回中带有 `subStandards`：** 子条目通常才是正确的锚点——横跨多个子条目的父标准对 1–3 道题
  来说太宽了。

存下**逐字原文的标准表述**（放入元信息块 (meta block)，绝不转述）、**编码**，以及下面每次调用
都要用到的 **`caseIdentifierUUID`**。确认它与教师所要求的一致。

---

## 查找学习组件

`find_learning_components_from_standard(caseIdentifierUUID)` 返回组成该标准的细粒度学习目标——
即候选的范围锚点。**全部**审阅；第一个返回的并不一定是可测性最强的。组件附带的任何约束
（数值范围、分母集合、运算类型、表征形式）都约束题目设计。**如果没有返回任何结果**，就在第 3 步
的提议中如实说明，改为从标准自身的子条目中选取——理由相同，同样停下来等确认。

---

## 查找进阶与连贯性图谱

`find_standards_progression_from_standard(caseIdentifierUUID, direction="backward")`，以及同一调用
改用 `direction="forward"`——两个方向都是必需的。返回结果携带着**连贯性图谱 (coherence map)**，
而每一条"低年级 vs. 本年级"归类路线的依据是这张图，而不是那串编码清单。从中提取：

1. **先备理解**——学生必须已经具备的东西。保留具体的低年级标准**编码**；指南会把"先备缺漏"类
   作答路由到一个指名的编码上。
2. **本标准的独特要求**——学生*在这个年级*学到的东西，此前不知道、此后也尚未形式化的东西。
3. **本年级 vs. 非本年级的错误分界线**——哪些错误意味着先备缺漏，哪些意味着本年级困惑。在这里
   定下来，而不是等到写稿时再定。

---

## 查找迷思概念与教学指导

`find_misconceptions_for_standard(caseIdentifierUUID, subject="Mathematics")` 返回有研究依据的
学生错误及相应的教学指导。**错误**驱动干扰项设计；**指导**把"回头复习低年级内容"变成一个有名字
的子技能或任务类型。

优先选取与**已确认的学习组件**最相关的 3–5 条错误，而不是针对整条标准。如果相关的不足三条，
用你自己的知识补足剩余位置；绝不捏造一条"有据可查"的错误。为每条记录下它属于**先备缺漏
(prerequisite gap)** 还是**本年级困惑 (on-grade confusion)**。

**署名：** 这些来源——无论是出版商、课程还是研究数据集——一律不出现在两份文件或任何对话消息中
（见 SKILL.md 的数据使用护栏）。

---

**KG 阶段完成。进入第 3 步的焦点提议（若焦点已确认，则进入第 4 步）。**

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
