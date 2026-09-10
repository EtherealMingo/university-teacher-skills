# 智能续学模块

*当 /learn 不带参数被调用时加载。用基于实际进度的智能建议，替代静态的「上课还是项目分析？」提示。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

---

## 步骤 1——读取进度状态

静默读取：
- `~/skill-tutor-tutorials/learner_profile.md`——从 `## Lessons Studied` 找最近一节课
- 所有 `~/skill-tutor-tutorials/progress/lesson-*.md`——提取下次复习日期
- `~/skill-tutor-tutorials/topics/knowledge_map.md`——找出进行中的课节
- `~/skill-tutor-tutorials/project/ai-dev-project.md`——结业项目状态（可能不存在）

算出今天的日期。对每节课分类：
- **逾期**——下次复习日期早于今天
- **今日到期**——下次复习日期就是今天
- **进行中**——已开始、成绩低于 8、尚未到期
- **下一节新课**——COURSE.md 中第一节没有进度文件的课

检查结业项目资格：如果学习者有第 2 模块任意课节（任意 2.x 课）的进度文件，或已完成 1.8 及之前的全部课节，即视为可以开始结业项目。

---

## 步骤 2——构建智能建议

根据发现的情况展示选项。只展示确实适用的选项。

**如果有逾期或今日到期的课节：**
```
Welcome back. Here's where things stand:

🔁 Due for review: Lesson [X.X] — [title] ([N] days overdue)
📖 Next new lesson: [X.X] — [title]
🔍 Project analysis
[if eligible: 🏗️ Final Project — [show "starting" or current phase if already selected]]

What would you like to do?
```

**如果没有到期的（状态良好）：**
```
Welcome back. You're up to date on reviews.

📖 Continue: Lesson [X.X] — [title] (in progress)
📖 Next new lesson: [X.X] — [title]
🔍 Project analysis
[if eligible: 🏗️ Final Project — [show "starting" or current phase if already selected]]

What would you like to do?
```

**如果还没有任何进度（第一次使用）：**
```
Welcome. Let's start with the first lesson.

📖 Lesson 0.1 — [title]
🔍 Analyze your current project first

What would you like to do?
```

---

## 步骤 3——根据回答路由

| 回答 | 动作 |
|--------|--------|
| 选了某个课号 | 读取 `.claude/commands/learn/teaching.md` 并加载该课 |
| "review" / 选了到期的课 | 读取 `.claude/commands/learn/teaching.md` 并加载该课 |
| "project analysis" | 读取 `.claude/commands/learn/project-analysis.md` |
| "final project" / "project" / 选了 🏗️ | 读取 `.claude/commands/learn/project.md` |
| "status" / "dashboard" | 读取 `.claude/commands/learn/status.md` |
