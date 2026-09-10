# 第三方组件声明（Third-Party Notices）

本仓库包含第三方开源项目的内容，位于 `vendor/` 目录。以下逐个列出**来源、版本、许可证与合规状态**。

复现日期：2026-09-10。所有 commit 为当日上游 `HEAD`（浅克隆）。

---

## ⚠️ 首先请阅读：两处许可证风险

1. **`vendor/ibook-skills/` 无许可证文件。**
   上游仓库 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills) 根目录**没有 `LICENSE`**，
   依法默认**保留全部权利**（all rights reserved）。本仓库收录其内容的副本**未获授权**。
   若你要复用、分发或商用这部分内容，**请先联系原作者取得许可**。

2. **`vendor/learning-education/thinking-toolkit/` 使用 CC BY-NC-SA 4.0。**
   该协议含 **NonCommercial（禁止商业使用）** 与 **ShareAlike（相同方式共享）** 两个限制。
   含有该内容的本仓库整体，在再分发时**不得用于商业目的**，且衍生作品需以相同协议发布。

如果你不同意上述任一条款，请删除对应目录；本仓库其余部分不受影响。

---

## 完整清单

| 本仓库路径 | 上游仓库 | 许可证 | 合规 |
|---|---|---|---|
| `vendor/awesome-benzi/` | [xxf-ai/awesome-benzi](https://github.com/xxf-ai/awesome-benzi) @ `2403ace` | MIT | ✅ |
| `vendor/education-skills/` | [ChatGPT3a01/claude-educational-ai-skills](https://github.com/ChatGPT3a01/claude-educational-ai-skills) @ `8f09b6c` | MIT | ✅ |
| `vendor/k12-teacher-skills/` | [anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) @ `281eb8d` | Apache-2.0 | ✅ 需保留 NOTICE（已随附） |
| `vendor/paper-slides/paper-analyst/` | [flyer-Li/paper-analyst](https://github.com/flyer-Li/paper-analyst) @ `1e385a3` | MIT | ✅ |
| `vendor/slides-polish/` | [parahall/polished-slide-visuals](https://github.com/parahall/polished-slide-visuals) @ `8f6f6ab` | MIT | ✅ |
| `vendor/learning-education/study-skill/` | [mordor-forge/study-skill](https://github.com/mordor-forge/study-skill) @ `dffa35f` | MIT（见其 README） | ✅ |
| `vendor/learning-education/tov-learn-reference/` | [TovTechOrg/Tov-learn](https://github.com/TovTechOrg/Tov-learn) @ `e09edae` | MIT | ✅ |
| `vendor/empirical-research/` | [eabeam/econ-skills](https://github.com/eabeam/econ-skills) @ `1b0238d` | CC BY 4.0 | ✅ 需署名（本文件即为署名） |
| `vendor/learning-education/thinking-toolkit/` | [Rogers-F/thinking-toolkit](https://github.com/Rogers-F/thinking-toolkit) @ `5a8dd95` | **CC BY-NC-SA 4.0** | ⚠️ 见上 |
| `vendor/ibook-skills/` | [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills) | **无许可证** | ⚠️ 见上 |
| `vendor/office-layer/` | 本仓库自建，非第三方 | 见根目录 `LICENSE` | ✅ |

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
**替代方案**：本仓库自建 `vendor/office-layer/`，能力对齐并针对中文场景加强
（中文排版、Word 原生批注、成绩分析）。

---

## 对上游内容做过的修改

| 位置 | 修改 | 原因 |
|---|---|---|
| `education-skills/` | 只取上游 `skills/` 目录，舍去 `tools/*.html` 网页版 | 网页版与本包 CLI 工作流无关 |
| `ibook-skills/` | 只取 5 个 skill（quiz-generator、course-description-analyzer、learning-graph-generator、glossary-generator、faq-generator） | 上游另有 25 个成书流程 skill，超出高校教师场景 |
| `k12-teacher-skills/` | 只取 `plugin/skills/` 下 4 个 skill | 舍去 evals 与 plugin 清单 |
| `learning-education/tov-learn-reference/` | 只取命令层文档，未收录其 9MB 课程素材 | 原仓库为希伯来文，且课程素材超出范围 |
| 各子 skill | 见 `skills/*/SKILL.md` 的「底座」一节 | 编排逻辑为本项目自写 |

除上表所列的**目录裁剪**外，`vendor/` 下的第三方文件**未作内容修改**，保持原样。

---

## 本仓库自建部分

以下内容为本项目原创，版权归本仓库作者所有，采用根目录 `LICENSE` 所载协议：

- 根目录 `SKILL.md`、`CONVENTIONS.md`、`README.md`、`ROADMAP.md`、`verify.py`
- `vendor/office-layer/`（全部脚本与文档）
- `skills/` 下全部 14 个子技能及其 `scripts/`
- `vendor/VENDOR.md`、本文件
