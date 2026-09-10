# 第三方组件声明（Third-Party Notices）

本仓库的第三方开源内容位于 `skills/` 目录下的 26 个**底座技能**中
（2026-09-10 由 `vendor/` 目录迁入，文档已全部译为简体中文；同日起按上游套件
嵌套为 `education-skills/`、`empirical-research/`、`ibook-skills/`、
`k12-teacher-skills/`、`learning-education/` 五个套件目录，`awesome-benzi`、
`paper-analyst`、`slides-polish` 三个独立件平铺）。
以下逐个列出**来源、版本、许可证与合规状态**。

复现日期：2026-09-10。所有 commit 为当日上游 `HEAD`（浅克隆）。

---

## ⚠️ 首先请阅读：两处许可证风险

1. **ibook 系列底座无许可证文件。**
   上游仓库 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills) 根目录**没有 `LICENSE`**，
   依法默认**保留全部权利**（all rights reserved）。涉及本仓库 5 个目录：
   `skills/ibook-skills/question-writing/`（上游原名 `quiz-generator`）、`skills/ibook-skills/learning-graph-generator/`、
   `skills/ibook-skills/glossary-generator/`、`skills/ibook-skills/faq-generator/`、`skills/ibook-skills/course-description-analyzer/`。
   本仓库收录其内容的副本**未获授权**（其中 quiz-generator 的 SKILL.md frontmatter 自称
   CC BY-NC 4.0，但仓库无 LICENSE，按无许可证处理）。
   若你要复用、分发或商用这部分内容，**请先联系原作者取得许可**。

2. **`skills/learning-education/thinking-toolkit/` 使用 CC BY-NC-SA 4.0。**
   该协议含 **NonCommercial（禁止商业使用）** 与 **ShareAlike（相同方式共享）** 两个限制。
   含有该内容的本仓库整体，在再分发时**不得用于商业目的**，且衍生作品需以相同协议发布。

如果你不同意上述任一条款，请删除对应目录；本仓库其余部分不受影响。

---

## 完整清单

| 本仓库路径 | 上游仓库 | 许可证 | 合规 |
|---|---|---|---|
| `skills/awesome-benzi/` | [xxf-ai/awesome-benzi](https://github.com/xxf-ai/awesome-benzi) @ `2403ace` | MIT | ✅ |
| `skills/education-skills/`（7 个 edu-* 目录） | [ChatGPT3a01/claude-educational-ai-skills](https://github.com/ChatGPT3a01/claude-educational-ai-skills) @ `8f09b6c` | MIT | ✅ |
| `skills/k12-teacher-skills/`（4 个 k12-* 目录） | [anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) @ `281eb8d` | Apache-2.0 | ✅ 需保留 NOTICE（已随附） |
| `skills/paper-analyst/` | [flyer-Li/paper-analyst](https://github.com/flyer-Li/paper-analyst) @ `1e385a3` | MIT | ✅ |
| `skills/slides-polish/` | [parahall/polished-slide-visuals](https://github.com/parahall/polished-slide-visuals) @ `8f6f6ab` | MIT | ✅ |
| `skills/learning-education/study-skill/` | [mordor-forge/study-skill](https://github.com/mordor-forge/study-skill) @ `dffa35f` | MIT（见其 README） | ✅ |
| `skills/learning-education/learning-paths/` | [TovTechOrg/Tov-learn](https://github.com/TovTechOrg/Tov-learn) @ `e09edae` | MIT | ✅ |
| `skills/empirical-research/econ-audit/`、`skills/empirical-research/data-dictionary/`、`skills/empirical-research/lit-review/` | [eabeam/econ-skills](https://github.com/eabeam/econ-skills) @ `1b0238d` | CC BY 4.0 | ✅ 需署名（本文件即为署名） |
| `skills/learning-education/thinking-toolkit/` | [Rogers-F/thinking-toolkit](https://github.com/Rogers-F/thinking-toolkit) @ `5a8dd95` | **CC BY-NC-SA 4.0** | ⚠️ 见上 |
| `skills/ibook-skills/question-writing/` 等 5 个 ibook 目录 | [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills) | **无许可证** | ⚠️ 见上 |
| `skills/office-layer/` | 本仓库自建，非第三方 | 见根目录 `LICENSE` | ✅ |

目录对照：

- **edu-\***（7 个，位于 `skills/education-skills/`）：`edu-teaching-design`、`edu-learning-analytics`、
  `edu-rural-education`、`edu-research-methods`、`edu-math-tech-education`、`edu-ai-tools`、`edu-ict-integration`
  （对应上游繁体中文目录：教學設計、學習分析、偏鄉教育、研究方法、數學科技教育、AI工具應用、ICT科技融入）
- **k12-\***（4 个，位于 `skills/k12-teacher-skills/`）：`k12-lesson-plan-creation`、
  `k12-lesson-differentiation`、`k12-lesson-prep`、`k12-check-for-understanding`
- **ibook 五件**（位于 `skills/ibook-skills/`）：`question-writing`（上游原名 `quiz-generator`）、
  `learning-graph-generator`、`glossary-generator`、`faq-generator`、`course-description-analyzer`

原 `learning-education` 由三个上游合成（原计划只给了「苏格拉底问答、闪卡、学习路径」
三个能力名，未给仓库，故按能力逐个寻找相似项目收录）：

| 本仓库路径 | 上游 | 覆盖能力 |
|---|---|---|
| `skills/learning-education/study-skill/` | [mordor-forge/study-skill](https://github.com/mordor-forge/study-skill) | 闪卡（FSRS-6 间隔重复） |
| `skills/learning-education/thinking-toolkit/` | [Rogers-F/thinking-toolkit](https://github.com/Rogers-F/thinking-toolkit) | 苏格拉底提问等 12 种结构化思考 |
| `skills/learning-education/learning-paths/` | [TovTechOrg/Tov-learn](https://github.com/TovTechOrg/Tov-learn) | 学习路径与进度追踪模型（仅取命令层文档，原仓库为希伯来文且含 9MB 课程素材，未整体收录） |

### 各上游版权归属

- **awesome-benzi** — Copyright (c) 2026 xxf-ai
- **claude-educational-ai-skills** — Copyright (c) 2026 曾慶良 (Ching-Liang Tseng)
- **k12-teacher-skills** — Copyright 2026 Anthropic, PBC（Apache-2.0）
- **polished-slide-visuals** — Copyright (c) 2026 Yoni Levin
- **paper-analyst** — 见其仓库 `LICENSE`
- **econ-skills** — CC BY 4.0
- **thinking-toolkit** — CC BY-NC-SA 4.0
- 其余见各自仓库

---

## 未收录的上游（重要说明）

### Anthropic 官方办公文档技能 — 已排除

本项目原本计划以 [anthropics/skills](https://github.com/anthropics/skills) 的
`docx` / `pptx` / `xlsx` / `pdf` 作为「文件产出唯一通道」，**核对后未收录**。

其 `LICENSE.txt` 为 **Proprietary**，明确禁止：

> Extract these materials from the Services or retain copies of these materials outside the
> Services; Reproduce or copy these materials …; Create derivative works based on these
> materials; Distribute, sublicense, or transfer these materials to any third party

即不得在服务外保留副本、不得复制、不得创作衍生作品、不得分发。
**替代方案**：本仓库自建 `skills/office-layer/`，能力对齐并针对中文场景加强
（中文排版、Word 原生批注、成绩分析）。

### 其他可参考但未收录

| 仓库 | 说明 | 为何未收 |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 官方技能集总仓库 | 其 docx/pptx/xlsx/pdf 为专有许可 |
| [jiankang1991/nsfc-benzi-audit](https://github.com/jiankang1991/nsfc-benzi-audit) | 国自然申请书诊断 | 克隆超时；`awesome-benzi` 已覆盖该场景 |
| [yhbcode000/paper-share-skills](https://github.com/yhbcode000/paper-share-skills) | 论文 → Beamer → 视频 → B 站 | 克隆失败；`paper-analyst` 已覆盖论文→PPT |
| [GarethManning/education-agent-skills](https://github.com/GarethManning/education-agent-skills) | 165 个教师技能 | 体量大且偏 K-12 与 EdTech 建设，超出当前范围 |

---

## 对上游内容做过的修改

### 迁移与翻译（2026-09-10，最大的一次内容改动）

- 全部底座从 `vendor/` 迁入 `skills/`，成为与主技能同构的一等技能目录
  （`SKILL.md` + `references/` + `scripts/`），`vendor/` 目录已删除。
- 同日随后按上游套件嵌套：edu-* 七件入 `education-skills/`、ibook 五件入 `ibook-skills/`、
  k12-* 四件入 `k12-teacher-skills/`、econ-audit / data-dictionary / lit-review 入
  `empirical-research/`、study-skill / thinking-toolkit / learning-paths 入
  `learning-education/`；技能名（frontmatter `name`）不变，仅目录位置移动。
- **所有文档译为简体中文**：英文底座（`k12-*`、ibook 五件、`econ-audit`、`data-dictionary`、
  `lit-review`、`paper-analyst`、`slides-polish`、`study-skill`、`learning-paths`）全文翻译；
  繁体中文底座（`edu-*` 七件，台湾 108 课纲口径）逐字转简体。
- 代码、脚本、数据与 `LICENSE`/`NOTICE` 法律文件**保持原文未译**。
- 目录改名两处：`ibook-skills/quiz-generator` → `skills/ibook-skills/question-writing/`
  （避免与主技能 `quiz-generator` 重名）；`tov-learn-reference` → `skills/learning-education/learning-paths/`。
- `question-writing` 的 frontmatter 删去了上游自称的 `CC BY-NC 4.0` 字段
  （与「仓库无 LICENSE」矛盾，见上方风险提示）。
- 各底座 `SKILL.md` 的 frontmatter `description` 改写为中文并补充 Triggers；
  末尾追加「来源与许可」一节。
- 上游仓库的 CI 配置（`study-skill` 的 `.github/`、`.pre-commit-config.yaml` 等）未收录；
  各上游 `README.md` 的有效内容已合并进对应 `SKILL.md`，不再单独保留。

### 收录时的目录裁剪

| 位置 | 修改 | 原因 |
|---|---|---|
| `edu-*` 七目录 | 只取上游 `skills/` 目录，舍去其 `tools/*.html` 网页版 | 网页版与本包 CLI 工作流无关 |
| ibook 五件 | 只取 ROADMAP 点名的 5 个 skill | 上游另有 25 个成书流程 skill，超出高校教师场景 |
| `k12-*` 四目录 | 只取 `plugin/skills/` 下 4 个 skill | 舍去 evals 与 plugin 清单 |
| `skills/learning-education/learning-paths/` | 只取命令层文档，未收录其 9MB 课程素材 | 原仓库为希伯来文，且课程素材超出范围 |
| 各主技能 | 见 `skills/` 下 22 个主技能 `SKILL.md` 的「底座」一节 | 编排逻辑为本项目自写 |

---

## 本仓库自建部分

以下内容为本项目原创，版权归本仓库作者所有，采用根目录 `LICENSE` 所载协议：

- 根目录 `SKILL.md`、`CONVENTIONS.md`、`README.md`、`ROADMAP.md`、`START-HERE.md`、
  `verify.py`、`install.sh`、本文件
- `skills/office-layer/`（全部脚本与文档）
- `skills/` 下 22 个主技能及其 `scripts/`
