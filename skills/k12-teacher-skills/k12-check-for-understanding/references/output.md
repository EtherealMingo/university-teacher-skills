# 产出——k12-check-for-understanding

动笔之前完整阅读本文件（SKILL.md 第 5 步）。

---

## 两份文档

每份检测产出**两份各自独立、自成一体的 `.html` 文件**——绝不合并成一个文件，绝不用
markdown。

- **`cfu_[主题-slug]_student.html`**——可打印、可原样直接分发：只有题干与选项（CR 则为作答
  空间），外加姓名/日期栏，别无他物。没有元信息块、没有正确答案标记、没有来源标签、没有
  关于下一步的措辞。
- **`cfu_[主题-slug]_teacher.html`**——元信息块、焦点与进阶提示框、每道题完整重现、正确答案、
  解读指南，以及"纵观全部作答"小结。

`[主题-slug]` 是几个小写的连字符词：`equivalent-fractions`。**题目文本在两份文件中完全一致**——
题干、选项、顺序都相同，图示也一样。只写一次，原样复用——这正是讲义可以不经删改直接发下去
的原因。

---

## 写文件

两份都**写入 `$OUTPUT_DIR`**——先 `mkdir -p "$OUTPUT_DIR"`，然后写
`"$OUTPUT_DIR"/cfu_equivalent-fractions_student.html` 和对应的 `_teacher.html`。这个运行时就从
那里交付；只写到 `/tmp` 的文件永远到不了教师手里。写完后列出目录，确认两份文件都在且内容
不是空架子。如果没有 `$OUTPUT_DIR`，就在回复中内联呈现两份文档，并清楚地分隔开。两份文件都要
能独立渲染：样式写在内联的 `<style>` 块里，不用任何外部 CSS、字体或脚本。

---

## 图示

内联 `<svg>` 读回成文本时不会说明它画了什么，所以要用文字把这一点带上——
`<title>4 groups of 3 dots each</title>` 和 `<desc>Four squares in a row. Each square contains 3
dots, for 12 dots in total.</desc>`，并按下面的方式接线。

- **`<title>`** 用读这道题所用的术语点名图的结构——"4 组，每组 3 个点"，而不是"骰子"；
  **`<desc>`** 补上学生仅凭这段文字解题所需的信息。两者都是面向学生的，所以都要按该年级的
  语言水平来写。
- **描述不替学生完成这道题的工作。** 动笔之前，先点名这道题要求学生做的那一件事——数出份数、
  认出硬币、比较两个数量——然后让文字写成：仅凭它解题的学生仍然必须亲自去做那一件事。一条被
  四等分的线段问哪个点在 3/4 处，*"A、B、C、D 四个点，分别在 0 之后的每一个刻度上"* 把数数的
  工作留给了学生；*"C 点距离 0 有 3 格"* 则已经替他们做完了。题目问一枚硬币值多少时，*"一枚
  边缘有齿纹的银色小硬币"* 把辨认留给学生；*"一枚一角硬币"* 则没有。把题目泄露出去的写法，
  是点出题目所问的那个属性——份数、位置、身份、比较——无论答案本身有没有出现在文字里。
- **只陈述图画所承载的东西。** 比较需要两样东西都画出来：页面上只有一枚硬币时，*"罐子里较小
  的硬币之一"* 说的是读者无从看到的事情。
- `role="img"` 加上 `aria-labelledby` 让屏幕阅读器能把它们读出来，且**两份**文件中的标记完全
  一致。当答案取决于只有图示才承载的某个属性时，题干也要点名它。

---

## 不谈出处，不谈过程

任何一份文件都不说任何东西来自哪里：干扰项那一行没有 `KG` 或 `Training` 徽标，没有来源列，
元信息块和提示框里没有徽章，也没有"某次查询没有返回结果"之类的说明。进阶查询返回空，是关于
这次检索的事实，而不是关于数学的事实，所以指南只陈述它确实拥有的先备与下一步路由，对其余
只字不提。检索到的数据依然塑造每一行；只是文件不再叙述它。（第三方名称按 SKILL.md 的数据使用
护栏一律不出现。）

两份文件读起来都应当像这份检测本来就存在一样。`Confirmed with teacher`、`by teacher request`、
`as you asked`，以及任何承载这类信息的徽章，都是对话从成品里透了出来——交付前你运行的那些检查
留下的任何痕迹也一样。要把焦点写成关于数学的事实——*"两个组件：辨认硬币面值，以及把一组混合
硬币相加。"*

---

## 样式

基础样式块，两份文件都用：

```css
body{font-family:Georgia,serif;margin:40px auto;padding:0 24px;color:#1a1a1a}
h1{font-size:1.35em;color:#2c2c2c;border-bottom:2px solid #444;padding-bottom:8px}
.item-number{font-size:.85em;font-weight:bold;text-transform:uppercase;color:#555;margin-bottom:8px}
.item-prompt{font-size:1.05em;line-height:1.7;margin-bottom:14px}
.choices{list-style:none;padding:0;margin:0 0 16px}
.choices li{padding:9px 13px;margin:7px 0;border:1px solid #767676;border-radius:4px}
```

学生文件追加：

```css
body{max-width:700px}
.name-line{margin:20px 0 32px}
.name-line span{display:inline-block;border-bottom:1px solid #767676;min-width:220px;margin-left:6px}
.item{margin:32px 0;page-break-inside:avoid}
.response-line{border-bottom:1px solid #767676;height:32px;margin:8px 0}
@media print{body{margin:0;padding:0 12px}}
```

教师文件追加：

```css
body{max-width:800px;background:#fafaf8}
h1{border-bottom-color:#d4a843}
h2{font-size:.95em;text-transform:uppercase;color:#666;margin:20px 0 8px}
.meta{background:#fff;border:1px solid #e0ddd5;border-radius:6px;padding:16px 20px;margin:20px 0;display:grid;grid-template-columns:200px 1fr;gap:0 12px}
.meta-label,.meta-value{padding:8px 0;border-bottom:1px solid #f0ede5}
.meta-label{font-weight:bold;color:#555}
.meta-label:last-of-type,.meta-value:last-of-type{border-bottom:none}
.item{background:#fff;border:1px solid #e0ddd5;border-radius:6px;padding:20px 24px;margin:24px 0}
.correct-answer{color:#2d6a2d;font-weight:bold;margin-bottom:16px}
table{width:100%;border-collapse:collapse;font-size:.92em}
th{background:#f0ede6;text-align:left;padding:10px 12px;border-bottom:2px solid #ddd}
td{padding:10px 12px;border-bottom:1px solid #eee;vertical-align:top;line-height:1.5}
tr.correct-row td{background:#f0f7f0}
.look-for,.lc-focus,.progression-ctx{padding:14px 18px;margin:20px 0;border-radius:6px;line-height:1.6}
.look-for{background:#fef9ec;border-left:4px solid #d4a843}
.lc-focus{background:#f1f8e9;border:1px solid #c5e1a5}
.progression-ctx{background:#f0f4ff;border:1px solid #b8c8f0}
.look-for strong,.lc-focus strong,.progression-ctx strong{display:block;margin-bottom:6px;font-size:.85em;text-transform:uppercase}
.look-for strong{color:#7a5c00} .lc-focus strong{color:#2e7d32} .progression-ctx strong{color:#1a56c4}
```

---

## 面向学生的模板

以 `<!DOCTYPE html>`、`<html lang="en">` 开头，head 里带上 `<meta charset="UTF-8">`、viewport
meta、`<title>CFU: [Topic]</title>`，以及含基础规则 + 学生规则的 `<style>`。然后：

```html
<body>
<main>

<h1>[Topic/Concept]</h1>
<div class="name-line">Name: <span>&nbsp;</span> &nbsp;&nbsp; Date: <span>&nbsp;</span></div>

<!-- Repeat per item. Prompt and choices only — nothing else. -->
<div class="item">
  <div class="item-number">Item 1</div>
  <div class="item-prompt">
    [Prompt text — identical to the teacher file. Where the answer turns on a property only the
    figure shows, this names that property.]
  </div>
  <svg viewBox="0 0 420 110" role="img" aria-labelledby="i1-t i1-d"
       xmlns="http://www.w3.org/2000/svg">
    <title id="i1-t">[what the figure shows, in the terms the item is read in]</title>
    <desc id="i1-d">[enough detail to work the item from this text alone]</desc>
  </svg>
  <ul class="choices">
    <li><strong>A.</strong> [Choice A]</li>
    <li><strong>B.</strong> [Choice B]</li>
    <!-- C, D likewise -->
  </ul>
  <!-- Constructed response instead: a few <div class="response-line"></div> in place of the <ul> -->
</div>

</main>
</body>
</html>
```

---

## 面向教师的模板

**其中的散段文字是教师笔记，不是评估规格书。** 每句一个意思，约 35 词以内；平实的说法在前，
专业术语放在后面的括号里；以学生为主语。*"学生能通过数出等分总份数（分母）在数轴上找到一个
非单位分数……"* 是教师的笔记；*"揭示学生能否协调好定位……的两个部分……"* 描述的则是检测的
设计。

外壳相同，标题用 `<title>CFU: [Topic] — Teacher Guide</title>`，样式用基础规则 + 教师规则。

```html
<body>
<main>

<h1>CFU: [Topic/Concept] — Teacher Guide</h1>

<div class="meta">
  <!-- One label/value span pair per row, these six in this order. Contents per references/math.md. -->
  <span class="meta-label">Standard</span>
  <span class="meta-value">[CCSS code] — [verbatim standard language from the retrieval]</span>
  <span class="meta-label">Grade</span>
  <span class="meta-value">[Grade]</span>
  <span class="meta-label">Rigor</span>
  <span class="meta-value">[Conceptual / Procedural / Application / Mixed]</span>
  <span class="meta-label">Learning goal</span>
  <span class="meta-value">[Two sentences, one thought each, under about 30 words. First: what a student who has this can do — "Students can …", scoped to the confirmed focus. Second: how that shows up in these items. Not "students understand [standard]".]</span>
  <span class="meta-label">Prerequisite standards</span>
  <span class="meta-value">[1–3 codes, each with a short gist]</span>
  <span class="meta-label">Leads to</span>
  <span class="meta-value">[1–2 codes]</span>
</div>

<div class="lc-focus">
  <strong>Focus</strong>
  [Three or four short sentences, students as the subject, one thought each: what students do in a teacher's words; the constraints the confirmed focus carries (number range, denominator set, operation, representational form) in a sentence of their own; why this focus now. A fact about the mathematics, not how it was settled.]
</div>

<div class="progression-ctx">
  <strong>Progression &amp; coherence context</strong>
  [2–3 sentences: what prerequisite understanding this assumes, what makes this standard's demand distinctive at this grade, and how that decides whether a response routes prior-grade or on-grade.]
</div>

<!-- Repeat per item -->
<div class="item">
  <!-- the same item-number / item-prompt / figure / choices markup as the student file, verbatim -->
  <h2>Correct answer &amp; interpretation guide</h2>
  <div class="correct-answer">✓ Correct answer: [Answer]</div>

  <table>
    <thead>
      <tr><th scope="col" style="width:22%">Response</th><th scope="col" style="width:40%">What it suggests</th><th scope="col">Suggested next step</th></tr>
    </thead>
    <tbody>
      <tr class="correct-row">
        <td>[Correct answer]</td>
        <td>Student [what they can now do, per the confirmed focus]</td>
        <td>[What extends or advances this]</td>
      </tr>
      <tr>
        <td>A. [Distractor]</td>
        <td>[What the student did, observably] — prerequisite gap: [prior-grade content not yet secure]</td>
        <td>[The specific prior standard code and the sub-skill to revisit]</td>
      </tr>
      <tr>
        <td>B. [Distractor]</td>
        <td>[What the student did, observably] — on-grade confusion: [which part of this demand]</td>
        <td>[Sub-skill or representation — distinct from every other row]</td>
      </tr>
      <!-- One row per remaining choice, same shape -->
    </tbody>
  </table>
</div>

<div class="look-for">
  <strong>What to look for across responses</strong>
  [2–3 sentences, grounded in the coherence map: whether a shared pattern points to one prior-grade gap those students can all be routed to, versus scattered on-grade confusions each needing different handling. Asset-based.]
</div>

</main>
</body>
</html>
```

---

Copyright 2026 Anthropic, PBC · Copyright 2026 Learning Commons · SPDX-License-Identifier: Apache-2.0
