#!/usr/bin/env bash
# Stop and remove Emporium project Docker containers (names from .env).
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
# shellcheck disable=SC1091
source "${ROOT_DIR}/scripts/lib/env.sh"

load_project_env "${ROOT_DIR}"
apply_postgres_defaults
apply_chroma_defaults

DRY_RUN=0
PURGE_VOLUMES=0
for arg in "$@"; do
  case "${arg}" in
    --dry-run) DRY_RUN=1 ;;
    --purge-volumes) PURGE_VOLUMES=1 ;;
    *)
      echo "Unknown option: ${arg}" >&2
      echo "Usage: $0 [--dry-run] [--purge-volumes]" >&2
      exit 1
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is not installed or not in PATH." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Cannot connect to the Docker daemon. Is Docker running?" >&2
  exit 1
fi

CONTAINERS=(
  "${EMPORIUM_CHROMA_ADMIN_CONTAINER}"
  "${EMPORIUM_CHROMA_CONTAINER}"
  "${EMPORIUM_DOCKER_CONTAINER}"
)

_remove_container() {
  local name="$1"
  if ! docker ps -a --format '{{.Names}}' | grep -qx "${name}"; then
    echo "[skip] Container '${name}' not found."
    return 0
  fi
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> docker rm -f ${name}"
    return 0
  fi
  echo "[run] Removing container '${name}'..."
  docker rm -f "${name}" >/dev/null
}

_remove_volume() {
  local vol="$1"
  if ! docker volume inspect "${vol}" >/dev/null 2>&1; then
    echo "[skip] Volume '${vol}' not found."
    return 0
  fi
  if [[ "${DRY_RUN}" == "1" ]]; then
    echo "  -> docker volume rm ${vol}"
    return 0
  fi
  echo "[run] Removing volume '${vol}'..."
  docker volume rm "${vol}" >/dev/null
}

echo "==> Emporium Docker stop (Admin → Chroma → Postgres)"
for name in "${CONTAINERS[@]}"; do
  _remove_container "${name}"
done

if [[ "${PURGE_VOLUMES}" == "1" ]]; then
  echo "==> Purge project volumes"
  _remove_volume "${EMPORIUM_CHROMA_VOLUME}"
  _remove_volume "${EMPORIUM_DOCKER_VOLUME}"
fi

if [[ "${DRY_RUN}" == "1" ]]; then
  echo "(dry-run — no changes made)"
else
  echo "[run] Done. Ports ${CHROMA_ADMIN_PORT}, ${CHROMA_PORT}, ${POSTGRES_PORT} should be free for this project."
fi
