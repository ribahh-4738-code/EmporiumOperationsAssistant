#!/usr/bin/env bash
# Start (or create) the project PostgreSQL Docker container.
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults

DRY_RUN="${DRY_RUN:-0}"

log_step() {
  echo "[install] $*"
}

run_cmd() {
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> $*"
  else
    eval "$@"
  fi
}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required. Install Docker and run ./install.sh again." >&2
  exit 1
fi

log_step "Ensure Docker container '${EMPORIUM_DOCKER_CONTAINER}' is running (image ${EMPORIUM_DOCKER_IMAGE}, port ${POSTGRES_PORT})"

if docker ps -a --format '{{.Names}}' | grep -qx "${EMPORIUM_DOCKER_CONTAINER}"; then
  if docker ps --format '{{.Names}}' | grep -qx "${EMPORIUM_DOCKER_CONTAINER}"; then
    log_step "Container already running."
  else
    run_cmd "docker start \"${EMPORIUM_DOCKER_CONTAINER}\""
  fi
else
  run_cmd "docker run -d \\
    --name \"${EMPORIUM_DOCKER_CONTAINER}\" \\
    -e POSTGRES_USER=\"${POSTGRES_USER}\" \\
    -e POSTGRES_PASSWORD=\"${POSTGRES_PASSWORD}\" \\
    -e POSTGRES_DB=\"${POSTGRES_DB}\" \\
    -p \"${POSTGRES_PORT}:5432\" \\
    -v \"${EMPORIUM_DOCKER_VOLUME}:/var/lib/postgresql/data\" \\
    \"${EMPORIUM_DOCKER_IMAGE}\""
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "  -> wait until PostgreSQL accepts connections on localhost:${POSTGRES_PORT}"
  exit 0
fi

log_step "Waiting for PostgreSQL to accept connections..."
for _ in $(seq 1 60); do
  if docker exec "${EMPORIUM_DOCKER_CONTAINER}" pg_isready -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; then
    log_step "PostgreSQL is ready."
    exit 0
  fi
  sleep 1
done

echo "Timed out waiting for PostgreSQL in container '${EMPORIUM_DOCKER_CONTAINER}'." >&2
exit 1
