# 课程内容可视化库

何时阅读本文件：为涉及公式、数学图像、科学图示或领域专属可视化的课程内容生成 visual-explainer 智能体时。

## 工作方式

study 技能扮演领域感知的调度器角色。当课程需要可视化内容时，技能判断*需要哪类*可视化，并在提示词中告诉 visual-explainer 智能体*使用哪些库*。两种渲染策略：

1. **Web 原生（内联）** —— 从 CDN 加载的 JS 库，在浏览器中渲染。最适合交互式内容。
2. **SVG 生成（预渲染）** —— Python/CLI 工具生成 SVG 文件，通过 `<img>` 标签嵌入 HTML。最适合领域专属图示。

## 策略选择

生成 visual-explainer 智能体时，根据内容类型附上相应的库说明：

| 内容类型 | 策略 | 库 | CDN/安装 |
|---|---|---|---|
| 公式 | Web 原生 | KaTeX | CDN |
| 2D 函数图像 | Web 原生 | JSXGraph | CDN |
| 3D 曲面/图形 | Web 原生 | Plotly.js | CDN |
| 物理仿真 | Web 原生 | p5.js + Matter.js | CDN |
| 通用图示 | Web 原生 | Mermaid.js | CDN |
| 电路图 | SVG 生成 | SchemDraw（Python） | pip |
| 分子结构 | SVG 生成 | RDKit（Python） | pip/conda |
| 星图 | SVG 生成 | Starplot（Python） | pip |
| 乐谱 | SVG 生成 | LilyPond | dnf |
| 向量场/流线 | SVG 生成 | Matplotlib（Python） | pip |
| 费曼图 | SVG 生成 | feynman（Python） | pip |
| 框图/流程图 | SVG 生成 | blockdiag（Python） | pip |
| DNA/基因特征 | SVG 生成 | DNA Features Viewer（Python） | pip |
| 系统发育树 | SVG 生成 | phyTreeViz（Python） | pip |

## Web 原生库（CDN）

### KaTeX —— 公式

用于任何包含数学公式的课程。LaTeX 语法，渲染为 HTML+CSS。

告诉 visual-explainer 智能体：
```
Include KaTeX for equation rendering. CDN setup:

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body);"></script>

Use $...$ for inline math and $$...$$ for display math. LaTeX syntax.
```

### JSXGraph —— 2D 数学绘图

用于函数图像、参数曲线、相图、向量场、交互几何。

```
Include JSXGraph for interactive 2D math plots. CDN:

<link href="https://cdn.jsdelivr.net/npm/jsxgraph/distrib/jsxgraph.css" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/jsxgraph/distrib/jsxgraphcore.js"></script>

JSXGraph is specifically designed for math education — supports sliders,
parametric curves, function plotting, differential equations visualization.
```

### Plotly.js —— 3D 科学可视化

用于 3D 曲面、等高线图、热图、复杂科学图形。

```
Include Plotly.js for 3D visualization. CDN:

<script src="https://cdn.plot.ly/plotly-3.4.0.min.js"></script>

Use Plotly for 3D surface plots, contour maps, and scientific data visualization.
WebGL-accelerated, interactive rotation/zoom.
```

### p5.js + Matter.js —— 物理仿真

用于交互式物理：单摆、弹簧、波、碰撞、粒子。

```
Include p5.js for rendering and Matter.js for physics. CDN:

<script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.11.1/p5.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/matter-js/0.19.0/matter.min.js"></script>

p5.js handles drawing/animation, Matter.js handles rigid body physics.
For wave/field simulations, p5.js alone is sufficient (no Matter.js needed).
```

### Kekule.js —— 交互式分子结构

用于需要交互式分子渲染的化学课程。

```
Include Kekule.js for molecular visualization. CDN:

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/kekule/dist/themes/default/kekule.css">
<script src="https://cdn.jsdelivr.net/npm/kekule/dist/kekule.min.js"></script>

MIT license. Supports 2D/3D structures, MOL/SDF/CML formats.
```

## SVG 生成库（Python/CLI）

对于这类库，study 技能生成一个 Python 脚本，通过 Bash 运行，
visual-explainer 再把生成的 SVG 嵌入 HTML 页面。

### SVG 生成模式

```python
# 在 practice 目录中生成 SVG
import subprocess
script = '''
import schemdraw
import schemdraw.elements as elm
# ... diagram code ...
d.save("practice/lesson-NN/diagrams/circuit.svg")
'''
# 写出脚本，用 uv 运行：
# uv run --with schemdraw python generate_diagram.py
```

然后告诉 visual-explainer：“Embed the SVG from practice/lesson-NN/diagrams/circuit.svg”

### SchemDraw —— 电路图

**安装：** `pip install schemdraw`
**LLM 友好度：** 极佳 —— 简单的命令式 Python API。

```python
import schemdraw
import schemdraw.elements as elm

with schemdraw.Drawing(file='circuit.svg') as d:
    d += elm.SourceV().label('V1\n5V')
    d += elm.Resistor().right().label('R1\n1kΩ')
    d += elm.Capacitor().down().label('C1\n1μF')
    d += elm.Line().left()
    d += elm.Ground()
```

### Matplotlib —— 向量场、相图、通用科学图形

**安装：** `pip install matplotlib`
**LLM 友好度：** 极佳 —— 训练数据最多的 Python 可视化库。

最适合：流线、等势面、相图、电场线、自定义科学图形。
通过 `fig.savefig('plot.svg')` 导出 SVG。

### RDKit —— 从 SMILES 生成化学结构

**安装：** `pip install rdkit`（或 conda）
**LLM 友好度：** 良好 —— SMILES 字符串是文本化的分子描述。

```python
from rdkit import Chem
from rdkit.Chem import Draw

mol = Chem.MolFromSmiles('CC(=O)OC1=CC=CC=C1C(=O)O')  # Aspirin
Draw.MolToFile(mol, 'aspirin.svg', size=(300, 300))
```

### Starplot —— 天文星图

**安装：** `pip install starplot`（Python 3.10+）
**LLM 友好度：** 良好 —— API 简洁，文档完善。

通过 matplotlib 后端生成星图、天区图和天体可视化的 SVG。

### LilyPond —— 乐谱

**安装：** `dnf install lilypond`
**LLM 友好度：** 良好 —— 类似 LaTeX 的文本 DSL。

```lilypond
\relative c' { c4 d e f | g2 g | a4 a a a | g1 | }
```
运行：`lilypond --svg -o output score.ly`

### DNA Features Viewer —— 基因图示

**安装：** `pip install dna_features_viewer`
**LLM 友好度：** 良好 —— 声明式 Python API。

### phyTreeViz —— 系统发育树

**安装：** `pip install phytreeviz`
**LLM 友好度：** 良好 —— 简单 CLI，输出 SVG。

### blockdiag —— 系统框图

**安装：** `pip install blockdiag`
**LLM 友好度：** 极佳 —— 类似 DOT/Graphviz 的文本 DSL。

```
blockdiag { A -> B -> C; B -> D; }
```
运行：`blockdiag -Tsvg -o diagram.svg input.diag`

## 单页组合

一个课程页面可以使用多个库。常见组合：

- **物理课：** KaTeX（公式）+ JSXGraph（函数图像）+ p5.js（仿真）
- **化学课：** KaTeX（反应方程式）+ Kekule.js（分子）+ 嵌入的 RDKit SVG
- **电子工程课：** KaTeX（电路方程）+ 嵌入的 SchemDraw SVG
- **生物课：** Mermaid（通路图）+ 嵌入的 DNA Features Viewer SVG
- **乐理：** KaTeX（音程计算）+ 嵌入的 LilyPond SVG
- **天文：** KaTeX（轨道力学）+ 嵌入的 Starplot SVG

## 优雅降级

如果某个 Python 库未安装，技能应当：
1. 在课程中注明：“安装 schemdraw 以绘制电路图：pip install schemdraw”
2. 退化为图示的 ASCII/文本表示
3. 绝不因缺少可视化库而让课程失败
