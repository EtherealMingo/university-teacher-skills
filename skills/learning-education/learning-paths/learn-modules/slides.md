# 幻灯片模块

*当学习者在会话中输入 `/learn slides` 或 "slides" 时加载。切换到逐字幻灯片朗读模式。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

---

## 概述

幻灯片模式逐字朗读课程脚本——不用 Journey 格式、不做改写。学习者听到的幻灯片与原文一字不差，必要时翻译为 `session.language`。练习仍由导师撰写（不是从练习文件中逐字照搬）。

---

## 步骤 1——解析课节

如果指定了课号（例如 `/learn slides 3.1`），加载该课的脚本文件。

如果没有给课号，使用会话中已加载的当前课。如果没有激活的课，询问学习者想要哪一课。

用与 `teaching.md` 相同的优先级解析脚本路径：
1. 先查项目根目录的 `./lessons/`
2. 回退到设置中的 `course.path`

按 `[מעבר שקף]` 切分脚本。

---

## 步骤 2——宣告模式

告诉学习者：
> "切换到幻灯片模式。我会逐字朗读每张幻灯片。说 **next** 前进，说 **stop slides** 返回教学模式，或说 **exercises** 获取本课练习。"

---

## 步骤 3——启动查看器

进入幻灯片模式时，启动幻灯片服务器并生成 HTML 查看器：

1. **启动服务器**（如果 7823 端口还没有在跑）。脚本路径相对于仓库根目录（会话期间 `$PWD` 即项目目录）：
   ```powershell
   Start-Process powershell -ArgumentList "-NoProfile -File `"$PWD\.claude\scripts\slide-server.ps1`"" -WindowStyle Normal
   Start-Sleep -Seconds 2
   ```

2. **解析课节在磁盘上的绝对路径**——即步骤 1 解析出的课节目录（在 `course.path` 下）。查看器预期该课节目录内有两个可选的资产子目录：
   - 幻灯片图片：`[LESSON_DIR]\digital-course-screenshots\`
   - TTS 脚本：`[LESSON_DIR]\digital-course-tts-scripts\`

   这些资产目录只随部分课程提供。如果当前课程的课节两个目录都没有，跳过查看器启动（步骤 3），改为在聊天中逐字朗读脚本文本。

3. **生成并打开查看器**：
   ```powershell
   & "$PWD\.claude\scripts\generate-slideshow.ps1" -LessonPath "ABSOLUTE_LESSON_PATH"
   Start-Process "$env:TEMP\tov_slideshow.html"
   ```

---

## 步骤 4——查看器已启动——保持安静

**查看器打开后，停止生成幻灯片内容。查看器完全接管 TTS 和导航。Claude 每张幻灯片的输出 = 0 token。**

告诉学习者：
> "查看器已打开。按 **A**（或 ⏭ 自动按钮）启动手动自动播放。← / → 手动翻页。P 暂停。"

然后**安静等待**学习者说话（例如 "stop slides"、一个问题、"exercises"）。

**不要：**
- 打出幻灯片内容
- 对每张幻灯片调用 `Invoke-RestMethod`——查看器会在每次翻页时自动调用 `postSlide()`
- 数幻灯片或播报进度
- 在学习者开口之前做任何事

**手动模式**（学习者没开自动）：学习者在查看器里用键盘/点击操作，TTS 通过查看器内部的 `postSlide()` 自动触发。

**自动模式**（学习者按了 A 或 Auto 按钮）：查看器在 `speaking→idle` 的 TTS 状态转换时自动翻页——完全免动手，0 Claude 参与。

**不要**套用 Journey 格式。**不要**在幻灯片之间问思考题。

---

## 步骤 4——练习

当学习者说 **exercises** 时：
- 不要逐字照读练习文件
- 基于到目前为止已讲过的幻灯片内容，撰写全新的互动练习
- 遵循练习设计规则：大多数练习应能直接通过 Claude 完成；只有当课节主题就是某个外部工具时，才布置该外部工具的练习

---

## 步骤 5——课节结束 / 退出

**当到达最后一张幻灯片时：**
1. 告诉学习者他们已学完本课
2. 问：测验还是小项目？
   - **测验**——就本课内容出 3–5 道题，一次一道
   - **小项目**——2–3 轮提示词就能完成的动手任务（除非课节主题就是某外部工具，否则不用外部工具）
3. **静默保存进度**——写入 `~/skill-tutor-tutorials/progress/lesson-{lesson_number}.md`：
   ```
   # Progress — Lesson X.Y

   **Completed:** [timestamp]
   **Slides covered:** all [N]
   **Summary:** [2–3 sentence summary of what was covered]
   ```
   保留文件中已有的任何内容。不要告诉学习者你正在保存。

**当学习者说 `stop slides` 或 `teaching mode` 时：**
- 保存进度，记录到目前为止已讲过的幻灯片（不写 "all [N]"——记下实际到达的最后一张）
- 回到教学模块（teaching module）中他们离开时的那张幻灯片
- 按之前设置的 `session.detail_level` 继续
