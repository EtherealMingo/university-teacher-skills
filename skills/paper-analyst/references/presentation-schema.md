# 演示文稿规范（Presentation Schema）

## 幻灯片计划 JSON 结构

```json
{
  "deck_title": "string",
  "content_source": "standard | extended",
  "audience": "lab | conference | general",
  "talk_style": "technical | overview | discussion",
  "duration_hint": "10min | 20min | 30min",
  "slide_count_target": 9,
  "user_overrides": {
    "emphasis": ["method", "results", "contributions"],
    "skip": ["limitations", "prior_work"],
    "extra_slides": []
  },
  "slides": [
    {
      "n": 1,
      "type": "cover",
      "title": "string",
      "subtitle": "string",
      "authors": "string",
      "venue_year": "string"
    },
    {
      "n": 2,
      "type": "table",
      "role": "metadata",
      "title": "论文基本信息",
      "table_source": "output-schema Section 1",
      "fields": ["标题", "作者", "单位", "Venue", "年份", "DOI/arXiv", "关键词"],
      "omit_if_missing": true
    },
    {
      "n": 3,
      "type": "split",
      "role": "background",
      "title": "string",
      "left": {
        "format": "paragraph",
        "content": "string"
      },
      "right": {
        "format": "figure | bullets",
        "figure_ref": "Fig. X",
        "figure_hint": "string",
        "bullets": ["string"]
      },
      "right_prefer_figure": true
    },
    {
      "n": 4,
      "type": "split",
      "role": "method",
      "title": "方法概述",
      "left": {
        "format": "bullets",
        "bullets": ["string"]
      },
      "right": {
        "format": "figure",
        "figure_ref": "Fig. X",
        "figure_type": "architecture | flowchart | equation | diagram",
        "figure_hint": "string"
      },
      "right_prefer_figure": true,
      "overflow": {
        "enabled": true,
        "max_pages": 2,
        "split_at": "模型架构 / 训练策略"
      }
    },
    {
      "n": 5,
      "type": "contributions",
      "role": "contributions",
      "title": "创新点分析",
      "items": [
        {
          "headline": "string",
          "detail": "string",
          "bold_keywords": ["string"]
        }
      ],
      "source": "output-schema Section 4",
      "max_items": 4
    },
    {
      "n": 6,
      "type": "results",
      "role": "results",
      "title": "实验结果",
      "source": "output-schema Section 5",
      "required_figure": true,
      "figure_ref": "Fig. X / Table X",
      "figure_type": "bar_chart | line_graph | pie_chart | table | figure",
      "figure_hint": "string",
      "content_blocks": [
        {
          "format": "text | bullets | table | figure",
          "content": "string"
        }
      ],
      "overflow": {
        "enabled": true,
        "max_pages": 3,
        "split_strategy": "per_case"
      }
    },
    {
      "n": 7,
      "type": "conclusion",
      "role": "discussion",
      "title": "作者结论",
      "source": "output-schema Section 5 作者结论 [原文声明]",
      "quotes": ["string"],
      "summary_bullets": ["string"]
    },
    {
      "n": 8,
      "type": "prior_work",
      "role": "prior_work",
      "title": "与前作的关系",
      "source": "output-schema Section 6 (extended mode only)",
      "group_focus": "string",
      "prior_papers": ["string"],
      "relationship": "string",
      "note": "[基于论文内引用，非外部检索]"
    },
    {
      "n": 9,
      "type": "closing",
      "title": "string",
      "questions": ["string", "string", "string"]
    }
  ]
}
```

## 字段规则

| 字段 | 必填 | 说明 |
|-------|----------|-------|
| `deck_title` | 是 | 论文标题（可用中文） |
| `content_source` | 是 | 由哪一层分析结果供料 |
| `audience` | 是 | 影响压缩程度 |
| `slide_count_target` | 是 | 默认 9；按 duration_hint 调整 |
| `user_overrides.emphasis` | 否 | 要展开的章节 |
| `user_overrides.skip` | 否 | 要省略的章节 |
| `slides[].role` | bullets 型必填 | 映射到 output-schema 章节 |
| `figure_needed` | 是 | 仅当图能切实帮助理解时为 true |
| `right_prefer_figure` | split 型必填 | true = 有图用图；false = 用 bullets |
| `right.format` | split 型必填 | "figure" 或 "bullets" —— 检查论文内容后设定 |
| `right.figure_type` | split 型必填 | "architecture"、"flowchart"、"equation" 或 "diagram" |
| `overflow.enabled` | method 型必填 | true = 内容密集时允许扩展到 max_pages |
| `overflow.split_at` | method 型必填 | 第 1 页与第 2 页之间的自然切分点 |
| `items[].headline` | contributions 型必填 | 贡献的一句话概括 |
| `items[].detail` | contributions 型必填 | 1-2 句展开说明 |
| `items[].bold_keywords` | contributions 型必填 | detail 文本中要加粗的关键术语 |
| `max_items` | contributions 型必填 | 上限 4；从第 4 节中选取证据最充分的 |
| `required_figure` | results 型必填 | true = 必须包含至少一张图/表 |
| `figure_type` | results 型必填 | 论文中优先的可视化类型 |
| `content_blocks` | results 型必填 | text/bullets/table/figure 块的有序组合 |
| `overflow.split_strategy` | results 型必填 | "per_case" = 每个实验案例一页 |

## duration_hint → slide_count_target 对照

| 时长 | 页数 |
|----------|--------|
| 10min | 6–7 |
| 20min | 9–10 |
| 30min | 12–14 |
