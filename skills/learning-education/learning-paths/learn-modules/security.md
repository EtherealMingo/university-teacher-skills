# 安全模块——安全审查

*当 /learn 以 "security [URL]" 或 "security" 参数被调用，或部署模块提议安全检查且学习者接受时加载。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

本模块的目标**不是**照本宣科地走一份静态检查清单——而是帮助学习者*在他们正在运行的应用中发现真实漏洞、理解每个漏洞为什么危险、并亲手修复*，从而在实操中学习。

线上 URL 能揭示代码审查漏掉的东西：实际被伺服（serve）的文件、服务器发送的响应头、响应出乎意料的端点。只要有 URL，就永远优先测试线上应用。

---

## 预备——获取 URL

从 `$ARGUMENTS` 解析 URL（以 `http://` 或 `https://` 开头）。

- **提供了 URL** → 存为 `target_url`，进入阶段 A（实扫）。
- **没有 URL** → 问："你的应用 URL 是什么？（例如：`https://my-app.onrender.com`）。如果还没部署——先运行 `/learn deploy`，拿到地址后再回来。"

---

## 阶段 A——线上 HTTP 实扫（静默进行，在说话之前）

对 `target_url` 静默运行以下 Bash 检查。记录每一个结果。

**1. TLS 与重定向**
```bash
# HTTP → HTTPS 重定向？
curl -s -o /dev/null -w "%{http_code} %{redirect_url}" http://TARGET_HOST/
# TLS 版本
curl -s -v --tlsv1.2 https://TARGET_URL/ 2>&1 | grep -E "SSL|TLS|issuer"
```

**2. 敏感文件——是否暴露？**
```bash
for path in /server.js /app.js /index.js /package.json /.env /config.js /upload.js; do
  code=$(curl -s -o /dev/null -w "%{http_code}" https://TARGET_URL$path)
  echo "$code $path"
done
```
200 = 严重暴露。404/403 = 正常。

**3. 安全响应头**
```bash
curl -s -I https://TARGET_URL/ | grep -iE "strict-transport|content-security|x-frame|x-content-type|referrer-policy|x-powered-by"
```
记录缺少哪些响应头，以及 `x-powered-by` 暴露了什么信息。

**4. 端点鉴权——不带认证试一下**
```bash
# 把 /api/upload-doc 换成学习者在阶段 B 提供的真实路径
curl -s -o /dev/null -w "%{http_code}" -X POST https://TARGET_URL/api/upload-doc \
  -H "Content-Type: application/json" -d '{"test":1}'
```
200/201 = 端点开放。401/403 = 有保护。

**5. /config 与暴露的端点**
```bash
curl -s https://TARGET_URL/config
```
检查它是否返回内部 ID、文档 ID 或环境变量名。

把所有结果保存在会话记忆中——阶段 C 会用到。

### 阶段 A.2——代码扫描（加分项，若能访问代码）

如果项目已在本地环境中打开，再跑代码检查：

| Pattern | What to flag |
|---------|-------------|
| `express.static(__dirname)` | 源代码暴露 |
| `innerHTML` | HTML injection |
| `req.body\.\w+` 传给外部服务 | Confused deputy |
| `error\.message` 出现在 `res.send` 中 | 信息泄露 |
| `helmet`——在 package.json 里吗？ | 缺安全响应头 |
| `express-rate-limit`——在吗？ | 缺速率限制 |
| `.env` 在 `.gitignore` 里吗？ | 可能泄露的机密 |

---

## 阶段 B——2 个聚焦问题（一条消息一起问）

简要展示阶段 A 的原始结果，然后问：

> "我对线上应用跑了几项检查。在总结之前，我还有两个问题。"

问题：

1. **除了 `/` 之外，还有哪些端点暴露到公网？**（例如：POST /api/save、POST /api/upload-doc、GET /config）——列出来。如果不确定——写「不知道」，我们一起找。
2. **有没有用户输入会被回显到页面上？**（评论、姓名、搜索、任何用户写了又能在屏幕上看到的东西——是/否）

---

## 阶段 C——按项目类型聚焦的检查清单

从**两个来源**构建本次审查：阶段 A 的发现 + 阶段 B 的回答。

不要把整份清单都过一遍——只讲与这个项目相关的部分。

### 类别 1——文件暴露

**检查：** `express.static` 是否伺服的根目录（`__dirname`）而不是 `public/` 目录？

如果是——这是严重问题。解释：

> "当你写 `express.static(__dirname)` 时，服务器会伺服**目录里的所有文件**——包括 `server.js`、`package.json`，如果有未加入 .gitignore 的机密文件——也一并暴露。互联网上的任何人都可以下载你的代码。"

修复：
```js
// ❌ 暴露一切
app.use(express.static(__dirname))

// ✅ 只伺服 public/
app.use(express.static(path.join(__dirname, 'public')))
```

---

### 类别 2——端点鉴权

**检查：** 是否有端点接受 POST/PUT/DELETE 却不校验身份？

如果是——高危。解释：

> "没有鉴权的端点就像对所有人敞开的门。任何知道地址的人都能发请求——从他们的浏览器、从 curl、从自动化脚本。"

共享密钥校验的最小模式：
```js
const secret = process.env.SYNC_SECRET
if (!secret) return res.status(503).json({ error: 'Service unavailable' })

const provided = req.headers['x-sync-key']
if (!provided || !timingSafeEqual(Buffer.from(provided), Buffer.from(secret))) {
  return res.status(401).json({ error: 'Unauthorized' })
}
```

解释 `timingSafeEqual`：普通比较（`===`）容易受到时序攻击（timing attack）——可以根据响应时间逐字符猜出密钥。`timingSafeEqual` 永远耗时相同。

---

### 类别 3——Confused Deputy（混淆代理人）

**检查：** 来自 `req.body` 的值（如 `docId`、`userId`、`path`）是否直接传给外部服务？

如果是——高危。解释：

> "这叫 'confused deputy'——你的服务器是外部服务的授权代理（deputy），但它允许攻击者告诉它*对谁*动手。用户发送 `docId: '别人的文档'`——服务器就对那份文档执行了操作。"

修复：
```js
// ❌ 用户控制目标
const docId = req.body.docId || process.env.DOC_ID

// ✅ 目标永远由服务器决定
const docId = process.env.DOC_ID
```

---

### 类别 4——HTML 注入

**检查：** 是否存在把用户输入值放进 `innerHTML` 的情况？

如果是——中危（若数据被存储并展示给其他用户则为高危）。解释：

> "当把用户输入的字符串直接放进 innerHTML 时，攻击者可以写 `<img src=x onerror='alert(document.cookie)'>`——它会在每个看到该页面的人的浏览器里运行。"

修复——简单的转义函数：
```js
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

// 用法：
element.innerHTML = escapeHtml(userInput)
// 或者更好：
element.textContent = userInput  // 完全不需要转义
```

---

### 类别 5——安全响应头

**检查：** `package.json` 里有 `helmet` 吗？

如果没有——中危。解释：

> "诸如 `X-Frame-Options`、`Content-Security-Policy`、`Strict-Transport-Security` 的 HTTP 响应头能抵御整类攻击——点击劫持（clickjacking）、MIME 嗅探、降级到 HTTP。`helmet` 一行就能全部加上。"

```bash
npm install helmet
```
```js
const helmet = require('helmet')
app.use(helmet())
```

---

### 类别 6——速率限制（Rate Limiting）

**检查：** 是否配置了 `express-rate-limit`？

如果没有——中危。解释：

> "没有速率限制，攻击者可以向你的端点发送数千请求——刷爆你的 API 配额、尝试爆破密码，或者直接打挂服务器。"

```bash
npm install express-rate-limit
```
```js
const rateLimit = require('express-rate-limit')
app.use('/api/', rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 分钟
  max: 30,                     // 每窗口 30 次请求
  message: { error: 'Too many requests' }
}))
```

---

### 类别 7——错误信息泄露

**检查：** 是否存在 `res.send(error.message)` 或 `res.json({ error: err.stack })`？

如果是——中危。解释：

> "详细的错误信息会向攻击者暴露代码结构、文件名、依赖版本——这些信息能帮他策划精确的攻击。"

```js
// ❌
res.status(500).send(error.message)

// ✅
console.error('Internal error:', error)  // 完整信息留在日志里
res.status(500).json({ error: 'Internal server error' })  // 对外只给通用信息
```

---

### 类别 8——机密管理

**检查：** `.env` 是否在 `.gitignore` 中？代码里有没有硬编码的密钥？

如果 `.env` 不在 `.gitignore` 里——立即定为严重。解释：

> "如果 `.env` 被提交进 git——任何能访问仓库的人（包括公开 GitHub 账户）都能永远看到你的所有密钥，即使之后删除也没用——因为 git 会保存历史。"

```
# .gitignore
.env
.env.local
*.pem
service-account*.json
```

---

## 阶段 D——总结报告

过完检查清单后，展示一份整齐的 report：

```
🔒 安全审查——[项目名]
═══════════════════════════════

🔴 严重（上线前必须修）：
  • [发现 + 相关代码行]

🟠 高危（尽快修）：
  • [发现]

🟡 中危（建议发布前修）：
  • [发现]

✅ 正常：
  • [检查结果正常的项]
```

报告末尾问：

> "想先从哪个发现开始？我可以陪你一步步完成修复。"

---

## 阶段 E——保存发现

保存到 `~/skill-tutor-tutorials/progress/security-[project-name].md`：

```markdown
# Security Review — [project name]
date: [date]

## ממצאים
[findings list with severity]

## תוקן
[fixed in this session]

## נותר
[still open]
```

保存后："我已经保存了这些发现。下次你运行 `/learn security` 时，我会给你看还剩哪些。"

---

## 返回规则

如果学习者想在审查后回到部署流程——说：

> "审查完成了。等你准备好——回到 `/learn deploy`，我们从停下的步骤继续。"
