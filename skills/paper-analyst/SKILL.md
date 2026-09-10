---
name: paper-analyst
description: "深度分析学术论文与研究类 PDF：五种分析模式（quick/standard/extended/presentation/presentation_with_figures）、反幻觉来源标注、按论文类型套用方法模板、自动生成组会 PPT。当用户上传或粘贴论文并希望理解它时使用。 Triggers: 帮我分析这篇论文、解读一下这篇 PDF、这篇 paper 讲了什么、帮我总结这篇研究的创新点、帮我准备组会汇报、把这篇论文做成 PPT 大纲、分析一下这篇论文与前作的关系。"
---

# Paper Analyst（论文分析师）

分析 PDF 或粘贴文本形式的学术论文。默认以中文输出。
所有输出遵循 `references/output-schema.md`。论文类型判定使用
`references/paper-type-rubric.md`。反幻觉规则见
`references/quality-checklist.md`。

## 功能亮点

- **5 种分析模式**：从一句话速览到带图表的组会 PPT，按需选择
- **反幻觉机制**：每个观点强制标注 `[原文声明]` 或 `[模型归纳]`，并绑定原文位置证据
- **论文类型感知**：先分类（AI/深度学习、传统算法、系统工程、实验实证、综述、跨学科），再套对应的方法分析模板
- **PDF 质量分层**：良好 / 降级 / 严重降级三档处理，优雅降级而非直接报错
- **PPT 自动化管道**：演讲模式下自动提取 PDF 图表、构建幻灯片计划、调用 `pptx` skill 生成文件
- **前作关系追踪**：`extended` 模式从参考文献中识别自引，推断课题组研究脉络（仅基于论文内部，不做外部检索）
- **中英双语触发**：中英文触发词均支持

## 依赖项

| 依赖 | 用途 | 安装 |
|------|------|------|
| `pymupdf` | PDF 图表提取 | `pip install pymupdf` |
| `pypdf` | PDF 元数据读取 | `pip install pypdf` |
| `pptx` skill | PPT 文件生成 | 单独安装，见其文档 |

Python 需 3.8+。仅当使用演讲模式生成 PPT 时才需要 `pptx` skill；仅当使用 `presentation_with_figures` 模式或元数据脚本时才需要 Python 依赖。

## 快速参考

| 文件 | 用途 |
|------|---------|
| `references/output-schema.md` | 章节结构与字段规则 |
| `references/paper-type-rubric.md` | 论文类型分类方法 |
| `references/quality-checklist.md` | 反幻觉检查清单 |
| `references/presentation-schema.md` | 幻灯片计划 JSON 规范 |
| `references/presentation-style-guide.md` | 幻灯片内容压缩规则 |
| `references/pptx-handoff.md` | 如何调用 pptx skill 渲染 |
| `scripts/extract_pdf_meta.py` | 可选：提取 PDF 元数据为 JSON |
| `scripts/extract_pdf_figures.py` | 可选：逐页提取 PDF 内嵌图表 |

## 模式选择

默认模式：`standard`。根据用户请求识别：

| 模式 | 触发词 | 输出 |
|------|---------|--------|
| `quick` | "quick"、"简单说"、"一句话"、"简要" | 头部信息行 + 基础信息 + 摘要 + 3 条贡献 |
| `standard` | （默认，最推荐） | 完整分析：第 1–5 节 |
| `extended` | "前作"、"课题组"、"prior work" | standard + 作者/课题组前作分析 |
| `presentation` | "PPT"、"组会"、"汇报大纲"、"slides" | standard + 幻灯片大纲 |
| `presentation_with_figures` | "图表"、"figures"、"带图"、"关键图" | presentation + 图表标注 |

无法判断时用 `standard`，并告知用户可以切换。

`standard` 及以上模式输出以下 6 个章节：基础信息（标题、作者、单位、Venue、年份、DOI、关键词）→ 摘要翻译与通俗解释 → 背景介绍 → 研究方法分析（按论文类型套模板）→ 创新点分析（最多 5 条，每条绑定原文证据）→ 研究结果与结论（具体数字 + 基线对比 + 局限性）。

## 工作流

### 第 1 步：评估输入质量

分析前先对 PDF 质量分级：
- **良好**：全文可提取
- **降级处理**：部分文字、扫描页、乱码编码
- **严重降级**：几乎无文字、纯图片 PDF

若降级：在头部信息行说明原因，用已有内容继续，明确标注所有缺口。绝不为填补缺口而编造内容。

可选：若用户环境有 Python，建议先运行 `scripts/extract_pdf_meta.py` 获取结构化元数据。

### 第 2 步：判定论文类型

阅读 `references/paper-type-rubric.md` 并分类。**不要**默认假设是 AI/ML 论文。
先输出类型标签和 2–3 条证据指标，再继续。

### 第 3 步：执行分析

按所选模式遵循 `references/output-schema.md`。在每一节中全程应用
`references/quality-checklist.md` 的所有规则。

### 第 4 步：输出前自检

定稿前核实：
- 每个不确定的字段都标了 `[不确定]` 或 `[未明确给出]`
- 每条贡献都标了 `[原文声明]` 或 `[模型归纳]`
- 没有静默省略任何章节 —— 跳过的章节要说明原因
- 论文类型标签与判定规则的证据相符

## 反幻觉规则

完整规则见 `references/quality-checklist.md`。以下是不可妥协的约束：

1. **来源标注**：`[原文声明]` = 论文中直接写明（引用位置）；
   `[模型归纳]` = 模型推断（说明推理依据）
2. **不确定性**：原文未提供时标 `[未明确给出]`；有歧义时标 `[不确定]`
3. **不做领域假设**：永远先判定论文类型
4. **不编造**：正文未给出的发表场合、DOI、年份、单位 → `[未明确给出]`
5. **证据绑定**：每条贡献必须引用章节/图/表/原文片段
6. **降级 PDF**：说明哪些章节不可读；不填补缺口

双标签示例：

```
[原文声明] 提出了 X 方法
证据：Section 3.2，"We propose X, which..."

[模型归纳] 该方法在低资源场景下可能有优势
依据：实验仅在小数据集上测试，作者未明确声明此优势
```

## 降级输入回退

| 情形 | 处理 |
|-----------|--------|
| 只有摘要可用 | 切换 `quick` 模式，注明限制 |
| 扫描版 PDF、无文字层 | 先请用户提供文字或做 OCR |
| 缺参考文献部分 | 跳过前作分析，注明缺失 |
| 图表不可读 | 跳过图表分析，注明缺失 |
| 非英文论文 | 翻译关键章节，注明源语言 |

## Extended 模式：作者前作

仅在 `extended` 模式下执行：
1. 从论文中提取全部作者姓名
2. 在参考文献列表中识别自引（存在共同作者）
3. 根据单位 + 论文标题推断课题组研究方向
4. 只从参考文献列表中列举前作 —— 不做网络检索，不用外部知识
5. 所有输出标注：`[基于论文内引用，非外部检索]`
6. 信息不足时：明确写出"信息不足，无法判断前作关系"

## Presentation 模式：PPT 生成

仅在 `presentation` 或 `presentation_with_figures` 模式下执行。

### 步骤 A：收集覆盖项

构建幻灯片计划前，检查用户是否指定了以下任一项：
- `audience`（lab / conference / general）—— 默认：`lab`
- `duration_hint`（10min / 20min / 30min）—— 默认：`20min`
- `talk_style`（technical / overview / discussion）—— 默认：`technical`
- `emphasis`（要展开的章节）
- `skip`（要省略的章节）

未指定则静默使用默认值。

### 步骤 B0：提取 PDF 图表（仅 presentation_with_figures）

构建幻灯片计划前，运行：
```
python scripts/extract_pdf_figures.py <pdf_path>
```
这会把所有图表保存到 `figures/`，并写出 `figures/index.json`，其中包含每张图片的 `name`、`path` 和 `page`。在交接（handoff）中为 `figure_ref` 赋值时使用该索引。

### 步骤 B：构建幻灯片计划

结构遵循 `references/presentation-schema.md`。
压缩规则遵循 `references/presentation-style-guide.md`。

- 把每个 slide role 映射到 output-schema 的对应章节
- 应用用户覆盖项（emphasis → 展开，skip → 省略）
- 对 `presentation_with_figures`：在以图为主要证据的方法/结果页设置 `figure_needed: true`；添加 `figure_ref` 与 `figure_hint`
- 页数由 duration_hint 决定（10min→6-7 页，20min→9-10 页，30min→12-14 页）

### 步骤 C：调用 pptx Skill

交接格式严格遵循 `references/pptx-handoff.md`。

- 传给 pptx 前剥掉所有 `[原文声明]` / `[模型归纳]` 标签
- 交接内容中**不**包含演讲者备注
- 自动调用 pptx skill —— 不要先询问用户
- 例外：若用户说"只要大纲" / "just the outline"，则以文本形式输出幻灯片计划，跳过 pptx

---

## 来源与许可

上游 [flyer-Li/paper-analyst](https://github.com/flyer-Li/paper-analyst)，MIT 许可证（Copyright (c) 2026 Yifei Li），许可证全文见随附 LICENSE，2026-09-10 收录（commit 1e385a3）；原文英文，本包译为简体中文。README 中的功能亮点、依赖项与输出结构说明已合并入本文。
