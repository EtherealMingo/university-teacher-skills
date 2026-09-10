# 进度模块

*在讲完至少一个章节后，以及收到 "stop" 命令时加载。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

---

## 保存教程文件

创建或更新 `~/skill-tutor-tutorials/tutorials/lesson-{lesson_number}.md`。

**如果文件不存在——创建：**

```markdown
---
topic: [lesson title]
lesson: {lesson_number}
source_project: [learner's project from profile]
understanding_score: null
last_quizzed: null
created: DD-MM-YYYY
last_updated: DD-MM-YYYY
---

# [Lesson Title]

## Why This Matters
[Connection to learner's goals — what they can do after this lesson]

## Topics Covered
[Bullet list of each section covered, in the learner's words — not copied from the script]

## Key Insights
[2–3 mental models the learner gained]

## In Your Project
[How the topics connect to the learner's specific project]

## Common Mistakes to Watch For
[What the learner got wrong or hesitated on]

## Practice
[Specific practice suggestion in the context of their project]

## Q&A
[Every question the learner asked + the short answer]

## Quiz History
[Updated by quiz module]
```

**如果文件已存在——只做更新：**
- 追加到 Topics Covered（已覆盖主题）
- 追加到 Key Insights（关键心得）
- 追加到 Q&A（问答）
- 刷新 `last_updated`
- **不要替换**已有内容

---

## 更新知识图谱

更新 `~/skill-tutor-tutorials/topics/knowledge_map.md`：

```markdown
# Knowledge Map

## Mastered Topics (score 8+)
- [Lesson X.X — Title]: [one sentence — what the learner can now do]

## Topics In Progress (score 4–7)
- [Lesson X.X — Title]: [what needs reinforcement]

## Topics to Explore
- [Lesson X.X]: [why relevant to learner's goals]

## Connections Between Topics
- [Lesson A] → [Lesson B]: [how they connect]
```

如果文件已存在——只做更新；不要删除之前的条目。

---

## 更新学习者档案

更新 `~/skill-tutor-tutorials/learner_profile.md`——添加/更新 `## Lessons Studied`：

```markdown
## Lessons Studied
| Lesson | Title | Score | Last Date |
|--------|-------|-------|-----------|
| X.X | [title] | X/10 | DD-MM-YYYY |
```

---

## 会话结束（收到 "stop" 命令时）

保存所有文件后，展示会话小结：
- 本次覆盖的内容
- 剩余的内容
- 基于知识图谱推荐的下一步
