#!/usr/bin/env bash
# Run psql against project PostgreSQL (Docker container or host).
set -euo pipefail

emporium_uses_docker_psql() {
  docker ps --format '{{.Names}}' 2>/dev/null | grep -qx "${EMPORIUM_DOCKER_CONTAINER}"
}

emporium_psql() {
  if emporium_uses_docker_psql; then
    docker exec "${EMPORIUM_DOCKER_CONTAINER}" \
      psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" "$@"
  else
    export_pg_vars
    psql -v ON_ERROR_STOP=1 -d "${POSTGRES_DB}" "$@"
  fi
}

emporium_psql_postgres_db() {
  if emporium_uses_docker_psql; then
    docker exec "${EMPORIUM_DOCKER_CONTAINER}" \
      psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d postgres "$@"
  else
    export_pg_vars
    psql -v ON_ERROR_STOP=1 -d postgres "$@"
  fi
}

emporium_psql_file() {
  local sql_file="$1"
  if emporium_uses_docker_psql; then
    docker exec -i "${EMPORIUM_DOCKER_CONTAINER}" \
      psql -v ON_ERROR_STOP=1 -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" < "${sql_file}"
  else
    export_pg_vars
    psql -v ON_ERROR_STOP=1 -d "${POSTGRES_DB}" -f "${sql_file}"
  fi
}
