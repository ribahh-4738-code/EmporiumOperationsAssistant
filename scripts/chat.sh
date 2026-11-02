#!/usr/bin/env bash
# Start interactive CLI chat (requires .venv and GEMINI_API_KEY in .env).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/ensure_env_keys.sh"
ensure_env_keys "${ROOT_DIR}"

if [[ -f "${ROOT_DIR}/.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${ROOT_DIR}/.env"
  set +a
fi

if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  echo "GEMINI_API_KEY não configurada em ${ROOT_DIR}/.env" >&2
  echo "Abra .env e defina: GEMINI_API_KEY=sua_chave (veja .env.example)." >&2
  exit 1
fi

if [[ ! -x "${ROOT_DIR}/.venv/bin/emporium-chat" ]]; then
  echo "Run ./install.sh first to create .venv and install the package." >&2
  exit 1
fi

exec "${ROOT_DIR}/.venv/bin/emporium-chat" "$@"
