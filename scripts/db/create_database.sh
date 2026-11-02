#!/usr/bin/env bash
# Create PostgreSQL database emporium_operation (idempotent).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ROOT_DIR}/.env"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "${ENV_FILE}"
  set +a
fi

POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_DB="${POSTGRES_DB:-emporium_operation}"

export PGHOST="${POSTGRES_HOST}"
export PGPORT="${POSTGRES_PORT}"
export PGUSER="${POSTGRES_USER}"
if [[ -n "${POSTGRES_PASSWORD:-}" ]]; then
  export PGPASSWORD="${POSTGRES_PASSWORD}"
fi

exists="$(psql -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" || true)"
if [[ "${exists}" == "1" ]]; then
  echo "Database '${POSTGRES_DB}' already exists."
else
  psql -d postgres -c "CREATE DATABASE ${POSTGRES_DB} ENCODING 'UTF8' TEMPLATE template0;"
  echo "Created database '${POSTGRES_DB}'."
fi
