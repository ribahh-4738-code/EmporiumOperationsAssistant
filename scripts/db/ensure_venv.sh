#!/usr/bin/env bash
# Create project virtualenv and install package in editable mode.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv"
DRY_RUN="${DRY_RUN:-0}"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> ensure .venv and pip install -e ."
  exit 0
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required." >&2
  exit 1
fi

if [[ ! -d "${VENV_DIR}" ]]; then
  echo "[run] Creating virtual environment at .venv"
  python3 -m venv "${VENV_DIR}"
else
  echo "[skip] Virtual environment .venv already exists"
fi

echo "[run] Installing package (editable)..."
"${VENV_DIR}/bin/pip" install -q --upgrade pip
"${VENV_DIR}/bin/pip" install -q -e "${ROOT_DIR}"
