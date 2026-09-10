---
name: university-teacher
description: "高校教师工作全流程 AI 提效总控。覆盖教学、科研、指导、评审、考核五大场景共 14 个子技能：教案与课件、出题与试卷分析、论文指导与答辩、项目申报、期刊审稿、教学竞赛、科普讲座、年度考核与职称材料、研究生组会、课堂互动与平时分。当教师说「帮我备课」「出一套题」「看看这篇论文」「写个本子」「准备职称材料」「组会安排」「写审稿意见」时使用，总控会路由到对应子技能。Triggers: 备课、教案、课件、出题、试卷分析、成绩分析、论文指导、开题、答辩、申报书、本子、审稿、职称、述职、组会、科普、平时分。"
---

# 高校教师 AI 提效技能包 · 总控

> **Goal**：把高校教师日常最耗时的 14 类工作交给 AI 出**初稿**，教师只做判断与补全。
> 本文件是路由入口；每个子技能是一套独立工作流。

## 使用前必读

| 文件 | 作用 |
|---|---|
| `CONVENTIONS.md` | **开发与使用宪法**：vendor-first、不虚构、人工确认位、敏感数据 |
| `vendor/VENDOR.md` | 上游底座溯源与**许可证合规说明** |
| `vendor/office-layer/SKILL.md` | **文件产出唯一通道**（docx/pptx/xlsx/pdf） |
| `README.md` | 场景全景（学期时间轴、按角色、14 个技能详解） |

## 环境自检与自举安装

**每次开始工作前先跑一次环境自检**，缺依赖就装：

```bash
# 自检：确认依赖与包完整性
python3 verify.py

# 若报缺依赖（docx/pptx/openpyxl），装一次即可
bash vendor/office-layer/bootstrap.sh
```

**如果本技能包只被部分安装或路径不对**（例如 `vendor/office-layer/scripts/` 不存在），
用自带安装脚本自举到正确位置：

```bash
# 自动探测各 agent 技能目录并软链（幂等，重复运行安全）
bash install.sh

# 或从零拉取（本包公开）
curl -fsSL https://raw.githubusercontent.com/EtherealMingo/university-teacher-skills/main/install.sh | bash
```

安装脚本会完成：取源 → 落到 `~/.local/share/university-teacher-skills` → 建 venv 装依赖
→ 软链到各 agent 技能目录 → 跑 `verify.py` 自检。

> **执行任何命令前，先 `cd` 到本包根目录。** 全部 `vendor/...` 路径都是相对包根写的，
> 换目录执行会找不到文件。

## 路由表

判断教师意图 → 打开对应 `skills/<name>/SKILL.md`。触发词不明确时，
**先确认四件事**：学科 / 课程名 / 学生层次 / 产出物格式。

### 教学

| 子技能 | 何时用（教师会这么说） | 底座 |
|---|---|---|
| [`lesson-plan`](skills/lesson-plan/SKILL.md) | 「写个教案」「这节课怎么设计」「教学设计」 | `vendor/education-skills/教學設計/` |
| [`lecture-slides`](skills/lecture-slides/SKILL.md) | 「做课件」「把这章做成 PPT」 | `vendor/office-layer/`（pptx） |
| [`quiz-generator`](skills/quiz-generator/SKILL.md) | 「出一套题」「编几道练习题」「随堂小测」 | `vendor/ibook-skills/quiz-generator/` |
| [`exam-pipeline`](skills/exam-pipeline/SKILL.md) | 「审核这套试卷」「出评分细则」「考后成绩分析」「试卷归档」 | `vendor/office-layer/`（xlsx 分析） |
| [`classroom-live`](skills/classroom-live/SKILL.md) | 「随堂投票题」「这节课的提问链」「互动记录算平时分」 | `vendor/ibook-skills/quiz-generator/` |
| [`teaching-contest`](skills/teaching-contest/SKILL.md) | 「准备教学竞赛」「设计示范课」「教学创新大赛」「说课稿」「模拟评委提问」 | `lesson-plan` 增强 + `vendor/education-skills/教學設計/` + `vendor/k12-teacher-skills/` + `awesome-benzi` 质量门（MOCK_REVIEW）+ `slides-polish` |

### 科研

| 子技能 | 何时用 | 底座 |
|---|---|---|
| [`research-assistant`](skills/research-assistant/SKILL.md) | 「实证研究怎么做」「帮我设计研究方案」「数据分析」 | `vendor/empirical-research/` |
| [`grant-proposal`](skills/grant-proposal/SKILL.md) | 「写本子」「申报书」「选题查重」「模拟评审」 | `vendor/awesome-benzi/` |
| [`paper-to-slides`](skills/paper-to-slides/SKILL.md) | 「论文做成汇报 PPT」「组会要讲这篇」 | `vendor/paper-slides/` + `vendor/slides-polish/` |
| [`peer-review`](skills/peer-review/SKILL.md) | 「写审稿意见」「这篇论文评审一下」「审稿意见怎么写」「这稿子能不能收」 | `vendor/paper-slides/` 论文类型量规 + `vendor/awesome-benzi/references/QUALITY_GATES.md` 问题分级 + `vendor/education-skills/學習分析/` 互评方法 + `vendor/empirical-research/econ-audit/` 方法学审查 + `vendor/office-layer/`（原生批注） |

### 指导

| 子技能 | 何时用 | 底座 |
|---|---|---|
| [`thesis-supervisor`](skills/thesis-supervisor/SKILL.md) | 「看开题报告」「写论文评语」「预判答辩问题」「批改论文」 | `vendor/office-layer/`（**原生批注**） |
| [`lab-meeting`](skills/lab-meeting/SKILL.md) | 「安排组会轮值」「文献派工」「生成组会纪要」 | `paper-to-slides` + `office-layer` |

### 考核与对外

| 子技能 | 何时用 | 底座 |
|---|---|---|
| [`annual-review`](skills/annual-review/SKILL.md) | 「写年度述职」「整理职称材料」「教学成果奖」 | `vendor/awesome-benzi/` 派生 |
| [`science-outreach`](skills/science-outreach/SKILL.md) | 「做个科普 PPT」「给中学生讲我的研究」「科普讲座怎么准备」「把研究讲给外行听」 | 独立底座：`vendor/office-layer/`（pptx）+ `vendor/slides-polish/` + `vendor/learning-education/thinking-toolkit/`（类比讲解）+ `vendor/education-skills/偏鄉教育/`（受众适配）。与 `lecture-slides` 是**不同**的风格体系，见其文档的风格对照表 |

## 三条全局铁律

1. **不虚构**。学生数据绝不生成；文献、政策条文、个人事实一律用 `【待补：…】` 占位。
2. **产出是初稿**。涉及评价、打分、结论的内容必须留人工确认位，AI 不给终稿。
3. **文件产出走 office-layer**。不用文本框拼表格，不生成 Markdown 当交付物。

## 敏感数据提醒

成绩、学号、姓名属个人信息。分析只在本机进行，任务结束后请删除中间文件。
交付说明里需注明「本文件含学生个人信息，请注意保管」。

## 组合用法（跨技能编排）

| 需求 | 编排 |
|---|---|
| 开学备课 | `lesson-plan` → `lecture-slides` → `classroom-live`（投票题） |
| 期末周 | `quiz-generator`（出题）→ `exam-pipeline`（审卷+分析+归档） |
| 指导一个毕业班 | `thesis-supervisor`（开题）→ 过程批注 → 答辩预案 |
| 申报季 | `grant-proposal`（查重→匹配→撰写→模拟评审） |
| 组会 | `lab-meeting`（派工）→ `paper-to-slides`（学生汇报稿） |
| 年底考核 | `annual-review`（成果归表→述职→职称） |

## 验收自检（维护本包时用）

改完任何子技能，过一遍 `CONVENTIONS.md` 第 8 节的自检清单，重点确认：
引用的 `vendor/` 路径**真实存在**、文件产出走了 office-layer、评价性内容留了人工确认位。
