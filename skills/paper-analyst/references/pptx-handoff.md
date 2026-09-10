# pptx Skill 交接（Handoff）格式

## 何时调用 pptx Skill

生成幻灯片计划（presentation-schema.md）后，用下面的结构化提示自动调用 `pptx` skill。**不要**询问用户 —— 直接调用。

## 交接提示模板

```
/pptx

Create a presentation with the following slides:

**Deck:** {{deck_title}}
**Style:** {{talk_style}}, audience: {{audience}}

{{for each slide}}
---
Slide {{n}}: {{title}}
Type: {{type}}
{{if bullets}}Bullets:
{{bullets joined by newline}}{{/if}}
{{if figure_needed}}[Insert {{figure_ref}}: {{figure_hint}}]{{/if}}
{{if questions}}Discussion questions:
{{questions joined by newline}}{{/if}}
{{/for}}
```

## 触发条件

当以下条件**全部**满足时自动调用 pptx skill：
1. 模式为 `presentation` 或 `presentation_with_figures`
2. 幻灯片计划已生成并确认（或用户在同一轮中未提出异议）
3. 用户没有明确说过"只要大纲" / "just the outline" / "不用生成PPT"

## 要传什么

- 以结构化提示（而非原始 JSON）传入填好的幻灯片计划
- 提示所描述的幻灯片计划应尽可能贴近
  `references/presentation-schema.md` 的 JSON 结构
- 开头一行带上 deck 标题与风格上下文
- 每张幻灯片作为一个带标签的块：标题 + 要点 + 图表提示

## 不传什么

- 原始 slides.json —— pptx skill 接受自然语言，不接受 JSON
- `[原文声明]` 等内部标签 —— 交接前剥掉
- 演讲者备注 —— 那是给分析输出用的，不进 PPT
