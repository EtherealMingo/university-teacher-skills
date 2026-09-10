#!/usr/bin/env bash
# ============================================================================
# 高校教师 AI 提效技能包 — 自举安装脚本
#
# 设计给 Agent 用，也给人用。装一份到固定位置，再往各 agent 技能目录做软链，
# 避免 105MB 的 venv 被复制十几遍。
#
# 用法：
#   bash install.sh                        # 自动探测并安装到全部 agent 技能目录
#   bash install.sh --target ~/.claude/skills   # 只装到指定目录
#   bash install.sh --prefix ~/opt/ut-skills    # 自定义安装位置
#   bash install.sh --no-deps              # 不建 venv（之后手动跑 bootstrap.sh）
#   bash install.sh --uninstall            # 卸载（只删软链与安装目录）
#
# 远程一键（仓库公开，可直接拉）：
#   curl -fsSL https://raw.githubusercontent.com/EtherealMingo/university-teacher-skills/main/install.sh | bash
# ============================================================================
set -euo pipefail

REPO_SLUG="EtherealMingo/university-teacher-skills"
REPO_URL="https://github.com/${REPO_SLUG}.git"
TARBALL="https://codeload.github.com/${REPO_SLUG}/tar.gz/refs/heads/main"
SKILL_DIR_NAME="university-teacher"

DEFAULT_PREFIX="${HOME}/.local/share/university-teacher-skills"
# 常见 agent 技能目录（存在才会被安装）
CANDIDATE_DIRS=(
  "${HOME}/.claude/skills"
  "${HOME}/.codex/skills"
  "${HOME}/.agents/skills"
  "${HOME}/.cc-switch/skills"
  "${HOME}/.cursor/skills"
  "${HOME}/.trae-cn/skills"
  "${HOME}/.kimi-code/skills"
  "${HOME}/.junie/skills"
  "${HOME}/.lingma/skills"
  "${HOME}/.lmstudio/skills"
  "${HOME}/Doubao/skills"
  "${HOME}/skills"
)

PREFIX="${DEFAULT_PREFIX}"
TARGET=""
DO_DEPS=1
DO_VERIFY=1
DO_LINK=1
FORCE=0
UNINSTALL=0

c_ok=$'\033[32m'; c_warn=$'\033[33m'; c_err=$'\033[31m'; c_dim=$'\033[2m'; c_off=$'\033[0m'
log()  { printf '  %s\n' "$*"; }
ok()   { printf "  [%sOK%s] %s\n"   "$c_ok"   "$c_off" "$*"; }
warn() { printf "  [%sWARN%s] %s\n" "$c_warn" "$c_off" "$*"; }
err()  { printf "  [%sFAIL%s] %s\n" "$c_err"  "$c_off" "$*" >&2; }
die()  { err "$*"; exit 1; }

usage() { sed -n '3,18p' "$0" | sed 's/^# \{0,1\}//'; exit 0; }

while [ $# -gt 0 ]; do
  case "$1" in
    --prefix)    PREFIX="$2"; shift 2 ;;
    --target)    TARGET="$2"; shift 2 ;;
    --no-deps)   DO_DEPS=0; shift ;;
    --no-verify) DO_VERIFY=0; shift ;;
    --no-link)   DO_LINK=0; shift ;;
    --force)     FORCE=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    -h|--help)   usage ;;
    *) die "未知参数：$1（用 --help 看用法）" ;;
  esac
done

# ---------------------------------------------------------------- 卸载
if [ "$UNINSTALL" = 1 ]; then
  log "卸载中……"
  for d in "${CANDIDATE_DIRS[@]}"; do
    link="${d}/${SKILL_DIR_NAME}"
    if [ -L "$link" ]; then rm -f "$link"; ok "移除软链 $link"; fi
  done
  if [ -d "$PREFIX" ]; then rm -rf "$PREFIX"; ok "移除安装目录 $PREFIX"; fi
  log "完成。未触碰任何个人文件。"
  exit 0
fi

echo
log "===== 高校教师 AI 提效技能包 · 安装 ====="
echo

# ---------------------------------------------------------------- 1. 取得源
SCRIPT_DIR=""
if [ -n "${BASH_SOURCE[0]:-}" ] && [ -f "${BASH_SOURCE[0]}" ]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

SRC=""
if [ -n "$SCRIPT_DIR" ] && [ -f "${SCRIPT_DIR}/SKILL.md" ] \
   && [ -f "${SCRIPT_DIR}/vendor/office-layer/scripts/docx_kit.py" ]; then
  SRC="$SCRIPT_DIR"
  log "[1/5] 从本地仓库安装：$SRC"
else
  log "[1/5] 本地无完整仓库，从 GitHub 下载……"
  TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
  if command -v git >/dev/null 2>&1; then
    git clone --depth 1 -q "$REPO_URL" "$TMP/repo" \
      && SRC="$TMP/repo" && ok "git clone 完成"
  fi
  if [ -z "$SRC" ]; then
    warn "git 不可用或克隆失败，改用 tarball"
    curl -fsSL --max-time 300 -o "$TMP/repo.tar.gz" "$TARBALL" || die "下载失败，请检查网络"
    mkdir -p "$TMP/repo"
    tar xzf "$TMP/repo.tar.gz" -C "$TMP/repo" --strip-components=1 || die "解压失败"
    SRC="$TMP/repo"
    ok "tarball 下载并解压完成"
  fi
fi
[ -f "${SRC}/SKILL.md" ] || die "源目录不完整（缺 SKILL.md）：$SRC"

# ---------------------------------------------------------------- 2. 落盘
copy_payload() {
  # 排除 .git、所有 venv（含包根可能存在的残留）、Python 缓存与 macOS 杂项
  mkdir -p "$2"
  ( cd "$1" && tar cf - \
      --exclude='./.git' \
      --exclude='*/.git' \
      --exclude='./.venv' \
      --exclude='*/.venv' \
      --exclude='__pycache__' \
      --exclude='*.pyc' \
      --exclude='.DS_Store' \
      . ) | ( cd "$2" && tar xf - )
}

echo
log "[2/5] 安装到 $PREFIX"
if [ "$SRC" = "$PREFIX" ]; then
  ok "源即安装位置，跳过复制"
elif [ "$FORCE" = 1 ]; then
  warn "--force：清除目标（含已装依赖），全量重装"
  rm -rf "$PREFIX"
  copy_payload "$SRC" "$PREFIX"
  ok "已全量安装到 $PREFIX"
elif [ -e "$PREFIX" ]; then
  # 幂等更新：默认保留 venv，只同步代码，避免每次重装都重新下载依赖
  VENV_TMP=""
  if [ -x "${PREFIX}/vendor/office-layer/.venv/bin/python" ]; then
    VENV_TMP="$(mktemp -d)"
    mv "${PREFIX}/vendor/office-layer/.venv" "${VENV_TMP}/.venv"
  fi
  rm -rf "$PREFIX"
  copy_payload "$SRC" "$PREFIX"
  if [ -n "$VENV_TMP" ]; then
    mv "${VENV_TMP}/.venv" "${PREFIX}/vendor/office-layer/.venv"
    rm -rf "$VENV_TMP"
    ok "代码已更新，已有 venv 已保留"
  else
    ok "代码已更新"
  fi
else
  copy_payload "$SRC" "$PREFIX"
  ok "已安装到 $PREFIX"
fi

# ---------------------------------------------------------------- 3. 依赖
echo
if [ "$DO_DEPS" = 1 ]; then
  log "[3/5] 安装文档产出层依赖（python-docx / pptx / openpyxl / matplotlib）"
  if [ -x "${PREFIX}/vendor/office-layer/.venv/bin/python" ] \
     && "${PREFIX}/vendor/office-layer/.venv/bin/python" -c "import docx,pptx,openpyxl" 2>/dev/null; then
    ok "依赖已存在，跳过"
  else
    if bash "${PREFIX}/vendor/office-layer/bootstrap.sh" >/tmp/ut-bootstrap.log 2>&1; then
      ok "依赖安装完成"
    else
      warn "依赖安装失败，详见 /tmp/ut-bootstrap.log"
      warn "技能文件已就位，但 docx/pptx/xlsx 产出不可用；可稍后重试："
      warn "  bash ${PREFIX}/vendor/office-layer/bootstrap.sh"
    fi
  fi
else
  log "[3/5] --no-deps，跳过依赖安装"
fi

# ---------------------------------------------------------------- 4. 软链
echo
if [ "$DO_LINK" = 1 ] && [ -z "$TARGET" ]; then
  log "[4/5] 链接到各 agent 技能目录"
  linked=0
  for d in "${CANDIDATE_DIRS[@]}"; do
    [ -d "$d" ] || continue
    link="${d}/${SKILL_DIR_NAME}"
    if [ -L "$link" ]; then
      rm -f "$link"
    elif [ -e "$link" ]; then
      warn "跳过 $d（已存在同名非软链目录）"
      continue
    fi
    ln -s "$PREFIX" "$link" && { ok "${d/#$HOME/~}/${SKILL_DIR_NAME}"; linked=$((linked+1)); }
  done
  [ "$linked" -gt 0 ] || warn "未发现任何 agent 技能目录，技能已装在 $PREFIX，请手动加入搜索路径"
  log "${c_dim}软链指向同一份安装，venv 不会重复占用空间${c_off}"
elif [ -n "$TARGET" ]; then
  log "[4/5] 安装到指定目录 $TARGET"
  mkdir -p "$TARGET"
  link="${TARGET}/${SKILL_DIR_NAME}"
  rm -rf "$link"
  if ln -s "$PREFIX" "$link" 2>/dev/null; then
    ok "$link -> $PREFIX"
  else
    cp -R "$PREFIX" "$link" && ok "已复制到 $link"
  fi
else
  log "[4/5] --no-link，跳过链接"
fi

# ---------------------------------------------------------------- 5. 自检
echo
if [ "$DO_VERIFY" = 1 ]; then
  log "[5/5] 完整性自检"
  if command -v python3 >/dev/null 2>&1; then
    ( cd "$PREFIX" && python3 verify.py 2>&1 | tail -20 ) || warn "自检有失败项，见上"
  else
    warn "无 python3，跳过自检"
  fi
else
  log "[5/5] --no-verify，跳过自检"
fi

# ---------------------------------------------------------------- 收尾
echo
log "===== 安装完成 ====="
cat <<EOF

  安装位置：$PREFIX
  技能入口：$PREFIX/SKILL.md

  给 Agent 的说明：
    - 本技能包入口是 SKILL.md（总控路由），它会按教师意图路由到 skills/<name>/SKILL.md
    - 全部 vendor/ 路径均相对本包根目录（$PREFIX），执行命令前先 cd 到该目录
    - 文件产出必须走 vendor/office-layer/，解释器用：
        $PREFIX/vendor/office-layer/.venv/bin/python

  给人看的用法：
    cd $PREFIX && cat SKILL.md      # 从路由表开始
    cd $PREFIX && python3 verify.py # 随时自检

EOF
