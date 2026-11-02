#!/usr/bin/env bash
# Create PostgreSQL database emporium_operation (idempotent).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults

DRY_RUN="${DRY_RUN:-0}"

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> ensure database '${POSTGRES_DB}' exists"
  exit 0
fi

psql_admin() {
  if docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_DOCKER_CONTAINER}"; then
    docker exec "${EMPORIUM_DOCKER_CONTAINER}" psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d postgres "$@"
  else
    export_pg_vars
    psql -v ON_ERROR_STOP=1 -d postgres "$@"
  fi
}

exists="$(psql_admin -tAc "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}'" || true)"
if [[ "${exists}" == "1" ]]; then
  echo "Database '${POSTGRES_DB}' already exists."
else
  psql_admin -c "CREATE DATABASE ${POSTGRES_DB} ENCODING 'UTF8' TEMPLATE template0;"
  echo "Created database '${POSTGRES_DB}'."
fi
