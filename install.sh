#!/usr/bin/env bash
# Emporium Operations Assistant — incremental local installation.
# Usage:
#   ./install.sh              Run all install steps
#   ./install.sh --dry-run    Show commands without executing
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

DRY_RUN=0
if [[ "${1:-}" == "--dry-run" ]] || [[ "${1:-}" == "preview" ]]; then
  DRY_RUN=1
fi
export DRY_RUN

ENV_FILE="${ROOT_DIR}/.env"
ENV_EXAMPLE="${ROOT_DIR}/.env.example"

log_step() {
  echo ""
  echo "==> $*"
}

run_cmd() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> $*"
  else
    eval "$@"
  fi
}

print_plan() {
  cat <<'EOF'
Installation plan (incremental; more steps will be added in future milestones):

  1. Check prerequisites (Docker)
  2. Create .env from .env.example if missing (dev defaults, no prompts)
  3. Start PostgreSQL in Docker (dedicated container + volume)
  4. Ensure database exists (emporium_operation)
  5. Apply db/schema.sql
  6. Verify public tables exist

Connection after install (from .env):
  Host: localhost
  Port: 5435 (default; avoids conflict with local PostgreSQL on 5432)
  User / password / database: see .env (defaults suitable for local dev only)

EOF
}

write_default_env() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> write ${ENV_FILE} from ${ENV_EXAMPLE} with dev PostgreSQL defaults"
    return 0
  fi
  if [[ -f "${ENV_FILE}" ]]; then
    echo "  .env already exists; keeping current file."
    return 0
  fi
  if [[ ! -f "${ENV_EXAMPLE}" ]]; then
    echo ".env.example not found." >&2
    exit 1
  fi
  sed 's/\r$//' "${ENV_EXAMPLE}" > "${ENV_FILE}"
  echo "  Created ${ENV_FILE} from .env.example (edit if you change ports or credentials)."
}

main() {
  print_plan

  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "(dry-run mode — no changes will be made)"
  fi

  log_step "Step 1: Prerequisites"
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> command -v docker"
  elif ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed or not in PATH." >&2
    exit 1
  else
    echo "  Docker: $(docker --version)"
  fi

  log_step "Step 2: Environment file"
  write_default_env

  load_project_env "${ROOT_DIR}"
  apply_postgres_defaults

  log_step "Step 3: PostgreSQL container"
  run_cmd "\"${ROOT_DIR}/scripts/db/ensure_postgres_container.sh\""

  log_step "Step 4: Database"
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> ${ROOT_DIR}/scripts/db/create_database.sh (idempotent; Docker may already create ${POSTGRES_DB})"
  else
    "${ROOT_DIR}/scripts/db/create_database.sh"
  fi

  log_step "Step 5: Schema"
  run_cmd "\"${ROOT_DIR}/scripts/db/apply_schema.sh\""

  log_step "Step 6: Verification"
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> list public tables and row counts in ${POSTGRES_DB}"
  else
    if docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_DOCKER_CONTAINER}"; then
      docker exec "${EMPORIUM_DOCKER_CONTAINER}" \
        psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c "\dt"
      docker exec "${EMPORIUM_DOCKER_CONTAINER}" \
        psql -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c \
        "SELECT relname AS table_name FROM pg_stat_user_tables ORDER BY relname;"
    else
      export_pg_vars
      psql -d "${POSTGRES_DB}" -c "\dt"
    fi
    echo ""
    echo "Install finished. PostgreSQL is available at localhost:${POSTGRES_PORT} (credentials in .env)."
  fi
}

main "$@"
