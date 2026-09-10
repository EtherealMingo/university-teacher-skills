# 状态模块

*当 $ARGUMENTS = "status" 时加载。生成 HTML 进度仪表盘。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

---

## 步骤 1——收集数据

静默读取这些文件：
- `~/skill-tutor-tutorials/topics/knowledge_map.md`
- 所有匹配 `~/skill-tutor-tutorials/progress/lesson-*.md` 的文件
- 所有匹配 `~/skill-tutor-tutorials/tutorials/lesson-*.md` 的文件（取 frontmatter：topic、understanding_score、last_quizzed）

从每个进度文件中提取：
- 课号
- 测验成绩与日期
- 下次建议复习日期

计算：
- **逾期（Overdue）**——下次复习日期早于今天
- **今日到期（Due today）**——下次复习日期就是今天
- **即将到期（Upcoming）**——下次复习日期在 7 天内
- **已掌握（Mastered）**——最近一次成绩 8 分及以上
- **进行中（In progress）**——已开始但最近一次成绩低于 8
- **未开始（Not started）**——没有进度文件（与 COURSE.md 课节清单交叉比对）

---

## 步骤 2——生成 HTML 仪表盘

保存到 `~/skill-tutor-tutorials/dashboard.html`：

```html
<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>Learning Dashboard</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', sans-serif; background: #F9FAFB; padding: 40px; color: #111827; }

    .header { margin-bottom: 32px; }
    .header h1 { font-size: 1.6rem; font-weight: 700; }
    .header p { color: #6B7280; font-size: 0.9rem; margin-top: 4px; }

    .stats { display: flex; gap: 16px; margin-bottom: 32px; flex-wrap: wrap; }
    .stat { background: white; border-radius: 10px; padding: 16px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); min-width: 120px; }
    .stat-value { font-size: 1.8rem; font-weight: 700; }
    .stat-label { font-size: 0.75rem; color: #6B7280; margin-top: 2px; }
    .stat.alert .stat-value { color: #EF4444; }
    .stat.good .stat-value { color: #10B981; }

    .section-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase;
                     letter-spacing: 1px; color: #6B7280; margin-bottom: 12px; }

    .due-list { margin-bottom: 32px; }
    .due-item { background: white; border-radius: 8px; padding: 14px 18px;
                margin-bottom: 8px; display: flex; justify-content: space-between;
                align-items: center; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
    .due-item .lesson-id { font-weight: 600; font-size: 0.9rem; }
    .due-item .lesson-topic { color: #6B7280; font-size: 0.85rem; }
    .due-item .badge { font-size: 0.75rem; padding: 3px 10px; border-radius: 999px; font-weight: 600; }
    .badge.overdue { background: #FEE2E2; color: #DC2626; }
    .badge.today { background: #FEF3C7; color: #D97706; }
    .badge.upcoming { background: #DBEAFE; color: #2563EB; }

    .lessons-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                    gap: 12px; margin-bottom: 40px; }
    .lesson-card { background: white; border-radius: 10px; padding: 16px;
                   box-shadow: 0 1px 3px rgba(0,0,0,0.07); border-top: 3px solid #E5E7EB; }
    .lesson-card.mastered { border-top-color: #10B981; }
    .lesson-card.in-progress { border-top-color: #F59E0B; }
    .lesson-card.not-started { border-top-color: #E5E7EB; opacity: 0.7; }
    .lesson-card .lesson-num { font-size: 0.75rem; color: #6B7280; }
    .lesson-card .lesson-name { font-size: 0.9rem; font-weight: 600; margin: 4px 0; }
    .lesson-card .score { font-size: 0.8rem; color: #6B7280; }
    .score-bar { height: 4px; background: #E5E7EB; border-radius: 2px; margin-top: 8px; }
    .score-fill { height: 4px; border-radius: 2px; background: #10B981; }
    .score-fill.mid { background: #F59E0B; }
    .score-fill.low { background: #EF4444; }
  </style>
</head>
<body>
  <div class="header">
    <h1>Learning Dashboard</h1>
    <p>Updated [DD-MM-YYYY]</p>
  </div>

  <div class="stats">
    <div class="stat good">
      <div class="stat-value">[N]</div>
      <div class="stat-label">Mastered</div>
    </div>
    <div class="stat">
      <div class="stat-value">[N]</div>
      <div class="stat-label">In Progress</div>
    </div>
    <div class="stat alert">
      <div class="stat-value">[N]</div>
      <div class="stat-label">Due for Review</div>
    </div>
    <div class="stat">
      <div class="stat-value">[avg]/10</div>
      <div class="stat-label">Avg Score</div>
    </div>
  </div>

  <!-- 仅当存在到期/逾期的课节时才显示本节 -->
  <div class="due-list">
    <div class="section-title">Due for Review</div>
    <div class="due-item">
      <div>
        <div class="lesson-id">Lesson [X.X]</div>
        <div class="lesson-topic">[topic title]</div>
      </div>
      <span class="badge overdue">Overdue</span>
    </div>
    <div class="due-item">
      <div>
        <div class="lesson-id">Lesson [X.X]</div>
        <div class="lesson-topic">[topic title]</div>
      </div>
      <span class="badge today">Today</span>
    </div>
  </div>

  <div class="section-title">All Lessons</div>
  <div class="lessons-grid">
    <!-- 对每节课重复 -->
    <div class="lesson-card mastered">
      <div class="lesson-num">0.1</div>
      <div class="lesson-name">[Lesson Title]</div>
      <div class="score">Score: 9/10</div>
      <div class="score-bar"><div class="score-fill" style="width: 90%"></div></div>
    </div>
    <div class="lesson-card in-progress">
      <div class="lesson-num">0.2</div>
      <div class="lesson-name">[Lesson Title]</div>
      <div class="score">Score: 6/10</div>
      <div class="score-bar"><div class="score-fill mid" style="width: 60%"></div></div>
    </div>
    <div class="lesson-card not-started">
      <div class="lesson-num">1.1</div>
      <div class="lesson-name">[Lesson Title]</div>
      <div class="score">Not started</div>
      <div class="score-bar"></div>
    </div>
  </div>
</body>
</html>
```

用步骤 1 收集的数据填好所有内容。按 COURSE.md 为每节课生成一张卡片。

---

## 步骤 3——向学习者汇报

保存文件后：

```
Dashboard saved: ~/skill-tutor-tutorials/dashboard.html
Open it in a browser to view your progress.

[N] lessons mastered · [N] in progress · [N] due for review
```

如果有逾期的课节，追加：
```
⚠️ [N] lessons are overdue for review: [lesson numbers]
Type `/learn` to see what to do next.
```
