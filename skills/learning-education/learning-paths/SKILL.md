---
name: learning-paths
description: 学习路径与进度追踪模型的命令层参考：收录 Tov-learn 智能导师系统 /learn 技能的 15 个功能模块文档，涵盖初始化设置、智能续学入口、教学循环、测验与间隔重复、进度存档与知识图谱、HTML 状态仪表盘、结业项目跟踪、项目架构访谈、幻灯片逐字朗读模式、部署选型向导、上线安全检查、学习数据导入导出，以及 CLI 优先的共享原则。当需要设计、理解或仿写一个「按课节推进、随堂提问、测验打分、间隔复习、进度落盘」的学习路径系统，或参考其命令分层、模块自治、每学习者数据隔离的写法时使用。Triggers: 帮我设计一个带进度追踪的学习路径系统；怎么给课程做间隔重复和复习提醒；我想参考一个 AI 导师技能的模块划分方式；学习进度和测验成绩数据应该怎么存；帮我做一个学习进度仪表盘。
---

# 学习路径与进度追踪（命令层参考）

> **Goal:** 提供一套「学习路径 + 进度追踪」智能导师系统的命令层参考实现——`/learn` 入口按模块路由，每个模块独立负责一个领域（设置、教学、测验、进度、项目、部署、安全、导入导出等），学习者数据全部落盘在用户主目录，可跨会话续学、按间隔重复算法安排复习。

本包是上游 Tov-learn 仓库（希伯来文 AI 课程平台）的**命令层参考文档**子集：仅收录技能模块的设计与操作文档，未收录课程素材本身。各模块文档描述了加载时机、执行步骤、数据文件格式与模块间协作约定。

总体架构、课程目录结构、学习者数据布局与新增模块的开发规则，见同目录的 `CLAUDE.md`（面向 AI 的操作指引，已译为简体中文）。

## 参考文档

`learn-modules/` 下共 15 篇模块文档：

- [setup.md](learn-modules/setup.md) — 初始化设置模块：会话语言、称呼方式、课程选择、TTS 语音、学习风格（标准/诊断/苏格拉底）与详略档位，以及可选的全局安装。
- [resume.md](learn-modules/resume.md) — 智能续学模块：`/learn` 无参数入口，读取进度状态后给出「该复习什么、下一节新课是什么」的智能建议并路由。
- [teaching.md](learn-modules/teaching.md) — 教学模块：加载课节脚本、按三种学习模式（标准/诊断/苏格拉底）逐节授课、Journey 讲解格式、随堂问答记录与结课流程。
- [quiz.md](learn-modules/quiz.md) — 测验模块：随堂测与全课测两种模式、选择题与自由回忆题命题规则、评分公式、薄弱点记录与间隔重复复习日期计算。
- [progress.md](learn-modules/progress.md) — 进度模块：课节教程文件（tutorial）的创建与追加、知识图谱更新、学习者档案维护与「stop」时的会话小结。
- [status.md](learn-modules/status.md) — 状态模块：汇总全部课节的掌握度与复习到期情况，生成 HTML 进度仪表盘。
- [project.md](learn-modules/project.md) — 结业项目模块：项目选题、分阶段检查清单（checklist）跟踪、求助记录与结业验收清单。
- [project-analysis.md](learn-modules/project-analysis.md) — 项目架构访谈模块：自动代码扫描 + 五问架构访谈，生成 HTML 架构图并更新学习者档案。
- [slides.md](learn-modules/slides.md) — 幻灯片模式模块：逐字朗读课节脚本、启动交互式 HTML 查看器、自动 TTS 与练习生成。
- [display.md](learn-modules/display.md) — 显示规范模块：全部面向学习者输出的统一格式标准（章节头、讲解块、答题反馈、测验题、成绩单、会话小结）。
- [deploy.md](learn-modules/deploy.md) — 部署向导模块：三问诊断 + 决策树帮学习者选择部署工具（GitHub Pages / Cloudflare / Render / Vercel），并引导其向共享 FAQ 贡献 PR。
- [security.md](learn-modules/security.md) — 安全检查模块：对线上 URL 做 HTTP 实扫（敏感文件、安全响应头、鉴权端点），按八类常见漏洞出分级报告并保存复查记录。
- [export.md](learn-modules/export.md) — 导出模块：把 `~/skill-tutor-tutorials/` 下的全部学习者数据打包为 ZIP，用于备份或迁移设备。
- [import.md](learn-modules/import.md) — 导入模块：从 ZIP 恢复学习者数据，支持全量替换、合并、仅新增三种导入模式。
- [cli-first.md](learn-modules/cli-first.md) — CLI 优先共享原则：任何模块引导学习者做安装、部署、仓库操作时，优先命令行而非点界面，保证可复现。
- [teaching.md](learn-modules/teaching.md) 等模块共同引用的显示规范见 display.md；TTS 助手指函数定义在入口 `learn.md`（未收录，见上游仓库）。

## 来源与许可

上游 [TovTechOrg/Tov-learn](https://github.com/TovTechOrg/Tov-learn)，MIT 许可证（LICENSE 已随附）；仅收录命令层参考文档（原仓库为希伯来文课程平台，课程素材未收录）；文档本包译为简体中文。
