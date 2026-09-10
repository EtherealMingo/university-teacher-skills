---
name: university-teacher
description: "高校教师工作全流程 AI 提效总控。覆盖教学、科研、指导、行政事务、考核五大场景共 22 个子技能：教案与课件、出题与试卷分析、论文指导与答辩、项目申报、期刊审稿、教学竞赛、研究生组会、学生竞赛与双创指导、学生事务与谈心谈话、实习实训、行政填报与迎检、会议纪要与通知、教学运行排期、学术通信、推荐信与证明、科普讲座、年度考核与职称材料。当教师说「帮我备课」「出一套题」「看看这篇论文」「写个本子」「指导学生做大创」「写封推荐信」「算教学工作量」「写个调课申请」时使用，总控会路由到对应子技能。Triggers: 备课、教案、课件、出题、试卷分析、成绩分析、论文指导、开题、答辩、申报书、本子、审稿、职称、述职、组会、科普、平时分、大创、挑战杯、推荐信、谈心谈话、实习、工作量、纪要、调课、监考、教材、邀请函。"
---

# 高校教师 AI 提效技能包 · 总控

> **Goal**：把高校教师日常最耗时的 22 类工作交给 AI 出**初稿**，教师只做判断与补全。
> 不只是教学科研，也覆盖带学生、填表格、写通知这些琐碎但躲不掉的事。
> 本文件是路由入口；每个子技能是一套独立工作流。

## 使用前必读

| 文件 | 作用 |
|---|---|
| `CONVENTIONS.md` | **开发与使用宪法**：底座复用、不虚构、人工确认位、敏感数据 |
| `THIRD_PARTY_NOTICES.md` | 上游底座溯源与**许可证合规说明** |
| `skills/office-layer/SKILL.md` | **文件产出唯一通道**（docx/pptx/xlsx/pdf） |
| `README.md` | 场景全景（学期时间轴、按角色、22 个主技能 + 26 个底座技能详解） |

> 底座技能（26 个，供主技能引用，也可单独使用）位于 `skills/` 下：同一上游的一套
> 收进一个套件目录（`education-skills/`、`empirical-research/`、`ibook-skills/`、
> `k12-teacher-skills/`、`learning-education/`），独立件（`office-layer/`、
> `awesome-benzi/`、`paper-analyst/`、`slides-polish/`）与主技能一样平铺。
> 清单见 `README.md`「底座技能」一节。

## 环境自检与自举安装

**每次开始工作前先跑一次环境自检**，缺依赖就装：

```bash
# 自检：确认依赖与包完整性
python3 verify.py

# 若报缺依赖（docx/pptx/openpyxl），装一次即可
bash skills/office-layer/bootstrap.sh
```

**如果本技能包只被部分安装或路径不对**（例如 `skills/office-layer/scripts/` 不存在），
用自带安装脚本自举到正确位置：

```bash
# 自动探测各 agent 技能目录并软链（幂等，重复运行安全）
bash install.sh

# 或从零拉取（本包公开）
curl -fsSL https://raw.githubusercontent.com/EtherealMingo/university-teacher-skills/main/install.sh | bash
```

安装脚本会完成：取源 → 落到 `~/.local/share/university-teacher-skills` → 建 venv 装依赖
→ 软链到各 agent 技能目录 → 跑 `verify.py` 自检。

> **执行任何命令前，先 `cd` 到本包根目录。** 全部 `skills/...` 底座路径都是相对包根写的，
> 换目录执行会找不到文件。

## 路由表

判断教师意图 → 打开对应 `skills/<name>/SKILL.md`。触发词不明确时，
**先确认四件事**：学科 / 课程名 / 学生层次 / 产出物格式。

### 教学

| 子技能 | 何时用（教师会这么说） | 底座 |
|---|---|---|
| [`lesson-plan`](skills/lesson-plan/SKILL.md) | 「写个教案」「这节课怎么设计」「教学设计」 | `skills/education-skills/edu-teaching-design/` |
| [`lecture-slides`](skills/lecture-slides/SKILL.md) | 「做课件」「把这章做成 PPT」 | `skills/office-layer/`（pptx） |
| [`quiz-generator`](skills/quiz-generator/SKILL.md) | 「出一套题」「编几道练习题」「随堂小测」 | `skills/ibook-skills/question-writing/` |
| [`exam-pipeline`](skills/exam-pipeline/SKILL.md) | 「审核这套试卷」「出评分细则」「考后成绩分析」「试卷归档」 | `skills/office-layer/`（xlsx 分析） |
| [`classroom-live`](skills/classroom-live/SKILL.md) | 「随堂投票题」「这节课的提问链」「互动记录算平时分」 | `skills/ibook-skills/question-writing/` |
| [`teaching-contest`](skills/teaching-contest/SKILL.md) | 「准备教学竞赛」「设计示范课」「教学创新大赛」「说课稿」「模拟评委提问」 | `lesson-plan` 增强 + `skills/education-skills/edu-teaching-design/` + `skills/k12-teacher-skills/k12-lesson-plan-creation/` 等 k12 四技能 + `skills/awesome-benzi/` 质量门（MOCK_REVIEW）+ `skills/slides-polish/` |

### 科研

| 子技能 | 何时用 | 底座 |
|---|---|---|
| [`research-assistant`](skills/research-assistant/SKILL.md) | 「实证研究怎么做」「帮我设计研究方案」「数据分析」 | `skills/empirical-research/econ-audit/` + `skills/empirical-research/data-dictionary/` + `skills/empirical-research/lit-review/` |
| [`grant-proposal`](skills/grant-proposal/SKILL.md) | 「写本子」「申报书」「选题查重」「模拟评审」 | `skills/awesome-benzi/` |
| [`paper-to-slides`](skills/paper-to-slides/SKILL.md) | 「论文做成汇报 PPT」「组会要讲这篇」 | `skills/paper-analyst/` + `skills/slides-polish/` |
| [`peer-review`](skills/peer-review/SKILL.md) | 「写审稿意见」「这篇论文评审一下」「审稿意见怎么写」「这稿子能不能收」 | `skills/paper-analyst/` 论文类型量规 + `skills/awesome-benzi/references/QUALITY_GATES.md` 问题分级 + `skills/education-skills/edu-learning-analytics/` 互评方法 + `skills/empirical-research/econ-audit/` 方法学审查 + `skills/office-layer/`（原生批注） |

### 指导（含学生工作）

| 子技能 | 何时用 | 底座 |
|---|---|---|
| [`thesis-supervisor`](skills/thesis-supervisor/SKILL.md) | 「看开题报告」「写论文评语」「预判答辩问题」「批改论文」 | `skills/office-layer/`（**原生批注**） |
| [`lab-meeting`](skills/lab-meeting/SKILL.md) | 「安排组会轮值」「文献派工」「生成组会纪要」 | `paper-to-slides` + `office-layer` |
| [`student-competition`](skills/student-competition/SKILL.md) | 「指导学生做大创」「挑战杯怎么带」「学生想参加互联网+」「看看学生的申报书」 | `skills/awesome-benzi/workflows/`（`student-innovation` / `challenge-cup` / `innovation-competition`）。**与 `grant-proposal` 的分工**：申报书正文 → `grant-proposal`；导师怎么带团队 → 本技能 |
| [`student-affairs`](skills/student-affairs/SKILL.md) | 「学生挂科太多怎么帮」「谈心谈话记录怎么写」「写个奖学金推荐意见」「学生想退学」 | `skills/education-skills/edu-learning-analytics/`（学情画像）+ `skills/learning-education/thinking-toolkit/`（谈话提问）+ `office-layer` |
| [`internship-practice`](skills/internship-practice/SKILL.md) | 「联系实习基地」「排实习安排表」「写实习指导记录」「实习材料要归档什么」 | `skills/office-layer/` + `skills/education-skills/edu-learning-analytics/` 评量规 |

### 行政事务

> 这一摊琐碎但躲不掉，且出错代价高（数据对不上被退回、通知漏发、排期撞车）。
> 共同纪律：**用检查代替记忆**，凡数据必须有出处，凡排期必须做冲突检测。

| 子技能 | 何时用 | 底座 |
|---|---|---|
| [`admin-reporting`](skills/admin-reporting/SKILL.md) | 「统计教学工作量」「专业认证材料怎么整」「教学检查要归档什么」「算课程目标达成度」 | `skills/awesome-benzi/references/QUALITY_GATES.md`（缺件三级分级）+ `office-layer` |
| [`meeting-notices`](skills/meeting-notices/SKILL.md) | 「写个教研会纪要」「起草个调课通知」「写学期工作总结」「整理会议任务分工」 | `skills/awesome-benzi/references/LANGUAGE_MODEL.md`（压公文套话）+ `office-layer` |
| [`teaching-ops`](skills/teaching-ops/SKILL.md) | 「写个调课申请」「安排监考表」「排期末考试时间」「申报教材」「补课怎么安排」 | `office-layer`（排期表 + 冲突检测）+ `INPUT_MODEL.md` 问题批次 |
| [`academic-correspondence`](skills/academic-correspondence/SKILL.md) | 「回复审稿邀请」「邀请专家来做报告」「写封合作邮件」「怎么婉拒审稿」「写会议征稿通知」 | `skills/awesome-benzi/references/LANGUAGE_MODEL.md` + `office-layer` |
| [`student-recommendation`](skills/student-recommendation/SKILL.md) | 「写封保研推荐信」「留学推荐信怎么写」「给这个学生写推荐」「这几个学生的推荐信别写重了」「开个在职证明」「写封会议邀请函」「专家推荐意见怎么写」「写封合作感谢信」 | `LANGUAGE_MODEL.md`（去套话）+ `EVIDENCE_MODEL.md`（防溢美无据）+ `office-layer`（**spec 人工确认位 + 原生批注** + xlsx）+ 自建 `scripts/cliche_scan.py`（套话与同批雷同扫描）。与 `academic-correspondence` 分工：**首次邮件邀约**走那边，**要盖章的正式邀请函文书**走本技能 |

### 考核与对外

| 子技能 | 何时用 | 底座 |
|---|---|---|
| [`annual-review`](skills/annual-review/SKILL.md) | 「写年度述职」「整理职称材料」「教学成果奖」 | `skills/awesome-benzi/` 派生 |
| [`science-outreach`](skills/science-outreach/SKILL.md) | 「做个科普 PPT」「给中学生讲我的研究」「科普讲座怎么准备」「把研究讲给外行听」 | 独立底座：`skills/office-layer/`（pptx）+ `skills/slides-polish/` + `skills/learning-education/thinking-toolkit/`（类比讲解）+ `skills/education-skills/edu-rural-education/`（受众适配）。与 `lecture-slides` 是**不同**的风格体系，见其文档的风格对照表 |

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
| 带一支大创队伍 | `student-competition`（选题→组队→过程检查）→ `grant-proposal`（申报书正文）→ `student-competition`（结题答辩） |
| 期末行政收尾 | `exam-pipeline`（成绩分析）→ `admin-reporting`（工作量统计+归档）→ `meeting-notices`（学期总结） |
| 新学期开课 | `teaching-ops`（排课/教材/监考）→ `lesson-plan` → `lecture-slides` |
| 学生求助季 | `student-affairs`（谈心谈话+帮扶）→ 需推荐则 `student-recommendation` |
| 年底考核 | `annual-review`（成果归表→述职→职称） |

## 验收自检（维护本包时用）

改完任何子技能，过一遍 `CONVENTIONS.md` 第 8 节的自检清单，重点确认：
引用的底座路径（`skills/` 下）**真实存在**、文件产出走了 office-layer、评价性内容留了人工确认位。
