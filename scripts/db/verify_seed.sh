#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults
export POSTGRES_HOST POSTGRES_PORT POSTGRES_USER POSTGRES_PASSWORD POSTGRES_DB

DRY_RUN="${DRY_RUN:-0}"
VENV_PYTHON="${ROOT_DIR}/.venv/bin/python"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> verify seed row counts against manifest"
  exit 0
fi

"${VENV_PYTHON}" -m emporium_operations_assistant.seed.verify
