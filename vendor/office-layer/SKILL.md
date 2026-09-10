---
name: office-layer
description: "中文办公文档产出层（自建）。当任何技能需要生成或修改 DOCX / PPTX / XLSX / PDF 文件时使用。覆盖：Word 文档（含原生批注、修订、页码、中文版式）、PowerPoint 课件（16:9、演讲者备注、信息密度检查）、Excel 表格与成绩分析（得分率/区分度/分布图）、PDF 导出。 Triggers: 生成 docx、导出 Word、写批注、做成绩分析、生成表格、做 PPT、导出 Excel。"
---

# Office Layer — 中文文档产出层

> **为什么自建**：ROADMAP 原计划引用 Anthropic 官方 docx/pptx/xlsx/pdf skill，但该四件套为
> **专有许可**（LICENSE.txt 明令禁止在 Services 之外保留副本、复制、创作衍生作品与分发）。
> 为让本技能包可自由分发，此处改为自建，并针对中文公文/学术排版做了专门处理。
> 详见 `../VENDOR.md` 的「许可证合规」一节。

**本层是本包唯一的文件产出通道。** 任何子 skill 需要交付 docx/pptx/xlsx/pdf，一律调用这里的脚本，
禁止用文本框拼「伪表格」、禁止手搓 OOXML 绕过本层。

## 环境准备（首次使用必做）

```bash
bash vendor/office-layer/bootstrap.sh          # 创建 .venv 并装依赖
PY=vendor/office-layer/.venv/bin/python
```

沙箱或受限环境下，`bootstrap.sh` 的自检会导入 matplotlib 并触发
`~/.matplotlib` 不可写的告警。**三个 kit 本身不依赖 matplotlib**（图表走 openpyxl 原生 chart），
只有你自己画自定义图时才需要可写缓存目录：

```bash
export MPLCONFIGDIR=/tmp/mplcache && mkdir -p /tmp/mplcache
```

因此上面的导出是**可选**的，不影响 docx/pptx/xlsx 的任何命令。

## 三个工具

### 1. `docx_kit.py` — Word

| 命令 | 用途 |
|---|---|
| `md --in a.md --out a.docx --title "标题"` | Markdown → DOCX。中文字体、标题层级、表格、页码、首行缩进两字 |
| `comment --in a.docx --out b.docx --comments c.json --author "指导教师"` | **在既有文档上写 Word 原生批注**（学生看得见的批注气球） |
| `spec --spec s.json --out a.docx` | 复杂排版：页眉页脚、评语模板、**人工确认位** |
| `inspect --in a.docx` | 读回段落/表格/批注/字数，用于自检 |

**批注是本层最关键的能力**，论文批改、开题意见、试卷审核都依赖它：

```json
[
  {"anchor": "技术路线与预期成果之间的对应关系尚不明确",
   "text": "请在图1中补充「方法→数据→结论」的对应关系。"}
]
```

- `anchor` 是**原文片段**，脚本会在正文与**表格单元格内**查找并锚定该区间。
- 锚点必须与正文逐字一致（含标点）。找不到会进 `failed` 并让进程以退出码 2 结束 —— **不要忽略这个非零退出码**。
- 落盘后是真 `word/comments.xml` + `commentRangeStart/End`，Word 打开即显示批注。

### 2. `pptx_kit.py` — PowerPoint

```bash
$PY .../pptx_kit.py build --spec s.json --out talk.pptx     # 16:9 生成
$PY .../pptx_kit.py notes --in talk.pptx --notes n.json     # 批量写演讲者备注
$PY .../pptx_kit.py inspect --in talk.pptx                  # 信息密度自检
```

规格片段：

```json
{"meta": {"title": "...", "subtitle": "...", "presenter": "..."},
 "slides": [{"title": "研究背景", "bullets": [{"text": "...", "level": 0}],
             "table": {"header": ["模型","MAPE"], "rows": [["LSTM","12.4"]]},
             "image": "/abs/path/fig1.png", "notes": "演讲备注"}]}
```

- 中文字体必须走 `a:ea`（脚本已处理），否则 PowerPoint 会用主题字体渲染，标题掉字重。
- `inspect` 会把单页正文 >220 字符的页面报进 `overdense` —— **这是提示你拆页，不是错误**。

### 3. `xlsx_kit.py` — Excel 与成绩分析

```bash
$PY .../xlsx_kit.py build   --spec s.json --out a.xlsx
$PY .../xlsx_kit.py analyze --in scores.xlsx --out analysis.xlsx \
    --first-q-col 3 --full-marks '[10,10,15,15,10,20,10,10]'
```

`analyze` 按教育测量学通行口径输出三个工作表（逐题分析 / 总体概况 / 分数段分布）与原生图表：

- **难度 P** = 该题平均得分 / 满分（即得分率，越大越容易）
- **区分度 D** = 高分组得分率 − 低分组得分率（高低分组各取总分前/后 27%）
- 判读：D≥0.4 优良｜0.3–0.39 良好｜0.2–0.29 尚可需修改｜<0.2 应淘汰
- 另给偏度/峰度作**正态性快评**，并在返回 JSON 里标出 `weak_questions` / `hard_questions` / `easy_questions`

> 区分度 <0.2 的行会被高亮；这是「这道题没区分出学生水平」的信号，多半是题目人人都对或人人都错。

## 铁律

1. **不虚构**：文档中出现的数据、文献、政策条文必须来自用户材料或明确占位，不得由模型补全。
2. **留人工确认位**：涉及评价、打分、结论的产出，必须在正文留显式占位（如 `【待教师确认：评分】`），
   AI 只出草稿，不直接给终稿。
3. **敏感数据本地处理**：成绩、学号、身份证号等不得外传；分析完成后提醒教师脱敏或删除中间文件。
4. **写完必须自检**：用 `inspect` 读回结构，确认段落数、批注数、表格数符合预期再交付。

## 故障排查

| 现象 | 处理 |
|---|---|
| `ModuleNotFoundError: docx/pptx/openpyxl` | 没走 venv。用 `vendor/office-layer/.venv/bin/python` |
| matplotlib 报 `~/.matplotlib` 不可写 | `export MPLCONFIGDIR=/tmp/mplcache` |
| `comment` 退出码 2 | 有锚点未命中，读返回 JSON 的 `failed` 逐条修正锚点文本 |
| PPTX 中文变等线/宋体 | 未走本层生成；不要手写 pptx |
| 表格渲染异常 | 本层已设 `Table Grid` 与列宽，不要自己加表格 XML |
