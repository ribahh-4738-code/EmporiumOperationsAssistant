#!/usr/bin/env bash
# Run pytest (default: unit + light RAG; no Postgres required).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

if [[ ! -x "${ROOT_DIR}/.venv/bin/pytest" ]]; then
  echo "Install dev dependencies first:" >&2
  echo "  ${ROOT_DIR}/.venv/bin/pip install -e \".[dev]\"" >&2
  exit 1
fi

if [[ "${1:-}" == "--integration" ]]; then
  shift
  exec "${ROOT_DIR}/.venv/bin/pytest" -q -m integration "$@"
fi

exec "${ROOT_DIR}/.venv/bin/pytest" -q -m "not integration" "$@"
