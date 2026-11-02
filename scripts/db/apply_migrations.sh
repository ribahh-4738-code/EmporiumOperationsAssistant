#!/usr/bin/env bash
# Apply pending SQL files from db/migrations/.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/psql.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults

DRY_RUN="${DRY_RUN:-0}"
MIGRATIONS_DIR="${ROOT_DIR}/db/migrations"

if [[ ! -d "${MIGRATIONS_DIR}" ]]; then
  echo "[skip] No migrations directory."
  exit 0
fi

shopt -s nullglob
migration_files=("${MIGRATIONS_DIR}"/[0-9][0-9][0-9]_*.sql)
shopt -u nullglob

if [[ ${#migration_files[@]} -eq 0 ]]; then
  echo "[skip] No migration SQL files in db/migrations/."
  exit 0
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> check and apply pending migrations from db/migrations/"
  for f in "${migration_files[@]}"; do
    echo "  -> maybe apply $(basename "$f")"
  done
  exit 0
fi

for migration_file in "${migration_files[@]}"; do
  version="$(basename "${migration_file}")"
  applied="$(emporium_psql -tAc "SELECT 1 FROM schema_migrations WHERE version = '${version}'" 2>/dev/null || true)"
  if [[ "${applied}" == "1" ]]; then
    echo "[skip] Migration already applied: ${version}"
    continue
  fi
  echo "[run] Applying migration: ${version}"
  emporium_psql_file "${migration_file}"
  emporium_psql -c "INSERT INTO schema_migrations (version) VALUES ('${version}');"
done
