# 大学教师 AI 提效 Skill 包 — 场景总览与实现状态

> 本文档由规划文档更新为**状态文档**，记录实际实现情况与偏离原计划之处。
> 开发约定见 `CONVENTIONS.md`，路由见 `SKILL.md`，底座溯源见 `vendor/VENDOR.md`。

## 0. 与原计划的三处重要偏离

### 偏离一：office-skills 未采用上游，改为自建

原计划以 `vendor/office-skills/`（Anthropic 官方 docx/pptx/xlsx/pdf）作为「文件产出唯一通道」。
核对许可证后**未采用**：该四件套为 **Proprietary** 许可，其 `LICENSE.txt` 明令禁止
「在 Services 之外保留副本」「复制」「创作衍生作品」「分发」。

改为自建 `vendor/office-layer/`，能力对齐且针对中文场景加强：

| 能力 | 说明 |
|---|---|
| `docx_kit.py` | Markdown→DOCX（中文字体/页码/首行缩进）、**Word 原生批注**、规格化评语模板、结构自检 |
| `pptx_kit.py` | 16:9 中文课件、演讲者备注批量写入、**信息密度自检**（overdense 告警） |
| `xlsx_kit.py` | 表格生成 + **成绩分析**（得分率/区分度/分数段分布/偏度峰度）+ 原生图表 |

其中「Word 原生批注」是 `thesis-supervisor` 的核心依赖，经实测可写入
`word/comments.xml` 与 `commentRangeStart/End`，Word 打开显示真正的批注气球。

### 偏离二：ROADMAP 声称「已完成」的 6 个 skill 实际不存在

原文档列出 6 个「已完成，勿重复开发」的 skill（lesson-plan、quiz-generator、lecture-slides、
paper-to-slides、research-assistant、grant-proposal），但本机上并无对应文件，`vendor/` 也不存在。
经确认，本次**全部从零实现**。

### 偏离三：部分底座在原文档中只给了能力名，未给仓库

`learning-education`（苏格拉底问答/闪卡/学习路径）与 `paper-slides`/`slides-polish`/
`empirical-research` 在原文档中只有名字。已按能力逐个寻找相似项目并收录，来源见 `vendor/VENDOR.md`。

## 1. 底座对照表（原计划 → 实际采用）

| 原计划 vendor | 实际采用 | ★ | 许可证 |
|---|---|---|---|
| office-skills | **自建** `office-layer/`（上游为专有许可） | — | 本包自有 |
| education-skills | [ChatGPT3a01/claude-educational-ai-skills](https://github.com/ChatGPT3a01/claude-educational-ai-skills) | 31 | MIT |
| ibook-skills | [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills) | 98 | ⚠ 无 LICENSE |
| awesome-benzi | [xxf-ai/awesome-benzi](https://github.com/xxf-ai/awesome-benzi) | 2 | MIT |
| learning-education | [mordor-forge/study-skill](https://github.com/mordor-forge/study-skill) + [Rogers-F/thinking-toolkit](https://github.com/Rogers-F/thinking-toolkit) + [TovTechOrg/Tov-learn](https://github.com/TovTechOrg/Tov-learn)（参考） | — | MIT |
| paper-slides | [flyer-Li/paper-analyst](https://github.com/flyer-Li/paper-analyst) | — | 见仓库 |
| slides-polish | [parahall/polished-slide-visuals](https://github.com/parahall/polished-slide-visuals) | 2 | 见仓库 |
| empirical-research | [eabeam/econ-skills](https://github.com/eabeam/econ-skills) | — | 见仓库 |
| （新增） | [anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) | 493 | Apache-2.0 |

## 2. 子技能清单（22 个）

### 教学（6）

| 子 skill | 覆盖场景 | 底座 |
|---|---|---|
| lesson-plan | 教案 / 教学设计 / 教学大纲 | education-skills/教學設計 |
| lecture-slides | 日常课件 | office-layer（pptx） |
| quiz-generator | 出题 / 测评 / A-B 卷 | ibook-skills/quiz-generator |
| exam-pipeline | 试卷审核 / 评分细则 / 成绩分析 / 归档 | office-layer（xlsx 分析） |
| classroom-live | 随堂投票 / 提问链 / 平时分 | ibook-skills + education-skills/學習分析 |
| teaching-contest | 教学竞赛 / 示范课 / 评委视角自评 | lesson-plan 增强 + 质量门 |

### 科研（4）

| 子 skill | 覆盖场景 | 底座 |
|---|---|---|
| research-assistant | 研究设计 / 文献综述 / 实证审计 | empirical-research |
| grant-proposal | 申报全流程（查重→匹配→撰写→模拟评审） | awesome-benzi + 自建 `topic_overlap.py` |
| paper-to-slides | 论文→组会/学术汇报 PPT | paper-slides + slides-polish |
| peer-review | 期刊审稿意见 | 自建（借鉴评价量规与质量门分级） |

### 指导（含学生工作，5）

| 子 skill | 覆盖场景 | 底座 |
|---|---|---|
| thesis-supervisor | 开题审查 / 过程稿批注 / 评语 / 答辩预案 | office-layer（**原生批注**） |
| lab-meeting | 组会轮值 / 文献派工 / 纪要 / 进度跟踪 | paper-to-slides + office-layer |
| student-competition | 大创 / 挑战杯 / 创青春 / 互联网+：选题→组队→过程督导→中期→结题→答辩 | awesome-benzi/workflows（student-innovation、challenge-cup、innovation-competition） |
| student-affairs | 学业预警 / 谈心谈话 / 评奖评优 / 心理危机转介 / 家长沟通 | education-skills/學習分析 + thinking-toolkit |
| internship-practice | 实习基地 / 协议 / 安排表 / 安全管理 / 指导记录 / 考核鉴定 / 归档 | office-layer + education-skills 评量规 |

### 行政事务（5）

> 共同纪律：**用检查代替记忆**，凡数据必须有出处，凡排期必须做冲突检测。

| 子 skill | 覆盖场景 | 底座 |
|---|---|---|
| admin-reporting | 教学工作量 / 专业认证 / 审核评估 / 达成度计算 / 教学检查归档 / 课程思政 / 实验室安全 | office-layer + awesome-benzi 质量门三级分级 |
| meeting-notices | 会议纪要 / 通知公文 / 工作总结与计划 / 发言稿 | LANGUAGE_MODEL（压公文套话）+ office-layer |
| teaching-ops | 调课停课 / 监考安排 / 考试排期 / 教材申报（含冲突检测） | office-layer + INPUT_MODEL 问题批次 |
| academic-correspondence | 审稿邀约回复 / 会议组织 / 合作洽谈 / 中英文学术邮件 | LANGUAGE_MODEL + office-layer |
| student-recommendation | 保研/留学/求职推荐信 / 专家推荐 / 证明 / 邀请函 | LANGUAGE_MODEL + EVIDENCE_MODEL + office-layer |

### 考核与对外（2）

| 子 skill | 覆盖场景 | 底座 |
|---|---|---|
| annual-review | 年度述职 / 职称材料 / 教学成果奖 | awesome-benzi workflow 派生 |
| science-outreach | 科普讲座 / 公众版叙事重构 | office-layer（pptx）+ slides-polish |

### 场景间的重要边界

| 边界 | 说明 |
|---|---|
| `grant-proposal` ↔ `student-competition` | 申报书**正文撰写**走前者；**导师怎么带团队**走后后者。两者有双向交接协议 |
| `lecture-slides` ↔ `paper-to-slides` ↔ `science-outreach` | 三者的视觉体系**不同**：日常授课 / 学术汇报 / 公众科普，不得混用 |
| `exam-pipeline` ↔ `admin-reporting` | 成绩分析走前者；工作量统计与迎检归档走后者 |
| `quiz-generator` → `exam-pipeline` | 有冻结字段契约，见 `quiz-generator` 的交接协议一节 |

## 3. 自建脚本

均为实测跑通，非纸面代码。

### 文档产出层（`vendor/office-layer/`）

| 脚本 | 用途 | 实测状态 |
|---|---|---|
| `scripts/docx_kit.py` | Word 生成与**原生批注** | ✅ 批注写入 `comments.xml` + `commentRangeStart/End`；表格单元格内锚点亦可 |
| `scripts/pptx_kit.py` | 课件生成与备注 | ✅ 生成 + 信息密度自检；越界备注索引静默忽略（须 `inspect` 回读） |
| `scripts/xlsx_kit.py` | 表格与成绩分析 | ✅ 40 人 8 题模拟数据，正确识别低区分度题与过难题 |
| `bootstrap.sh` | 依赖引导 | ✅ 建 venv、装依赖、自检原生批注支持 |

### 子技能脚本（`skills/*/scripts/`）

| 脚本 | 所属 | 用途 | 实测状态 |
|---|---|---|---|
| `topic_overlap.py` | grant-proposal | 选题查重（用词/方法/场景三维度） | ✅ 同题 0.668 判「疑似撞车」，同域异法 0.42 判「需切割」 |
| `roster_plan.py` | lab-meeting | 组会轮值表生成与公平性校验 | ✅ 18 周含节假日跳过，点评人不自评，汇报次数极差 1 |
| `status_colorize.py` | lab-meeting | 进度表状态色标（`xlsx_kit build` 不支持逐格填充，故设此薄后处理层） | ✅ 五种状态正确落盘 |
| `participation_score.py` | classroom-live | 可逐行举证的平时分计算 | ✅ 封顶与权重和校验均生效 |
| `desc_stats.py` | research-assistant | 描述统计与交叉表 | ✅ csv / xlsx 双输入路径 |
| `dedup_merge.py` | annual-review | 成果去重归表 | ✅ 见下「已修复缺陷」 |
| `word_gate.py` | annual-review | 述职字数门 | ✅ passed / blocked 两路径 |

### 包级

| 脚本 | 用途 |
|---|---|
| `install.sh` | 自举安装：取源 → 落盘 → 建依赖 → 软链到各 agent 技能目录 → 自检。幂等，支持 `--uninstall` |
| `verify.py` | 包完整性自检（结构 / frontmatter / vendor 路径真实性 / 纪律 / 冒烟） |

### 本轮实测发现的缺陷（已修复）

| 缺陷 | 现象 | 修复 |
|---|---|---|
| `docx_kit.py` 批注只遍历正文 | 审查意见表通篇是表格，表格内锚点报「未找到」 | 增加 `iter_paragraphs()` 递归遍历表格单元格 |
| `pptx_kit.py` 误用 `add_run(text)` | python-pptx 的 `add_run()` 不收文本参数，直接 TypeError | 增加 `_run()` helper，先建后赋 |
| `dedup_merge.py` 编号键短路 | 「有收录号」与「无收录号」的同一条论文永远合不到一起——而隔年重复填报正由此产生 | 改为多候选键匹配（编号键 + 名称键），任一命中即合并并登记别名 |
| `quiz-generator` 误把 FSRS 当现成命令 | 上游 `scripts/fsrs/` 只有 Go 源码、不含二进制，本机亦无 Go 工具链 | 文档补前置检查 + 手工排程降级方案，并强制在交付说明声明「非自动调度」 |


## 4. 验收自检

跑 `python3 verify.py` 会逐项检查：

- [x] 14 个子技能目录与 `SKILL.md` 齐全
- [x] frontmatter 含 `name` + `description`，description 带 Triggers 与 ≥3 个教师真实口语触发短语
- [x] 所有引用的 `vendor/` 路径**真实存在**（脚本自动比对，杜绝凭记忆写路径）
- [x] 每个子技能都指向 office-layer 产出通道
- [x] 「不虚构」与「人工确认位」纪律已写入
- [x] office-layer 三个脚本可正常拉起

## 5. 后续可做

| 项 | 说明 |
|---|---|
| 实时数据接入 | 对接教务系统导出格式，省去手工整理成绩表 |
| 题库沉淀 | 把 `quiz-generator` 产出按课程/知识点归档，形成可复用题库 |
| 模板库 | 收集各校评语模板、试卷审批表、职称评审表，做成 `templates/` |
| 分发合规 | 对外分发前须处理 `vendor/ibook-skills/` 的无许可证问题（见 `vendor/VENDOR.md`） |
