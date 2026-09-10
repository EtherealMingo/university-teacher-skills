---
name: slides-polish
description: "制作设计师水准的 .pptx 幻灯片：真实投影、平滑贝塞尔曲线、渐变填充、真正的箭头、丰富的 SVG 图标——这些是 python-pptx 原生形状在 Keynote 或 Google Slides 中无法可靠渲染的视觉效果。当用户想要"好看"的幻灯片、"现代风 deck"、"精修的演示文稿"、"设计师水准"的页面、提供了设计师色板，或对 python-pptx 生成的 deck 视觉质量不满意时使用。任何超出纯文本+项目符号的幻灯片都优先用它而不是裸 python-pptx。 Triggers: 帮我把这个 PPT 做得好看一点、这个 deck 在 Keynote 里箭头全没了、我要一份设计师水准的幻灯片、按这个色板做一套现代风的 PPT、这个幻灯片太丑了帮我美化一下、python-pptx 做的投影在 Keynote 里显示不对。"
---

# 精修幻灯片视觉：HTML/SVG → PNG → pptx 管线

本技能在 Anthropic 的 `document-skills:pptx` skill 之上叠加一条富视觉管线。.pptx 的脚手架（创建文件、幻灯片版式、标题、页脚、页码、Keynote/LibreOffice 转图工作流）用 **pptx skill**；任何视觉丰富的幻灯片的**正文**则用**本技能的** HTML/SVG → headless-Chrome → PNG 管线。

## 为什么不用 python-pptx 画正文

python-pptx 只暴露了基础形状（`MSO_SHAPE.RECTANGLE`、`ROUNDED_RECTANGLE`、`OVAL` 等），你可以挂 OOXML 效果（`<a:outerShdw>`）来假装精致设计。但实践中，只要幻灯片需要以下任何一项，python-pptx 路线产出的效果在 Keynote/Google Slides 里就是错的 —— 而大多数人恰恰是用 Keynote/Google Slides 打开 .pptx 的：

- **真实投影。** OOXML `<a:outerShdw>` 在 PowerPoint 里能渲染，在 Keynote 里明显劣化。用偏移矩形造假投影，看起来像没对齐的边框残影。
- **平滑曲线。** 贝塞尔衰减曲线（如遗忘曲线图）、带箭头的弧线、图表下方的渐变填充区域。python-pptx 没有能画好这些的原语。
- **真正的箭头。** python-pptx 里 `slide.shapes.add_connector(2, ...)` 的箭头在 Keynote 打开或导入 Google Slides 时**不会**渲染箭头头部，只会渲染成普通直线。实心块箭头（`MSO_SHAPE.RIGHT_ARROW`）能用，但当你想要连接符风格的流程图配干净箭头尖时，它看起来像个楔子。
- **渐变填充、基于 marker 的 SVG 箭头、单个元素上的柔和高斯阴影。**
- **真正的图标。** 手工制作的 SVG 图标（书、天平、人物、地球、反馈环、带对勾的代码括号）读起来是设计；unicode 字符画和通用 Office 形状读起来是草稿。
- **排版打磨。** 斜体 Lora/Georgia 标题、衬线+无衬线混排、行内彩色强调（如西语句子里 ser 用绿色、estar 用蓝色）。

解法是：把幻灯片正文渲染成一个带内联 SVG 的 HTML 页面，用 headless Chrome 截图，再通过 `slide.shapes.add_picture()` 把 PNG 嵌进 .pptx。标题、页脚、页码保留为原生 python-pptx 文本，在 PowerPoint 里仍可编辑。

## 管线

```
HTML + inline SVG  ──▶  headless Chrome screenshot  ──▶  PNG  ──▶  python-pptx add_picture()
```

### 1. 幻灯片版式 —— 实测可用的尺寸

16:9 的 .pptx 幻灯片是 13.333" × 7.5"。标题、页脚、页码这些"镶边"会吃掉纵向空间。使用以下位置：

| 元素        | 位置                                | 原因                                                            |
|----------------|------------------------------------------|----------------------------------------------------------------|
| 标题文本  | `x=0.6, y=0.40, w=SLIDE_W-1.2, h=0.95`   | 比自然的 `y=0.65` 上移，给正文图片留出更多空间 |
| 绿色下划线 | `y=1.32`，长度 `1.5"`            | 标题下的紧凑标线 —— 整套 deck 反复出现的母题       |
| 嵌入图片 | `x=0.42, y=1.50, w=12.50, h=5.68`        | 占幻灯片宽度的 94%，位于下划线与页脚带之间  |
| 页脚带    | `y=7.18–7.50`                             | 淡蓝色条，放公司名 + 页码                  |

`img_h = 5.68` 来自保持 HTML 画布宽高比：`12.5 * (1000/2200) = 5.68`。图片底边在 `1.50 + 5.68 = 7.18`，恰好接上页脚带 —— 不重叠、不留缝。

### 2. HTML 画布

```html
<div class="wrap" style="width: 2200px; height: 1000px; padding: 25px 40px; box-sizing: border-box;">
  …
</div>
```

`2200 × 1000`（2.2:1）与嵌入图片的宽高比精确一致，Chrome 截图能铺满画布、不留黑边。`padding: 25px 40px` 是刻意压紧的 —— 原因见下文"相信 Keynote，别信浏览器"一节。

### 3. 用 headless Chrome 渲染（走 Bash，不走 Playwright MCP）

通过 `Bash` 工具直接调用 Chrome：

```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
"$CHROME" --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --screenshot=/tmp/slide_05_body.png \
  --window-size=2200,1000 \
  file:///tmp/slide_05_body.html
```

headless 模式下 Chrome 能读 `file://` URL —— 不需要起 HTTP 服务。

**不要为此用 Playwright MCP。** 实践中我们在 Playwright MCP 上反复撞上 `claude-opus-4-7 is temporarily unavailable` 安全分类器故障，整个工作流都被卡住。走 Bash 调 Chrome 没有这个问题，更快，还少一个活动部件。

### 4. 嵌入 python-pptx

```python
img_w = 12.5
img_h = img_w * (1000 / 2200)  # 5.68 — 保持画布宽高比
img_x = (SLIDE_W - img_w) / 2  # 0.42 — 水平居中
img_y = 1.50
slide.shapes.add_picture("/tmp/slide_05_body.png",
                          Inches(img_x), Inches(img_y),
                          Inches(img_w), Inches(img_h))
```

标题 + 页脚保留为原生 python-pptx 文本，沿用 `document-skills:pptx` 的脚手架（或你自己写的同风格辅助函数）。

## 相信 Keynote，别信浏览器

HTML 的浏览器预览和 Keynote 渲染出的幻灯片之间差异之大，每次都会坑到你。把下面几条内化，否则每张幻灯片都得白迭代一轮：

- **浏览器预览里的字号看起来比在幻灯片上读起来的大得多。** 把所有字号在 Chrome 里"感觉对"的基础上再加 15–30%。
- **HTML 画布内的留白在幻灯片上会读成大片的空洞死区。** 把 wrap 的内边距狠狠压紧 —— 2200px 画布用 `25–30px`，而不是你默认会用的 `50–80px`。
- **在浏览器里看起来垂直居中的内容，到 Keynote 里会飘到顶部。** 显式地给内层小节加 `justify-content: center` 或 `flex: 1`；不要想当然。

唯一可靠的验证方式是：渲染 .pptx，用 Keynote 导出 PNG，降采样，亲眼看实际渲染出来的幻灯片：

```bash
# 通过 Keynote AppleScript 把 deck 导出为逐页 PNG
osascript <<'EOF'
tell application "Keynote"
    activate
    set theDoc to open POSIX file "/path/to/presentation.pptx"
    delay 3
    export theDoc to POSIX file "/tmp/deck_slides" as slide images with properties {image format:PNG, skipped slides:false}
    delay 2
    close theDoc saving no
end tell
EOF

# 降采样给 Read 工具用（单维上限 2000px）
sips -Z 1800 /tmp/deck_slides/disneylingo_slides.005.png --out /tmp/preview_05.png
```

然后 `Read` 那张降采样 PNG。**这才是唯一的真相视角。** 浏览器预览在字号、内容密度、垂直居上全都会骗你。绝不要仅凭浏览器预览就宣布一张幻灯片完成。

## HTML/CSS 坑（都是真实踩过的 bug，不是理论）

下面这些坑我们反复踩过。写 HTML 之前先内化。

### Flex 子元素只在两个条件同时满足时才会拉伸

`.wrap` 里的 `.card` 只有在以下情况才会拉伸填满 `.wrap` 的高度：
1. `.wrap` 有显式 `height`（或本身是正在增长的 flex 项），**且**
2. `.wrap` 是 `align-items: stretch`（这是默认值，但很容易被上游的 `center` 或 `flex-start` 覆盖）。

当你的卡片看起来被困在画布中央 —— 内容挤在中间、上下大片空白 —— 几乎总是这个原因。

### 内容默认飘向顶部

`display: flex; flex-direction: column;` 的容器，内容填不满高度时会堆在顶部、底部留空。按视觉意图选修法：

- 容器加 `justify-content: center` —— 把所有内容作为一个整体居中。
- `justify-content: space-between` —— 首尾元素顶到上/下，中间元素均分。
- 给应该吃掉余量的那一节加 `flex: 1` —— 其余保持自然高度。

### 全局 SVG 覆盖画布的连接线很脆弱

我们为一个中心辐射式（hub-and-spoke）单元图试过这个方案（一个绝对定位的 SVG 盖满整个画布，路径从右侧的原子卡连到左侧的单元卡）。坐标数学一直对不齐，因为：

- `position: absolute; inset: 0;` 相对于最近的定位祖先的 *padding box* 解析，而不是 content box。
- `preserveAspectRatio="none"` 会非均匀拉伸 viewBox，在源坐标里看着对的路径，渲染后落到意想不到的位置。

**优先用组件级内联 SVG 箭头。** 在每个需要箭头的行旁放一个小型左/右箭头 SVG，用 CSS 定尺寸，不涉及全局坐标系：

```html
<div class="atom-row">
  <div class="arrow">
    <svg width="120" height="52" viewBox="0 0 92 40">
      <polygon points="0,20 28,4 28,14 92,14 92,26 28,26 28,36" fill="#79DF4D"/>
    </svg>
  </div>
  <div class="atom">…</div>
</div>
```

把"全局 SVG 覆盖画布"留给真正需要它的场景 —— 比如横跨整页的三叉连接线，或者一张*本身就是*正文的遗忘曲线图。即便如此，也要让 SVG 的 `viewBox` 固定且与实际版式尺寸一致，并且每次改动后用 Read 工具核验。

## 设计系统纪律

设计师会给你一套色板。严格照用。辅助色调（正文用的藏青墨色、图注用的石墨灰、从品牌色衍生的淡蓝/淡绿卡片底色）可以接受 —— 它们是层级，不是新品牌色。

两条规则：

1. **绝不发明第四种品牌色。** 如果设计师给的是绿 + 蓝 + 背景色，就不要"为了视觉趣味"引入珊瑚色、桃色、黄色或任何暖色。deck 需要更有冲击力时，通过排版、版式密度、对比度或动态感（投影、现有色板内的渐变）来找 —— 而不是新色相。用户对色板漂移极其敏感。
2. **选定一个重复母题，到处用它。** 我们的 deck 在每张内容页标题下用一条粗绿色下划线。仅这一个母题 —— 每张幻灯片都可见 —— 立刻建立了用户能识别的连贯感。其他选项：固定角落里的小色点、统一颜色的圆形图标底、单一粗细的强调条纹。选一个。在每张内容页上重复它。

## 迭代循环

不要渲染一次就交付。循环是：

1. **起草** HTML，用 headless Chrome 渲染成 PNG，用 `Read` 目检。
2. **嵌入** PNG 到 .pptx（`add_picture()`）；重新生成 .pptx。
3. **导出** .pptx 为 PNG（Keynote AppleScript）。
4. **降采样**（`sips -Z 1800`）。
5. **检查**降采样后的幻灯片 PNG（`Read`）。检查项：内容飘向顶部/底部、字号可读性、空洞死区、与标题+页脚的对齐、色板纪律。
6. **调整** HTML 的内边距/字号/flex，回到第 1 步。

每张幻灯片预计要 2–4 轮才能到位。每一轮浏览器预览都会误导你 —— 只有 Keynote 导出才说真话。

## 文件组织

保持有序，让每张幻灯片能独立迭代：

```
/tmp/slide_02_problem.html     # 第 2 页正文的源 HTML
/tmp/slide_02_problem.png      # 渲染出的 2200×1000 PNG
/tmp/slide_03_personal.html
/tmp/slide_03_personal.png
…
/tmp/generate_deck.py          # python-pptx 生成器（嵌入各 PNG）
~/path/to/presentation.pptx    # 最终产物
/tmp/deck_slides/              # Keynote 导出的 PNG（每页一张）
/tmp/preview_02.png            # 降采样后供 Read 工具检查
```

重渲单页 = `chrome --screenshot ... slide_02.html` → `python3 generate_deck.py` → Keynote 导出 → `sips` → `Read`。每页的 HTML 独立存放；生成器按路径引用各 PNG。

## 从 `document-skills:pptx` 拿什么

用那个 skill 做这些事：
- 创建 .pptx 文件结构、设定幻灯片尺寸（`prs.slide_width = Inches(13.333)`）。
- 标题 + 页脚 + 页码脚手架（或按同样思路自己写辅助函数）。
- Keynote / LibreOffice 幻灯片转 PNG 的模式（本技能的 `osascript` 块是一种变体 —— `soffice --headless --convert-to pdf` + `pdftoppm` 是另一种）。
- 读取已有 deck 时用 `markitdown` 提取文本。

不要照抄那个 skill 的 "Design Ideas" 一节。它的色板表和字体搭配是不错的起点，但上文的设计系统纪律（单一母题、不要第四种颜色、只用设计师给的色板）更严格，在有真实设计师参与时效果更好 —— 而只要本技能是正确工具，就属于这种情况。

## 前置条件

- **Python 3.10+** 及 `python-pptx`（`pip install python-pptx`）
- **Google Chrome**（headless 渲染步骤用）—— 大多数工作站已装
- **macOS Keynote** 或 **LibreOffice**（验证循环用 —— 把 .pptx 导出成 PNG）
- **Anthropic 的 `pptx` skill**（来自 <https://github.com/anthropics/skills>），用于建 deck 的脚手架（幻灯片、标题、页码）。本技能叠加在它之上。

## 何时触发本技能

本技能的 description 有意写得宽泛。以下情形应触发：

- 用户要"精修的 deck"、"现代风演示"、"设计师水准的幻灯片"，或"把这个做得好看点"
- 用户给出设计师提供的色板，要求 deck 严格遵守
- 用户反馈 python-pptx 做的 deck 在 Keynote / Google Slides 里箭头或投影显示不对
- 用户要的不只是纯文本和项目符号（图示、流程、图标、中心辐射图、层叠形状、图表）

以下情形**不**触发：纯文本提取、只含要点的 deck、deck 合并、`pptx` 转 `pdf` —— 这些直接用 Anthropic 的 `pptx` skill。

## 示例演示

`examples/` 目录里有一个端到端可跑的演示。进入该目录后：

```bash
# 1. 把精修的 HTML 正文渲染成 2200×1000 PNG
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-sandbox --hide-scrollbars \
  --screenshot=example_body.png --window-size=2200,1000 \
  file://$PWD/example_body.html

# 2. 构建 2 页 before/after .pptx（第 1 页：原生 pptx，第 2 页：HTML/SVG 嵌入）
python3 build_demo.py

# 3. 打开看
open demo.pptx
```

第 1 页是原始 python-pptx 的效果（断掉的箭头、缺失的投影），第 2 页是 HTML/SVG 嵌入的效果 —— 同样的版式、颜色和内容，注意看箭头、投影、图标与排版的差别。`examples/before_after.png` 是两者的拼图对比。本技能教会的正是如何自动产出第 2 页那种版本。

`examples/` 内各文件：

```
examples/
├── example_body.html       # 精修的 HTML 幻灯片正文（"AFTER"效果）
├── example_body.png        # 渲染输出（2200×1000）
├── build_demo.py           # 构建 2 页 before/after .pptx
├── demo.pptx               # 成品 deck（用 Keynote 打开！）
├── _before_mock.html       # 对原始 python-pptx 输出的逼真复刻，用于对比
├── before_after.png        # before/after 对比拼图
└── _make_hero.py           # 把 before/after 两张 PNG 拼成对比图
```

---

## 来源与许可

上游 [parahall/polished-slide-visuals](https://github.com/parahall/polished-slide-visuals)，MIT 许可证，许可证见上游仓库，2026-09-10 收录（commit 8f6f6ab）；原文英文，本包译为简体中文。该技能构建于 [Anthropic 的 `pptx` skill](https://github.com/anthropics/skills/tree/main/document-skills/pptx) 之上：.pptx 创建、幻灯片版式与 Keynote/LibreOffice 转换工作流的大部分基础能力来自那里，本技能是针对视觉质量维度的专项增强。README 中的触发条件、前置条件与示例演示说明已合并入本文。
