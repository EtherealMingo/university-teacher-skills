# Markdown、冻结与 DOCX 契约

## 目录

- 草稿语法
- 块映射与修订
- 冻结
- DOCX 装配
- 一致性
- 暂存、续跑与清理

## 草稿语法

`MD-SYNTAX-001` `draft.md` 使用 UTF-8 和 LF。

`MD-SYNTAX-002` 最多一个 `#` 总标题；`##` 对应模板一级栏目；`###`、`####` 对应内部论证单元。

`MD-SYNTAX-003` 允许普通段落、真实有序/无序列表、管道表格、`[n]` 数字引用键和 `【待补：……】`。

`MD-SYNTAX-004` 禁止 HTML、脚本、外部包含、执行链接、嵌入命令和任务管理语言。

`MD-SYNTAX-005` 模板固定文字、图片和复杂表格对象保存在 Schema 与资源清单，不复制进正文。

## 块映射与修订

`MD-MAP-001` 每个可见块具有稳定 `block_id`、`section_id`、类型、顺序和来源锚点。

`MD-MAP-002` `draft-map.json` 不复制正文。

`MD-MAP-003` 每次保存使 `revision` 加一。

`MD-MAP-004` 字符、顺序、层级、列表或表格变化都清除冻结及后续状态。

`MD-MAP-005` 所有正文写入必须经过 `draft_store`。

## 冻结

`MD-FREEZE-001` 冻结前重新运行内容门并确认无阻断。

`MD-FREEZE-002` 规范化为 UTF-8、LF、Unicode NFC，清除行尾空白并保留一个文件末尾换行。

`MD-FREEZE-003` 验证 Markdown 与映射的块数、类型和顺序。

`MD-FREEZE-004` 分别计算正文、映射和内容报告 SHA-256，并记录修订号。

`MD-FREEZE-005` 构建前重算三个哈希；变化返回 `E_DRAFT_CHANGED_AFTER_FREEZE` 或 `E_DRAFT_MAP_MISMATCH`。

## DOCX 装配

`MD-DOCX-001` 构建器只接受冻结稿、模板 Schema、样式配置、恢复资源和命名策略。

`MD-DOCX-002` 总标题和栏目标题使用模板指定或普通加粗段落；内部标题使用普通加粗正文段落。

`MD-DOCX-003` 正文使用 `Normal`；列表使用真实 numbering；表格保留行列和合并拓扑。

`MD-DOCX-004` 待补占位使用红色 `Missing Fact` 字符样式；`[n]` 引用键保持可见，不得改写、隐藏或删除。

`MD-DOCX-005` 官方图片按来源锚点恢复。

`MD-DOCX-006` 模板/通知明文格式优先；无要求时使用 A4、小四仿宋、1.5 倍行距、首行缩进两字符和宋体五号表格。

`MD-DOCX-007` 禁止 Office/WPS 装饰性标题样式、边框、底纹、主题色和下划线。

## 一致性

`MD-PARITY-001` Markdown 和 DOCX 使用同一 Unicode NFC 可见文本模型。

`MD-PARITY-002` 比较总标题、栏目 ID/顺序、块数量/类型/顺序、块文本、列表、表格拓扑/单元格和占位符。

`MD-PARITY-003` 允许 Word 自动编号显示、软换行、分页、页码字段和必要排版空段差异。

`MD-PARITY-004` 不改变中文标点、数字、大小写、引用键或可见字符。

`MD-PARITY-005` 其他新增、删除或替换返回 `E_DRAFT_DOCX_MISMATCH`。

## 暂存、续跑与清理

`MD-DELIVERY-001` 只在会话 `build` 目录创建 `staged.docx`。

`MD-DELIVERY-002` 渲染器可用时首次构建在 `RENDER_REVIEW_PENDING` 停止，用户目录不产生文件；渲染器缺失时跳过复核、记录警告并直接原子交付。

`MD-DELIVERY-003` 续跑复核会话 ID、DOCX 哈希、页数和全部页面覆盖。

`MD-DELIVERY-004` 目标名为 `<模板名>-完成稿.docx`；冲突使用稳定递增后缀，不覆盖文件。

`MD-DELIVERY-005` 同卷使用原子替换；跨卷复制到隐藏暂存名，刷新、验哈希后重命名。

`MD-DELIVERY-006` 成功、不可恢复失败、取消或终止清理草稿、Schema、恢复文件、暂存文件和渲染页。

`MD-DELIVERY-007` 可恢复版式问题在活动会话内保留冻结稿并废弃后续产物。
