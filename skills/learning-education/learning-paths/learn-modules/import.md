# 导入模块——导入学习者数据

把学习者数据从 ZIP 文件（由 `/learn export` 创建）导入到 `~/skill-tutor-tutorials/`。

---

## 步骤 1——获取导入路径

如果 `$ARGUMENTS` 中包含文件路径（以 `.zip` 结尾），直接使用它。

否则，默认使用 `[CWD]/tov-learn-export-[TODAY].zip`——与导出模块相同的默认值：

```powershell
$date = Get-Date -Format "yyyy-MM-dd"
$default = "$(Get-Location)\tov-learn-export-$date.zip"
Test-Path $default
```

如果默认文件**存在** → 静默使用它（无需询问）。
如果默认文件**不存在** → 询问学习者："当前目录中没有找到导出文件。ZIP 文件的路径是什么？"

---

## 步骤 2——校验文件

运行：

```powershell
Test-Path "IMPORT_PATH"
```

如果**不存在** → 告诉学习者文件未找到并停止。

窥探 ZIP 内部，验证它是有效的 tov-learn 导出文件：

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("IMPORT_PATH")
$entries = $zip.Entries | Select-Object -ExpandProperty FullName
$zip.Dispose()
$hasSettings = ($entries | Where-Object { $_ -eq 'settings.json' }).Count -gt 0
"hasSettings=$hasSettings|count=$($entries.Count)"
```

如果没有找到 `settings.json` → 警告学习者这可能不是有效的 tov-learn 导出文件，并询问（AskUserQuestion，单选）：
- **仍然继续**——继续导入
- **取消**——取消

---

## 步骤 3——预览内容

向学习者展示 ZIP 包含的内容：

```powershell
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip = [System.IO.Compression.ZipFile]::OpenRead("IMPORT_PATH")
$entries = $zip.Entries | Select-Object -ExpandProperty FullName
$zip.Dispose()
$groups = $entries | Where-Object { $_ -ne '' } |
  Group-Object { ($_ -split '/')[0] }
foreach ($g in $groups) { "$($g.Name): $($g.Count) קבצים" }
"סך הכל: $($entries.Count) פריטים"
```

同时检查本设备上已有多少数据：

```powershell
$ex = Get-ChildItem "$HOME\skill-tutor-tutorials" -Recurse -File -ErrorAction SilentlyContinue
$ex.Count
```

---

## 步骤 4——选择导入模式

询问（AskUserQuestion，单选），使用 `session.language` 回复：

**问题：** "如何导入？"

**选项：**
1. **全部替换**——删除所有现有数据并替换为文件内容（推荐用于迁移到新设备）
2. **合并**——导入新文件并覆盖有变更的现有文件，但保留仅存在于本设备的文件（推荐）
3. **仅追加**——只导入尚不存在的文件，不覆盖任何内容
4. **取消**——不做任何更改

如果学习者选择**取消** → 停止并确认没有任何改动。

---

## 步骤 5A——全部替换

```powershell
$dest = "$HOME\skill-tutor-tutorials"
if (Test-Path $dest) { Get-ChildItem $dest | Remove-Item -Recurse -Force }
Expand-Archive -Path "IMPORT_PATH" -DestinationPath $dest -Force
$count = (Get-ChildItem $dest -Recurse -File).Count
"imported=$count"
```

---

## 步骤 5B——合并（新增 + 覆盖变更文件，保留仅存在于设备的文件）

解压到临时目录，然后复制 ZIP 中的所有文件——覆盖已存在的文件，但不动仅存在于设备上的文件：

```powershell
$temp = "$env:TEMP\tov-import-temp"
if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
Expand-Archive -Path "IMPORT_PATH" -DestinationPath $temp -Force
$dest = "$HOME\skill-tutor-tutorials"
$added = 0; $updated = 0
Get-ChildItem $temp -Recurse -File | ForEach-Object {
  $rel    = $_.FullName.Substring($temp.Length).TrimStart('\/')
  $target = Join-Path $dest $rel
  $isNew  = -not (Test-Path $target)
  $dir    = Split-Path $target -Parent
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir -Force | Out-Null }
  Copy-Item $_.FullName $target -Force
  if ($isNew) { $added++ } else { $updated++ }
}
Remove-Item $temp -Recurse -Force
"added=$added|updated=$updated"
```

---

## 步骤 5C——仅追加（不覆盖）

解压到临时目录，然后只复制本设备上尚不存在的文件：

```powershell
$temp = "$env:TEMP\tov-import-temp"
if (Test-Path $temp) { Remove-Item $temp -Recurse -Force }
Expand-Archive -Path "IMPORT_PATH" -DestinationPath $temp -Force
$dest = "$HOME\skill-tutor-tutorials"
$imported = 0; $skipped = 0
Get-ChildItem $temp -Recurse -File | ForEach-Object {
  $rel    = $_.FullName.Substring($temp.Length).TrimStart('\/')
  $target = Join-Path $dest $rel
  if (-not (Test-Path $target)) {
    $dir = Split-Path $target -Parent
    if (-not (Test-Path $dir)) { New-Item -ItemType Directory $dir -Force | Out-Null }
    Copy-Item $_.FullName $target
    $imported++
  } else { $skipped++ }
}
Remove-Item $temp -Recurse -Force
"imported=$imported|skipped=$skipped"
```

---

## 步骤 6——确认

报告成功（使用 `session.language` 回复）：

**全部替换：**
```
✅ ייבוא הושלם!

📁 [N] קבצים יובאו
📍 ~/skill-tutor-tutorials/

הקלד /learn כדי להמשיך ללמוד.
```

**合并：**
```
✅ ייבוא הושלם!

📥 נוספו: [N] קבצים חדשים
🔄 עודכנו: [N] קבצים קיימים

הקלד /learn כדי להמשיך ללמוד.
```

**仅追加：**
```
✅ ייבוא הושלם!

📥 יובאו: [N] קבצים חדשים
⏭ נדלגו: [N] קבצים (כבר קיימים)

הקלד /learn כדי להמשיך ללמוד.
```
