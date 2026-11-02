#!/usr/bin/env bash
# Apply db/schema.sql to the configured PostgreSQL (Docker or host).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults

DRY_RUN="${DRY_RUN:-0}"
SCHEMA_FILE="${ROOT_DIR}/db/schema.sql"

if [[ ! -f "${SCHEMA_FILE}" ]]; then
  echo "Schema file not found: ${SCHEMA_FILE}" >&2
  exit 1
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> apply ${SCHEMA_FILE} to database ${POSTGRES_DB}"
  if docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "${EMPORIUM_DOCKER_CONTAINER}"; then
    echo "  -> docker exec -i ${EMPORIUM_DOCKER_CONTAINER} psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f - < db/schema.sql"
  else
    echo "  -> PGPASSWORD=*** psql -h ${POSTGRES_HOST} -p ${POSTGRES_PORT} -U ${POSTGRES_USER} -d ${POSTGRES_DB} -f db/schema.sql"
  fi
  exit 0
fi

if docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_DOCKER_CONTAINER}"; then
  docker exec -i "${EMPORIUM_DOCKER_CONTAINER}" \
    psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" < "${SCHEMA_FILE}"
else
  export_pg_vars
  psql -v ON_ERROR_STOP=1 -d "${POSTGRES_DB}" -f "${SCHEMA_FILE}"
fi

echo "Schema applied to '${POSTGRES_DB}'."
