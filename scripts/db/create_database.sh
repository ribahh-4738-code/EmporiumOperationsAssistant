#!/usr/bin/env bash
# Create PostgreSQL database emporium_operation (idempotent).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/psql.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults

DRY_RUN="${DRY_RUN:-0}"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> ensure database '${POSTGRES_DB}' exists"
  exit 0
fi

exists="$(emporium_psql_postgres_db -tAc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" || true)"
if [[ "${exists}" == "1" ]]; then
  echo "[skip] Database '${POSTGRES_DB}' already exists."
else
  emporium_psql_postgres_db -c "CREATE DATABASE ${POSTGRES_DB} ENCODING 'UTF8' TEMPLATE template0;"
  echo "[run] Created database '${POSTGRES_DB}'."
fi
