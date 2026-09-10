# 初始化设置模块

*当 settings.json 不存在，或 $ARGUMENTS = "setup" 时由 learn.md 加载。*

使用用户在 B 节中回答的语言回复。无法判断时默认希伯来语。

---

## A. 展示当前设置

如果 `~/skill-tutor-tutorials/settings.json` 存在，展示一张友好的汇总表：会话语言、课程路径、TTS 开/关、语音名称、TTS 语言、语速和模式。

如果文件不存在——直接跳到 B 节。

---

## B. 会话语言

使用 `AskUserQuestion` 工具：

```
question: "In which language would you like the session to run?"
header: "Session Language"
options:
  - label: "עברית"
    description: "המערכת תתקשר איתך בעברית"
  - label: "English"
    description: "The system will communicate with you in English"
```

把 `session.language` 设为 `"he"` 或 `"en"`。此后所有交流都使用该语言。

---

## B.1. 称呼方式（仅希伯来语）

**仅当 `session.language == "he"` 时运行本节。选择英语则整节跳过。**

使用 `AskUserQuestion`：

```
question: "איך להתייחס אליך בשיחה?"
header: "פנייה"
options:
  - label: "אתה (יחיד זכר)"
    description: "פנייה בלשון זכר"
  - label: "את (יחיד נקבה)"
    description: "פנייה בלשון נקבה"
  - label: "ניטרלי / מעורב"
    description: "ללא פנייה מגדרית — מתאים לקבוצות מעורבות או העדפה אישית"
  - label: "רבים / רבות"
    description: "פנייה בלשון רבים — ציין אם זכר (אתם) או נקבה (אתן)"
```

*（该工具会自动为自由文本追加 "Other" 选项——按其原值使用。）*

将结果存为 `session.address`。示例：
- "אתה (יחיד זכר)" → `"masculine"`
- "את (יחיד נקבה)" → `"feminine"`
- "ניטרלי / מעורב" → `"neutral"`
- "רבים / רבות" → `"plural-m"` 或 `"plural-f"`（必要时追问）
- 自由文本 → 原样存为 `"other:<text>"`

**此后的所有希伯来语交流都使用 `session.address`。**

---

## B.2. 为希伯来语用户安装 RTL 扩展

**仅当 `session.language == "he"` 时运行本节。选择英语则整节跳过。**

首先检查扩展是否已安装：

```powershell
code --list-extensions | Select-String "yechielby.claude-code-rtl"
```

**如果已安装：** 整节跳过——无需任何提示。

**如果未安装：** 使用 `AskUserQuestion`：

```
question: "האם להתקין את תוסף ה-RTL?"
header: "תוסף RTL"
options:
  - label: "כן, התקן"
    description: "yechielby.claude-code-rtl — משפר תצוגת עברית ב-Claude Code"
  - label: "לא תודה"
    description: "דלג על שלב זה"
```

**如果选择是：** 先告诉用户：

> "正在安装扩展。注意安装可能会打断会话——如果发生这种情况：若会话还开着，输入 **继续**；若已关闭，开一个新会话并输入 **`/learn setup`**。"

然后运行：

```powershell
code --install-extension yechielby.claude-code-rtl
```

命令完成后，补充：

> "扩展加载后，请激活一次自动模式：
> `Ctrl+Shift+P` ← **Activate RTL (Auto)**
>
> **为什么这很重要？** 没有该模式，所有文本都按从左到右显示——希伯来语会反向出现，段落从错误的一侧开始，读起来很费劲。Auto 模式会自动识别哪个对话气泡是希伯来语、哪个是英语，并把每一个都按正确方向排列——你什么都不用做。
>
> 该扩展会在屏幕底部的状态栏加一个小按钮——随时可以从中切换模式或彻底关闭。"

**如果选择否：** 静默跳过，继续 C 节。

---

## C. 课程选择

使用 `AskUserQuestion` 工具展示课程选择器：

```
question: "באיזה מסלול תרצה ללמוד?"
header: "בחירת מסלול"
options:
  - label: "AI Dev"
    description: "פיתוח מוצרי AI עם Claude Code ו-API (המסלול הפעיל היחיד)"
  - label: "נתיב מותאם אישית"
    description: "הגדרת נתיב מסלול ידנית"
```

把选择映射到设置：

| 选择 | course.name | course.path |
|-------|-------------|-------------|
| AI Dev | `ai-dev` | `courses/ai-dev/lessons` |
| 自定义路径 | （问名称） | （问路径） |

> AI Engineer 课程已归档到 `courses/_archive/ai-engineer/`。如果学习者需要它——可以输入自定义路径：`courses/_archive/ai-engineer/lessons`。

如果学习者输入了带自由文本的 "Other"——按自定义路径处理。

---

## D. TTS 设置

使用 `AskUserQuestion` 工具：

```
question: "האם תרצה שהמורה ידבר בקול?"
header: "קול מורה"
options:
  - label: "כן"
    description: "המערכת תקרא את התשובות בקול"
  - label: "לא"
    description: "טקסט בלבד"
```

**如果选择是：**

1. 运行 PowerShell 列出可用语音：
```powershell
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.SpeechSynthesis.SpeechSynthesizer,Windows.Media.Speech,ContentType=WindowsRuntime]
[Windows.Media.SpeechSynthesis.SpeechSynthesizer]::AllVoices | ForEach-Object { "$($_.DisplayName) — $($_.Language)" }
```

2. 展示列表并询问想要哪个语音（自由文本——列表是动态的）。

3. 使用 `AskUserQuestion` 工具询问语速：

```
question: "באיזה קצב תרצה שהמורה ידבר?"
header: "קצב דיבור"
options:
  - label: "רגיל"
    description: "קצב ברירת מחדל (0)"
  - label: "איטי"
    description: "מומלץ למתחילים (-2)"
  - label: "מהיר"
    description: "למי שרוצה להאיץ (+2)"
```

映射：רגיל（正常）→ 0，איטי（慢）→ -2，מהיר（快）→ 2。

4. 使用 `AskUserQuestion` 工具询问 TTS 模式：

```
question: "מתי תרצה שהמורה ידבר?"
header: "מצב קול"
options:
  - label: "אוטומטי"
    description: "מדבר אחרי כל תשובה"
  - label: "לפי דרישה"
    description: "רק כשתבקש"
```

映射：אוטומטי（自动）→ `"auto"`，לפי דרישה（按需）→ `"on-demand"`。

5. 用配置好的会话语言朗读一句问候来测试语音。

6. 使用 `AskUserQuestion` 工具：

```
question: "הקול נשמע טוב?"
header: "בדיקת קול"
options:
  - label: "כן, מעולה"
    description: "שמור את ההגדרות"
  - label: "לא, שנה קול"
    description: "חזור לבחירת קול (שלב 2)"
```

**如果选择否：** 设置 `tts.enabled = false`。

---

## D.5. 学习风格

使用 `AskUserQuestion`（两个问题，可以一起展示）：

```
question: "איך תעדיף ללמוד בדרך כלל?"
header: "סגנון למידה"
options:
  - label: "standard — הסבר ואז שאלה (ברירת מחדל)"
    description: "אסביר כל נושא ואז אשאל שאלה לבדיקת הבנה"
  - label: "diagnostic — בחן אותי קודם"
    description: "תבחן אותי על כל השיעור קודם, ותלמד אותי רק את מה שטעיתי"
  - label: "socratic — הדרך אותי בשאלות"
    description: "תשאל שאלות שיובילו אותי לגלות את התשובות בעצמי"
```

```
question: "איזו רמת פירוט מתאימה לך?"
header: "רמת פירוט"
options:
  - label: "detail 1 — קצר מאוד"
    description: "רק הרעיון המרכזי, 1–2 משפטים לשקף"
  - label: "detail 2 — ברירת מחדל"
    description: "מאוזן — הסבר + דוגמה + שאלה"
  - label: "detail 3 — עומק מלא"
    description: "כל הפרטים, תוספות, השוואות"
```

映射到值：
- mode：`"standard"` / `"diagnostic"` / `"socratic"`
- detail_level：`1` / `2` / `3`

---

## E. 保存设置

保存 `~/skill-tutor-tutorials/settings.json`：

```json
{
  "session": {
    "language": "he",
    "address": "masculine"
  },
  "course": {
    "name": "ai-dev",
    "path": "courses/ai-dev/lessons"
  },
  "tts": {
    "enabled": true,
    "voice_name": "[selected voice name]",
    "voice_lang": "[voice language code]",
    "rate": 0,
    "mode": "auto"
  },
  "learning_style": {
    "mode": "standard",
    "detail_level": 2
  }
}
```

---

## F. 全局安装（可选）

默认情况下 `/learn` 在本仓库内即可工作——无需安装。只有当学习者想在*其他*项目中运行 `/learn` 时，全局安装才有用（面向未来的跨仓库使用场景）。

**注意取舍：** 全局副本是第二份事实来源（second source of truth）。如果仓库里的模块之后被修改，全局副本就会过时，直到重新同步。大多数学习者应该选「否」。

使用 `AskUserQuestion` 工具：

```
question: "להתקין את /learn גם בפרויקטים אחרים? (רוב הלומדים: לא)"
header: "התקנה גלובלית"
options:
  - label: "לא, רק בריפו הזה"
    description: "/learn יעבוד בתוך הריפו. מומלץ — אין עותק כפול שעלול להתיישן."
  - label: "כן, התקן גלובלית"
    description: "אעתיק את המודולים ל-~/.claude/commands כדי שאפשר יהיה להשתמש מכל מקום."
```

**如果选择否：** 跳过——确认设置已保存且 `/learn` 在本仓库内已可用。

**如果选择是：** 把技能文件复制到全局 Claude 命令目录，然后提醒：今后对仓库的修改需要重新运行 setup 来重新同步。

```powershell
$dest = "$env:USERPROFILE\.claude\commands"
if (!(Test-Path $dest)) { New-Item -ItemType Directory -Force -Path $dest | Out-Null }
Copy-Item -Force "$PWD\.claude\commands\learn.md" "$dest\learn.md"

$moduleDest = "$dest\learn"
if (!(Test-Path $moduleDest)) { New-Item -ItemType Directory -Force -Path $moduleDest | Out-Null }
Copy-Item -Force "$PWD\.claude\commands\learn\*.md" "$moduleDest\"
```

---

## G. 设置完成——必须执行

**无论学习者选择了哪些选项，完成以上所有步骤后都必须发送这条消息。**

用 `session.language` 发送一条总结消息，包括：
1. 确认设置已完成、配置已保存。
2. 一行回顾所选配置（语言、课程、TTS 开/关）。
3. 询问下一步想做什么——提议从第一课开始，或跳到指定课节。

示例（英语）：
```
Setup complete! Here's your configuration:
- Language: English
- Course: AI Dev
- Voice: Off

Ready to start learning. Would you like to begin with Lesson 0.1, or jump somewhere specific?
```

即使之前有任何小节被跳过、或学习者对可选项说了「否」，也不要跳过这一步。
