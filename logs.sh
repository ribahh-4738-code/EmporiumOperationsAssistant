#!/usr/bin/env bash
# Follow structured assistant log (run from a second terminal while ./chat.sh is active).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${ROOT_DIR}"

# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"
load_project_env "${ROOT_DIR}"

LOG_PATH="${ASSISTANT_LOG_PATH:-.run/assistant.jsonl}"
if [[ "${LOG_PATH}" != /* ]]; then
  LOG_PATH="${ROOT_DIR}/${LOG_PATH}"
fi

mkdir -p "$(dirname "${LOG_PATH}")"
touch "${LOG_PATH}"

if [[ "${1:-}" == "--pretty" ]]; then
  if [[ ! -x "${ROOT_DIR}/.venv/bin/python" ]]; then
    echo "Run ./install.sh first." >&2
    exit 1
  fi
  tail -F "${LOG_PATH}" | "${ROOT_DIR}/.venv/bin/python" -m emporium_operations_assistant.observability.pretty
else
  echo "Following ${LOG_PATH} (use --pretty for readable lines)"
  tail -F "${LOG_PATH}"
fi
