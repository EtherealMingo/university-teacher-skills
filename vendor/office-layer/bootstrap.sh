#!/usr/bin/env bash
# office-layer 依赖引导脚本
# 用法：bash vendor/office-layer/bootstrap.sh
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="${HERE}/.venv"
PIP_INDEX="${PIP_INDEX:-https://pypi.tuna.tsinghua.edu.cn/simple}"
HOST_ARGS=()
case "${PIP_INDEX}" in
  *tuna*|*aliyun*|*douban*) HOST_ARGS=(--trusted-host "$(echo "${PIP_INDEX}" | awk -F/ '{print $3}')") ;;
esac

if [ ! -x "${VENV}/bin/python" ]; then
  echo "[1/3] 创建虚拟环境 ${VENV}"
  python3 -m venv "${VENV}"
else
  echo "[1/3] 复用已有虚拟环境 ${VENV}"
fi

echo "[2/3] 安装依赖（默认清华镜像，可用 PIP_INDEX 覆盖）"
"${VENV}/bin/python" -m pip install -q --disable-pip-version-check \
  --timeout 90 --retries 5 -i "${PIP_INDEX}" "${HOST_ARGS[@]}" \
  python-docx python-pptx openpyxl pillow pypdf matplotlib

echo "[3/3] 自检"
MPLCONFIGDIR="${MPLCONFIGDIR:-/tmp/mplcache}" "${VENV}/bin/python" - <<'PY'
import os, sys
os.makedirs(os.environ.get("MPLCONFIGDIR", "/tmp/mplcache"), exist_ok=True)
ok = True
for m in ("docx", "pptx", "openpyxl", "PIL", "pypdf", "matplotlib"):
    try:
        mod = __import__(m)
        print(f"  OK   {m:11} {getattr(mod, '__version__', '')}")
    except ImportError as e:
        ok = False
        print(f"  FAIL {m:11} {e}")
from docx import Document
c = hasattr(Document(), "add_comment")
print(f"  {'OK  ' if c else 'FAIL'} 原生批注支持: {c}  (需 python-docx >= 1.2.0)")
sys.exit(0 if (ok and c) else 1)
PY

cat <<'EOF'

就绪。调用方式：

  PY="vendor/office-layer/.venv/bin/python"
  $PY vendor/office-layer/scripts/docx_kit.py inspect --in 某文件.docx

受限环境请先导出可写的 matplotlib 缓存目录：
  export MPLCONFIGDIR=/tmp/mplcache && mkdir -p /tmp/mplcache
EOF
