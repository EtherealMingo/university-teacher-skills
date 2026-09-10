# 工作区生命周期

何时阅读本文件：在任何智能体客户端中实现 `study init`、`study start`、
`study break`、`study status`，或恢复一个会话时。

## 事实来源

学习工作区是持久状态的边界。智能体的会话记忆有帮助，
但永远不是权威。

必需的工作区文件：

```
.study-config.json
.fsrs/cards.json
lessons/
practice/
notes/
```

`.study-config.json` 中的 `session_state` 决定恢复行为：

```json
{
  "phase": "idle",
  "pending_action": null,
  "context": null,
  "energy": null,
  "time_budget_minutes": null
}
```

## 阶段（Phases）

| 阶段 | 含义 | 恢复行为 |
|---|---|---|
| `idle` | 没有被中断的课程会话 | 开始全新会话 |
| `teaching` | 智能体写完或正在写课程讲义 | 读取当前课程并继续教学 |
| `practicing` | 用户正在做练习 | 检查 `practice/lesson-NN/` 并询问是继续还是评审 |
| `reviewing` | 智能体正在评审用户的工作 | 读取 git diff 并继续反馈 |
| `review` | 专门的 FSRS 复习会话 | 继续到期卡片的复习 |
| `break` | 会话被有意暂停 | 遵循 `pending_action` |

不要在 `study break` 中把 `phase` 设为 `idle`，那会丢失恢复上下文。

## Init 契约

1. 创建工作区目录并运行 `git init`。
2. 把所选模板复制进工作区。
3. 创建 `lessons/`、`practice/`、`notes/` 和 `.fsrs/`。
4. 如果 `.fsrs/cards.json` 不存在，创建为空的 FSRS 存储。
5. 写入 `.study-config.json`。
6. 以 `[agent] init study workspace` 提交初始状态。

## Start 契约

1. 在做任何其他事之前，先读取 `.study-config.json`。
2. 如果 `session_state.phase != "idle"`，恢复会话而不是开始新工作。
3. 如果是全新会话，递增 `progress.session_count` 并更新
   `progress.last_session`。
4. 按 `references/fsrs-spaced-repetition.md` 运行 FSRS 排期检查。
5. 根据精力和到期卡片，进入复习热身或课程工作。

## 课程完成契约

当一节课通过最终评审：

1. 添加一张 id 为 `lesson-NN` 的 FSRS 卡片。
2. 在 `.study-config.json` 中把该课程标记为 `completed`。
3. 递增 `progress.lessons_completed`。
4. 仅当没有待办工作时，才把 `session_state.phase` 设为 `idle`。
5. 以 `[agent] complete lesson NN` 提交。

## Break 契约

当用户要求停止、暂停或休息：

1. 提交所有有意义的未提交变更。
2. 把 `session_state.phase` 设为当前的非 idle 阶段。
3. 把 `session_state.pending_action` 设为一个具体的下一步。
4. 把 `session_state.context` 设为足够的信息，让另一个智能体
   在没有聊天记录的情况下也能恢复。
5. 如果已知，保留 `session_state.energy` 和 `time_budget_minutes`。
6. 写入 `notes/session-YYYY-MM-DD.md`。
7. 以 `[session] end session N` 提交。

好的 `pending_action` 示例：

- `review practice/lesson-01 implementation`
- `continue explaining Lesson 2 exercise requirements`
- `ask user for FSRS rating for lesson-03`

反面示例：

- `continue`
- `do next`
- `remember what we were doing`

## 恢复契约

恢复会话时：

1. 读取 `.study-config.json`。
2. 读取 `lessons[]` 中列出的当前课程文件，或从
   `progress.current_lesson` 推断。
3. 如果存在，读取最新的 `notes/session-*.md`。
4. 查看 git 状态和相关的练习文件。
5. 明确告诉用户将恢复什么：
   `正在恢复：第 N 课《<标题>》：<pending_action>。`
6. 如果之前记录的精力已过时或缺失，询问当前精力。

## 跨智能体规则

- 绝不让关键状态依赖之前的聊天记录。
- 绝不让课程进度依赖某个特定智能体的记忆层。
- 除 `<skill-dir>` 工具路径外，所有路径都相对于工作区。
- 如果由另一个智能体恢复会话，它不应该需要知道会话是哪个
  智能体创建的。
