---
name: book-installer
description: "安装与配置智能教材基础设施：从零搭建全新的 MkDocs Material 教材（init textbook）、安装 41 项功能中的任意项（数学公式、吉祥物、学习图谱查看器、Google Analytics GA4、自定义 404、看板），并生成教材度量报告。按需路由到对应安装指南。Triggers: 「搭建一本新教材」「初始化教材项目」「给教材加数学公式支持」「安装学习图谱查看器」「生成教材统计报告」「给教材加个吉祥物」。"
metadata:
  ibook.version: "1.0.1"
---

# 教材安装器（Book Installer）

**版本：** 1.0.1

### 更新日志

- **v1.0.1**——`references/learning-mascot.md`（步骤 5）中的权威吉祥物 CSS
  现在以 `.md-typeset img.mascot-admonition-img` 为目标，取代裸
  `.mascot-admonition-img` 选择器。Material 主题的 `.md-typeset img { height: auto }`
  优先级压过了裸类选择器，导致只有宽度生效，竖版姿态渲染高度远超
  `--mascot-size`（90px 宽的姿态在 clocks-and-watches 一书中实测高达
  93-210px）。类名本身不变，因此章节 Markdown、
  `validate-chapter-mascots.py` 与 glightbox 的 `skip_classes`
  都无需改动。已有的书应更新自己 `docs/css/mascot.css` 中的选择器。

- **v1.0**——本技能的第一个受跟踪版本号。新增
  `references/mascot-placement-rules.md` 作为吉祥物何时出现、出现频率
  的单一权威来源，以及 `scripts/render-mascot-guide.py`（把这些规则
  渲染进书本的 `CONTENT-GENERATION-GUIDE.md`，位于哨兵注释之间，
  副本只重新生成、绝不手工编辑）。旧的每章固定上限被一条非正式
  指引取代：按章节概念数缩放（约每 2 个概念 1 个提示块，按读者
  年龄调整），仅为建议、永不构成硬失败。
  `scripts/validate-chapter-mascots.py` 现在还会报告 encourage 姿态类名
  的弃用拼写 `-encouraging`（`mascot.css` 从未定义过它，渲染出来
  没有样式），并把第 1 章自我介绍从它总是会触犯的 1-3 句上限中豁免。
  版本号记在 `metadata:` 之下，而不是裸 `version:` 键（严格的打包
  校验会拒绝后者）。

## 概述

本元技能负责智能教材项目的安装与配置任务。它把五个安装技能合并为
单一入口，按需加载具体的安装指南。

## 何时使用本技能

用户请求以下事项时使用：

- 搭建新的 MkDocs Material 项目
- 从零创建新智能教材（0 号功能 scaffold）
- 安装学习图谱查看器
- 配置带 hooks 的技能使用追踪
- 把书注册进 Google Analytics（GA4 Measurement ID）
- 引导项目基础设施建设

## 步骤 1：处理帮助请求

如果用户说 "help"、"what can you do" 或 "list features"，直接展示
下面这张编号清单（不要加载参考文件）：

```
Book Installer Features (most → least common):

 0. New textbook scaffold - complete mkdocs.yml + docs/ tree + license for an empty directory (run once at project birth)
 1. Simple mkdocs.yml template - Minimal starter config for new projects (see feature 0)
 2. Site logo - Add custom logo to header
 3. Favicon - Browser tab/bookmark icon
 3b. Generate favicon from mascot - Auto-generate favicon.ico from neutral.png mascot image
 4. Cover image & social preview - Home page image + og:image metadata
 4b. Generate cover image prompt - Create a prompt for generating a cover image using text-to-image AI (DALL-E, Midjourney, etc.)
 4c. Social media preview hook - Inject og:* / twitter:* meta tags via MkDocs hook (no Cairo required)
 5. Math equations - KaTeX (recommended) or MathJax
 6. Code syntax highlighting - Language-aware code blocks
 7. Code copy button - One-click copy for code blocks
 8. Mermaid diagrams - Flowcharts, sequence diagrams from text
 9. Content tabs - Tabbed sections for alternatives
10. Image zoom (GLightbox) - Click to enlarge images
11. Custom admonitions - Prompt boxes with copy button
12. Interactive quizzes - Self-assessment questions
13. Abbreviations & tooltips - Glossary hover definitions
14. Task lists - Checkbox lists
15. Simple feedback - Thumbs up/down per page
16. Detailed comments (Giscus) - GitHub Discussions integration
17. Tags & categorization - Page tagging system
18. Search enhancements - Suggestions and highlighting
19. Table of contents config - TOC sidebar options
20. Blog support - Add blog section
21. Announcement bar - Dismissible top banner
22. Privacy & cookie consent - GDPR compliance
23. Learning graph viewer - Interactive concept visualization
24. Skill usage tracker - Claude Code analytics hooks
25. Google Analytics - requires a Google Analytics property ID G-*
26. .gitignore installer - make sure that `site` and `.cache` are not in the main branch
27. extra CSS installer for iframe and customer prompt admonition
28. extra JavaScript installer - for prompt admonition copy button
29. Feature checklist - auto-detect and document which features are implemented
30. Learning mascot - add a pedagogical agent character to guide students
31. Instructor's guide - comprehensive teacher's guide with classroom tips
32. Custom 404 page - friendly error page with mascot image
33. Document status indicators - colored dots in nav showing page lifecycle state
34. Kanban board - GitHub Projects board for tracking textbook development
35. Mascot chapter updater - retrofit existing chapters with mascot admonitions
36. About page - professional about.md with motivation, author bio, and citations
37. Slide generator - install slide-viewer MicroSim and generate slides.md decks for chapters
38. Reading level analysis - Flesch-Kincaid grade level report for all chapters
39. Generate all supplementary content - glossary, FAQ, per-chapter quizzes & references, book metrics, diagram reports, about page, landing page, README
40. Book metrics report - chapters, concepts, glossary/FAQ counts, quiz & reference totals, diagrams, equations, MicroSims, word count & equivalent pages (book-metrics.md + chapter-metrics.md)
41. MkDocs-serve warning - MkDocs-only hook that warns when a Zensical-built book is previewed with `mkdocs serve` (recommended for every Zensical-designed book during the MkDocs-to-Zensical transition)

Type a number or feature name to install.

Note: If you see `navigation.tabs` in mkdocs.yml, remove it. These books
use side navigation optimized for wide landscape screens.
```

展示清单后，等用户指定要哪项功能。

---

## 步骤 1b：检查导航标签页（既有项目）

处理既有 mkdocs.yml 时，永远检查并移除导航标签页：

```yaml
# 如果 mkdocs.yml 中有这些行，删除：
theme:
  features:
    - navigation.tabs        # 删除
    - navigation.tabs.sticky # 删除
```

这些书使用为宽屏横屏优化的侧边导航。顶部导航标签浪费纵向空间，
不适合这种版式。

---

## 步骤 2：识别安装类型

把用户的请求匹配到对应的安装指南：

### 路由表

| 触发关键词 | 动作 | 用途 |
|------------------|--------|---------|
| help, what can you do, features, capabilities, list features | 展示编号清单（步骤 1） | 快速功能总览 |
| init textbook, scaffold textbook, brand new book, empty directory, fresh start, new textbook from scratch, 0 | `references/init-textbook.md` | 从零引导一本全新教材（mkdocs.yml + docs/ + license + contact + social-override hook）——在任何其他功能**之前**先运行 |
| 1, simple mkdocs, minimal template, starter config | `references/init-textbook.md` | 权威脚手架（取代旧的最小模板） |
| google analytics, GA4, measurement id, tracking id, G-, analytics property, register analytics, 25 | `references/google-analytics.md` | 创建 GA4 媒体资源，把 G-* Measurement ID 写入 mkdocs.yml 的 extra.analytics，验证标签，部署 |
| enrich, add feature, 数字 2-24, 具体功能名 | `references/mkdocs-features.md` | 安装指定功能 |
| new project, mkdocs, textbook, bootstrap, setup, template, new book | `references/init-textbook.md` | 创建新 MkDocs Material 项目（0 号功能脚手架） |
| graph viewer, learning graph, visualization, interactive graph, concept viewer | `references/learning-graph-viewer.md` | 给既有项目加学习图谱查看器 |
| track skills, skill usage, activity tracking, hooks, usage analytics | `references/skill-tracker.md` | 配置带 hooks 的技能追踪 |
| generate cover image prompt, generate cover image, auto cover image prompt, create cover image promt, run cover prompt script | `references/cover-image-generator.md` | 从书本自身内容生成高质量封面图提示词；通过 API/ChatGPT 自动生成图片是可选项，仅在明确要求时运行 |
| cover image, home page, montage, book cover, index page | `references/home-page-template.md` | 创建带封面图与社交元数据的主页 |
| social media preview, social card, social meta, og:image, og:title, og:description, open graph, twitter card, twitter image, linkedin preview, slack unfurl, bk-check-social-cover, social hook, social override | `references/social-media-preview.md` | 安装在每个页面注入 og:* 与 twitter:* meta 标签的免 Cairo hook |
| logo, site logo, branding, upper left, header icon | `references/mkdocs-features.md` | 添加自定义 logo，含 AI 提示词示例 |
| favicon, browser tab, bookmark icon, .ico | `references/mkdocs-features.md` | 添加 favicon，含 AI 提示词示例 |
| generate favicon, favicon from mascot, mascot favicon, favicon.ico from png, create favicon | `references/favicon-generator.md` | 用 Python 从吉祥物 neutral.png 生成 favicon.ico |
| math, equations, latex, mathjax, katex | `references/mkdocs-features.md` | 添加数学公式支持 |
| feature checklist, generate feature checklist, feature status, what features | `references/feature-checklist-generator.md` | 自动检测并记录已实现的功能 |
| quiz, quizzes, assessment, multiple choice | `references/mkdocs-features.md` | 添加交互测验 |
| feedback, thumbs up, thumbs down, was this helpful | `references/mkdocs-features.md` | 添加页面反馈小组件 |
| comments, giscus, discussions | `references/mkdocs-features.md` | 添加评论系统 |
| image zoom, lightbox, glightbox, click to enlarge | `references/mkdocs-features.md` | 添加点击图片放大 |
| code highlighting, syntax, copy button | `references/mkdocs-features.md` | 添加代码语法高亮 |
| mermaid, diagrams, flowchart | `references/mkdocs-features.md` | 添加 Mermaid 图支持 |
| admonition, callout, prompt box, copy prompt | `references/mkdocs-features.md` | 添加带复制按钮的自定义提示块 |
| mascot, learning mascot, pedagogical agent, character, guide character, persona | `references/learning-mascot.md` | 添加引导学生学习的吉祥物 |
| instructor guide, teacher guide, teachers guide, instructor's guide, classroom guide | `references/instructors-guide.md` | 生成完整的教师指南 |
| 404, error page, not found, custom 404, page not found | `references/custom-404-page.md` | 添加带吉祥物的自定义 404 页 |
| document status, page status, status indicators, status dots, nav status, page lifecycle, review workflow | `references/document-status.md` | 在导航侧栏加彩色状态圆点 |
| kanban, project board, kanban board, project management, github project, task board, milestones, 34 | `references/kanban-board.md` | 为教材开发创建 GitHub Projects 看板 |
| mascot chapter, update chapter, retrofit mascot, place mascot, add mascot to chapter, 35 | `references/mascot-chapter-updater.md` | 按摆放规则给既有章节补装吉祥物提示块 |
| mascot placement rules, mascot rules, how often mascot, mascot frequency, which mascot pose, mascot admonition guidelines | `references/mascot-placement-rules.md` | 各姿态何时用/用多少的**权威**单一来源规则（只读，永不复述） |
| about page, about, about.md, about this book, author bio, cite this book, citation, 36 | `references/about-page.md` | 生成含缘起、作者简介与引用方式的专业 about 页 |
| slide generator, slides, slide deck, slide viewer, presentation, generate slides, install slide viewer, 37 | `references/slide-generator.md` | 安装 slide-viewer MicroSim 并为章节生成 slides.md 幻灯片 |
| reading level, readability, flesch kincaid, grade level, reading analysis, 38 | `references/reading-level-analysis.md` | 分析各章阅读水平一致性 |
| generate all supplementary content, supplementary content, complete the book, finish the book, book completion, generate glossary faq quiz, generate all content, all supplementary, 39 | `references/supplementary-content-generator.md` | 在一个协调工作流中生成术语表、FAQ、各章测验与参考文献、教材度量、图示报告、about 页、着陆页和 README |
| book metrics, generate metrics, book-metrics, chapter metrics, content statistics, word count, page count, equivalent pages, book composition, metrics report, 40 | `references/book-metrics.md` | 通过 bk-generate-book-metrics 生成 book-metrics.md、chapter-metrics.md 以及 book-metadata.json 中的 metrics 块 |
| mkdocs serve warning, serve warning, warn on mkdocs serve, wrong builder, wrong renderer, zensical transition, zensical warning, mkdocs vs zensical, transition guard, broken iframe in mkdocs serve, 41 | `references/mkdocs-serve-warning.md` | 安装 MkDocs 专用 hook：当用 Zensical 构建的书被 `mkdocs serve` 预览时发出警告（仅适用于用 Zensical 构建部署的书） |

### 决策树

```
在问帮助或 book-installer 能做什么？
  → 是：直接展示编号清单（步骤 1）

在空目录里从零创建新项目/新教材？
  → 是：init-textbook.md（0 号功能——权威脚手架）

要把书注册进 Google Analytics（GA4 / G-* Measurement ID）？
  → 是：google-analytics.md

要给既有项目加学习图谱查看器？
  → 是：learning-graph-viewer.md

要配置技能使用追踪？
  → 是：skill-tracker.md

想从书本内容【生成】高质量封面图提示词？
  → 是：cover-image-generator.md（默认产出提示词；API/ChatGPT 自动生成仅在明确要求时运行）

要【手工】做封面图，或配置带社交元数据的主页？
  → 是：home-page-template.md

要安装社交分享预览 hook（og:* / twitter:* meta 标签），
或修复 bk-check-social-cover 运行失败？
  → 是：social-media-preview.md（免 Cairo；这是默认方案）

想生成展示已实现功能的清单？
  → 是：feature-checklist-generator.md

想从吉祥物 neutral.png 自动【生成】favicon.ico？
  → 是：favicon-generator.md（用 Python/Pillow 运行 scripts/generate-favicon.py）

想加品牌元素（logo、favicon、封面图）？
  → 是：mkdocs-features.md（品牌功能一节）

想加引导学生学习的吉祥物（教学代理）？
  → 是：learning-mascot.md

想生成教师指南？
  → 是：instructors-guide.md

想要带吉祥物的自定义 404 错误页？
  → 是：custom-404-page.md

想在导航侧栏加彩色状态圆点追踪页面生命周期？
  → 是：document-status.md

想要 GitHub Projects 看板追踪教材开发？
  → 是：kanban-board.md

想给既有章节补装吉祥物提示块？
  → 是：mascot-chapter-updater.md

想生成含作者简介与引用方式的专业 about 页？
  → 是：about-page.md

想安装幻灯片查看器并为章节生成幻灯片？
  → 是：slide-generator.md

想分析各章阅读水平一致性？
  → 是：reading-level-analysis.md

想一次过生成全部补充内容（术语表、FAQ、各章测验与参考文献、
教材度量、图示报告、about 页、着陆页、README）？
  → 是：supplementary-content-generator.md

只想生成教材度量（章节、概念、字数/页数、
图示/MicroSim/测验总数）到 book-metrics.md 与 chapter-metrics.md？
  → 是：book-metrics.md

想警告那些对 Zensical 构建部署的书误运行 `mkdocs serve` 的人
（MkDocs 到 Zensical 的过渡护栏）？
  → 是：mkdocs-serve-warning.md（仅当本书用 Zensical 部署；不清楚就问）

想加某项具体功能（公式、测验、反馈等）？
  → 是：mkdocs-features.md（然后按具体功能说明操作）
```

## 步骤 2：加载匹配到的指南

从 `references/` 读取对应的指南文件，按其安装工作流执行。

## 步骤 3：执行安装

每份指南包含：
1. 前置条件与要求
2. 分步安装命令
3. 配置选项
4. 验证步骤
5. 排错提示

## 可用安装指南

### mkdocs-features.md

**用途：** 全部 MkDocs 功能增强的详细配置

**包含：** 帮助输出中 2-24 号功能的完整配置片段，包括：
- mkdocs.yml 的 YAML
- 需要创建的 JavaScript 文件
- 需要创建的 CSS 文件
- 使用示例

**何时使用：**
- 用户按编号或名称选择功能
- 用户要某项功能的详细配置
- 用户有一份最小 mkdocs.yml，想丰富它

### init-textbook.md（0 号功能）

**用途：** 在空目录中搭建全新智能教材的权威脚手架

**创建：**
- mkdocs.yml（侧边导航、搜索、admonition、arithmatex、exclude_docs、schema URI）
- docs/ 树：index、about、course-description、contact、license、chapters/、learning-graph/、sims/、css/extra.css、img/（封面 + 许可证徽章）
- CONTENT-GENERATION-GUIDE.md（CIS 驱动的字数目标、反注水规则、MicroSim 与 Markdown 规则——供 book-chapter-generator 与 chapter-content-generator 读取）
- plugins/social_override.py hook（逐页覆盖 og:/twitter: 图片）
- .gitignore 与 VS Code 工作区文件
- MicroSim 状态指示管线（scaffold/built/approved）

**模板：** 单一权威副本在 `assets/init-textbook/`

**前置条件：**
- 空（或接近空）的项目目录——拒绝覆盖 mkdocs.yml、docs/index.md 或 docs/license.md

### google-analytics.md（25 号功能）

**用途：** 把书注册为 Google Analytics 4 媒体资源，并把 Measurement ID 接进 mkdocs.yml

**创建：**
- GA4 媒体资源 + Web 数据流（通过 Claude in Chrome）
- mkdocs.yml 中写入 G-* Measurement ID 的 `extra.analytics` 块
- 构建期标签验证、提交与 gh-deploy

**前置条件：**
- Claude in Chrome 扩展已连接；用户已登录 Google Analytics
- mkdocs.yml 中已设 site_url

### learning-graph-viewer.md

**用途：** 给既有教材添加交互式学习图谱浏览

**创建：**
- 交互式 vis-network 图谱查看器
- 搜索、过滤与统计功能
- 与既有 learning-graph.json 的集成

**前置条件：**
- 既有 MkDocs 项目
- learning-graph.json 文件存在

### skill-tracker.md

**用途：** 配置 Claude Code 技能使用追踪

**创建：**
- 追踪技能调用的 hook 脚本
- 活动日志目录结构
- 用量分析报告脚本

**前置条件：**
- 已安装 Claude Code
- 存在 ~/.claude 目录

### social-media-preview.md

**用途：** 安装免 Cairo 的 MkDocs hook，在每个页面输出 Open Graph 与 Twitter Card meta 标签

**创建：**
- `plugins/social_override.py`——`on_post_page` hook，注入/替换 `og:title`、`og:description`、`og:image`、`og:type`、`og:url` 与 `twitter:*` 标签
- mkdocs.yml 中引用该文件的 `hooks:` 块

**特性：**
- 从每页 frontmatter 读 `image:`、`title:`、`description:`；缺省回退到 `img/cover.png` 与全站值
- 用 `site_url` 拼接图片路径输出绝对 `og:image` URL（让爬虫与 `bk-check-social-cover` 能 HEAD 请求）
- 无需 `mkdocs-material[imaging]` / Cairo——常见情况的默认方案
- 与 Cairo 存在时的完整 `social` 插件兼容：把它自动生成的 `/assets/images/social/...` URL 替换为声明的 `cover.png`
- 用 `~/.local/bin/bk-check-social-cover` 验证（它强制 `og:image` 的 basename 为 `cover.png` 且图片可达）

**前置条件：**
- 既有 MkDocs Material 项目，已设 `site_url:`
- `docs/img/cover.png`（缺失则先走 `cover-image-generator.md` 或 `home-page-template.md`）
- 主页 frontmatter 含 `title:` 与 `description:`（通常来自 `home-page-template.md`）

### home-page-template.md

**用途：** 创建带封面图与社交媒体优化的专业主页

**创建：**
- 带正确 frontmatter 元数据的 docs/index.md
- 蒙太奇背景封面的 AI 生图提示词
- Open Graph 与 Twitter Card 配置

**特性：**
- 封面图设计指引（1.91:1 宽高比）
- 按主题给蒙太奇元素建议
- 社交媒体预览优化
- 各种书籍主题的示例提示词

**前置条件：**
- 既有 MkDocs 项目
- 可用的 AI 生图工具（DALL-E、Midjourney 等）

### learning-mascot.md

**用途：** 设计并实现引导学生学习教材的教学代理（学习吉祥物）

**创建：**
- 角色设计（名字、物种、外观、性格、口头禅）
- 保持姿态一致的 AI 生图提示词
- 三种实现方式：内联图片、自定义 CSS 提示块、或 JavaScript 自动侦测
- 带自动透明通道/4px 裁边检查与全部七种提示块预览的吉祥物测试页
- CONTENT-GENERATION-GUIDE.md 中的角色写作规范，其中的摆放规则渲染自 `references/mascot-placement-rules.md`

**特性：**
- 按学科给吉祥物建议并附理由
- 七种标准姿态（neutral、welcome、thinking、tip、warning、encouraging、celebration）
- 三个复杂度层级的实现方式
- 防止滥用的克制指引

**前置条件：**
- 既有 MkDocs Material 项目
- 可用的 AI 生图工具（DALL-E、Midjourney 等）

### instructors-guide.md

**用途：** 为教材生成完整的教师指南

**创建：**
- `docs/teachers-guide/index.md`（大学层次用 `docs/instructors-guide/index.md`）
- mkdocs.yml 中的导航条目

**特性：**
- 讲解智能教材的五个等级
- 章节、MicroSim、术语表、FAQ、测验与参考文献的详细使用说明
- 课堂建议（课前/课中/课后、节奏把控）
- 面向外部 LMS 页面的 MicroSim iframe 嵌入指南
- 用大白话讲解知识共享许可（能做什么/不能做什么）
- 分步自定义指南（fork、clone、改颜色/标题/logo、部署）
- Google Analytics 配置说明
- xAPI/LRS 概览，含 FERPA/COPPA/GDPR 合规警告
- 面向教师的学习图谱使用技巧
- 教学代理（吉祥物）文档（如有吉祥物）
- 所有专业术语先定义后使用——不假定任何先验知识

**前置条件：**
- 既有 MkDocs Material 项目
- 至少已写好部分章节内容

### custom-404-page.md

**用途：** 添加以项目学习吉祥物为主角的自定义 404 错误页

**创建：**
- `overrides/404.html`——继承 Material 基础主题的 Jinja2 模板，含吉祥物图片、友好提示与回首页链接
- mkdocs.yml 中 `custom_dir` 与 `static_templates` 的更新

**特性：**
- 使用吉祥物的 warning 姿态（或其他姿态）居中展示
- 继承 Material 主题的完整站点导航（页头、侧栏、页脚）
- 提示语可定制，与吉祥物的性格与口吻一致
- 绝对图片路径，任何 URL 深度下 404 都正常

**前置条件：**
- 既有 MkDocs Material 项目
- `docs/img/mascot/` 中已有吉祥物图片（没有则先走 `learning-mascot.md`）

### document-status.md

**用途：** 在导航侧栏为每页加彩色状态圆点，追踪页面生命周期状态

**创建：**
- mkdocs.yml 中的 `extra.status` 配置
- extra.css 中彩色状态圆点的 CSS 规则
- 各页面 frontmatter 的 `status:` 字段

**特性：**
- 三态工作流（spec-complete → prototype → ready-for-testing）
- 导航侧栏可见的彩色圆点（红、橙、绿）
- 悬停显示提示文字
- 状态码可按任意工作流自定义

**前置条件：**
- 既有 MkDocs Material 项目
- `extra_css` 中引用了自定义 CSS 文件

### reading-level-analysis.md

**用途：** 分析全部章节的 Flesch-Kincaid 年级水平一致性

**创建：**
- `docs/learning-graph/chapter-reading-levels.md`——逐章阅读水平报告

**使用脚本：** `scripts/analyze-reading-levels.py`

**特性：**
- 剥除 Markdown/HTML 格式，只分析纯正文
- 逐章表格：FK 年级与说明
- 汇总统计（均值、中位数、极差、标准差）
- 解读差异是否有意义的说明小节
- 区分词汇导致的分数虚高与真实难度差异

**前置条件：**
- 既有 MkDocs 项目，章节位于 `docs/chapters/`
- Python `textstat` 库（`pip install textstat`）

### book-metrics.md

**用途：** 为智能教材生成全书级与逐章的完整度量

**创建：**
- `docs/learning-graph/book-metrics.md`——书籍构成 + 面向学生的内容度量表
- `docs/learning-graph/chapter-metrics.md`——逐章分解
- 把全书总计的 `metrics` 块合并进 `docs/learning-graph/book-metadata.json`（作者字段保留）

**使用脚本：** `bk-generate-book-metrics`（解析 `$BK_HOME/src/book-metrics/book-metrics.py`）；回退方案 `python3 "$BK_HOME/src/book-metrics/book-metrics.py" docs`

**特性：**
- 追踪全部 12 项书籍构成元素，标 Required/Recommended/Optional 状态
- 统计概念、章节、MicroSim、故事、术语、FAQ、测验题、参考文献、图示、公式、字数、链接、附录、吉祥物姿态
- 估算等效印刷页数并记录开发阶段
- 产出 intelligent-textbooks 案例研究索引所展示的各项总数

**前置条件：**
- 既有 MkDocs 项目，章节位于 `docs/chapters/`
- 已导出 `$BK_HOME` 且 `bk-generate-book-metrics` 在 `$PATH` 上

### favicon-generator.md

**用途：** 从吉祥物的 `neutral.png` 生成符合 Web 标准的多分辨率 `favicon.ico`

**创建：**
- `docs/img/favicon.ico`——多分辨率图标（16、32、48、64、128、256 px）嵌入单个 `.ico` 文件

**使用脚本：** `scripts/generate-favicon.py`

**工作原理：**
- 侦测非透明像素的包围盒（裁掉不可见边距）
- 把可见内容居中放在方形画布上，边距可配
- 用 Lanczos 重采样逐级缩到各 favicon 尺寸
- 支持透明或白色背景画布

**前置条件：**
- 吉祥物图片位于 `docs/img/mascot/neutral.png`（图片不必是方形）
- Python `Pillow` 库（`pip install Pillow`）

### cover-image-generator.md

**用途：** 在 `docs/img/cover-image-prompt.md` 精心打造一条高质量封面图提示词，取材自书名、课程描述、概念清单、吉祥物与 MicroSim 截图。图片自动生成是可选项，仅在用户明确要求时运行。

**提供：**
- 从书本自身内容挑选 6-10 个蒙太奇概念的指引
- 覆盖主题/语气、标题字体、蒙太奇、吉祥物、风格/色彩与避雷项的详细提示词模板
- 推荐的人工审阅回路：把提示词贴进文生图工具，比较草稿，迭代提示词后再定稿
- 可选的自动化路径（API、浏览器自动化或本地提示词）与排错——仅在明确要求时使用

**前置条件：**
- 既有 MkDocs 项目，含 mkdocs.yml
- docs/course-description.md 中有书本内容描述
- 仅当要求自动生成时：OpenAI API 计费、ChatGPT Pro 订阅或免费 AI 生图工具

### kanban-board.md

**用途：** 创建用于追踪教材开发进度的 GitHub Projects (v2) 看板

**创建：**
- Board（Kanban）布局的 GitHub Projects 看板
- 优先级字段（高/中/低）
- 13 项标准教材里程碑草稿
- `docs/project-management.md`，含列说明与工作流指南
- README 中关于看板的小节

**特性：**
- 通过 `gh project` CLI 命令自动搭建
- 自动把关联项目链到仓库
- 预填与教材开发 12 步工作流对应的里程碑
- `gh` 命令失败时的手工搭建回退说明

**前置条件：**
- 已安装并完成认证的 `gh` CLI
- GitHub token 具备 `project` scope（`gh auth refresh -s project`）
- 既有 MkDocs 项目，含 mkdocs.yml

### supplementary-content-generator.md

**用途：** 在一个协调工作流中为智能教材生成全部标准补充内容

**产出（按执行顺序）：**
- `docs/about.md`——专业 about 页（经 `about-page.md` 参考）
- `docs/glossary.md`——符合 ISO 11179 的术语表（经 `glossary-generator` 技能）
- `docs/faq.md`——不少于 30 题的 FAQ（经 `faq-generator` 技能）
- `docs/chapters/*/quiz.md`——各章测验（经 `quiz-generator` 技能）
- `docs/chapters/*/references.md`——各章参考文献（经 `reference-generator` 技能）
- `docs/img/cover.png`——书籍封面图 + 社交预览 hook（经 `cover-image-generator.md` + `social-media-preview.md`）
- 教材度量报告（经 `bk-generate-book-metrics` 脚本）
- 图示报告（经 `bk-diagram-reports` 脚本）
- `README.md`——在度量之后生成、可嵌入内容统计的 GitHub 向 README（经 `book-publisher` 的 readme 路由——技能）
- `docs/index.md`——主着陆页最后生成，以便链接以上全部（经 `home-page-template.md`）
- 为所有生成文件更新的 mkdocs.yml 导航条目

**执行顺序：** about → 术语表 → FAQ → 测验 → 参考文献 → 封面图 → 度量 → 图示报告 → README → 着陆页 → 导航更新 → 验证

**模型指引：** 所有文本生成步骤用 Sonnet。此工作流中创建的任何 MicroSim 必须使用 `claude-opus-4-7` 并开 `high` thinking——Opus 在 MicroSim 所需的编码与空间推理上显著更强。

**前置条件：**
- 既有 MkDocs 项目，含 `mkdocs.yml`
- `docs/course-description.md` 存在
- `docs/learning-graph/learning-graph.json` 存在
- `docs/chapters/` 下至少有一章

### slide-generator.md

**用途：** 把 slide-viewer MicroSim 装进智能教材项目，并为指定章节生成演示风格的 `slides.md` 幻灯片

**创建：**
- `docs/sims/slide-viewer/`——查看器外壳（main.html、script.js、local.css、index.md）：抓取任意渲染后的 MkDocs 页面 URL，按 `<hr>` 元素切分内容，一次渲染一页幻灯片，支持键盘 + 按钮导航
- `docs/chapters/<slug>/slides.md`——每章：标题页、以 `---` 分隔的内容页、提取练习、过渡、庆祝收尾
- 每章 `index.md` 与其 `slides.md` 顶部的三按钮导航条（`Content`、`Slides`、`Slides in Viewer`）
- mkdocs.yml 导航重构：带幻灯片的章节拥有 `Content` / `Slides` 子条目

**特性：**
- 查看器读取 MkDocs 渲染后的 HTML（绝不读原始 `.md`——MkDocs 不直接提供 `.md`）
- 吉祥物集成：每页 neutral 姿态，最后一页 celebration 姿态（存在 `docs/img/mascot/neutral.png` 与 `celebration.png` 时使用；否则静默缺席）
- 首页/末页跳转按钮、`Home`/`End` 键、全屏、目录浮层
- 按项目语气/风格规则把章节 `index.md` 蒸馏为 15-28 页幻灯片

**前置条件：**
- 既有 MkDocs Material 项目，`docs/chapters/` 已有内容
- 章节 `index.md` 有真实内容（不只是脚手架）——生成前指南会检查行数
- 可选：经 `learning-mascot.md` 安装吉祥物

### mascot-placement-rules.md

**用途：** 吉祥物何时可出现、出现频率、哪个姿态承担哪种教学任务的单一权威来源

**使用方：** `learning-mascot.md`、`mascot-chapter-updater.md`、`instructors-guide.md` 与 `chapter-content-generator` 技能——全部按路径引用本文件，不复述其规则

**包含：**
- 提示块格式，以及 Markdown 与裸 HTML 图片路径规则
- 摆放表（情境 → 姿态 → 每章数量）
- 硬上限：不背靠背摆放、一个 welcome 和一个 celebration、正文 1-3 句；总数是按章节概念数缩放的非正式指引（约每 2 个概念 1 个提示块），并按读者年龄调整
- 全部七种姿态各自的教学设计规则
- 一次性的第 1 章自我介绍模式
- 生成后验证规则

**重要：** 绝不把本文件的表格或数字手工复制进其他技能或书本。技能按路径引用它；书本经 `scripts/render-mascot-guide.py` 获得渲染副本，拼接在哨兵注释之间以便重新生成。从仓库根运行 `scripts/bk-check-mascot-rules` 可验证没有复述混入。

### mascot-chapter-updater.md

**用途：** 按权威的 `references/mascot-placement-rules.md`，把吉祥物提示块补装到既有章节 Markdown 的正确位置

**创建：**
- 只对指定章节文件的就地编辑（不新建文件）
- 编辑前展示给用户确认的摆放计划

**特性：**
- LLM 驱动的语义摆放工作流（不做正则自动插入）
- 强制执行 `references/mascot-placement-rules.md` 定义的硬上限（总数上限、最多一个 welcome 和一个 celebration、不背靠背）
- 针对目录式 URL 渲染的图片路径指引（从渲染页往回数 `../`）
- 语气与正文规则：1-3 句、保持角色、针对本章内容
- 用 `scripts/validate-chapter-mascots.py` 验证，标记数量超限、背靠背、图片缺失与正文过长

**前置条件：**
- 吉祥物图片在 `docs/img/mascot/` 或 `docs/img/mascots/`
- `docs/css/mascot.css` 已加载且吉祥物测试页渲染正常
- 以绝对路径指定具体章节文件

### mkdocs-serve-warning.md

**用途：** 安装一个 MkDocs 专用 hook：当用 Zensical 构建部署的书被 `mkdocs serve` 预览时记录警告——在 MkDocs 到 Zensical 的过渡期，推荐每本 Zensical 设计的书都装（此时 MkDocs 仍与 Zensical 并存安装）

**创建：**
- `hooks/mkdocs_serve_warning.py`——从 `assets/mkdocs-serve-warning/mkdocs_serve_warning.py` 逐字复制
- mkdocs.yml 中的一条 `hooks:` 条目（追加到既有列表，绝不新建第二个 `hooks:` 键——重复键会静默丢弃第一个列表）
- 仅当项目禁止使用 `hooks:` 时，加一条 AGENTS.md 例外说明

**特性：**
- 解释预览为什么看起来不对：MkDocs 不改写相对 `<iframe src>` 路径，顶层页面嵌入的 MicroSim 会显示为破框（`zensical build` 与 `zensical serve` 都会改写）
- Zensical 从不加载 `hooks:` 条目，同一份 `mkdocs.yml` 对两个构建器都有效
- 只在 `serve` 时警告，`build` 从不，因此 `mkdocs build --strict` 仍通过；也能捕获 `mkdocs serve --clean`
- 不启动服务器即可验证：模拟 MkDocs 的启动事件

**前置条件：**
- 本书用 Zensical 构建部署（不要装在 MkDocs 部署的书上——那条消息会是假的）
- `mkdocs.yml` 与 MkDocs 1.4 或更新版本

## 示例

### 示例 1：请求帮助
**用户：** "book-installer help"
**路由：** 关键词 "help" → 展示编号清单
**动作：** 展示编号功能清单（步骤 1），然后等用户选择功能

### 示例 2：添加具体功能
**用户：** "Add math equation support to my book"
**路由：** 关键词 "math" → `references/mkdocs-features.md`
**动作：** 加载 mkdocs-features.md，找到 Math Equations 一节，应用配置

### 示例 2b：按编号选择
**用户：** "5"
**路由：** 帮助清单后的编号选择 → `references/mkdocs-features.md`
**动作：** 加载 mkdocs-features.md，找到 Math Equations（第 5 项），应用配置

### 示例 2c：简单模板
**用户：** "1"
**路由：** 编号 1 → `references/init-textbook.md`（权威脚手架）
**动作：** 加载 init-textbook.md，搭建起始配置与 docs/ 树

### 示例 3：新教材项目
**用户：** "I want to create a new intelligent textbook about machine learning"（空目录）
**路由：** 关键词 "create"、"new"、"textbook" → `references/init-textbook.md`
**动作：** 读 init-textbook.md，收集 SITE_NAME/SITE_DESCRIPTION，确认替换表，从 `assets/init-textbook/` 搭建

### 示例 3b：注册 Google Analytics
**用户：** "Add Google Analytics to this book" 或 "25"
**路由：** 关键词 "google analytics"、"GA4"、"25" → `references/google-analytics.md`
**动作：** 读 google-analytics.md；创建 GA4 媒体资源，把 G-* ID 写入 mkdocs.yml 的 extra.analytics，验证标签，部署

### 示例 4：添加图谱查看器
**用户：** "Add an interactive viewer for the learning graph"
**路由：** 关键词 "viewer"、"learning graph"、"interactive" → `references/learning-graph-viewer.md`
**动作：** 读 learning-graph-viewer.md 并按其工作流执行

### 示例 5：追踪技能用量
**用户：** "I want to track which skills I use most often"
**路由：** 关键词 "track"、"skills"、"usage" → `references/skill-tracker.md`
**动作：** 读 skill-tracker.md 并按其工作流执行

### 示例 6：创建封面图
**用户：** "Help me create a cover image for my textbook"
**路由：** 关键词 "cover image"、"textbook" → `references/home-page-template.md`
**动作：** 读 home-page-template.md 并按其工作流执行

### 示例 7：配置带社交分享的主页
**用户：** "I need to add og:image metadata to my home page"
**路由：** 关键词 "og:image"、"home page" → `references/home-page-template.md`
**动作：** 读 home-page-template.md 并按其工作流执行

### 示例 8：生成封面图提示词
**用户：** "generate cover image" 或 "book-installer generate cover image"
**路由：** 关键词 "generate cover image" → `references/cover-image-generator.md`
**动作：** 读 cover-image-generator.md，收集素材（书名、课程描述、概念清单、吉祥物、MicroSim 截图），写出 `docs/img/cover-image-prompt.md`，建议用户贴进文生图工具并审阅草稿。仅当用户明确要求自动生成时，才询问 API key/ChatGPT Pro/macOS 并运行 `generate-cover.sh`

### 示例 9：添加学习吉祥物
**用户：** "I want to add a mascot character to my math textbook"
**路由：** 关键词 "mascot"、"character" → `references/learning-mascot.md`
**动作：** 读 learning-mascot.md，引导用户完成角色设计，生成 AI 生图提示词，按选定方式实现（内联、CSS 提示块或 JS 侦测）

### 示例 10：生成功能清单
**用户：** "generate a feature checklist" 或 "what features do I have"
**路由：** 关键词 "feature checklist" → `references/feature-checklist-generator.md`
**动作：** 读 feature-checklist-generator.md，运行检测脚本，生成带检测状态的 docs/feature-checklist.md

### 示例 11：生成教师指南
**用户：** "add a teacher's guide" 或 "create instructor guide"
**路由：** 关键词 "teacher guide"、"instructor guide" → `references/instructors-guide.md`
**动作：** 读 instructors-guide.md，从 mkdocs.yml/course-description.md/CLAUDE.md 收集项目变量，代入全部变量生成指南，加入导航

### 示例 12：创建看板
**用户：** "set up a kanban board for my textbook" 或 "create a project board"
**路由：** 关键词 "kanban"、"project board" → `references/kanban-board.md`
**动作：** 读 kanban-board.md，验证 gh 认证具备 project scope，创建 GitHub Project，关联仓库，填入里程碑，创建 docs/project-management.md，更新导航与 README

### 示例 13：生成 About 页
**用户：** "create an about page" 或 "add about.md with author bio and citations"
**路由：** 关键词 "about page"、"about"、"author bio"、"citation" → `references/about-page.md`
**动作：** 读 about-page.md，从 mkdocs.yml/course-description.md 收集项目变量，生成含全部小节（缘起、作者简介、引用格式）的 docs/about.md，加入导航

### 示例 14：给既有章节加吉祥物
**用户：** "add Sparky admonitions to chapter 2" 或 "place the mascot in docs/chapters/02-ohms-law/index.md"
**路由：** 关键词 "mascot chapter"、"place mascot"、"add mascot to chapter" → `references/mascot-chapter-updater.md`
**动作：** 读 mascot-chapter-updater.md，通览章节，提出带行号的摆放计划，等用户确认后应用编辑，运行 validate-chapter-mascots.py，并处理所有标记

### 示例 15：从吉祥物生成 Favicon
**用户：** "generate favicon from mascot" 或 "create favicon.ico from neutral.png"
**路由：** 关键词 "generate favicon"、"mascot favicon"、"favicon from mascot" → `references/favicon-generator.md`
**动作：** 读 favicon-generator.md，确认 `docs/img/mascot/neutral.png` 存在且已装 Pillow，从项目根运行 `scripts/generate-favicon.py`，然后把 mkdocs.yml 的 `theme.favicon` 更新为 `img/favicon.ico`

### 示例 15b：安装社交分享预览 Hook
**用户：** "add the social media preview mkdocs hook" 或 "my bk-check-social-cover is failing" 或 "install og:image meta tags"
**路由：** 关键词 "social media preview"、"og:image"、"bk-check-social-cover"、"social hook" → `references/social-media-preview.md`
**动作：** 读 social-media-preview.md，按参考中的确切代码在项目根创建 `plugins/social_override.py`，在 `mkdocs.yml` 加顶层 `hooks: - plugins/social_override.py` 块，运行 `mkdocs build`，验证九个 og:* / twitter:* meta 标签出现在 `site/index.html` 中，然后对部署 URL 或在 `/<project>/` 下暂存构建的本地服务器运行 `bk-check-social-cover`

### 示例 17：生成全部补充内容
**用户：** "generate all supplementary content" 或 "complete the book" 或 "39"
**路由：** 关键词 "supplementary content"、"complete the book"、"39" → `references/supplementary-content-generator.md`
**动作：** 读 supplementary-content-generator.md。先盘点既有文件。然后按序执行步骤 2-12：生成 about 页、着陆页、README、术语表、FAQ、各章测验与参考文献，运行 `bk-generate-book-metrics` 与 `bk-diagram-reports`，更新 mkdocs.yml 导航，运行验证 bash 检查。报告哪些文件已创建、跳过或缺失。

### 示例 16：安装幻灯片查看器并生成章节幻灯片
**用户：** "install the slide viewer and make slides for chapters 1 and 2" 或 "generate slides for chapter 3"
**路由：** 关键词 "slide"、"slides"、"slide viewer"、"generate slides"、"slide deck" → `references/slide-generator.md`
**动作：** 读 slide-generator.md，把 slide-viewer 资产复制进 docs/sims/slide-viewer/，询问为哪些章节生成幻灯片，为每章创建 slides.md（标题 + 以 `---` 分隔的内容页 + 提取练习 + 过渡 + 庆祝），在每章 index.md 顶部加三按钮导航条，把该章的 mkdocs.yml 条目重构为 Content/Slides 子条目，并把幻灯片链接追加到查看器的 index.md

### 示例 18：生成教材度量
**用户：** "generate book metrics" 或 "how many words/chapters/MicroSims does this book have" 或 "40"
**路由：** 关键词 "book metrics"、"generate metrics"、"metrics report"、"40" → `references/book-metrics.md`
**动作：** 读 book-metrics.md，从项目根运行 `bk-generate-book-metrics`（或回退 `python3 "$BK_HOME/src/book-metrics/book-metrics.py" docs`），确认 `book-metrics.md`、`chapter-metrics.md` 与 `book-metadata.json` 中的 `metrics` 块已写出；若不在，则把两份报告加进 `mkdocs.yml` 的 Learning Graph 导航

### 示例 19：安装 MkDocs-Serve 警告
**用户：** "warn people who run mkdocs serve" 或 "add the zensical transition guard" 或 "my MicroSim iframes are broken under mkdocs serve" 或 "41"
**路由：** 关键词 "mkdocs serve warning"、"zensical transition"、"transition guard"、"41" → `references/mkdocs-serve-warning.md`
**动作：** 确认本书用 Zensical 构建部署（不清楚就问；若用 MkDocs 部署则停止）。把 `assets/mkdocs-serve-warning/mkdocs_serve_warning.py` 复制到 `hooks/`，把 `hooks/mkdocs_serve_warning.py` 追加到 `mkdocs.yml` 既有 `hooks:` 列表（仅当缺失时才创建该键），然后**不启动** `mkdocs serve` 进行验证：`mkdocs build --strict` 以 0 退出且无警告；模拟 `on_startup(command="serve")` 会打印警告。请用户在自己的终端里运行一次 `mkdocs serve` 实际查看。

## 常见工作流

### 完整项目搭建

全新项目通常按以下顺序安装：
1. `init-textbook.md`——搭建项目结构（0 号功能）
2. `cover-image-generator.md`——生成高质量封面图提示词（自动生成可选，按请求）
3. `home-page-template.md`——配置带封面图元数据的主页
4. `social-media-preview.md`——安装 og:* / twitter:* meta 标签 hook（用 `bk-check-social-cover` 验证）
5. `learning-graph-viewer.md`——添加图谱可视化（学习图谱存在之后）
6. `skill-tracker.md`——启用用量分析（可选）
7. `google-analytics.md`——把书注册进 GA4（25 号功能，可选）
8. `supplementary-content-generator.md`——章节就绪后一次过生成全部补充内容（术语表、FAQ、测验、参考文献、度量、about、README）
9. `mkdocs-serve-warning.md`——仅当本书用 Zensical 构建部署：警告误运行 `mkdocs serve` 的人（41 号功能；过渡期推荐每本 Zensical 设计的书都装，最好紧跟第 4 步之后，使其并入既有 `hooks:` 列表）

### 验证命令

任何安装完成后，用以下命令验证：
```bash
# MkDocs 项目
mkdocs serve
# 访问 http://127.0.0.1:8000/[project-name]/

# 技能追踪器
cat ~/.claude/activity-logs/skill-usage.jsonl | tail -5
```

---

## 来源与许可

本技能收录自上游仓库 [dmccreary/ibook-skills](https://github.com/dmccreary/ibook-skills)，
2026-10-19 补录（因 `question-writing` 等五件的 `$BK_HOME` 引用指向本技能）。
上游仓库**无 LICENSE 文件**，依法默认保留全部权利；本仓库收录其内容副本**未获授权**，
复用、分发或商用前请先联系原作者取得许可。详见仓库根目录 `THIRD_PARTY_NOTICES.md`。

收录时做过的修改：frontmatter `description` 改写为中文并补充 Triggers；
删除 frontmatter 中上游自称的 `license: CC BY-NC 4.0` 字段（与「仓库无 LICENSE」矛盾）；
正文译为简体中文（路由表的触发关键词保留英文原文，因为它们是实际匹配的用户输入）；
代码块、命令、文件路径与模板保持原文。`references/` 下除 `mkdocs-nav-editing.md` 外，
其余参考文档与 `assets/` 模板本批次保留英文原文，后续批次翻译。
