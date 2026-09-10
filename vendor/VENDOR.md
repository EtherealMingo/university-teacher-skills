# vendor/ 底座溯源表

本目录收录上游开源技能作为「底座」。**vendor-first 原则**：实现任何能力前先查这里，
已有底座则引用，禁止重写。

复现时间：2026-09-10。所有 commit 为当日 `HEAD`（浅克隆）。

## 收录清单

| 本包路径 | 上游仓库 | ★ | 许可证 | commit |
|---|---|---|---|---|
| `awesome-benzi/` | [xxf-ai/awesome-benzi](https://github.com/xxf-ai/awesome-benzi) | 2 | MIT | `2403ace` |
| `education-skills/` | [ChatGPT3a01/claude-educational-ai-skills](https://github.com/ChatGPT3a01/claude-educational-ai-skills) | 31 | MIT | `8f09b6c` |
| `ibook-skills/` | [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills) | 98 | ⚠ 仓库无 LICENSE 文件 | 见下 |
| `k12-teacher-skills/` | [anthropics/k12-teacher-skills](https://github.com/anthropics/k12-teacher-skills) | 493 | Apache-2.0 | `281eb8d` |
| `learning-education/` | 见下（三个上游合成） | — | MIT | 见下 |
| `paper-slides/` | [flyer-Li/paper-analyst](https://github.com/flyer-Li/paper-analyst) | — | 见仓库 | `1e385a3` |
| `slides-polish/` | [parahall/polished-slide-visuals](https://github.com/parahall/polished-slide-visuals) | 2 | 见仓库 | `8f6f6ab` |
| `empirical-research/` | [eabeam/econ-skills](https://github.com/eabeam/econ-skills) | — | 见仓库 | `1b0238d` |
| `office-layer/` | **自建，非上游** | — | 本包自有 | — |

`learning-education/` 由三个上游合成（ROADMAP 只给了「苏格拉底问答、闪卡、学习路径」三个能力名，
未给仓库，故按能力逐个寻找相似项目）：

| 子目录 | 上游 | 覆盖能力 |
|---|---|---|
| `study-skill/` | [mordor-forge/study-skill](https://github.com/mordor-forge/study-skill) | 闪卡（FSRS-6 间隔重复） |
| `thinking-toolkit/` | [Rogers-F/thinking-toolkit](https://github.com/Rogers-F/thinking-toolkit) | 苏格拉底提问等 12 种结构化思考 |
| `tov-learn-reference/` | [TovTechOrg/Tov-learn](https://github.com/TovTechOrg/Tov-learn) | 学习路径与进度追踪模型（仅取命令层文档，原仓库为希伯来文且含 9MB 课程素材，未整体收录） |

## 许可证合规

### 已排除：Anthropic 官方 office skill

ROADMAP 原定以 `anthropics/skills` 的 `docx` / `pptx` / `xlsx` / `pdf` 作为「文件产出唯一通道」。
核对后**未收录**，原因见其 `LICENSE.txt`（Proprietary）：

> ADDITIONAL RESTRICTIONS: ... users may not: Extract these materials from the Services or
> retain copies of these materials outside the Services; Reproduce or copy these materials ...
> Create derivative works based on these materials; Distribute, sublicense, or transfer these
> materials to any third party

即：不得在服务外保留副本、不得复制、不得创作衍生作品、不得分发。收入本包并对外提供会构成违约。
**替代方案**：自建 `office-layer/`（见下），能力对齐且增加了中文排版与原生批注支持。

### 需注意：ibook-skills 无许可证文件

`dmccreary/ibook-skills` 仓库根目录无 `LICENSE`，依法默认保留全部权利。
当前仅**收录未修改副本**供本机自用。若本包需要对外分发，应先向作者取得授权或移除该目录。

### 其余

`awesome-benzi`、`education-skills`、`k12-teacher-skills`、`learning-education` 三上游均为
MIT / Apache-2.0，可自由使用与分发（Apache-2.0 需保留 `NOTICE`，已随附）。

## 对上游做过的修改

| 位置 | 修改 | 原因 |
|---|---|---|
| `education-skills/` | 只取上游 `skills/` 目录，舍去其 `tools/*.html` 网页版 | 网页版与本包 CLI 工作流无关 |
| `ibook-skills/` | 只取 ROADMAP 点名的 5 个 skill | 上游另有 25 个成书流程 skill，超出高校教师场景 |
| `k12-teacher-skills/` | 只取 `plugin/skills/` 下 4 个 skill | 舍去 evals 与 plugin 清单 |
| `awesome-benzi/` | 原样收录，未改代码 | 其质量门与工作流直接复用 |
| 各子 skill | 见各 `skills/*/SKILL.md` 的「底座」一节 | 编排逻辑为本包自写 |

## 未收录但可作参考的上游

| 仓库 | 说明 | 为何未收 |
|---|---|---|
| [anthropics/skills](https://github.com/anthropics/skills) | 官方技能集总仓库 | 其 docx/pptx/xlsx/pdf 为专有许可 |
| [jiankang1991/nsfc-benzi-audit](https://github.com/jiankang1991/nsfc-benzi-audit) | 国自然申请书诊断 | 克隆超时；`awesome-benzi` 已覆盖该场景 |
| [yhbcode000/paper-share-skills](https://github.com/yhbcode000/paper-share-skills) | 论文 → Beamer → 视频 → B 站 | 克隆失败；`paper-analyst` 已覆盖论文→PPT |
| [GarethManning/education-agent-skills](https://github.com/GarethManning/education-agent-skills) | 165 个教师技能 | 体量大且偏 K-12 与 EdTech 建设，超出当前范围 |
