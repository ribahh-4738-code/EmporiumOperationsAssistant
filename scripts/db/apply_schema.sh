#!/usr/bin/env bash
# Apply db/schema.sql to the configured PostgreSQL (Docker or host).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/psql.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults

DRY_RUN="${DRY_RUN:-0}"
SCHEMA_FILE="${ROOT_DIR}/db/schema.sql"

if [[ ! -f "${SCHEMA_FILE}" ]]; then
  echo "Schema file not found: ${SCHEMA_FILE}" >&2
  exit 1
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> apply ${SCHEMA_FILE} to database ${POSTGRES_DB} (idempotent DDL)"
  exit 0
fi

echo "[run] Applying schema from db/schema.sql (idempotent)..."
emporium_psql_file "${SCHEMA_FILE}"
echo "[run] Schema applied to '${POSTGRES_DB}'."
