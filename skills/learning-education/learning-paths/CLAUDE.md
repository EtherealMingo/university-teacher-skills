# Tov-learn —— 智能学习系统

基于 Claude Code skills 构建的智能导师系统。

---

## 技能模块

`/learn` 技能由独立模块组成。每个模块负责一个领域，且完全自治。

| 模块 | 文件 | 内容 |
|-------|------|------|
| 入口 + 路由 | `.claude/commands/learn.md` | 路由 + TTS 助手指函数 + 步骤 0-2 |
| 初始化设置 | `.claude/commands/learn/setup.md` | 首次设置、语音、全局安装 |
| 智能续学 | `.claude/commands/learn/resume.md` | 智能入口——根据进度建议下一步动作 |
| 教学 | `.claude/commands/learn/teaching.md` | 加载课节、Journey 格式、教学循环 |
| 测验 | `.claude/commands/learn/quiz.md` | 考试、评分、间隔重复（spaced repetition） |
| 进度 | `.claude/commands/learn/progress.md` | 保存教程文件（tutorials）、知识图谱 |
| 状态 | `.claude/commands/learn/status.md` | HTML 仪表盘——全部课节、成绩、待复习 |
| 项目架构分析 | `.claude/commands/learn/project-analysis.md` | 代码扫描、架构师访谈、HTML 架构图 |
| 幻灯片 | `.claude/commands/learn/slides.md` | 逐字朗读脚本、交互式查看器、自动 TTS |
| 导出 | `.claude/commands/learn/export.md` | 导出全部学习者数据为 ZIP——备份/迁移设备 |
| 导入 | `.claude/commands/learn/import.md` | 从 ZIP 导入学习者数据——全量替换或仅追加 |
| 部署 | `.claude/commands/learn/deploy.md` | 选择部署工具（GitHub Pages / Cloudflare / Render / Vercel）、CLI 优先、向 FAQ 贡献 |
| CLI 优先（参考） | `.claude/commands/learn/cli-first.md` | 共享原则——优先 CLI 而非仪表盘；其他模块引用它 |

辅助脚本位于 `.claude/scripts/`（PowerShell——幻灯片服务器、HTML 生成器）。

**开发规则：** 每个模块自治——不假设其他模块已加载。模块需要的信息由它自己读取。TTS 助手指函数定义在 `learn.md` 中，在每个模块之前加载。

---

## 课程结构

```
courses/
  [course-name]/
    COURSE.md                          ← 名称、描述、模块列表、默认 course.path
    lessons/
      [XX-module-name]/
        [X.Y]-[lesson-name]/
          [X.Y]_script.txt             ← 脚本（按 [מעבר שקף] 切分）
          [X.Y]_exercises.md           ← 练习
```

唯一启用的课程是 **AI Dev**——它是所有位置（setup、模板、文档）的默认值。

| 课程 | 目录 | course.path | 状态 |
|------|--------|-------------|-------|
| AI Dev | `courses/ai-dev/` | `courses/ai-dev/lessons` | 启用（默认） |
| AI Engineer | `courses/_archive/ai-engineer/` | `courses/_archive/ai-engineer/lessons` | 已归档——不在 setup 中提供；仅可通过自定义路径访问 |

---

## 数据——按学习者存储（在仓库之外）

保存于 `~/skill-tutor-tutorials/`：

```
settings.json                          ← 语言、TTS、course.name、course.path
learner_profile.md                     ← 个人档案 + 当前学习者
tutorials/lesson-X.Y.md               ← 课节小结 + 问答
progress/lesson-X.Y.md                ← 成绩 + 建议复习日期
topics/knowledge_map.md               ← 完整知识图谱
architectures/[project-name].html     ← 架构图
```

---

## 添加新模块

1. 在 `.claude/commands/learn/[module-name].md` 创建文件
2. 在上面的模块表格中添加一行
3. 在 `learn.md` 中添加路由（步骤 2——路由表）
4. （可选）如果启用了全局安装——更新 `setup.md` 第 F 节中被复制的文件列表。默认：`/learn` 仅从本仓库运行，不做全局安装。
