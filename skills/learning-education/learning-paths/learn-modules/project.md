# 项目模块

*当 /learn 以 "project" 参数被调用，或学习者从智能续学（resume）中选择结业项目时加载。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

---

## 步骤 1——加载项目状态

读取 `~/skill-tutor-tutorials/project/ai-dev-project.md`。

- **不存在** → 进入项目选题（步骤 2）
- **存在，status = in_progress** → 进入项目仪表盘（步骤 3）
- **存在，status = completed** → 展示完成总结，并询问他们想要复盘还是展示

---

## 步骤 2——项目选题

加载 `courses/ai-dev/lessons/03-final-project/projects.md`。

展示每个项目的简短摘要：

```
🎓 פרויקט גמר — AI Dev

בחרו פרויקט אחד. כל הפרויקטים מחייבים: deploy פעיל, הדגמה חיה בפני הכיתה, ו-commit history אמיתי.

א — מערכת תמיכת לקוחות WhatsApp (14 שעות | בינונית-גבוהה)
WhatsApp webhook + Vertex AI + Supabase + Next.js Dashboard.

ב — Document Intelligence Service (12 שעות | בינונית-גבוהה)
PDF/CSV → Vertex AI Structured Output → Dashboard + REST API.

ג — סוכן Intelligence יומי בTelegram (12 שעות | גבוהה)
Agent Loop מאפס, 5+ Tools, Cloudflare Cron.

ד — מנוע Code Review אוטונומי לGitHub (16 שעות | גבוהה)
3 Specialist Agents במקביל → PR Comment אוטומטי.

איזה פרויקט בוחרים?
```

学习者选定后，从 `projects.md` 加载所选项目的完整规格说明。然后创建 `~/skill-tutor-tutorials/project/ai-dev-project.md`：

```markdown
---
project: [א/ב/ג/ד]
project_title: [title]
selected_at: DD-MM-YYYY
status: in_progress
current_phase: 1
total_phases: [N from project spec]
---

## Checklist
[all phase lines from the chosen project's שלבי הפרויקט, formatted as:]
- [ ] שלב 1 — [phase title]
- [ ] שלב 2 — [phase title]
...

## Project Checklist (final)
[all checklist items from the chosen project's Checklist section, all unchecked]

## Help Requests

## Notes
```

然后进入步骤 3。

---

## 步骤 3——项目仪表盘

根据状态文件展示当前状态：

```
🏗️ פרויקט [letter] — [title]

התקדמות:
✅ שלב 1 — [title] (done)
🔄 שלב 2 — [title] ← עכשיו
☐ שלב 3 — [title]
...

מה רוצים לעשות?
1. עזרה עם שלב [N] (הנוכחי)
2. סמן שלב [N] כ-Done
3. הצג checklist מלא של ה-deliverables
4. הצג מפרט מלא של השלב הנוכחי
```

---

## 步骤 4——处理命令

**阶段求助 / 具体问题：**
- 从 `projects.md` 加载所选项目的相关阶段
- 结合该具体阶段的上下文作答
- 参考 `learner_profile.md` 中学习者的技术背景
- 追加到 `ai-dev-project.md` 的 "Help Requests"（求助记录）小节

**把阶段标记为完成：**
- 更新 `ai-dev-project.md` 中的检查清单——把 `[ ]` 标为 `[x]`
- 推进 `current_phase` 计数器
- 展示更新后的仪表盘（步骤 3）
- 如果所有阶段都完成 → 进入步骤 5

**checklist / 交付物：**
- 展示 `projects.md` 中全部最终检查项及其当前的勾选/未勾选状态

**规格 / spec：**
- 展示 `projects.md` 中当前阶段的完整规格说明

---

## 步骤 5——项目完成

当所有阶段都标记为完成时，更新状态文件：
- `status: completed`
- 添加 `completed_at: DD-MM-YYYY`

展示：

```
🎉 סיימת את פרויקט [letter]!

לפני ההגשה — ודא:
☐ GitHub repo URL עם commit history אמיתי (לא push אחד בסוף)
☐ URL פעיל — פתוח מכל מכשיר, לא localhost
☐ CLAUDE.md מתועד עם Tech Stack ו-Conventions
☐ חישוב עלות מדויק: X ש"ח ל-100 בקשות/יום
☐ מצגת 10 דקות מוכנה + הדגמה חיה שעובדת

בהצלחה בהגשה!
```

更新 `~/skill-tutor-tutorials/topics/knowledge_map.md`——在「已掌握主题」（Mastered Topics）下添加：
```
- Final Project [letter] — [title]: deployed [URL], completed [date]
```
