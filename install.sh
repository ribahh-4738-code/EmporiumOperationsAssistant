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

print_plan() {
  cat <<'EOF'
Installation plan (incremental):

  1. Prerequisites (Docker, Python 3)
  2. Environment file (.env)
  3. PostgreSQL Docker container
  4. Database emporium_operation
  5. Schema (db/schema.sql, DDL only)
  6. Pending migrations (db/migrations/*.sql)
  7. Python virtualenv and dependencies
  8. Seed import (truncate CSV-backed tables + load data/*.csv)
  9. Verify row counts vs manifest
 10. Assistant defaults (profile + module prompts, idempotent)

Steps marked [skip] are omitted when already satisfied.

EOF
}

write_default_env() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> create ${ENV_FILE} from ${ENV_EXAMPLE} if missing"
    return 0
  fi
  if [[ -f "${ENV_FILE}" ]]; then
    echo "[skip] .env already exists."
    return 0
  fi
  if [[ ! -f "${ENV_EXAMPLE}" ]]; then
    echo ".env.example not found." >&2
    exit 1
  fi
  sed 's/\r$//' "${ENV_EXAMPLE}" > "${ENV_FILE}"
  echo "[run] Created ${ENV_FILE} from .env.example."
}

main() {
  print_plan
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "(dry-run mode — no changes will be made)"
  fi

  log_step "Step 1: Prerequisites"
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> command -v docker && command -v python3"
  else
    command -v docker >/dev/null || { echo "Docker is required." >&2; exit 1; }
    command -v python3 >/dev/null || { echo "python3 is required." >&2; exit 1; }
    echo "[run] Docker: $(docker --version)"
    echo "[run] Python: $(python3 --version)"
  fi

  log_step "Step 2: Environment file"
  write_default_env
  if [[ "${DRY_RUN}" != "1" ]]; then
    # shellcheck disable=SC1091
    source "${ROOT_DIR}/scripts/lib/ensure_env_keys.sh"
    ensure_env_keys "${ROOT_DIR}"
  fi

  load_project_env "${ROOT_DIR}"
  apply_postgres_defaults

  log_step "Step 3: PostgreSQL container"
  "${ROOT_DIR}/scripts/db/ensure_postgres_container.sh"

  log_step "Step 4: Database"
  "${ROOT_DIR}/scripts/db/create_database.sh"

  log_step "Step 5: Schema"
  "${ROOT_DIR}/scripts/db/apply_schema.sh"

  log_step "Step 6: Migrations"
  "${ROOT_DIR}/scripts/db/apply_migrations.sh"

  log_step "Step 7: Python environment"
  "${ROOT_DIR}/scripts/db/ensure_venv.sh"

  log_step "Step 8: Import seed data (truncate + CSV load)"
  "${ROOT_DIR}/scripts/db/import_seed.sh"

  log_step "Step 9: Verify seed data"
  "${ROOT_DIR}/scripts/db/verify_seed.sh"

  log_step "Step 10: Assistant defaults"
  "${ROOT_DIR}/scripts/db/seed_assistant.sh"

  if [[ "${DRY_RUN}" != "1" ]]; then
    echo ""
    echo "Install finished. PostgreSQL at localhost:${POSTGRES_PORT} (see .env)."
  fi
}

main "$@"
