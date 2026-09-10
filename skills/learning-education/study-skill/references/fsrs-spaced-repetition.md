# FSRS 间隔重复系统

何时阅读本文件：为已完成课程创建复习项时、在会话开始时呈现复习热身时，或处理 `study review` 命令时。

## FSRS 工作原理（简述）

FSRS 为每个概念（卡片）跟踪三个数值：

- **难度（Difficulty, D）**：记住这个概念的难易程度 [1-10]
- **稳定度（Stability, S）**：回忆概率下降到 90% 所需的天数
- **可提取性（Retrievability, R）**：当前成功回忆的概率 [0-1]

每次复习后，用户对自己的回忆情况进行评分：1=再来一次（忘了）、2=困难、3=良好、4=简单。算法据此更新 D、S、R 并安排下次复习。

稳定度越高 = 复习间隔越长。难度影响稳定度增长的速度。系统会根据用户的实际表现，适应每个概念的真实难度。

## 调用 Go 二进制程序

FSRS 调度器是已安装 study 技能中的一个 Go 二进制程序。由于 `study start`
是在生成的学习工作区中运行的，绝不要通过工作区相对路径
`scripts/fsrs/...` 调用它。应将 `<skill-dir>` 解析为包含
study 技能 `SKILL.md` 的目录，然后用绝对路径或技能相对路径调用构建好的二进制程序：

```bash
FSRS_BIN="<skill-dir>/scripts/fsrs/fsrs"
```

所有命令均向 stdout 输出 JSON。

通过环境变量设置卡片存储路径：
```bash
FSRS_STORE=.fsrs/cards.json
```

### 命令

**课程完成时添加卡片：**
```bash
FSRS_STORE=.fsrs/cards.json "$FSRS_BIN" add "lesson-03" "Goroutine Channels" 3
```
输出：新卡片的 JSON。

**检查有哪些到期待复习：**
```bash
FSRS_STORE=.fsrs/cards.json "$FSRS_BIN" schedule
```
输出：
```json
{
  "due_count": 2,
  "cards": [
    {"id": "lesson-01", "topic": "Goroutines", "lesson_num": 1, "due": "2026-04-04T...", "state": 2, "difficulty": 5.5, "stability": 12.3, "reviews": 4, "lapses": 0, "elapsed_days": 3}
  ]
}
```

**记录一次复习结果：**
```bash
FSRS_STORE=.fsrs/cards.json "$FSRS_BIN" review "lesson-01" 3
```
评分标准：1=再来一次、2=困难、3=良好、4=简单。输出：带有新到期日期的更新后卡片。

**查看全部卡片概览：**
```bash
FSRS_STORE=.fsrs/cards.json "$FSRS_BIN" status
```

## 混合复习模型

### 集成式复习（会话开始时）

1. 运行 `fsrs schedule` 检查到期项
2. 若有到期项：
   - 最多呈现 **3 条**作为热身（限时约 5 分钟）
   - 对每一项，基于课程主题给出回忆提示
   - 请用户回忆该概念（先不要展示答案）
   - 用户作答后，展示课程讲义中的正确答案
   - 询问：“感觉如何？1=完全忘了、2=很难想起、3=记住了、4=很轻松”
   - 运行 `fsrs review <id> <rating>` 记录
3. 若无到期项，直接进入课程

### 独立式复习（`study review`）

1. 运行 `fsrs schedule` 获取全部到期项（不设上限）
2. 按同样的「回忆 → 评分」流程逐条呈现
3. 全部复习完后展示小结：复习了多少条、平均评分
4. 若无到期项：“现在没有到期复习项。下次复习在 N 天后。”

### 复习提示格式

对每张卡片，根据课程讲义创建回忆提示：

```
复习：第 3 课 —— Goroutine Channels

你能解释一下吗：[课程中的关键概念]
- 它是什么？
- 什么场景下会用到它？
- 常见的坑是什么？

想一想，然后告诉我你记得的内容。
```

用户作答后，展示 `lessons/03-*.md` 中的参考答案，并请其自评。

### 无愧疚规则

- 绝不展示连击计数或“距上次复习已过 N 天”
- 绝不因错过复习而让用户愧疚（“你有 15 条过期未复习！”）
- 如果有项目过期，照常呈现即可 —— 排期交给算法处理
- 如果用户在会话开始时跳过复习，静默继续
- 被跳过的项目会留在队列中等待下次
