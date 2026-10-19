<!-- 权威副本。不要分叉复制进其他技能；按路径引用：
     $BK_HOME/skills/book-installer/references/mkdocs-nav-editing.md

     `$BK_HOME` 指向 ibook-skills 的检出位置，与具体代理无关。
     不要使用 `~/.claude/skills/`、`~/.codex/skills/` 或
     `~/.gemini/antigravity/skills/` 下的路径——那些路径各自绑定某一个
     代理框架，而这些技能要在所有框架上运行。如果 `$BK_HOME` 未设置，
     本文件位于包含调用方技能的技能根目录下的
     `book-installer/references/mkdocs-nav-editing.md`。 -->

# 编辑 mkdocs.yml 导航——权威规则

每个为智能教材新增页面的内容技能（章节、术语表、FAQ、测验、
参考文献、报告）都必须编辑 `mkdocs.yml` 的 `nav:` 小节。这是
共享规则：调用方技能说明要加**什么**，本指南说明**如何**安全地加。

## 核心规则

1. **先读后写。** 编辑前永远先读当前的 `mkdocs.yml`。绝不要依据
   对话早期留下的过时副本编辑。
2. **串行化导航编辑。** 绝不让两个代理（或两个并行任务）同时修改
   `mkdocs.yml`——并发编辑会造成需要人工修复的不一致。如果批量
   工作流并行生成多章/多份测验，先把导航变更收集起来，最后一次性
   应用。
3. **只动你的部分。** 只新增或更新调用方技能拥有的条目；不要删除、
   重排或「顺手清理」其他导航条目。
4. **保持 YAML 结构。** 对齐既有缩进。`nav:` 块是顺序敏感的——
   新条目要插入约定位置（见下方摆放表），而不是盲目追加到末尾。
5. **绝不添加 `navigation.tabs`。** 这些书使用为宽屏横屏优化的
   侧边导航。如果在 `theme.features` 里看到 `navigation.tabs`，
   告诉用户移除它。
6. **编辑后验证。** 确认没有导航条目指向不存在的文件
   （`mkdocs build --strict` 能抓到这类问题）。

## 约定摆放位置

| 产物 | 在导航中的位置 |
|----------|--------------|
| 章节 | `Chapters:` 之下、`List of Chapters: chapters/index.md` 之后 |
| 各章测验 / 参考文献 | 嵌套在该章条目之下 |
| 术语表 | 靠近末尾，License/Contact 之前 |
| FAQ | 靠近末尾，与术语表相邻 |
| 质量报告（测验、FAQ、图示、度量） | `Learning Graph:` 之下 |
| About 页 | 最后 |

## 章节标签约定

导航侧栏很窄。章节标签里**不要**拼出 "Chapter X"——只写编号，
因为列表上方已有 `Chapters:` 标题：

```yaml
nav:
  - Chapters:
    - List of Chapters: chapters/index.md
    - 1. Introduction to AI: chapters/01-intro-ai/index.md
    - 2. Getting Started: chapters/02-getting-started/index.md
```

当一章有了子页面（测验、参考文献），把它们嵌套进去，主页面标签
用 `Content:`（同样，标签里不要带 "Chapter" 前缀）：

```yaml
    - 1. Introduction to AI:
      - Content: chapters/01-intro-ai/index.md
      - Quiz: chapters/01-intro-ai/quiz.md
      - Annotated References: chapters/01-intro-ai/references.md
```

## 导航末尾的产物

```yaml
nav:
  # ... chapters, learning graph ...
  - FAQ: faq.md
  - Glossary: glossary.md
  - License: license.md
  - Contact: contact.md
```

## 学习图谱报告

```yaml
  - Learning Graph:
    # ... existing learning graph pages ...
    - FAQ Quality Report: learning-graph/faq-quality-report.md
    - FAQ Coverage Gaps: learning-graph/faq-coverage-gaps.md
    - Quiz Generation Report: learning-graph/quiz-generation-report.md
    - Diagrams Table: learning-graph/diagram-table.md
    - Diagrams Details: learning-graph/diagram-details.md
```
