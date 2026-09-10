# CLI 优先参考

*共享原则。任何模块都可以用「遵循 cli-first」来引用本文档。*

在引导学习者进行任何安装、部署或仓库操作时——**优先使用命令行，而不是点击仪表盘。** 目标是让学习者理解正在发生什么、练出可复用的肌肉记忆，并最终得到一个可复现的工作流。

## 规则

1. **先给命令，再解释它。** 永远不要只给命令而不附上一行说明：它做什么、为什么这么做。
2. **优先使用官方 CLI** 而非网页 UI：
   - GitHub → `gh`（`gh repo create`、`gh pr create`、`gh auth login`）
   - Cloudflare → `wrangler`（`wrangler deploy`、`wrangler pages deploy`、`wrangler login`）
   - Render → `render` CLI，或提交到仓库的 `render.yaml` 蓝图（blueprint）
   - Vercel → `vercel`，Netlify → `netlify`
   - Git → 原生 `git`（`git init`、`git add`、`git commit`、`git push`）
3. **只有当 CLI 确实做不到时才用 UI**——例如首次 OAuth 登录、添加付款方式，或一次性的账户验证。要明确说明「这一步只能用 UI，因为……」。
4. **可复现性：** 优先使用命令和提交进仓库的配置文件（`wrangler.toml`、`render.yaml`、`.github/workflows/`），而不是手动仪表盘设置，这样全新克隆（fresh clone）后配置依然有效。
5. **Windows 提示：** 学习者很可能在用 PowerShell。给出 PowerShell 安全的命令（用 `$env:VAR`，而不是 `export`）。这些 CLI 大多可通过 `npm i -g` 或 `winget` 跨平台安装。
6. **机密（secrets）绝不能以明文进入仓库或命令历史。** 使用平台的机密存储（`wrangler secret put`、`gh secret set`、Render 环境变量）——并解释为什么。

## 相关时可出示的迷你速查表

```bash
# GitHub
gh auth login                 # 一次性登录（打开浏览器——仅 UI 步骤）
gh repo create my-app --public --source=. --push

# Cloudflare Workers / Pages
npm i -g wrangler
wrangler login                # 一次性登录（浏览器）
wrangler deploy               # 部署一个 Worker
wrangler pages deploy ./dist  # 把静态构建产物部署到 Pages
wrangler secret put API_KEY   # 安全地存储机密

# Git 基础
git init && git add . && git commit -m "init" && git push
```
