# 测验模块

*当使用 "quiz me" 触发语时加载。TTS 助手指函数定义在 learn.md 中。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

---

## 测验模式

| 触发语 | 范围 | 题目 |
|---------|-------|-----------|
| `quiz me` | 仅本次会话已讲过的章节 | 4 道选择题 + 1 道自由作答 |
| `quiz me full` / `quiz full` | **整份**课节脚本（加载 `{lesson_number}_script.txt`，按 `[מעבר שקף]` 切分，使用全部章节——不要假设固定数量） | 8 道选择题 + 1 道自由作答 |

出题之前，阅读 `~/skill-tutor-tutorials/tutorials/lesson-{lesson_number}.md` 中的 **Quiz History**（测验历史）。如果学习者以前测过这节课，**变换题目**——换角度、换干扰项，并偏向此前记录过的薄弱点。所有题目都必须事实正确、且紧扣课节内容。

---

## 测验形式

**步骤 1——选择题（在一次 `AskUserQuestion` 调用中批量给出）。**

构建选择题（普通模式 4 道，full 模式 8 道 → 分两次 `AskUserQuestion` 调用，每次 4 道），覆盖以下类型：

1. **事实型**——是什么 / 怎么做
2. **意义型**——后果与动机
3. **场景型**——「如果发生了 X，你会怎么做？」
4. **薄弱点型**（*普通模式*）——学习者本次会话中犹豫过的章节。*full 模式没有会话历史 → 替换为一道联结两个章节的**综合**题。*

每道题：**1 个正确选项 + 2–3 个貌似合理的干扰项**，全部使用 `session.language`。`AskUserQuestion` 会自动追加一个 **"Other"** 选项——如果学习者选了它并自由输入，对该答案做定性评判。设置 `multiSelect: false`。

**重要——绝不要在测验选项上使用 `description` 字段。** 描述在学习者作答前就能看到，会泄露或暗示正确答案。每个选项的 `description` 都留空或完全省略。

**重要——变换正确答案的位置：** 正确选项在每道题中必须出现在不同位置。永远不要把正确答案放在所有题目的同一槽位（例如总是第一个）。要分散到各个位置——例如：第 1 题→第 3 位，第 2 题→第 1 位，第 3 题→第 2 位，第 4 题→第 3 位。这能防止按规律猜答案。

**步骤 2——最后来一道自由作答的回忆题。**

在选择题之后，问**一道**开放式问题（综合型或「用自己的话解释」）。这是回忆测试——等待学习者输入答案。

---

## 评分

先给 **1–10** 的总分，然后立即展示**完整复盘表**——每道题一行：

| # | 题目 | 你的答案 | 正确答案 | 简要解析 |
|---|-------|--------|------------|----------|
| 1 | ... | ✅ / ❌ [答了什么] | [正确答案] | [一两句为什么] |

表格规则：
- 展示**每一道**题——选择题和自由作答都要。
- 答对的：标 ✅，仍然展示正确答案和一句「为什么对」。
- 答错或部分正确的：标 ❌，展示学习者的答案、正确答案，并用 1–2 句解释概念。
- 自由作答：引用学习者答案中的关键想法，对照预期的关键想法。
- 解析使用 `session.language`，每条最多 2 句。

评分公式（保持不变）：
- **普通模式：** 每道选择题答对 = 1.5 分（共 6 分）+ 自由作答最多 4 分 → 满分 10。
- **Full 模式：** 每道选择题答对 = 1 分（共 8 分）+ 自由作答最多 2 分 → 满分 10。

*（若启用了 TTS，朗读成绩小结——跳过表格）*

---

## 保存成绩——两个位置

**A. 更新** `~/skill-tutor-tutorials/tutorials/lesson-{lesson_number}.md`：

追加到文件末尾：
```markdown
## Quiz History

| Date | Score | Weak Points |
|------|-------|-------------|
| DD-MM-YYYY | X/10 | [topics to revisit] |
```

更新 frontmatter：`understanding_score: X` 和 `last_quizzed: DD-MM-YYYY`。

**B. 保存 / 更新** `~/skill-tutor-tutorials/progress/lesson-{lesson_number}.md`：

```markdown
# Progress: Lesson {lesson_number}

## Sessions
| Date | Sections Covered | Quiz Score | Notes |
|------|-----------------|-----------|-------|
| DD-MM-YYYY | [list] | X/10 | [weak points] |

## Spaced Repetition
- Score 1–3: review within 2 days
- Score 4–6: review within 13 days
- Score 7–8: review within 34 days
- Score 9–10: review within 89 days

Next recommended review: [date based on score]
```

---

## 下一课推荐

保存成绩后，加载 `~/skill-tutor-tutorials/topics/knowledge_map.md`，并根据已覆盖的内容推荐一节相关的课。
