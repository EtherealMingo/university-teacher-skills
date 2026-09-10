# 项目架构分析模块

*当学习者选择「项目分析」时加载。*

全程使用 `session.language` 回复。使用 `session.address` 称呼学习者。

---

## 阶段 A——自动代码扫描（静默进行，在提问之前）

使用 Glob 扫描项目根目录，查找：
- `package.json`、`requirements.txt`、`Pipfile`、`pyproject.toml`、`go.mod`、`*.csproj`、`Cargo.toml`
- `docker-compose.yml`、`Dockerfile`、`.env.example`
- `CLAUDE.md`——如果存在，阅读它
- 顶层目录结构：`src/`、`app/`、`lib/`、`api/`、`services/`

从扫描结果中：识别技术栈、语言、框架、外部服务（imports、环境变量、配置文件）。

---

## 阶段 B——架构师访谈（5 个问题，一次一个）

1. **"这个项目是做什么的——用一句话、从业务层面讲？"**（不是技术层面——它为用户解决什么问题？）
2. **"用户是谁，他们需要在其中做什么？"**（2–3 个主要用例）
3. **"项目连接了哪些外部服务？"**（扫描中未发现的任何服务）
4. **"当前和预期的规模是多少？"**（用户数、请求量、季节性负载）
5. **"架构中最大的痛点或不确定点是什么？"**（瓶颈、技术债、让你担忧的事情）

---

## 阶段 C——生成架构图 HTML

保存到：`~/skill-tutor-tutorials/architectures/[project-name].html`

```html
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
  <meta charset="UTF-8">
  <title>Architecture: [project name]</title>
  <style>
    /* Layer colors:
       Client = #3B82F6 | API/Backend = #10B981 | Services = #8B5CF6
       Data = #F59E0B | External = #6B7280
    */
    body { font-family: 'Segoe UI', sans-serif; background: #F9FAFB; padding: 40px; direction: rtl; }
    h1 { font-size: 1.8rem; color: #111827; margin-bottom: 4px; }
    .subtitle { color: #6B7280; margin-bottom: 40px; font-size: 1rem; }
    .arch-diagram { display: flex; flex-direction: column; gap: 16px; max-width: 900px; margin: 0 auto; }
    .layer { border-radius: 12px; padding: 20px; }
    .layer-title { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px; opacity: 0.7; }
    .components { display: flex; gap: 12px; flex-wrap: wrap; }
    .component { background: white; border-radius: 8px; padding: 14px 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-width: 140px; }
    .component-name { font-weight: 600; font-size: 0.95rem; }
    .component-tech { font-size: 0.75rem; color: #6B7280; margin-top: 2px; }
    .component-desc { font-size: 0.8rem; color: #374151; margin-top: 6px; }
    .arrow { text-align: center; font-size: 1.5rem; color: #9CA3AF; margin: 4px 0; }
    .arrow-label { font-size: 0.75rem; color: #9CA3AF; }
    .bottom-section { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 32px; max-width: 900px; margin-right: auto; }
    .info-box { background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }
    .info-box h3 { font-size: 0.9rem; font-weight: 700; color: #374151; margin-bottom: 12px; }
    .info-box ul { list-style: none; padding: 0; margin: 0; }
    .info-box li { font-size: 0.85rem; color: #6B7280; padding: 4px 0; border-bottom: 1px solid #F3F4F6; }
    .concern { color: #EF4444 !important; }
  </style>
</head>
<body>
  <h1>[Project Name]</h1>
  <p class="subtitle">[Short business description]</p>
  <div class="arch-diagram">
    <div class="layer" style="background: #EFF6FF; border: 1px solid #BFDBFE;">
      <div class="layer-title" style="color: #3B82F6;">Client Layer</div>
      <div class="components">
        <div class="component">
          <div class="component-name">[component name]</div>
          <div class="component-tech">[technology]</div>
          <div class="component-desc">[short description]</div>
        </div>
      </div>
    </div>
    <div class="arrow">↓ <span class="arrow-label">[connection type]</span></div>
    <!-- Continue layers based on project -->
  </div>
  <div class="bottom-section">
    <div class="info-box">
      <h3>Tech Stack</h3>
      <ul><!-- technology + usage --></ul>
    </div>
    <div class="info-box">
      <h3>Points of Concern</h3>
      <ul>
        <li class="concern">[concern 1]</li>
      </ul>
    </div>
  </div>
</body>
</html>
```

**准则：** 仅根据扫描 + 访谈的发现构建各层。使用项目中的真实名称。箭头标注连接类型（REST、WebSocket、Queue 等）。外部服务放在单独的底层。

保存后，告诉学习者文件路径，并请他们在浏览器中打开。

---

## 阶段 D——更新学习者档案

更新 `~/skill-tutor-tutorials/learner_profile.md`：

```markdown
## Current Project
[Project name] — [short business description]

## Architecture Notes
- Stack: [main technologies]
- Scale: [current and expected]
- Pain points: [from the interview]
```

完成后，询问学习者是否想学习一节能解决他们所提挑战的课。
