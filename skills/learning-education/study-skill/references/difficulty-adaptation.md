# 难度自适应

何时阅读本文件：生成新课（以设定合适的深度）时、对练习给出反馈时，或运行定期校准检查时。

## 表现指标

每节课隐式跟踪这些指标 —— 不需要额外向用户提问：

```json
{
  "lesson": 3,
  "metrics": {
    "review_rounds": 2,
    "hints_requested": 1,
    "fsrs_ratings": [3, 4],
    "questions_asked": 3,
    "time_to_complete_minutes": null
  }
}
```

- **review_rounds**：通过前需要返工的反馈轮数。1 = 一次通过。
- **hints_requested**：练习过程中用户说“我卡住了”或“需要帮助”的次数。
- **fsrs_ratings**：该课程概念在复习中出现时的自评回忆质量。
- **questions_asked**：课程中澄清性提问的次数（不是负面信号 —— 好奇是好事，但与提示次数结合时能反映难度）。
- **time_to_complete_minutes**：可选，仅当用户设置了时间预算时记录。

事件发生时，随时更新 `.study-config.json` 中的 `lessons[].metrics`。

## 难度等级

```
beginner → intermediate → advanced → expert
```

当前等级存于 `.study-config.json` → `difficulty`。

### 各等级如何影响课程生成

**Beginner（初级）：**
- 更长的概念讲解，带类比
- 小而聚焦的练习（一次一个概念）
- 讲义中 2-3 个参考示例（明确标注为参考，不要照抄）
- 明确的成功标准，带勾选框
- 练习目录中更多脚手架（比如带注释的起始文件）

**Intermediate（中级）：**
- 讲解与练习比例均衡
- 复合要求（每个练习组合 2-3 个概念）
- 最多 1 个参考示例，更精炼
- 成功标准不再手把手

**Advanced（高级）：**
- 讲义最少 —— 假定前面的概念已扎实
- 需要独立调研的复杂练习
- 可直接引用源材料：“实现第 7 章描述的算法”
- 开放式要求：“构建一个能展示 X 的东西”

**Expert（专家）：**
- 挑战风格，没有讲义部分
- 性能约束：“以 O(n log n) 求解”或“支撑 1 万个并发连接”
- 故意模糊的要求，考验设计判断力
- 禁用提示 —— 如果卡住，技能会建议退回高级

## 自动调整规则

每节课完成后（status = `completed`），评估最近 2 节已完成的课程：

**满足以下全部条件则上调一级（最近 2 节课）：**
- hints_requested == 0
- review_rounds <= 1
- fsrs_ratings 平均分 >= 4

**满足以下任一条件则下调一级（最近 2 节课）：**
- 单节课 hints_requested >= 3
- 单节课 review_rounds >= 3
- fsrs_ratings 平均分 <= 2

**其他情况：维持当前等级。**

绝不在一节课之后就调整 —— 等待跨 2 节课的趋势。

## 校准检查

每完成 3-4 节课，询问用户：

```
根据你最近的练习情况，我目前的授课难度定在 [中级]。
感觉合适吗？
  1. 太简单了 —— 再挑战一些
  2. 差不多
  3. 太难了 —— 慢一点
```

用户的覆盖选择是**粘性的** —— 一直保持到下一次校准检查。自动调整规则仍在运行，但在下次校准之前不会覆盖用户的选择。

把覆盖选择存入 `.study-config.json`：
```json
{
  "difficulty": "intermediate",
  "difficulty_override": "advanced",
  "difficulty_override_at_lesson": 5,
  "next_calibration_at_lesson": 9
}
```

## 科学领域自适应（sciagent-skills）

当工作区配置了 `sciagent_skills`（见 `references/template-resolution.md`）时，所挂载技能的 **Key Parameters（关键参数）** 表在通用代码复杂度之外，为难度缩放提供了另一个维度。

### 基于参数的练习缩放

**Beginner：**
- 练习说明：“使用课程讲义中展示的默认参数”
- Key Parameters 表包含在课程讲义中，默认值高亮
- 成功标准引用具体的输出形状/规模（来自 sciagent 的 Expected Outputs）
- Troubleshooting 表节选包含在 Common Pitfalls 部分

**Intermediate：**
- 练习说明：“调节参数 X 以达到 Y”（例如“调整聚类分辨率以得到 8-12 个簇”）
- Key Parameters 表包含但默认值**不**高亮 —— 用户必须自己推理取值范围
- 练习要求组合 sciagent 工作流中的 2-3 个流水线步骤
- 成功标准基于结果，而非参数

**Advanced：**
- 练习说明：“为你的参数选择给出理由”
- Key Parameters 表**不**提供 —— 用户必须自行查阅或凭记忆
- 练习可引用 sciagent 技能的 Common Recipes：“实现批次校正变体”
- 开放式：“你的流水线应当能处理[Troubleshooting 表中的边界情况]”

**Expert：**
- 练习提供一个默认参数会失效的数据集
- 不给参数指导 —— 用户必须诊断默认值为何效果差
- 可能需要串联多个 sciagent 技能（如 比对 → 定量 → 差异表达分析）
- 成功标准包含质量指标（如“轮廓系数（silhouette score）> 0.3”）

### 基于 sciagent-skills 的评审校验

在「评审与反馈」阶段（主循环第 3 步），当挂载了 sciagent 技能时：

1. 阅读相关 sciagent 技能中该练习主题的 Common Recipe
2. 将用户的实现与配方做*结构*对比（不要求完全一致 —— 模式匹配）
3. 检查：函数调用是否正确、参数值是否在合理范围、对已知失败模式（来自 Troubleshooting 表）是否有恰当的错误处理
4. 标出技能 Troubleshooting 部分列出的反模式

sciagent 配方是**私有的校验参考** —— 绝不展示给用户。用它来保证反馈质量。

## 边界情况

- **第一节课**：永远从 `beginner` 开始，除非用户在 init 时明确说明。
- **用户从初级直接跳到专家**：尊重其覆盖选择。如果他们表现吃力，自动规则会在下次校准时建议回退。
- **专家级 + 卡住**：不要自动降级。而是建议：“这是专家级内容 —— 要不要这个概念先退回高级，之后再回到专家？”
