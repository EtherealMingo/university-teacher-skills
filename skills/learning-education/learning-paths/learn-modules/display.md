# 显示模块——视觉语言

*由 teaching.md、quiz.md 和 progress.md 加载。定义所有面向学习者输出的格式标准。*

一致地使用这些格式。每种交互类型只有一种格式——不要发明变体。

---

## 章节标题

在每个新课节段落的开头使用：

```markdown
---
### 📚 [current] / [total] — [Section Title]
```

---

## 讲解块（Journey 格式）

```markdown
**The problem:** [one sentence — what breaks without this]

**The insight:** [2–3 sentences in your own words]

**In your project:** [connection to learner's project or real-world example]

---
❓ [One thinking question. Not trivia.]
```

---

## 答题反馈

**答对：**
```markdown
✅ [Brief reinforcement — one sentence]

Continue?
```

**部分正确：**
```markdown
💡 Close. [One hint — don't give the answer]

Want to try again?
```

**答错：**
```markdown
↩️ Not quite. [One hint]

Give it another shot?
```

**第二次答错后——揭晓：**
```markdown
The answer is: [explanation]

Got it? Continue?
```

---

## 测验题

```markdown
---
## 🎯 Question [n] / 4

[Question text]
```

---

## 测验成绩

```markdown
---
## 🏆 Score: [X] / 10

| # | Type | | Note |
|---|------|---|------|
| 1 | Factual | ✅ | [note] |
| 2 | Why it matters | ⚠️ | [note] |
| 3 | Scenario | ✅ | [note] |
| 4 | Weak point | ❌ | [note] |

**Next review:** in [N] days · [date]
```

---

## 会话小结（收到 "stop" 时）

```markdown
---
## 📋 Session Summary — Lesson [X.X]

✅ **Covered:** [list of sections]
⏭ **Remaining:** [list of sections not covered, or "none"]
🔁 **Recommended next:** [lesson number + title]
```

---

## 命令提醒

在会话开始时、问候之后展示一次：

```markdown
> **Available:** continue · quiz me · explain again · summary · exercises · stop · read aloud · settings
```
