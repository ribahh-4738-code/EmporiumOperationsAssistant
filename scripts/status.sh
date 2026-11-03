#!/usr/bin/env bash
# Health check: PostgreSQL, Chroma, RAG collection chunk count.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/ensure_env_keys.sh"
ensure_env_keys "${ROOT_DIR}"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"
load_project_env "${ROOT_DIR}"
apply_postgres_defaults
apply_chroma_defaults

if [[ ! -x "${ROOT_DIR}/.venv/bin/python" ]]; then
  echo "Run ./install.sh first." >&2
  exit 1
fi

exec "${ROOT_DIR}/.venv/bin/python" -m emporium_operations_assistant.observability.status
