# 导出模块——导出学习者数据

把 `~/skill-tutor-tutorials/` 下的全部学习者数据导出为一个 ZIP 文件，可转移到另一台设备或留作备份。

---

## 步骤 1——检查来源

静默运行：

```powershell
Test-Path "$HOME\skill-tutor-tutorials"
```

如果目录**不存在** → 告诉学习者（使用 `session.language`）：
- 未找到学习者数据。请先运行 `/learn setup`。

如果**存在** → 继续。

---

## 步骤 2——收集文件清单

运行：

```powershell
$base = "$HOME\skill-tutor-tutorials"
$files = Get-ChildItem $base -Recurse -File -ErrorAction SilentlyContinue
$groups = $files | Group-Object { $_.DirectoryName.Replace($base, '').TrimStart('\').Split('\')[0] }
foreach ($g in $groups) {
  $label = if ($g.Name -eq '') { 'שורש' } else { $g.Name }
  "$label ($($g.Count) קבצים)"
}
"סך הכל: $($files.Count) קבצים"
```

简要展示将导出的内容摘要（例如："settings.json、3 个教程文件、3 个进度文件、知识图谱……"）。

---

## 步骤 3——确定目标位置

获取今天的日期和当前工作目录：

```powershell
Get-Date -Format "yyyy-MM-dd"
(Get-Location).Path
```

默认路径：`[CURRENT_WORKING_DIR]/tov-learn-export-[DATE].zip`

直接使用默认路径继续——无需询问。只有当用户在 `$ARGUMENTS` 中明确指定了其他路径时才询问（例如 `/learn export C:\backups\my.zip`）。

---

## 步骤 4——创建 ZIP

确保目标目录存在，然后运行：

```powershell
$src  = "$HOME\skill-tutor-tutorials"
$dest = "CWD\tov-learn-export-DATE.zip"   # 用步骤 3 的值替换 CWD 和 DATE
$destDir = Split-Path $dest -Parent
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Force $destDir | Out-Null }
if (Test-Path $dest) { Remove-Item $dest -Force }
Compress-Archive -Path "$src\*" -DestinationPath $dest -CompressionLevel Optimal
$size = [math]::Round((Get-Item $dest).Length / 1KB, 1)
"$dest|$size KB"
```

如果命令失败 → 展示错误并停止；不要谎报成功。

---

## 步骤 5——确认

报告成功（使用 `session.language` 回复）：

```
✅ ייצוא הושלם!

📦 נשמר ב: [DEST_PATH]
📁 [N] קבצים | [SIZE]

כדי לייבא את הגיבוי במכשיר אחר:
/learn import
```
